"""Iteración 2 de ADD — QA-04 (el proveedor de identidad institucional cae 30 min).

Parte A (cola M/G/c con la caída inyectada): ¿qué les pasa a los votantes que YA tienen
sesión cuando el IdP cae? Con workers síncronos, cada login que espera el timeout del
IdP bloquea un worker; con reintentos, lo bloquea 3 veces más tiempo.

Parte B (Monte Carlo de la jornada de 8 h): ¿cuántos votantes que llegan durante la
caída se quedan sin votar al cierre, según la hora en que ocurra la caída?

Supuestos (🔶) en SUPUESTOS; se documentan en docs/architecture/add/iteracion-2.md.
Parte de la configuración de la iteración 1 (sesión + correo asíncrono + caché).
"""
from __future__ import annotations

import heapq
import random
import statistics

from fitness.rendimiento import TIPOS, VARIANTES as VAR_REND, tiempo_servicio

SUPUESTOS = {
    "timeout_idp_s": 5.0,           # timeout configurado en el cliente HTTP del adaptador OIDC
    "intentos_reintento": 3,        # ConReintentos (Lab 07)
    "umbral_breaker": 3,            # fallas consecutivas que abren el circuito
    "espera_breaker_s": 30.0,       # tiempo en ABIERTO antes de dejar pasar una prueba
    "falla_rapida_ms": 5.0,         # responder "proveedor no disponible" con el circuito abierto
    "timeout_cliente_s": 30.0,      # el navegador / Nginx corta la solicitud a los 30 s
    "workers_votacion": 4,
    "workers_login": 4,             # pool separado (bulkhead) solo para el callback OIDC
    "duracion_caida_s": 1800,
    # Parte B
    "p_vuelve_sin_aviso": 0.70,     # votante que ve un error genérico y vuelve más tarde
    "p_vuelve_con_aviso": 0.90,     # ve "IdP caído, vuelva a las HH:MM o vaya a la mesa" + anuncio oficial
    "mesa_atendentes": 3,           # mesa de contingencia del comité (código de un solo uso, ADR-003)
    "mesa_s_por_votante": 40.0,
    "extension_cierre_s": 1800,     # el comité extiende el cierre 30 min si hubo caída
}

# Perfil de llegadas de la jornada 08:00–16:00 (25 000 votantes), en franjas de 15 min (🔶)
# 18 % llega en los primeros 15 min (correo masivo de apertura = 5 votos/s, QA-03).
PERFIL_PCT = ([18, 2, 1.5, 1.5] + [2.5] * 4 + [2] * 4 + [2.5] * 4 + [3.5] * 4 + [2.5] * 4 + [2.5] * 4
              + [3, 3, 4, 5])
assert abs(sum(PERFIL_PCT) - 100) < 1e-9, sum(PERFIL_PCT)
PADRON = 25_000
JORNADA_S = 8 * 3600

VARIANTES = {
    "sin_tacticas": dict(reintentos=False, breaker=False, bulkhead=False, contingencia=False),
    "reintentos": dict(reintentos=True, breaker=False, bulkhead=False, contingencia=False),
    "breaker_bulkhead": dict(reintentos=True, breaker=True, bulkhead=True, contingencia=False),
    "breaker_bulkhead_contingencia": dict(reintentos=True, breaker=True, bulkhead=True, contingencia=True),
}


class Breaker:
    """Circuit breaker mínimo (misma lógica que ConCircuitBreaker de la guía, con reloj simulado)."""

    def __init__(self, umbral: int, espera_s: float) -> None:
        self.umbral, self.espera = umbral, espera_s
        self.fallas, self.abierto_desde = 0, None

    def estado(self, ahora: float) -> str:
        if self.abierto_desde is None:
            return "CERRADO"
        return "SEMIABIERTO" if ahora - self.abierto_desde >= self.espera else "ABIERTO"

    def registrar(self, ok: bool, ahora: float) -> None:
        if ok:
            self.fallas, self.abierto_desde = 0, None
            return
        self.fallas += 1
        if self.fallas >= self.umbral or self.estado(ahora) == "SEMIABIERTO":
            self.abierto_desde = ahora


