"""Iteración 1 de ADD — QA-03 (rendimiento en el pico de apertura).

Modelo: la API Django (gunicorn síncrono) es una cola M/G/c. Cada votante hace
4 solicitudes (login OIDC, ver papeleta, emitir voto, ver comprobante). Con workers
síncronos, la espera a un servicio externo (proveedor de identidad, SMTP) OCUPA
el worker, así que se cuenta como tiempo de servicio.

Todos los tiempos son SUPUESTOS (🔶) porque VotoEPIS aún no tiene mediciones reales;
están en SUPUESTOS y se documentan en docs/architecture/add/iteracion-1.md.
"""
from __future__ import annotations

import heapq
import math
import random
import statistics

# ----------------------------- supuestos (🔶) ---------------------------------
SUPUESTOS = {
    "solicitudes_por_votante": 4,
    "mediana_idp_ms": 250,      # validar token / intercambiar código con el proveedor de identidad
    "mediana_smtp_ms": 400,     # enviar el comprobante por correo de forma síncrona
    "mediana_local_ms": {"login": 30, "papeleta": 40, "emitir": 60, "comprobante": 20},
    "mediana_papeleta_cache_ms": 8,
    "sigma_local": 0.5,         # dispersión lognormal (cola larga moderada)
    "sigma_externo": 0.6,
    "workers": 4,               # gunicorn en un VPS de 2 vCPU (ADR-001, R-03)
}
TIPOS = ("login", "papeleta", "emitir", "comprobante")

# Variantes evaluadas (tácticas): qué hace cada solicitud según la variante
VARIANTES = {
    "sin_tacticas": dict(idp_en_cada_solicitud=True, correo_sincrono=True, cache_papeleta=False, workers=4),
    "escalar_8_workers": dict(idp_en_cada_solicitud=True, correo_sincrono=True, cache_papeleta=False, workers=8),
    "sesion": dict(idp_en_cada_solicitud=False, correo_sincrono=True, cache_papeleta=False, workers=4),
    "sesion_correo_async": dict(idp_en_cada_solicitud=False, correo_sincrono=False, cache_papeleta=False, workers=4),
    "tres_tacticas": dict(idp_en_cada_solicitud=False, correo_sincrono=False, cache_papeleta=True, workers=4),
}

# Niveles de carga en VOTOS por segundo (25 000 votantes en 8 h)
NIVELES = {
    "normal": 25_000 / (8 * 3600),   # 0,87 votos/s
    "hora_punta": 2.0,
    "pico_apertura": 5.0,            # QA-03: ~4 500 votantes en 15 min tras el correo masivo
    "estres_2x": 10.0,
}
PRESUPUESTO_P95_MS = 2000            # QA-03


def _lognormal(rnd: random.Random, mediana: float, sigma: float) -> float:
    return rnd.lognormvariate(math.log(mediana), sigma)


def tiempo_servicio(rnd: random.Random, tipo: str, variante: dict, mediana_idp_ms: float | None = None) -> float:
    """Tiempo (ms) que un worker queda ocupado atendiendo una solicitud."""
    s = SUPUESTOS
    idp = s["mediana_idp_ms"] if mediana_idp_ms is None else mediana_idp_ms
    if tipo == "papeleta" and variante["cache_papeleta"]:
        t = _lognormal(rnd, s["mediana_papeleta_cache_ms"], s["sigma_local"])
    else:
        t = _lognormal(rnd, s["mediana_local_ms"][tipo], s["sigma_local"])
    if tipo == "login" or variante["idp_en_cada_solicitud"]:
        t += _lognormal(rnd, idp, s["sigma_externo"])
    if tipo == "emitir" and variante["correo_sincrono"]:
        t += _lognormal(rnd, s["mediana_smtp_ms"], s["sigma_externo"])
    return t


def simular(votos_s: float, variante: str | dict = "tres_tacticas", segundos: int = 900,
            semilla: int = 7, mediana_idp_ms: float | None = None, workers: int | None = None) -> dict:
    """Cola M/G/c durante `segundos`. Devuelve percentiles (ms) de 'emitir' y de todas las solicitudes."""
    v = VARIANTES[variante] if isinstance(variante, str) else variante
    c = workers or v["workers"]
    rnd = random.Random(semilla)
    lam = votos_s * SUPUESTOS["solicitudes_por_votante"]
    t, llegadas = 0.0, []
    while True:
        t += rnd.expovariate(lam)
        if t >= segundos:
            break
        llegadas.append((t, rnd.choice(TIPOS)))
    libres = [0.0] * c                                   # instante (s) en que cada worker queda libre
    heapq.heapify(libres)
    resp = {k: [] for k in TIPOS}
    ocupado = 0.0
    for a, tipo in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(a, libre)
        serv = tiempo_servicio(rnd, tipo, v, mediana_idp_ms) / 1000
        ocupado += serv
        heapq.heappush(libres, inicio + serv)
        resp[tipo].append((inicio + serv - a) * 1000)

    def pct(xs, q):
        xs = sorted(xs)
        return xs[int(q * (len(xs) - 1))]

    todas = [x for xs in resp.values() for x in xs]
    return {
        "solicitudes": len(llegadas),
        "utilizacion": ocupado / (c * segundos),
        "p50_emitir": pct(resp["emitir"], 0.50),
        "p95_emitir": pct(resp["emitir"], 0.95),
        "p95_todas": pct(todas, 0.95),
        "media_emitir": statistics.mean(resp["emitir"]),
    }


