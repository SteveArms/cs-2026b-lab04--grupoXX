"""Iteración 3 de ADD — QA-02 (auditoría externa) y QA-06 (secreto en la exportación).

Prototipo (no simulación de colas): construye el registro de auditoría de una jornada de
25 000 votos y ataca el registro para medir qué alteraciones detecta el auditor externo:

* "tabla_simple": eventos sin protección (lo que hay hoy con el puerto RegistroAuditoria).
* "cadena": cada evento guarda hash = SHA-256(hash_anterior + evento) (append-only).
* "cadena_anclada": además, el hash de cabeza se entrega al auditor externo cada 15 min y al cierre.

También mide si la exportación de papeletas permite adivinar el voto por su posición.
Los eventos NUNCA llevan la opción ni el correo (ADR-002).
"""
from __future__ import annotations

import hashlib
import random
import time

PADRON = 25_000
JORNADA_S = 8 * 3600
GENESIS = "0" * 64
SUPUESTOS = {
    "votantes_que_votan": 25_000,
    "rechazos": 2_000,             # duplicados, fuera de ventana, no habilitados
    "periodo_anclaje_s": 900,      # el hash de cabeza se entrega al auditor cada 15 min (decisión de la iteración 3)
    "opciones": {"Lista A": 0.46, "Lista B": 0.38, "Blanco": 0.10, "Nulo": 0.06},
    "lock_ms_por_voto": 60,        # la transacción del voto retiene la cabeza de la cadena (🔶)
}


def _h(prev: str, evento: dict) -> str:
    """hash = SHA-256(hash_anterior | seq | t | tipo | eleccion_id). Serialización canónica y fija."""
    texto = f"{prev}|{evento['seq']}|{evento['t']}|{evento['tipo']}|{evento['eleccion_id']}"
    return hashlib.sha256(texto.encode()).hexdigest()


def generar_eventos(semilla: int = 1) -> list[dict]:
    rnd = random.Random(semilla)
    n = SUPUESTOS["votantes_que_votan"] + SUPUESTOS["rechazos"]
    tiempos = sorted(rnd.uniform(0, JORNADA_S) for _ in range(n))
    motivos = ["INTENTO_VOTO_DUPLICADO", "VOTO_FUERA_DE_VENTANA", "VOTANTE_NO_HABILITADO"]
    tipos = ["VOTO_EMITIDO"] * SUPUESTOS["votantes_que_votan"] + [rnd.choice(motivos) for _ in range(SUPUESTOS["rechazos"])]
    rnd.shuffle(tipos)
    return [{"seq": i, "t": round(t), "tipo": tipo, "eleccion_id": "E-2026-DELEGADOS"} for i, (t, tipo) in enumerate(zip(tiempos, tipos))]


def encadenar(eventos: list[dict]) -> list[dict]:
    prev, salida = GENESIS, []
    for e in eventos:
        h = _h(prev, e)
        salida.append({**e, "hash": h})
        prev = h
    return salida


def verificar(registro: list[dict], anclas: dict[int, str] | None = None, encadenado: bool = True) -> bool:
    """Lo que hace el auditor externo: recalcula la cadena y la compara con las anclas recibidas."""
    if not encadenado:
        # sin cadena solo puede comprobar que las secuencias son consecutivas
        return [r["seq"] for r in registro] == list(range(len(registro)))
    prev = GENESIS
    for r in registro:
        e = {k: v for k, v in r.items() if k != "hash"}
        if _h(prev, e) != r["hash"]:
            return False
        prev = r["hash"]
    if anclas:
        por_seq = {r["seq"]: r["hash"] for r in registro}
        return all(por_seq.get(seq) == h for seq, h in anclas.items())
    return True


def anclas_de(registro: list[dict], periodo_s: int) -> list[tuple[float, int, str]]:
    """(instante de publicación, seq de cabeza, hash) cada `periodo_s` y al cierre."""
    salida, corte = [], periodo_s
    for i, r in enumerate(registro):
        while r["t"] >= corte:
            if i:
                salida.append((corte, registro[i - 1]["seq"], registro[i - 1]["hash"]))
            corte += periodo_s
    salida.append((JORNADA_S, registro[-1]["seq"], registro[-1]["hash"]))
    return salida


ATAQUES = ("modificar_1", "borrar_1", "reordenar_2", "reescribir_desde_i")


