from abc import ABC, abstractmethod
from uuid import UUID

class RegistroAuditoria(ABC):
    @abstractmethod
    def registrar(self, evento: str, eleccion_id: UUID) -> None:
        ...
