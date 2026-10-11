# Bitácora de uso de IA — VotoEPIS (Lab 05)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 05/10 | Gemini | Generación de clases para Padrón y Votación | Atributo `estudiante_id` dentro de `Papeleta` | Violaba el secreto del voto (ADR-002, RF-04) | Corregida |
| 2 | 06/10 | Gemini | Generación de secuencia para emitir voto | Registrar la opción elegida en la auditoría | Permitía reconstruir el sentido del voto | Corregida |
| 3 | 07/10 | Gemini | Esqueleto Python 3.10 para Padrón y Votación | Monolito sin módulos y dependencias cruzadas | Se separó en paquetes `padron`, `votacion` y `compartido` | Corregida |
| 4 | 08/10 | Gemini | Diagrama de paquetes a partir de la arquitectura | Acoplamiento bidireccional entre Votación y Auditoría | Generaba ciclo (C4). Se creó el puerto en `compartido` (ADR-004) | Corregida |
| 5 | 09/10 | Gemini | Auditor de consistencia sobre los diagramas UML | "Falta asociación entre Participacion y Papeleta" | Falso positivo: asociarlas vulnera la Ley 29733 y el voto secreto | Rechazada (Falso positivo) |

## Anexo: Prompts Completos

### Prompt 4 (Diagrama de paquetes acíclico):
"Actúa como arquitecto de software. Contexto: monolito modular de VotoEPIS. Genera un diagrama de paquetes en PlantUML que evite dependencias cíclicas entre Votación y Auditoría, aplicando inversión de dependencias mediante un paquete compartido."

### Prompt 5 (Auditor de consistencia):
"Actúa como auditor de diseño UML. Analiza clases.puml, secuencia-emitir-voto.puml, estados-eleccion.mmd, actividades-escrutinio-acta.puml y paquetes.puml. Reporta hallazgos sobre las reglas C1, C2, C3, C4 y C5 en una tabla indicando regla, elemento y problema."