def tabla() -> list[dict]:
    filas = []
    for var in VARIANTES:
        for nivel, votos in NIVELES.items():
            r = simular(votos, var)
            filas.append({"variante": var, "nivel": nivel, "votos_s": round(votos, 2), **r})
    return filas


def sensibilidad_idp(medianas=(100, 200, 250, 300, 350, 400, 450, 500, 600, 800, 1000), votos_s=5.0) -> dict:
    """p95 de emitir en el pico según la latencia del proveedor de identidad."""
    return {var: [simular(votos_s, var, mediana_idp_ms=m)["p95_emitir"] for m in medianas]
            for var in ("sin_tacticas", "tres_tacticas")} | {"medianas": list(medianas)}


def _main(salida_img: str = "docs/architecture/add/img") -> None:  # pragma: no cover
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    filas = tabla()
    print(f"{'variante':22} {'nivel':14} {'votos/s':>7} {'util.':>6} {'p50 emitir':>11} {'p95 emitir':>11} {'cumple':>7}")
    for f in filas:
        cumple = "sí" if f["p95_emitir"] <= PRESUPUESTO_P95_MS else "NO"
        print(f"{f['variante']:22} {f['nivel']:14} {f['votos_s']:7.2f} {f['utilizacion']:6.0%} "
              f"{f['p50_emitir']:9.0f}ms {f['p95_emitir']:9.0f}ms {cumple:>7}")
    sens = sensibilidad_idp()
    print("\nSensibilidad (pico 5 votos/s) — mediana IdP ms:", sens["medianas"])
    for var in ("sin_tacticas", "tres_tacticas"):
        print(f"  {var:15}", [round(x) for x in sens[var]])

    os.makedirs(salida_img, exist_ok=True)
    etiquetas = {"sin_tacticas": "Sin tácticas (4 workers)", "escalar_8_workers": "Escalar a 8 workers",
                 "sesion": "Sesión (IdP solo en login)", "sesion_correo_async": "Sesión + correo asíncrono",
                 "tres_tacticas": "Sesión + correo async + caché"}
    colores = ["#c0392b", "#7f8c8d", "#e67e22", "#2980b9", "#27ae60"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2))
    niveles = list(NIVELES)
    ancho = 0.16
    for i, var in enumerate(VARIANTES):
        ys = [next(f["p95_emitir"] for f in filas if f["variante"] == var and f["nivel"] == n) for n in niveles]
        xs = [j + (i - 2) * ancho for j in range(len(niveles))]
        barras = ax1.bar(xs, ys, ancho, label=etiquetas[var], color=colores[i])
        for b, y in zip(barras, ys):
            txt = "satura" if y > 60_000 else (f"{y/1000:.1f}s" if y >= 1000 else f"{y:.0f}")
            ax1.text(b.get_x() + b.get_width() / 2, y * 1.12, txt, ha="center", va="bottom", fontsize=6.5, rotation=90)
    ax1.axhline(PRESUPUESTO_P95_MS, ls="--", c="k", lw=1)
    ax1.text(-0.45, PRESUPUESTO_P95_MS * 1.6, "QA-03: p95 ≤ 2 s", fontsize=8)
    ax1.set_yscale("log")
    ax1.set_ylim(50, 3e8)
    ax1.set_xticks(range(len(niveles)))
    ax1.set_xticklabels([f"{n.replace('_', ' ')}\n{NIVELES[n]:.2f} votos/s" for n in niveles], fontsize=8)
    ax1.set_ylabel("p95 de 'emitir voto' (ms, escala log)")
    ax1.set_title("Tácticas de rendimiento frente a la carga (15 min por nivel)")
    ax1.legend(fontsize=7.5, loc="upper left", ncol=2)
    for var, c, et in (("sin_tacticas", "#c0392b", "Sin tácticas"), ("tres_tacticas", "#27ae60", "Tres tácticas")):
        ax2.plot(sens["medianas"], sens[var], "o-", c=c, label=et)
    ax2.axhline(PRESUPUESTO_P95_MS, ls="--", c="k", lw=1)
    ax2.set_yscale("log")
    ax2.set_xlabel("Mediana de latencia del proveedor de identidad (ms)")
    ax2.set_ylabel("p95 de 'emitir voto' en el pico (ms, log)")
    ax2.set_title("Punto de sensibilidad: latencia del IdP (5 votos/s)")
    ax2.text(110, PRESUPUESTO_P95_MS * 1.3, "QA-03: p95 ≤ 2 s", fontsize=8)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    ruta = os.path.join(salida_img, "iteracion-1-rendimiento.png")
    fig.savefig(ruta, dpi=130)
    print("\nGráfico:", ruta)


if __name__ == "__main__":  # pragma: no cover
    _main()
