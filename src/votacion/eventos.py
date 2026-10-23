"""Notificaciones y auditoría desacopladas: patrón Observer (E4).

El servicio PUBLICA hechos ("voto_emitido", "voto_rechazado") y no sabe quién los escucha.
Agregar un interesado nuevo = suscribirlo; el servicio no cambia (Abierto/Cerrado).

Privacidad (ADR-002): los eventos de auditoría solo llevan la elección, NUNCA la opción elegida.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None: ...


class PublicadorEventos:
    def __init__(self) -> None:
        self._suscriptores: dict[str, list[Suscriptor]] = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict) -> None:
        for suscriptor in self._suscriptores.get(evento, []):
            suscriptor.actualizar(evento, datos)


class AuditoriaMemoria(Suscriptor):
    """Registro de auditoría en memoria (puerto RegistroAuditoria del Lab 05, ADR-004)."""

    def __init__(self) -> None:
        self.eventos: list[str] = []

    def actualizar(self, evento, datos):
        codigo = "VOTO_EMITIDO" if evento == "voto_emitido" else datos["motivo"]
        self.eventos.append(f"{codigo}:{datos['eleccion_id']}")


class NotificadorComprobante(Suscriptor):
    """Envía el comprobante de participación por correo si el votante lo pidió."""

    def __init__(self, correo_sdk) -> None:
        self._correo = correo_sdk

    def actualizar(self, evento, datos):
        if datos.get("enviar_correo"):
            self._correo.enviar(datos["correo"], "Comprobante de participación",
                                f"Tu código de comprobante es {datos['codigo']}")


class ContadorParticipacion(Suscriptor):
    """Tablero de participación en vivo: cuenta votos emitidos por elección (sin datos del votante)."""

    def __init__(self) -> None:
        self.por_eleccion: dict[object, int] = {}

    def actualizar(self, evento, datos):
        eleccion = datos["eleccion_id"]
        self.por_eleccion[eleccion] = self.por_eleccion.get(eleccion, 0) + 1