def simular_caida(variante: str, votos_s: float = 2.0, segundos: int = 3600, inicio_caida: float = 900,
                  semilla: int = 11, mediana_idp_ms: float | None = None,
                  duracion_caida_s: float | None = None) -> dict:
    """Parte A: una hora de hora punta con el IdP caído entre inicio_caida e inicio_caida + 30 min.

    Con duracion_caida_s=0 no hay caída y las métricas "durante la caída" se miden en toda la ventana.
    """
    s, v = SUPUESTOS, VARIANTES[variante]
    base = VAR_REND["tres_tacticas"]
    dur = s["duracion_caida_s"] if duracion_caida_s is None else duracion_caida_s
    fin_caida = inicio_caida + dur
    ventana = (inicio_caida, fin_caida) if dur else (0.0, float(segundos))
    rnd = random.Random(semilla)
    lam = votos_s * 4
    t, llegadas = 0.0, []
    while True:
        t += rnd.expovariate(lam)
        if t >= segundos:
            break
        llegadas.append((t, rnd.choice(TIPOS)))

    pool_v = [0.0] * s["workers_votacion"]
    pool_l = [0.0] * s["workers_login"] if v["bulkhead"] else pool_v
    heapq.heapify(pool_v)
    heapq.heapify(pool_l)
    br = Breaker(s["umbral_breaker"], s["espera_breaker_s"]) if v["breaker"] else None
    llamadas_caido, emitir_caida, login_caida, ultimo_emitir_lento = 0, [], [], None
    for a, tipo in llegadas:
        pool = pool_l if tipo == "login" else pool_v
        libre = heapq.heappop(pool)
        inicio = max(a, libre)
        caido = inicio_caida <= inicio < fin_caida
        if tipo == "login":
            if br and br.estado(inicio) == "ABIERTO":
                serv = s["falla_rapida_ms"] / 1000
            elif caido:
                intentos = 1 if (br and br.estado(inicio) == "SEMIABIERTO") or not v["reintentos"] else s["intentos_reintento"]
                llamadas_caido += intentos
                serv = intentos * s["timeout_idp_s"]
                if br:
                    br.registrar(False, inicio + serv)
            else:
                serv = tiempo_servicio(rnd, tipo, base, mediana_idp_ms) / 1000
                if br:
                    br.registrar(True, inicio + serv)
        else:
            serv = tiempo_servicio(rnd, tipo, base) / 1000
        heapq.heappush(pool, inicio + serv)
        r = inicio + serv - a
        if tipo == "emitir" and r > 2.0:
            ultimo_emitir_lento = a
        if ventana[0] <= a < ventana[1]:
            (login_caida if tipo == "login" else emitir_caida if tipo == "emitir" else []).append(r)

    def p95(xs):
        xs = sorted(xs)
        return xs[int(0.95 * (len(xs) - 1))] * 1000 if xs else 0.0

    return {
        "p95_emitir_durante_caida_ms": p95(emitir_caida),
        "pct_emitir_cortadas": 100 * sum(r > s["timeout_cliente_s"] for r in emitir_caida) / max(1, len(emitir_caida)),
        "p95_login_durante_caida_ms": p95(login_caida),
        "llamadas_al_idp_caido": llamadas_caido,
        # segundos, después de que el IdP vuelve, hasta que 'emitir' deja de superar 2 s (cola vaciada)
        "recuperacion_s": max(0.0, (ultimo_emitir_lento or 0.0) - fin_caida) if dur else 0.0,
    }


def sensibilidad_lentitud_idp(medianas=(250, 500, 750, 1000, 2000), votos_s: float = 5.0) -> dict:
    """IdP LENTO (no caído) en el pico de 5 votos/s: el breaker no se abre; solo el bulkhead aísla 'emitir'."""
    return {"medianas": list(medianas)} | {
        var: [simular_caida(var, votos_s, segundos=900, inicio_caida=0, duracion_caida_s=0, semilla=7,
                            mediana_idp_ms=m)["p95_emitir_durante_caida_ms"] for m in medianas]
        for var in ("reintentos", "breaker_bulkhead")}


def _llegadas_en(rnd: random.Random, desde: float, hasta: float) -> int:
    """Votantes (Poisson) que llegan entre desde y hasta según el perfil de 15 min."""
    total = 0.0
    for i, pct in enumerate(PERFIL_PCT):
        a, b = i * 900, (i + 1) * 900
        solape = max(0.0, min(b, hasta) - max(a, desde))
        total += PADRON * pct / 100 * solape / 900
    # aproximación normal de Poisson (media grande)
    return max(0, round(rnd.gauss(total, total ** 0.5)))


def montecarlo_jornada(variante: str, dias: int = 2000, semilla: int = 3) -> dict:
    """Parte B: la caída de 30 min empieza a una hora uniforme de la jornada."""
    s, v = SUPUESTOS, VARIANTES[variante]
    rnd = random.Random(semilla)
    perdidos, afectados = [], []
    for _ in range(dias):
        ini = rnd.uniform(0, JORNADA_S - 60)
        fin = min(ini + s["duracion_caida_s"], JORNADA_S)
        n = _llegadas_en(rnd, ini, fin)
        atendidos_mesa = 0
        if v["contingencia"]:
            atendidos_mesa = min(n, int(s["mesa_atendentes"] * (fin - ini) / s["mesa_s_por_votante"]))
        resto = n - atendidos_mesa
        tiempo_tras_caida = JORNADA_S - fin + (s["extension_cierre_s"] if v["contingencia"] else 0)
        if tiempo_tras_caida < 300:                     # la caída alcanza el cierre: no hay cómo volver
            p = 0.0
        else:
            p = s["p_vuelve_con_aviso"] if v["breaker"] else s["p_vuelve_sin_aviso"]
        vuelven = sum(rnd.random() < p for _ in range(resto)) if resto < 3000 else round(rnd.gauss(resto * p, (resto * p * (1 - p)) ** 0.5))
        afectados.append(n)
        perdidos.append(resto - vuelven)
    perdidos.sort()
    return {
        "afectados_media": statistics.mean(afectados),
        "perdidos_media": statistics.mean(perdidos),
        "perdidos_p95": perdidos[int(0.95 * (len(perdidos) - 1))],
        "pct_perdidos_de_afectados": 100 * sum(perdidos) / max(1, sum(afectados)),
    }


