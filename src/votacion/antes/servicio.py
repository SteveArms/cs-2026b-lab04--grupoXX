"""VERSIÓN INGENUA (antes del refactor) del flujo crítico "emitir un voto secreto".

Se conserva a propósito para comparar métricas y comportamiento con la versión
refactorizada (Lab 07). Corresponde a docs/design/secuencia-emitir-voto.puml.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from votacion.externos import CorreoSDK, OtpComiteSDK, ProveedorIdentidadSDK


@dataclass
class Opcion:
    etiqueta: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Votante:
    correo: str
    habilitado: bool = True


@dataclass
class Papeleta:
    # ADR-002: la papeleta NO referencia al votante.
    eleccion_id: UUID
    opcion_id: UUID


@dataclass
class Eleccion:
    nombre: str
    opciones: list[Opcion] = field(default_factory=list)
    fin: datetime | None = None
    estado: str = "CONFIGURADA"
    acta_firmada: bool = False
    id: UUID = field(default_factory=uuid4)


class ServicioVotacion:
    def __init__(self, idp=None, otp=None, correo=None) -> None:
        self.idp = idp or ProveedorIdentidadSDK()
        self.otp = otp or OtpComiteSDK()
        self.correo = correo or CorreoSDK()
        self.eventos: list[str] = []
        self.participaciones: set[tuple[str, UUID]] = set()
        self.urna: list[Papeleta] = []

    # ------------------------------------------------------------------ flujo crítico
    def emitir_voto(self, votante, eleccion, opcion_id, medio, credencial, enviar_correo=False):
        autenticado, correo_verificado = False, None
        if medio == "OIDC":
            for intento in range(3):
                try:
                    r = self.idp.validar_token(credencial)
                    autenticado, correo_verificado = r["ok"], r.get("email")
                    break
                except TimeoutError:
                    if intento == 2:
                        autenticado = False
        elif medio == "OTP":
            for intento in range(3):
                try:
                    codigo_http, correo_verificado = self.otp.verificar(votante.correo, credencial)
                    autenticado = codigo_http == 200
                    break
                except TimeoutError:
                    if intento == 2:
                        autenticado = False
        else:
            raise ValueError(f"Medio de autenticación no soportado: {medio}")
        if not autenticado or correo_verificado != votante.correo:
            self.eventos.append(f"AUTENTICACION_FALLIDA:{eleccion.id}")
            raise PermissionError("Autenticación fallida")

        if eleccion.estado != "ABIERTA":
            self.eventos.append(f"VOTO_FUERA_DE_VENTANA:{eleccion.id}")
            if eleccion.estado == "CONFIGURADA":
                raise ValueError("La elección aún no abre")
            elif eleccion.estado == "CERRADA":
                raise ValueError("La elección ya cerró")
            else:
                raise ValueError("La elección no está abierta")
        if not votante.habilitado:
            self.eventos.append(f"VOTANTE_NO_HABILITADO:{eleccion.id}")
            raise PermissionError("El votante no está habilitado")
        if (votante.correo, eleccion.id) in self.participaciones:
            self.eventos.append(f"INTENTO_VOTO_DUPLICADO:{eleccion.id}")
            raise ValueError("Ya emitiste tu voto")
        if opcion_id not in [o.id for o in eleccion.opciones]:
            raise ValueError("Opción inválida")

        codigo = secrets.token_hex(8)
        self.participaciones.add((votante.correo, eleccion.id))
        self.urna.append(Papeleta(eleccion.id, opcion_id))
        self.eventos.append(f"VOTO_EMITIDO:{eleccion.id}")
        if enviar_correo:
            self.correo.enviar(votante.correo, "Comprobante de participación",
                               f"Tu código de comprobante es {codigo}")
        return codigo

    # ------------------------------------------------------------------ ciclo de vida
    def abrir(self, eleccion):
        if eleccion.estado == "CONFIGURADA":
            if len(eleccion.opciones) < 2:
                raise ValueError("Se requieren al menos 2 opciones")
            eleccion.estado = "ABIERTA"
        elif eleccion.estado == "ABIERTA":
            raise ValueError("La elección ya está abierta")
        else:
            raise ValueError(f"No se puede abrir una elección {eleccion.estado}")

    def cerrar(self, eleccion, ahora):
        if eleccion.estado == "ABIERTA":
            if eleccion.fin is not None and ahora < eleccion.fin:
                raise ValueError("Aún no culmina la ventana de votación")
            eleccion.estado = "CERRADA"
        elif eleccion.estado == "CONFIGURADA":
            raise ValueError("La elección aún no abre")
        else:
            raise ValueError(f"No se puede cerrar una elección {eleccion.estado}")

    def escrutar(self, eleccion):
        if eleccion.estado == "CERRADA":
            n_papeletas = sum(1 for p in self.urna if p.eleccion_id == eleccion.id)
            n_participaciones = sum(1 for (_, e) in self.participaciones if e == eleccion.id)
            if n_papeletas != n_participaciones:
                raise ValueError("Urna no íntegra: papeletas distintas de participaciones")
            eleccion.estado = "ESCRUTADA"
        else:
            raise ValueError(f"No se puede escrutar una elección {eleccion.estado}")

    def firmar_acta(self, eleccion):
        if eleccion.estado == "ESCRUTADA":
            eleccion.acta_firmada = True
        else:
            raise ValueError(f"No se puede firmar el acta de una elección {eleccion.estado}")

    def publicar(self, eleccion):
        if eleccion.estado == "ESCRUTADA":
            if not eleccion.acta_firmada:
                raise ValueError("Se requiere el acta firmada para publicar")
            eleccion.estado = "PUBLICADA"
        else:
            raise ValueError(f"No se puede publicar una elección {eleccion.estado}")

    # ------------------------------------------------------------------ conteo (solo lectura)
    def conteo(self, eleccion) -> dict[str, int]:
        resultado: dict[str, int] = {o.etiqueta: 0 for o in eleccion.opciones}
        for p in self.urna:
            if p.eleccion_id == eleccion.id:
                for o in eleccion.opciones:
                    if o.id == p.opcion_id:
                        resultado[o.etiqueta] += 1
        return resultado
