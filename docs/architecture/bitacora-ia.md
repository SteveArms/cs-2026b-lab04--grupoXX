# Bitácora de uso de IA — VotoEPIS

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 29/09 | Gemini | Prompt RCRTF: Propuesta de 3 estilos para sistema de votación digital con ~300 concurrentes | Monolito en capas, Monolito modular y Microservicios con Kubernetes | Recomendó microservicios. Se rechazó por violar R-01 (1 mes), R-02 (2 devs) y R-03 (1 VPS). Sobredimensionado para 300 usuarios. | Rechazada |
| 2 | 29/09 | Gemini | Abogado del diablo sobre Monolito Modular en un solo VPS | Alertó sobre cuello de botella en BD y acoplamiento accidental entre módulos | Se verificó y aceptó: se añadieron transacciones ACID independientes, linters de imports (`import-linter`) y esquemas lógicos separados. | Aceptada |
| 3 | 30/09 | Gemini | Generación de código Mermaid para arquitectura monolítica modular | Código con sintaxis de subgraphs y capas | Se detectaron enlaces redundantes entre actores y módulos internos; se corrigió para que todo pase primero por la capa de Presentación Web. | Corregida |
| 4 | 01/10 | Gemini | Generación de script en Python con la librería `diagrams` | Script usando clases no estándar (`diagrams.generic.blank`) para representar la urna | El módulo arrojó error de importación. Se verificó en la documentación oficial de `diagrams.mingrammer.com` y se usaron nodos nativos. | Corregida |
| 5 | 02/10 | Gemini | Alternativa de votación anónima basada en Smart Contracts / Blockchain privada | Implementar un ledger distribuido para registrar cada voto | Se descartó por alta complejidad de despliegue, curva de aprendizaje y nula necesidad técnica para el alcance de un MVP en 1 mes. | Rechazada |

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
