"""Fitness functions DE CALIDAD de VotoEPIS (Lab 08, E5).

Convierten los escenarios del árbol de utilidad en pruebas. Si alguien cambia una decisión
de las iteraciones de ADD (p. ej., vuelve a enviar el correo de forma síncrona, quita el
bulkhead o deja de anclar la cadena), la integración continua falla.

Las FF-04 a FF-08 verifican el MODELO de decisión (fitness/), no un despliegue real:
sus supuestos están en fitness/*.py (SUPUESTOS) y en docs/architecture/add/.
La FF-09 verifica el código real de src/ (ADR-002).
Las FF estructurales (FF-01 a FF-03) están en .importlinter.
"""
import dataclasses
import time

from fitness.auditoria import (ATAQUES, SUPUESTOS as SUP_AUD, acierto_por_posicion, encadenar, generar_eventos,
                               tasa_deteccion, verificar)
from fitness.disponibilidad import SUPUESTOS as SUP_DISP, simular_caida
from fitness.rendimiento import NIVELES, VARIANTES, simular

PRESUPUESTO_P95_MS = 2000          # QA-03 y QA-04


# ---------------------------------------------------------------- QA-03 rendimiento
def test_ff04_rendimiento_pico_de_apertura():
    """QA-03: 5 votos/s en el pico -> p95 de 'emitir voto' <= 2 s (iteración 1)."""
    r = simular(NIVELES["pico_apertura"], "tres_tacticas")
    assert r["p95_emitir"] <= PRESUPUESTO_P95_MS, f"p95={r['p95_emitir']:.0f} ms excede el presupuesto"
    assert r["utilizacion"] <= 0.70, f"utilización {r['utilizacion']:.0%}: sin margen para ráfagas"


def test_ff04b_el_correo_del_comprobante_sigue_siendo_asincrono():
    """Protege la táctica de mayor efecto de la iteración 1 (ADR-006)."""
    assert VARIANTES["tres_tacticas"]["correo_sincrono"] is False
    assert VARIANTES["tres_tacticas"]["idp_en_cada_solicitud"] is False


# ---------------------------------------------------------------- QA-04 disponibilidad
def test_ff05_idp_caido_no_afecta_a_votantes_con_sesion():
    """QA-04: IdP caído 30 min -> con sesión p95 <= 2 s, 0 solicitudes cortadas (iteración 2)."""
    r = simular_caida("breaker_bulkhead")
    assert r["p95_emitir_durante_caida_ms"] <= PRESUPUESTO_P95_MS
    assert r["pct_emitir_cortadas"] == 0


def test_ff05b_breaker_protege_al_idp_caido():
    """QA-04: <= 1 llamada cada 30 s al IdP caído (más las que abren el circuito)."""
    limite = SUP_DISP["duracion_caida_s"] / 30 + SUP_DISP["umbral_breaker"]
    con = simular_caida("breaker_bulkhead")["llamadas_al_idp_caido"]
    sin = simular_caida("reintentos")["llamadas_al_idp_caido"]
    assert con <= limite, f"{con} llamadas al IdP caído (límite {limite:.0f})"
    assert con < sin / 5


def test_ff06_bulkhead_aisla_emitir_de_un_idp_lento():
    """S1 de la iteración 1: con el IdP lento (1 s de mediana) 'emitir' sigue cumpliendo QA-03."""
    r = simular_caida("breaker_bulkhead", votos_s=5.0, segundos=900, inicio_caida=0,
                      duracion_caida_s=0, semilla=7, mediana_idp_ms=1000)
    assert r["p95_emitir_durante_caida_ms"] <= PRESUPUESTO_P95_MS


# ---------------------------------------------------------------- QA-02 auditabilidad
def test_ff07_auditor_detecta_toda_alteracion_de_eventos_anclados():
    """QA-02: 100 % de alteraciones detectadas (iteración 3, cadena + anclaje cada 15 min)."""
    assert SUP_AUD["periodo_anclaje_s"] <= 900, "el anclaje debe ser al menos cada 15 min"
    for ataque in ("modificar_1", "borrar_1", "reordenar_2"):
        assert tasa_deteccion("cadena_anclada", ataque, ensayos=10) == 1.0, ataque
    assert tasa_deteccion("cadena_anclada", "reescribir_desde_i", ensayos=20, solo_anclados=True) == 1.0
    assert set(ATAQUES) >= {"modificar_1", "borrar_1", "reordenar_2", "reescribir_desde_i"}


def test_ff07b_verificacion_del_auditor_en_menos_de_10_min():
    registro = encadenar(generar_eventos())
    t0 = time.perf_counter()
    assert verificar(registro)
    assert time.perf_counter() - t0 < 600


def test_ff07c_eventos_de_auditoria_sin_datos_del_voto():
    """ADR-002: los eventos no llevan opción, correo ni identificador del votante."""
    campos = set(generar_eventos()[0])
    assert campos == {"seq", "t", "tipo", "eleccion_id"}


# ---------------------------------------------------------------- QA-06 secreto
def test_ff08_exportacion_mezclada_no_revela_el_voto():
    """QA-06: acierto por posición <= tasa base (opción más votada)."""
    tasa_base = max(SUP_AUD["opciones"].values())
    assert acierto_por_posicion(mezclar=True) <= tasa_base


def test_ff09_la_papeleta_no_referencia_al_votante():
    """ADR-002 sobre el código REAL: ninguna Papeleta de src/ guarda datos del votante."""
    import votacion.dominio
    import votacion.servicio
    prohibidos = {"votante", "correo", "estudiante", "estudiante_id", "votante_id", "email", "dni", "timestamp"}
    for modulo in (votacion.servicio, votacion.dominio):
        campos = {f.name for f in dataclasses.fields(modulo.Papeleta)}
        assert not campos & prohibidos, f"{modulo.__name__}.Papeleta expone {campos & prohibidos}"