def atacar(registro: list[dict], ataque: str, rnd: random.Random, recalcular: bool) -> list[dict]:
    """Un administrador con acceso total a la BD altera el registro. Con recalcular=True rehace los hashes."""
    r = [dict(x) for x in registro]
    i = rnd.randrange(len(r) - 1)
    if ataque == "modificar_1":
        r[i]["tipo"] = "VOTO_EMITIDO" if r[i]["tipo"] != "VOTO_EMITIDO" else "INTENTO_VOTO_DUPLICADO"
    elif ataque == "borrar_1":
        del r[i]
    elif ataque == "reordenar_2":
        r[i], r[i + 1] = r[i + 1], r[i]
    elif ataque == "reescribir_desde_i":
        del r[i]
        for k, x in enumerate(r):            # renumera para que las secuencias sigan consecutivas
            x["seq"] = k
        recalcular = True
    if recalcular and "hash" in r[0]:
        prev = GENESIS
        for x in r:
            x["hash"] = _h(prev, {k: v for k, v in x.items() if k != "hash"})
            prev = x["hash"]
    return r, i


def tasa_deteccion(variante: str, ataque: str, ensayos: int = 100, semilla: int = 5,
                   periodo_anclaje_s: int | None = None, solo_anclados: bool = False) -> float:
    rnd = random.Random(semilla)
    eventos = generar_eventos()
    registro = eventos if variante == "tabla_simple" else encadenar(eventos)
    anc = anclas_de(registro, periodo_anclaje_s or SUPUESTOS["periodo_anclaje_s"]) if variante == "cadena_anclada" else []
    detectados = anclados = detectados_anclados = 0
    for _ in range(ensayos):
        t_ataque = rnd.uniform(0, JORNADA_S)                     # cuándo actúa el atacante
        vistos = [x for x in registro if x["t"] <= t_ataque] or registro[:2]
        alterado, i = atacar(vistos, ataque, rnd, recalcular=False)
        resto = registro[len(vistos):]
        if ataque == "reescribir_desde_i" or variante == "tabla_simple":
            completo = alterado + [dict(x) for x in resto]
            if "hash" in registro[0]:                            # el atacante rehace TODA la cadena
                prev = GENESIS
                for k, x in enumerate(completo):
                    x["seq"] = k
                    x["hash"] = _h(prev, {kk: v for kk, v in x.items() if kk != "hash"})
                    prev = x["hash"]
            else:
                for k, x in enumerate(completo):
                    x["seq"] = k
        else:
            completo = alterado + resto                          # altera sin rehacer los hashes
        anclas = {seq: h for (pub, seq, h) in anc if pub <= t_ataque}   # solo las ya entregadas al auditor
        ok = verificar(completo, anclas, encadenado=variante != "tabla_simple")
        detectados += not ok
        if anclas and i <= max(anclas):                          # el evento alterado ya estaba anclado
            anclados += 1
            detectados_anclados += not ok
    if solo_anclados:
        return detectados_anclados / max(1, anclados)
    return detectados / ensayos


def tiempos() -> dict:
    eventos = generar_eventos()
    t0 = time.perf_counter()
    reg = encadenar(eventos)
    t1 = time.perf_counter()
    assert verificar(reg)
    t2 = time.perf_counter()
    lam = 5.0                                                     # pico QA-03
    return {
        "eventos": len(reg),
        "us_por_append": (t1 - t0) / len(reg) * 1e6,
        "verificacion_s": t2 - t1,
        "utilizacion_lock_pico": lam * SUPUESTOS["lock_ms_por_voto"] / 1000,
        "capacidad_votos_s": 1000 / SUPUESTOS["lock_ms_por_voto"],
    }


def acierto_por_posicion(mezclar: bool, semilla: int = 9) -> float:
    """El atacante conoce el ORDEN en que votaron (p. ej., por el registro de participación o porque
    los vio votar) y adivina el voto de cada uno por la posición de la papeleta en la exportación."""
    rnd = random.Random(semilla)
    ops, pesos = zip(*SUPUESTOS["opciones"].items())
    votos = rnd.choices(ops, weights=pesos, k=PADRON)             # papeleta i = voto del i-ésimo votante
    exportado = votos[:]
    if mezclar:
        rnd.shuffle(exportado)
    return sum(a == b for a, b in zip(votos, exportado)) / PADRON


