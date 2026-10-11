from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Estudiante:
    correo_institucional: str
    habilitado: bool = True
    id: UUID = field(default_factory=uuid4)

@dataclass
class Participacion:
    estudiante_id: UUID
    eleccion_id: UUID
    codigo_comprobante: str
    fecha_hora: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

class RepositorioPadron(ABC):
    @abstractmethod
    def buscar_habilitado(self, correo: str) -> Estudiante | None:
        ...

    @abstractmethod
    def existe_participacion(self, estudiante_id: UUID, eleccion_id: UUID) -> bool:
        ...

    @abstractmethod
    def guardar_participacion(self, p: Participacion) -> None:
        ...
