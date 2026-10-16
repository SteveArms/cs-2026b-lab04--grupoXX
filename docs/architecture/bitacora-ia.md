## Tabla resumen
 
| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 16/10/2026 | Claude | Comparar los componentes C4 (nivel 3) con `docs/design/paquetes.puml` y la arquitectura del Lab 04 | Modelar 6 componentes con las mismas dependencias que `paquetes.puml`; señaló que `arquitectura.mmd` y el README conservan la flecha `Votacion -->\|registra eventos\| Auditoria` | Esa flecha crea el ciclo `votacion → auditoria → escrutinio → votacion`, que el ADR-004 dice haber eliminado con el puerto `RegistroAuditoria` en `compartido`. Se corrigió el Mermaid del Lab 04 (artefacto equivocado) | Corregida |
| 2 | 16/10/2026 | Claude y Structurizr CLI | Generar el DSL y exportarlo a C4-PlantUML y Mermaid | Etiquetar los sistemas externos con `"Externo"` y un estilo gris | `validate` sin errores. En Mermaid los externos salen grises; en C4-PlantUML la etiqueta se pierde (`$tags=""`) y salen del mismo azul que VotoEPIS | Aceptada con limitación documentada |
| 3 | 16/10/2026 | Claude | Prompt IA 1 con el inventario y los ADR | 3 contenedores: aplicación web, API Django y PostgreSQL | Se justifica la web separada (corre en el navegador del usuario; la guía pide 3 o más contenedores). Se rechazó Nginx y Docker Compose como contenedores (infraestructura, E5) y Redis/Celery (no figuran en los ADR) | Aceptada con ajustes |

## Anexo: Prompts completos

### Prompt 1 (Generación de alternativas)
> Actúa como arquitecto de software senior. Contexto: Sistema VotoEPIS para elección digital de delegados de la EPIS-UNSA. Padrón electoral, voto secreto, conteo automático y actas auditables. Concurrencia pico: ~300 votantes. Restricciones: 2 developers, 1 mes de plazo, 1 único VPS de bajo costo, cumplimiento de la Ley 29733. Propón 3 alternativas de estilo arquitectónico indicando fortalezas, debilidades y qué atributos favorecen.

### Prompt 2 (Crítica adversarial / Abogado del diablo)
> Actúa como abogado del diablo. Critica duramente la alternativa del Monolito Modular para VotoEPIS en un solo servidor: ¿qué riesgos existen de acoplamiento, fallas en la base de datos y saturación en hora pico? Enumera mitigaciones técnicas concretas.

### Prompt 3 (Diagrama Mermaid)
> Genera el código Mermaid (`flowchart TD`) para VotoEPIS considerando: actores (Estudiante, Comité, Auditor), monolito con módulos (Autenticación, Padrón, Votación, Escrutinio, Auditoría) y servicios externos (PostgreSQL, Correo Institucional).

### Prompt 4 (Script de Despliegue)
> Escribe un script en Python usando la librería `diagrams` que modele un despliegue en un VPS Ubuntu con Nginx, Django, PostgreSQL, Grafana y servicios de autenticación externa.

### Prompt 5 (Mecanismo de Integridad y Secreto)
> ¿Es conveniente utilizar una blockchain ligera o tablas desacopladas con hash SHA-256 para garantizar el secreto del voto y auditoría en un sistema electoral universitario de 1 mes de plazo?