def _main(salida_img: str = "docs/architecture/add/img") -> None:  # pragma: no cover
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    variantes = ("tabla_simple", "cadena", "cadena_anclada")
    res = {v: {a: tasa_deteccion(v, a) for a in ATAQUES} for v in variantes}
    print("Tasa de detección por el auditor externo (100 ataques por celda)")
    print(f"{'':16}" + "".join(f"{a:>20}" for a in ATAQUES))
    for v in variantes:
        print(f"{v:16}" + "".join(f"{res[v][a]:>19.0%} " for a in ATAQUES))
    periodos = [900, 1800, 3600, 4 * 3600, JORNADA_S]
    sens = [tasa_deteccion("cadena_anclada", "reescribir_desde_i", periodo_anclaje_s=p) for p in periodos]
    print("Sensibilidad (reescritura) vs periodo de anclaje (min):", [p // 60 for p in periodos], [f"{x:.0%}" for x in sens])
    print("Reescrituras de eventos YA anclados detectadas (cada 15 min):",
          f"{tasa_deteccion('cadena_anclada', 'reescribir_desde_i', solo_anclados=True):.0%}")
    t = tiempos()
    print(f"Costo: {t['eventos']} eventos, {t['us_por_append']:.1f} µs por append, verificación completa {t['verificacion_s']:.2f} s;"
          f" lock en el pico: utilización {t['utilizacion_lock_pico']:.0%}, capacidad {t['capacidad_votos_s']:.1f} votos/s")
    a_orden, a_mezcla = acierto_por_posicion(False), acierto_por_posicion(True)
    base = max(SUPUESTOS["opciones"].values())
    print(f"Secreto: acierto adivinando el voto por posición — orden de inserción {a_orden:.0%}, mezclada {a_mezcla:.1%}"
          f" (tasa base = {base:.0%}: decir siempre la opción más votada)")

    os.makedirs(salida_img, exist_ok=True)
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.8))
    nombres = {"modificar_1": "Modificar 1", "borrar_1": "Borrar 1", "reordenar_2": "Reordenar 2",
               "reescribir_desde_i": "Reescribir y\nrehacer hashes"}
    colores = {"tabla_simple": "#c0392b", "cadena": "#e67e22", "cadena_anclada": "#27ae60"}
    etiquetas = {"tabla_simple": "Tabla simple", "cadena": "Cadena de hashes", "cadena_anclada": "Cadena + anclaje cada 15 min"}
    w = 0.26
    for k, v in enumerate(variantes):
        ys = [res[v][a] * 100 for a in ATAQUES]
        bs = axs[0].bar([i + (k - 1) * w for i in range(len(ATAQUES))], ys, w, color=colores[v], label=etiquetas[v])
        for b, y in zip(bs, ys):
            axs[0].text(b.get_x() + b.get_width() / 2, y + 1.5, f"{y:.0f}", ha="center", fontsize=7)
    axs[0].set_xticks(range(len(ATAQUES)))
    axs[0].set_xticklabels([nombres[a] for a in ATAQUES], fontsize=8)
    axs[0].set_ylabel("% de alteraciones detectadas")
    axs[0].set_ylim(0, 115)
    axs[0].axhline(100, ls="--", c="k", lw=1)
    axs[0].set_title("QA-02: ¿el auditor externo detecta la alteración?")
    axs[0].legend(fontsize=7.5, loc="center left")
    xs = list(range(len(periodos)))
    axs[1].plot(xs, [x * 100 for x in sens], "o-", c="#27ae60")
    for xx, x in zip(xs, sens):
        axs[1].annotate(f"{x:.0%}", (xx, x * 100), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
    axs[1].set_xticks(xs)
    axs[1].set_xticklabels(["15 min", "30 min", "1 h", "4 h", "solo al cierre"])
    axs[1].set_xlabel("Periodo de anclaje")
    axs[1].set_ylim(0, 110)
    axs[1].set_ylabel("% de reescrituras detectadas")
    axs[1].set_title("Punto de sensibilidad: frecuencia del anclaje")
    bs = axs[2].bar(["Orden de\ninserción", "Exportación\nmezclada", "Tasa base\n(opción más votada)"],
                    [a_orden * 100, a_mezcla * 100, base * 100], color=["#c0392b", "#27ae60", "#95a5a6"])
    for b, y in zip(bs, [a_orden, a_mezcla, base]):
        axs[2].text(b.get_x() + b.get_width() / 2, y * 100 + 2, f"{y:.0%}", ha="center", fontsize=9)
    axs[2].set_ylim(0, 115)
    axs[2].set_ylabel("% de votos adivinados")
    axs[2].set_title("QA-06: adivinar el voto por la posición\nde la papeleta en la exportación")
    fig.tight_layout()
    ruta = os.path.join(salida_img, "iteracion-3-auditoria.png")
    fig.savefig(ruta, dpi=130)
    print("Gráfico:", ruta)


if __name__ == "__main__":  # pragma: no cover
    _main()
