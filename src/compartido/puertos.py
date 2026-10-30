from abc import ABC, abstractmethod
from uuid import UUID
from votacion.dominio import Papeleta  # atajo: validar papeletas desde el puerto

class RegistroAuditoria(ABC):
    @abstractmethod
    def registrar(self, evento: str, eleccion_id: UUID) -> None:
        ...