def _main(salida_img: str = "docs/architecture/add/img") -> None:  # pragma: no cover
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    a = {k: simular_caida(k) for k in VARIANTES}
    b = {k: montecarlo_jornada(k) for k in VARIANTES}
    print("Parte A — hora punta (2 votos/s), IdP caído 30 min")
    for k, r in a.items():
        print(f"  {k:30} p95 emitir={r['p95_emitir_durante_caida_ms']:9.0f} ms  cortadas={r['pct_emitir_cortadas']:5.1f} %"
              f"  p95 login={r['p95_login_durante_caida_ms']:8.0f} ms  llamadas IdP caído={r['llamadas_al_idp_caido']:5d}"
              f"  recuperación={r['recuperacion_s']:.0f} s")
    sens = sensibilidad_lentitud_idp()
    print("IdP LENTO en el pico (5 votos/s) — mediana IdP ms:", sens["medianas"])
    for var in ("reintentos", "breaker_bulkhead"):
        print(f"  p95 emitir {var:18}", [round(x) for x in sens[var]])
    print("Parte B — Monte Carlo 2000 jornadas (caída de 30 min a hora aleatoria)")
    for k, r in b.items():
        print(f"  {k:30} afectados={r['afectados_media']:6.0f}  perdidos media={r['perdidos_media']:6.0f}"
              f"  p95={r['perdidos_p95']:5d}  ({r['pct_perdidos_de_afectados']:.1f} % de los afectados)")

    os.makedirs(salida_img, exist_ok=True)
    nombres = ["Sin tácticas", "Reintentos (3)", "Breaker +\nbulkhead", "Breaker + bulkhead\n+ contingencia"]
    colores = ["#c0392b", "#e67e22", "#2980b9", "#27ae60"]
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.8))
    vals = [a[k]["p95_emitir_durante_caida_ms"] / 1000 for k in VARIANTES]
    bars = axs[0].bar(nombres, vals, color=colores)
    axs[0].axhline(2, ls="--", c="k", lw=1)
    axs[0].set_yscale("log")
    axs[0].set_ylabel("segundos (log)")
    axs[0].set_title("p95 de 'emitir voto' de votantes CON sesión\ndurante la caída (2 votos/s)")
    for bb, y in zip(bars, vals):
        axs[0].text(bb.get_x() + bb.get_width() / 2, y * 1.1, f"{y:.2f} s" if y < 10 else f"{y:.0f} s", ha="center", fontsize=8)
    vals = [a[k]["llamadas_al_idp_caido"] for k in VARIANTES]
    bars = axs[1].bar(nombres, vals, color=colores)
    axs[1].set_title("Llamadas al proveedor de identidad\nmientras está caído (30 min)")
    for bb, y in zip(bars, vals):
        axs[1].text(bb.get_x() + bb.get_width() / 2, y + max(vals) * 0.02, str(y), ha="center", fontsize=8)
    vals = [b[k]["perdidos_media"] for k in VARIANTES]
    p95s = [b[k]["perdidos_p95"] for k in VARIANTES]
    bars = axs[2].bar(nombres, vals, color=colores, yerr=[[0] * 4, [p - m for p, m in zip(p95s, vals)]], capsize=4)
    axs[2].set_title("Votantes afectados que NO votan al cierre\n(media y p95 de 2000 jornadas simuladas)")
    for bb, y, k in zip(bars, vals, VARIANTES):
        axs[2].text(bb.get_x() + bb.get_width() / 2, y * 0.5, f"{y:.0f}\n({b[k]['pct_perdidos_de_afectados']:.0f} %)",
                    ha="center", fontsize=8, color="white", fontweight="bold")
    for ax in axs:
        ax.tick_params(axis="x", labelsize=7.5)
    fig.tight_layout()
    ruta = os.path.join(salida_img, "iteracion-2-disponibilidad.png")
    fig.savefig(ruta, dpi=130)
    print("Gráfico:", ruta)


if __name__ == "__main__":  # pragma: no cover
    _main()
