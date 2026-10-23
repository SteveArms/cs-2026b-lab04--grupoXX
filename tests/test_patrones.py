"""Pruebas que DEMUESTRAN cada patrón aplicado (solo sobre la versión refactorizada)."""
import inspect

import pytest

import votacion.servicio as srv
from votacion.autenticacion import (AutenticadorVotante, FabricaAutenticadores, OidcAdapter,
                                    OtpAdapter, ResultadoAutenticacion)
from votacion.externos import OtpComiteSDK, ProveedorIdentidadSDK

ANA = "ana@unsa.edu.pe"


# ------------------------------------------------------------------ E2: Adapter
def test_adapter_oidc_traduce_el_diccionario_del_sdk():
    sdk = ProveedorIdentidadSDK(tokens={"t": ANA})
    assert OidcAdapter(sdk).autenticar(ANA, "t") == ResultadoAutenticacion(True, ANA)
    assert OidcAdapter(sdk).autenticar(ANA, "malo") == ResultadoAutenticacion(False, None)


def test_adapter_otp_traduce_la_tupla_del_sdk():
    sdk = OtpComiteSDK(codigos={ANA: "111"})
    assert OtpAdapter(sdk).autenticar(ANA, "111") == ResultadoAutenticacion(True, ANA)
    assert OtpAdapter(sdk).autenticar(ANA, "999") == ResultadoAutenticacion(False, None)


def test_los_adaptadores_no_contienen_reglas_de_negocio():
    # El adaptador solo traduce: no conoce elecciones, estados ni habilitación.
    for clase in (OidcAdapter, OtpAdapter):
        fuente = inspect.getsource(clase)
        assert "Eleccion" not in fuente and "habilitado" not in fuente


# ------------------------------------------------------------------ E2: Factory
def test_factory_rechaza_un_medio_no_registrado():
    with pytest.raises(ValueError):
        FabricaAutenticadores().crear("HUELLA")


# ------------------------------------------------------------------ E2: Strategy + Open/Closed
def test_open_closed_nuevo_medio_sin_modificar_el_servicio():
    class TokenComite(AutenticadorVotante):          # medio NUEVO: no toca ServicioVotacion
        def autenticar(self, correo_esperado, credencial):
            return ResultadoAutenticacion(credencial == "sello-comite", correo_esperado)

    s = srv.ServicioVotacion()
    s.fabrica.registrar("COMITE", TokenComite)
    e = srv.Eleccion("Delegados", [srv.Opcion("A"), srv.Opcion("B")])
    s.abrir(e)
    s.emitir_voto(srv.Votante(ANA), e, e.opciones[0].id, "COMITE", "sello-comite")
    assert s.conteo(e)["A"] == 1


def test_el_servicio_ya_no_conoce_los_medios_concretos():
    fuente = inspect.getsource(srv.ServicioVotacion)
    assert '"OIDC"' not in fuente and '"OTP"' not in fuente
    assert "validar_token" not in fuente and "verificar(" not in fuente


# ------------------------------------------------------------------ E3: State
import re
from datetime import datetime, timedelta

import votacion.estados as est

FIN = datetime(2026, 10, 20, 18, 0)

ACCIONES = {
    "abrir": lambda e: e.abrir(),
    "cerrar": lambda e: e.cerrar(FIN + timedelta(hours=1)),
    "escrutar": lambda e: e.escrutar(0, 0),
    "firmar_acta": lambda e: e.firmar_acta(),
    "publicar": lambda e: e.publicar(),
}


def eleccion_en(estado):
    """Lleva una elección real hasta el estado pedido usando solo transiciones válidas."""
    e = est.Eleccion("Delegados", [est.Opcion("A"), est.Opcion("B")], fin=FIN)
    pasos = {"CONFIGURADA": [], "ABIERTA": ["abrir"], "CERRADA": ["abrir", "cerrar"],
             "ESCRUTADA": ["abrir", "cerrar", "escrutar"],
             "PUBLICADA": ["abrir", "cerrar", "escrutar", "firmar_acta", "publicar"]}
    for accion in pasos[estado]:
        ACCIONES[accion](e)
    assert e.estado == estado
    return e


# transiciones permitidas según estados-eleccion.mmd (Lab 05)
VALIDAS = {("CONFIGURADA", "abrir"), ("ABIERTA", "cerrar"), ("CERRADA", "escrutar"),
           ("ESCRUTADA", "firmar_acta"), ("ESCRUTADA", "publicar")}
ESTADOS = ["CONFIGURADA", "ABIERTA", "CERRADA", "ESCRUTADA", "PUBLICADA"]
INVALIDAS = [(s, a) for s in ESTADOS for a in ACCIONES if (s, a) not in VALIDAS]


@pytest.mark.parametrize("estado,accion", INVALIDAS)
def test_state_impide_transiciones_invalidas(estado, accion):
    e = eleccion_en(estado)
    with pytest.raises(ValueError):
        ACCIONES[accion](e)
    assert e.estado == estado          # la elección no cambió


@pytest.mark.parametrize("estado,accion,destino", [
    ("CONFIGURADA", "abrir", "ABIERTA"), ("ABIERTA", "cerrar", "CERRADA"),
    ("CERRADA", "escrutar", "ESCRUTADA"), ("ESCRUTADA", "firmar_acta", "ESCRUTADA"),
])
def test_state_cada_transicion_valida(estado, accion, destino):
    e = eleccion_en(estado)
    ACCIONES[accion](e)
    assert e.estado == destino


def test_state_publicar_requiere_acta_firmada():
    e = eleccion_en("ESCRUTADA")
    with pytest.raises(ValueError):
        e.publicar()
    e.firmar_acta()
    e.publicar()
    assert e.estado == "PUBLICADA"


def test_state_los_nombres_coinciden_con_el_enum_del_lab_05():
    from votacion.dominio import EstadoEleccion as EnumLab05
    assert [c.nombre for c in (est.Configurada, est.Abierta, est.Cerrada, est.Escrutada, est.Publicada)] \
        == [x.value for x in EnumLab05]


def test_state_las_clases_de_estado_no_preguntan_por_el_nombre_de_otro_estado():
    fuente = inspect.getsource(est)
    assert not re.search(r"\.estado\s*(==|!=)|nombre\s*(==|!=)", fuente)


def test_el_servicio_ya_no_tiene_condicionales_sobre_el_ciclo_de_vida():
    fuente = inspect.getsource(srv.ServicioVotacion)
    for nombre in ("CONFIGURADA", "CERRADA", "ESCRUTADA", "PUBLICADA"):
        assert f'"{nombre}"' not in fuente
