"""Pruebas de CARACTERIZACIÓN: describen lo que el sistema hace hoy (comportamiento observable).

El mismo conjunto se ejecuta sobre la versión ANTES y, desde E2, también sobre la versión DESPUÉS.
Si todas pasan en ambas, el refactor conservó el comportamiento. Ninguna prueba usa servicios reales.
"""
import importlib
from datetime import datetime, timedelta

import pytest

from votacion.externos import CorreoSDK, OtpComiteSDK, ProveedorIdentidadSDK

VERSIONES = ["votacion.antes.servicio", "votacion.servicio"]

ANA = "ana@unsa.edu.pe"
BETO = "beto@unsa.edu.pe"
FIN = datetime(2026, 10, 20, 18, 0)


@pytest.fixture(params=VERSIONES)
def m(request):
    return importlib.import_module(request.param)


def idp(**kw):
    return ProveedorIdentidadSDK(tokens={"tok-ana": ANA, "tok-beto": BETO}, **kw)


def eleccion_abierta(m, s, opciones=2):
    e = m.Eleccion("Delegados EPIS", [m.Opcion(f"Lista {i}") for i in range(opciones)], fin=FIN)
    if opciones >= 2:
        s.abrir(e)
    return e


# ---------------------------------------------------------------- éxito y secreto
def test_voto_oidc_exitoso_registra_participacion_papeleta_y_auditoria(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    codigo = s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    assert len(codigo) == 16
    assert s.conteo(e) == {"Lista 0": 1, "Lista 1": 0}
    assert s.eventos == [f"VOTO_EMITIDO:{e.id}"]


def test_la_papeleta_no_referencia_al_votante_ni_la_auditoria_a_la_opcion(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    s.emitir_voto(m.Votante(ANA), e, e.opciones[1].id, "OIDC", "tok-ana")
    papeleta = s.urna[0]
    assert not hasattr(papeleta, "votante") and not hasattr(papeleta, "correo")
    assert all(ANA not in ev and str(e.opciones[1].id) not in ev for ev in s.eventos)


def test_voto_con_otp_de_contingencia(m):
    s = m.ServicioVotacion(otp=OtpComiteSDK(codigos={ANA: "123456"}))
    e = eleccion_abierta(m, s)
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OTP", "123456")
    assert s.conteo(e)["Lista 0"] == 1


# ---------------------------------------------------------------- rechazos
def test_voto_duplicado_se_rechaza_y_se_audita(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    with pytest.raises(ValueError):
        s.emitir_voto(m.Votante(ANA), e, e.opciones[1].id, "OIDC", "tok-ana")
    assert sum(s.conteo(e).values()) == 1
    assert s.eventos[-1] == f"INTENTO_VOTO_DUPLICADO:{e.id}"


def test_votar_con_eleccion_no_abierta_se_rechaza_y_se_audita(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    s.cerrar(e, FIN + timedelta(minutes=1))
    with pytest.raises(ValueError):
        s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    assert s.eventos == [f"VOTO_FUERA_DE_VENTANA:{e.id}"]
    assert sum(s.conteo(e).values()) == 0


def test_votante_no_habilitado_se_rechaza(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    with pytest.raises(PermissionError):
        s.emitir_voto(m.Votante(ANA, habilitado=False), e, e.opciones[0].id, "OIDC", "tok-ana")
    assert s.eventos == [f"VOTANTE_NO_HABILITADO:{e.id}"]


def test_credencial_invalida_no_consume_el_voto_y_no_se_reintenta(m):
    proveedor = idp()
    s = m.ServicioVotacion(idp=proveedor)
    e = eleccion_abierta(m, s)
    with pytest.raises(PermissionError):
        s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "token-falso")
    assert proveedor.llamadas == 1  # un rechazo NO se reintenta (solo los timeouts)
    # el votante puede votar después con una credencial válida
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    assert sum(s.conteo(e).values()) == 1


def test_credencial_de_otra_persona_no_sirve(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    with pytest.raises(PermissionError):
        s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-beto")
    assert sum(s.conteo(e).values()) == 0


def test_medio_no_soportado_no_altera_la_urna(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    with pytest.raises(ValueError):
        s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "HUELLA", "x")
    assert sum(s.conteo(e).values()) == 0 and s.urna == []


def test_opcion_invalida_se_rechaza_sin_registrar(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    otra = m.Opcion("No existe")
    with pytest.raises(ValueError):
        s.emitir_voto(m.Votante(ANA), e, otra.id, "OIDC", "tok-ana")
    assert s.urna == [] and s.eventos == []


# ---------------------------------------------------------------- reintentos
def test_reintenta_tras_dos_timeouts_y_logra_autenticar(m):
    proveedor = idp(fallas=2)
    s = m.ServicioVotacion(idp=proveedor)
    e = eleccion_abierta(m, s)
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    assert proveedor.llamadas == 3
    assert sum(s.conteo(e).values()) == 1


def test_tres_timeouts_seguidos_fallan_la_autenticacion(m):
    proveedor = idp(fallas=3)
    s = m.ServicioVotacion(idp=proveedor)
    e = eleccion_abierta(m, s)
    with pytest.raises(PermissionError):
        s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    assert proveedor.llamadas == 3
    assert s.eventos == [f"AUTENTICACION_FALLIDA:{e.id}"]


# ---------------------------------------------------------------- comprobante por correo
def test_comprobante_por_correo_solo_si_se_pide_y_sin_revelar_la_opcion(m):
    correo = CorreoSDK()
    s = m.ServicioVotacion(idp=idp(), correo=correo)
    e = eleccion_abierta(m, s)
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana", enviar_correo=False)
    assert correo.bandeja == []
    codigo = s.emitir_voto(m.Votante(BETO), e, e.opciones[1].id, "OIDC", "tok-beto", enviar_correo=True)
    assert len(correo.bandeja) == 1
    msg = correo.bandeja[0]
    assert msg["destino"] == BETO and codigo in msg["cuerpo"]
    assert "Lista" not in msg["cuerpo"]


# ---------------------------------------------------------------- ciclo de vida (Lab 05)
def test_ciclo_de_vida_completo(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    assert e.estado == "ABIERTA"
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    s.cerrar(e, FIN + timedelta(minutes=1))
    assert e.estado == "CERRADA"
    s.escrutar(e)
    assert e.estado == "ESCRUTADA"
    s.firmar_acta(e)
    assert e.estado == "ESCRUTADA" and e.acta_firmada is True
    s.publicar(e)
    assert e.estado == "PUBLICADA"


def test_abrir_exige_dos_o_mas_opciones(m):
    s = m.ServicioVotacion()
    e = m.Eleccion("Delegados", [m.Opcion("Única")], fin=FIN)
    with pytest.raises(ValueError):
        s.abrir(e)
    assert e.estado == "CONFIGURADA"


def test_no_se_cierra_antes_de_la_hora_de_fin(m):
    s = m.ServicioVotacion()
    e = eleccion_abierta(m, s)
    with pytest.raises(ValueError):
        s.cerrar(e, FIN - timedelta(minutes=1))
    assert e.estado == "ABIERTA"


def test_publicar_sin_acta_firmada_falla(m):
    s = m.ServicioVotacion()
    e = eleccion_abierta(m, s)
    s.cerrar(e, FIN)
    s.escrutar(e)
    with pytest.raises(ValueError):
        s.publicar(e)
    assert e.estado == "ESCRUTADA"


def test_no_se_puede_escrutar_si_la_urna_no_es_integra(m):
    s = m.ServicioVotacion(idp=idp())
    e = eleccion_abierta(m, s)
    s.emitir_voto(m.Votante(ANA), e, e.opciones[0].id, "OIDC", "tok-ana")
    s.urna.pop()  # alguien altera la urna: papeletas (0) != participaciones (1)
    s.cerrar(e, FIN)
    with pytest.raises(ValueError):
        s.escrutar(e)
    assert e.estado == "CERRADA"


def test_transiciones_invalidas_desde_estados_incorrectos(m):
    s = m.ServicioVotacion()
    e = eleccion_abierta(m, s)
    with pytest.raises(ValueError):
        s.abrir(e)                # ya está abierta
    with pytest.raises(ValueError):
        s.escrutar(e)             # aún no está cerrada
    with pytest.raises(ValueError):
        s.firmar_acta(e)          # aún no está escrutada
