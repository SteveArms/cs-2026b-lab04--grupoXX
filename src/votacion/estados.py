"""Ciclo de vida de la elección: patrón State (E3).

Implementa la máquina de estados de docs/design/estados-eleccion.mmd (Lab 05).
La clase base PROHÍBE todas las transiciones; cada estado redefine SOLO las permitidas,
por lo que una transición inválida es imposible por construcción.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Opcion:
    etiqueta: str
    id: UUID = field(default_factory=uuid4)


class EstadoEleccion:
    nombre = "?"
    admite_votos = False

    def abrir(self, eleccion):
        self._prohibida("abrir")

    def cerrar(self, eleccion, ahora):
        self._prohibida("cerrar")

    def escrutar(self, eleccion, total_papeletas, total_participaciones):
        self._prohibida("escrutar")

    def firmar_acta(self, eleccion):
        self._prohibida("firmar el acta de")

    def publicar(self, eleccion):
        self._prohibida("publicar")

    def _prohibida(self, accion):
        raise ValueError(f"No se puede {accion} una elección {self.nombre}")


class Configurada(EstadoEleccion):
    nombre = "CONFIGURADA"

    def abrir(self, eleccion):
        if len(eleccion.opciones) < 2:                       # guarda: [2 o más opciones]
            raise ValueError("Se requieren al menos 2 opciones")
        eleccion.cambiar_a(Abierta())


class Abierta(EstadoEleccion):
    nombre = "ABIERTA"
    admite_votos = True

    def cerrar(self, eleccion, ahora):
        if eleccion.fin is not None and ahora < eleccion.fin:   # guarda: [hora >= fin]
            raise ValueError("Aún no culmina la ventana de votación")
        eleccion.cambiar_a(Cerrada())


class Cerrada(EstadoEleccion):
    nombre = "CERRADA"

    def escrutar(self, eleccion, total_papeletas, total_participaciones):
        if total_papeletas != total_participaciones:           # guarda: [papeletas = participaciones]
            raise ValueError("Urna no íntegra: papeletas distintas de participaciones")
        eleccion.cambiar_a(Escrutada())


class Escrutada(EstadoEleccion):
    nombre = "ESCRUTADA"

    def firmar_acta(self, eleccion):                           # no cambia de estado (Lab 05)
        eleccion.acta_firmada = True

    def publicar(self, eleccion):
        if not eleccion.acta_firmada:                          # guarda: [acta firmada]
            raise ValueError("Se requiere el acta firmada para publicar")
        eleccion.cambiar_a(Publicada())


class Publicada(EstadoEleccion):
    nombre = "PUBLICADA"                                       # estado final: no permite transiciones


@dataclass
class Eleccion:
    """Contexto del patrón State: delega cada operación en el estado actual."""

    nombre: str
    opciones: list[Opcion] = field(default_factory=list)
    fin: datetime | None = None
    acta_firmada: bool = False
    id: UUID = field(default_factory=uuid4)
    _estado: EstadoEleccion = field(default_factory=Configurada, repr=False)

    @property
    def estado(self) -> str:
        return self._estado.nombre

    @property
    def admite_votos(self) -> bool:
        return self._estado.admite_votos

    def cambiar_a(self, nuevo: EstadoEleccion) -> None:
        self._estado = nuevo

    def abrir(self):
        self._estado.abrir(self)

    def cerrar(self, ahora):
        self._estado.cerrar(self, ahora)

    def escrutar(self, total_papeletas, total_participaciones):
        self._estado.escrutar(self, total_papeletas, total_participaciones)

    def firmar_acta(self):
        self._estado.firmar_acta(self)

    def publicar(self):
        self._estado.publicar(self)
