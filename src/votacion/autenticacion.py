"""Autenticación del votante: Strategy + Adapter + Factory (E2) + Decorator de reintentos (E4).

* Strategy : `AutenticadorVotante` es la interfaz común; cada medio es una estrategia intercambiable.
* Adapter  : `OidcAdapter` y `OtpAdapter` traducen cada SDK externo (interfaces distintas) a esa interfaz.
* Factory  : `FabricaAutenticadores` (registro) crea la estrategia por nombre. Agregar un medio = registrarlo.
* Decorator: `ConReintentos` agrega reintentos ante TimeoutError sin modificar los adaptadores ni el servicio.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from votacion.externos import OtpComiteSDK, ProveedorIdentidadSDK


@dataclass(frozen=True)
class ResultadoAutenticacion:
    autenticado: bool
    correo: str | None = None


class AutenticadorVotante(ABC):
    """Puerto común: todos los medios de autenticación se usan igual."""

    @abstractmethod
    def autenticar(self, correo_esperado: str, credencial: str) -> ResultadoAutenticacion: ...


# ---------- ADAPTER: traduce cada SDK a la interfaz AutenticadorVotante ----------
class OidcAdapter(AutenticadorVotante):
    def __init__(self, sdk: ProveedorIdentidadSDK) -> None:
        self._sdk = sdk

    def autenticar(self, correo_esperado, credencial):
        r = self._sdk.validar_token(credencial)          # devuelve un dict
        return ResultadoAutenticacion(r["ok"], r.get("email"))


class OtpAdapter(AutenticadorVotante):
    def __init__(self, sdk: OtpComiteSDK) -> None:
        self._sdk = sdk

    def autenticar(self, correo_esperado, credencial):
        codigo_http, correo = self._sdk.verificar(correo_esperado, credencial)  # devuelve una tupla
        return ResultadoAutenticacion(codigo_http == 200, correo)


# ---------- DECORATOR: agrega reintentos sin modificar los adaptadores ----------
class ConReintentos(AutenticadorVotante):
    """Reintenta SOLO ante TimeoutError. Un rechazo (credencial inválida) NO se reintenta."""

    def __init__(self, interno: AutenticadorVotante, intentos: int = 3) -> None:
        self._interno = interno
        self._intentos = intentos

    def autenticar(self, correo_esperado, credencial):
        for _ in range(self._intentos):
            try:
                return self._interno.autenticar(correo_esperado, credencial)
            except TimeoutError:
                continue
        return ResultadoAutenticacion(False)


# ---------- FACTORY (registro): crea la estrategia adecuada por nombre ----------
class FabricaAutenticadores:
    def __init__(self) -> None:
        self._creadores: dict[str, Callable[[], AutenticadorVotante]] = {}

    def registrar(self, medio: str, creador: Callable[[], AutenticadorVotante]) -> None:
        self._creadores[medio] = creador

    def crear(self, medio: str) -> AutenticadorVotante:
        if medio not in self._creadores:
            raise ValueError(f"Medio de autenticación no soportado: {medio}")
        return ConReintentos(self._creadores[medio]())


def fabrica_por_defecto(idp: ProveedorIdentidadSDK, otp: OtpComiteSDK) -> FabricaAutenticadores:
    fabrica = FabricaAutenticadores()
    fabrica.registrar("OIDC", lambda: OidcAdapter(idp))
    fabrica.registrar("OTP", lambda: OtpAdapter(otp))
    return fabrica
