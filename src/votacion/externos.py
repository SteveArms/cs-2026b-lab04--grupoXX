"""Servicios externos SIMULADOS del módulo Votación (sin red ni claves de API).

Las interfaces son distintas entre sí a propósito, como ocurre con SDK reales:
cada uno devuelve un tipo de dato diferente y puede fallar por timeout.
"""
from __future__ import annotations


class ProveedorIdentidadSDK:
    """Proveedor de identidad institucional (OIDC, ADR-003). Responde con un diccionario."""

    def __init__(self, tokens: dict[str, str] | None = None, fallas: int = 0) -> None:
        self._tokens = tokens or {}
        self._fallas = fallas
        self.llamadas = 0

    def validar_token(self, token: str) -> dict:
        self.llamadas += 1
        if self.llamadas <= self._fallas:
            raise TimeoutError("El proveedor de identidad no respondió")
        correo = self._tokens.get(token)
        return {"ok": correo is not None, "email": correo}


class OtpComiteSDK:
    """Contingencia (ADR-003): código de un solo uso emitido por el comité.
    Responde con una tupla (código HTTP, correo verificado)."""

    def __init__(self, codigos: dict[str, str] | None = None, fallas: int = 0) -> None:
        self._codigos = codigos or {}
        self._fallas = fallas
        self.llamadas = 0

    def verificar(self, correo: str, otp: str) -> tuple[int, str | None]:
        self.llamadas += 1
        if self.llamadas <= self._fallas:
            raise TimeoutError("El servicio OTP no respondió")
        if self._codigos.get(correo) == otp:
            return 200, correo
        return 401, None


class CorreoSDK:
    """Servicio de correo institucional. Guarda lo enviado en una bandeja en memoria."""

    def __init__(self) -> None:
        self.bandeja: list[dict] = []

    def enviar(self, destino: str, asunto: str, cuerpo: str) -> dict:
        self.bandeja.append({"destino": destino, "asunto": asunto, "cuerpo": cuerpo})
        return {"enviado": True}
