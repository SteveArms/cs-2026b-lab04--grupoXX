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


---

## Lab 08 — Diseño de la arquitectura con ADD (VotoEPIS: 25 000 votantes, auditoría externa)

> **Borrador:** las filas resumen lo que propuso el asistente (Claude) al preparar este material y cómo se verificó con las simulaciones de `fitness/`. Reemplacen `<fecha>` y adapten la herramienta y los prompts a sus interacciones reales. La guía pide **5 o más** interacciones y **al menos un falso positivo refutado** (fila 5).

| # | Etapa | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|---|
| 1 | E1 | <fecha> | Claude | Prompt IA 1: escenarios de seis partes para 25 000 votantes en 8 h con auditoría externa | Escenario de rendimiento «soportar 25 000 usuarios concurrentes»; QA de doble voto como (H,H); «el voto debe ser secreto» | 25 000 en 8 h son 0,87 votos/s de promedio, no 25 000 concurrentes: se reescribió como 5 votos/s en el pico. Doble voto bajado a (H,M) porque el ADR-002 ya tiene la restricción única. Secreto reescrito con medida (acierto ≤ tasa base) | Corregida |
| 2 | E2 | <fecha> | Claude | Prompt IA 2: tácticas para QA-03 respetando ADR-001 | Migrar a microservicios + Kubernetes para «escalar horizontalmente» | Simulación M/G/c: con sesión + correo asíncrono + caché, el monolito da p95 = 229 ms en el pico con 54 % de utilización. Viola R-01, R-02 y R-03 | Rechazada |
| 3 | E2 | <fecha> | Claude | Prompt IA 2 (continuación) | «Con 8 workers el pico queda resuelto» | La simulación muestra que con 8 workers el pico sigue saturado (117 %): el problema son las esperas a IdP y SMTP, no la CPU. Queda como plan B | Corregida |
| 4 | E2 | <fecha> | Claude | Prompt IA 2 (continuación) | Cola asíncrona de votos («aceptar ahora, registrar después») | Rompe el ADR-002: se confirmaría un voto que aún no es durable. Lo asíncrono es el correo del comprobante, no el voto | Rechazada |
| 5 | E3 | <fecha> | Claude | Prompt IA 3 (evaluador adversario) sobre nuestro árbol e iteración 1 | Riesgo: «PostgreSQL será el cuello de botella; agreguen réplicas de lectura y Redis» | Falso positivo: 5 votos/s × 60 ms ≈ 30 % de utilización del candado de escritura; las lecturas pesadas ya están en caché y una réplica no ayuda a escribir | Rechazada (falso positivo) |
| 6 | E4 | <fecha> | Claude | Tácticas de contingencia para QA-04 (IdP caído) | OTP por correo institucional como plan de contingencia | Falla de modo común: el correo institucional probablemente es del mismo proveedor que el IdP (🔶 verificar con la OTI). Se reemplazó por la mesa del comité con código de un solo uso + extensión del cierre | Corregida |
| 7 | E4 | <fecha> | Claude | Tácticas de integridad del registro para QA-02 | Blockchain para el registro de auditoría y firma digital de cada evento | El prototipo muestra que cadena de hashes + anclaje externo detecta el 100 % de alteraciones ya ancladas. La firma con una clave en el mismo VPS no protege contra el administrador | Rechazada |
| 8 | E4 | <fecha> | Claude | Frecuencia del anclaje | «Basta con publicar el hash final en el acta» | Con anclaje solo al cierre se detecta el 0 % de las reescrituras completas (sensibilidad medida: 15 min → 92 %). Se fijó el anclaje cada 15 min | Corregida |

### Anexo Lab 08: prompts completos
<pegar el texto exacto de los Prompts IA 1, 2 y 3 usados, con el contexto que se les pasó>
