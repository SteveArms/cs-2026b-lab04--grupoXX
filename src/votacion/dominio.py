from __future__ import annotations
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from padron.dominio import Estudiante, Participacion, RepositorioPadron
from compartido.puertos import RegistroAuditoria

class EstadoEleccion(Enum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    ESCRUTADA = "ESCRUTADA"
    PUBLICADA = "PUBLICADA"

class EleccionNoAbierta(Exception):
    pass

class VotoDuplicado(Exception):
    pass

@dataclass
class Opcion:
    etiqueta: str
    id: UUID = field(default_factory=uuid4)

@dataclass
class Papeleta:
    eleccion_id: UUID
    opcion_id: UUID
    id: UUID = field(default_factory=uuid4)

@dataclass
class Eleccion:
    nombre: str = ""
    inicio: datetime | None = None
    fin: datetime | None = None
    estado: EstadoEleccion = EstadoEleccion.CONFIGURADA
    acta_firmada: bool = False
    opciones: list[Opcion] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def configurar(self, nombre: str, inicio: datetime, fin: datetime) -> None:
        if inicio >= fin:
            raise ValueError("El inicio debe preceder al fin")
        self.nombre, self.inicio, self.fin = nombre, inicio, fin

    def agregar_opcion(self, opcion: Opcion) -> None:
        self.opciones.append(opcion)

    def esta_abierta(self) -> bool:
        return self.estado == EstadoEleccion.ABIERTA

    def abrir(self) -> None:
        if self.estado != EstadoEleccion.CONFIGURADA or len(self.opciones) < 2:
            raise ValueError("Requiere estado CONFIGURADA y al menos 2 opciones")
        self.estado = EstadoEleccion.ABIERTA

    def cerrar(self, ahora: datetime) -> None:
        if self.estado != EstadoEleccion.ABIERTA:
            raise ValueError("Solo se cierra una elección ABIERTA")
        if self.fin and ahora < self.fin:
            raise ValueError("Aún no culmina la ventana de votación")
        self.estado = EstadoEleccion.CERRADA

    def escrutar(self, total_papeletas: int, total_participaciones: int) -> None:
        if self.estado != EstadoEleccion.CERRADA or total_papeletas != total_participaciones:
            raise ValueError("Urna no íntegra: papeletas != participaciones")
        self.estado = EstadoEleccion.ESCRUTADA

    def firmar_acta(self) -> None:
        if self.estado != EstadoEleccion.ESCRUTADA:
            raise ValueError("Solo se firma el acta de una elección ESCRUTADA")
        self.acta_firmada = True

    def publicar(self) -> None:
        if self.estado != EstadoEleccion.ESCRUTADA or not self.acta_firmada:
            raise ValueError("Se requiere acta firmada para publicar")
        self.estado = EstadoEleccion.PUBLICADA

class RepositorioVotacion(ABC):
    @abstractmethod
    def buscar_eleccion(self, id: UUID) -> Eleccion:
        ...

    @abstractmethod
    def guardar_papeleta(self, p: Papeleta) -> None:
        ...

class NotificadorCorreo(ABC):
    @abstractmethod
    def enviar_comprobante(self, correo: str, codigo: str) -> None:
        ...

class CorreoAdapter(NotificadorCorreo):
    def enviar_comprobante(self, correo: str, codigo: str) -> None:
        raise NotImplementedError("Integración con servicio SMTP institucional pendiente")

class ServicioVotacion:
    def __init__(
        self,
        repo_votacion: RepositorioVotacion,
        repo_padron: RepositorioPadron,
        notificador: NotificadorCorreo,
        auditoria: RegistroAuditoria,
    ) -> None:
        self._votacion = repo_votacion
        self._padron = repo_padron
        self._notificador = notificador
        self._auditoria = auditoria

    def emitir_voto(
        self,
        estudiante: Estudiante,
        eleccion_id: UUID,
        opcion_id: UUID,
        enviar_correo: bool,
    ) -> str:
        eleccion = self._votacion.buscar_eleccion(eleccion_id)
        if not eleccion.esta_abierta():
            self._auditoria.registrar("VOTO_FUERA_DE_VENTANA", eleccion_id)
            raise EleccionNoAbierta()
        if self._padron.existe_participacion(estudiante.id, eleccion_id):
            self._auditoria.registrar("INTENTO_VOTO_DUPLICADO", eleccion_id)
            raise VotoDuplicado()

        codigo = secrets.token_hex(8)
        self._padron.guardar_participacion(Participacion(estudiante.id, eleccion_id, codigo))
        self._votacion.guardar_papeleta(Papeleta(eleccion_id, opcion_id))
        self._auditoria.registrar("VOTO_EMITIDO", eleccion_id)
        if enviar_correo:
            self._notificador.enviar_comprobante(estudiante.correo_institucional, codigo)
        return codigo
