# Auditoría de Consistencia C1-C5 — VotoEPIS

| Regla | Elemento | Hallazgo de la IA | Veredicto del Equipo |
| :---: | :--- | :--- | :--- |
| **C3** | Participacion - Papeleta | "Falta asociación entre Participacion y Papeleta; no se puede saber quién emitió cada voto." | **FALSO POSITIVO IDENTIFICADO Y RECHAZADO**: La IA ignora el secreto del voto electoral (RF-04, ADR-002). Asociar ambas tablas rompería el secreto del voto y violaría la Ley 29733. |
| **C2** | Transición Eleccion | "firmarActa() en el diagrama de estados no cambia el estado y apunta a sí misma en ESCRUTADA." | **Aceptado**: Solo cambia el atributo `acta_firmada = True`, el cual es guarda para pasar a PUBLICADA. Se aclara con una nota en Mermaid. |
| **C4** | Paquetes | "Alerta de ciclo entre Votacion y Auditoria." | **Falso positivo**: El puerto RegistroAuditoria se extrajo a compartido (ADR-004), por lo que Votación no depende de Auditoría. |
| **C1** | Secuencia | "POST /elecciones/{id}/voto no figura en clases.puml." | **Falso positivo de modelado**: Pertenece al controlador web (framework), no a la lógica pura del dominio. |
| **C5** | Lenguaje ubicuo | "Diferencia de nombres entre timestamp y fecha_hora." | **Aceptado y corregido**: Se unificó a `fecha_hora` en todas las capas. |
