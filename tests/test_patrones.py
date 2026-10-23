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
