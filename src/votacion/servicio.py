"""Versión REFACTORIZADA del flujo "emitir un voto secreto" (Lab 07).

E2: la autenticación por medio usa Strategy + Adapter + Factory (ver autenticacion.py).
E3: el ciclo de vida de la elección usa State (ver estados.py).
E4: la auditoría y el comprobante usan Observer (eventos.py); los reintentos, un Decorator (autenticacion.py).
Nota: este módulo es independiente de votacion/dominio.py (esqueleto del Lab 05).
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass
from uuid import UUID

from votacion.autenticacion import fabrica_por_defecto
from votacion.estados import Eleccion, Opcion  # noqa: F401  (re-exportadas: API pública del módulo)
from votacion.eventos import (AuditoriaMemoria, ContadorParticipacion, NotificadorComprobante,
                              PublicadorEventos)
from votacion.externos import CorreoSDK, OtpComiteSDK, ProveedorIdentidadSDK


@dataclass
class Votante:
    correo: str
    habilitado: bool = True


@dataclass
class Papeleta:
    # ADR-002: la papeleta NO referencia al votante.
    eleccion_id: UUID
    opcion_id: UUID


class ServicioVotacion:
    def __init__(self, idp=None, otp=None, correo=None, fabrica=None) -> None:
        self.idp = idp or ProveedorIdentidadSDK()
        self.otp = otp or OtpComiteSDK()
        self.correo = correo or CorreoSDK()
        self.fabrica = fabrica or fabrica_por_defecto(self.idp, self.otp)
        self.auditoria = AuditoriaMemoria()
        self.contador = ContadorParticipacion()
        self.publicador = PublicadorEventos()                # Observer: se pueden suscribir más interesados
        self.publicador.suscribir("voto_emitido", self.auditoria)
        self.publicador.suscribir("voto_rechazado", self.auditoria)
        self.publicador.suscribir("voto_emitido", self.contador)
        self.publicador.suscribir("voto_emitido", NotificadorComprobante(self.correo))
        self.participaciones: set[tuple[str, UUID]] = set()
        self.urna: list[Papeleta] = []

    @property
    def eventos(self) -> list[str]:
        return self.auditoria.eventos

    # ------------------------------------------------------------------ flujo crítico
    def emitir_voto(self, votante, eleccion, opcion_id, medio, credencial, enviar_correo=False):
        autenticador = self.fabrica.crear(medio)            # Factory -> Strategy (+ Decorator de reintentos)
        resultado = autenticador.autenticar(votante.correo, credencial)
        if not resultado.autenticado or resultado.correo != votante.correo:
            self._rechazar("AUTENTICACION_FALLIDA", eleccion, PermissionError("Autenticación fallida"))
        if not eleccion.admite_votos:
            self._rechazar("VOTO_FUERA_DE_VENTANA", eleccion,
                           ValueError(f"La elección no admite votos: está {eleccion.estado}"))
        if not votante.habilitado:
            self._rechazar("VOTANTE_NO_HABILITADO", eleccion,
                           PermissionError("El votante no está habilitado"))
        if (votante.correo, eleccion.id) in self.participaciones:
            self._rechazar("INTENTO_VOTO_DUPLICADO", eleccion, ValueError("Ya emitiste tu voto"))
        if opcion_id not in [o.id for o in eleccion.opciones]:
            raise ValueError("Opción inválida")

        codigo = secrets.token_hex(8)
        self.participaciones.add((votante.correo, eleccion.id))
        self.urna.append(Papeleta(eleccion.id, opcion_id))
        self.publicador.publicar("voto_emitido", {                   # NUNCA incluye la opción (ADR-002)
            "eleccion_id": eleccion.id, "correo": votante.correo,
            "codigo": codigo, "enviar_correo": enviar_correo})
        return codigo

    def _rechazar(self, motivo, eleccion, error):
        self.publicador.publicar("voto_rechazado", {"motivo": motivo, "eleccion_id": eleccion.id})
        raise error

    # ------------------------------------------------------------------ ciclo de vida (State)
    def abrir(self, eleccion):
        eleccion.abrir()

    def cerrar(self, eleccion, ahora):
        eleccion.cerrar(ahora)

    def escrutar(self, eleccion):
        n_papeletas = sum(1 for p in self.urna if p.eleccion_id == eleccion.id)
        n_participaciones = sum(1 for (_, e) in self.participaciones if e == eleccion.id)
        eleccion.escrutar(n_papeletas, n_participaciones)

    def firmar_acta(self, eleccion):
        eleccion.firmar_acta()

    def publicar(self, eleccion):
        eleccion.publicar()

    # ------------------------------------------------------------------ conteo (solo lectura)
    def conteo(self, eleccion) -> dict[str, int]:
        resultado: dict[str, int] = {o.etiqueta: 0 for o in eleccion.opciones}
        for p in self.urna:
            if p.eleccion_id == eleccion.id:
                for o in eleccion.opciones:
                    if o.id == p.opcion_id:
                        resultado[o.etiqueta] += 1
        return resultado
