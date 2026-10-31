# Bitácora de uso de IA — VotoEPIS

**Construcción de Software · EPIS - UNSA · Semestre 2026-B**  
**Autores:** Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando

---

## 1. Registro de Interacciones — Lab 04 (Fundamentos y Alternativas)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 29/09 | Gemini | Prompt RCRTF: Propuesta de 3 estilos para sistema de votación digital con ~300 concurrentes | Monolito en capas, Monolito modular y Microservicios con Kubernetes | Recomendó microservicios. Se rechazó por violar R-01 (1 mes), R-02 (2 devs) y R-03 (1 VPS). Sobredimensionado para 300 usuarios. | Rechazada |
| 2 | 29/09 | Gemini | Abogado del diablo sobre Monolito Modular en un solo VPS | Alertó sobre cuello de botella en BD y acoplamiento accidental entre módulos | Se verificó y aceptó: se añadieron transacciones ACID independientes, linters de imports (`import-linter`) y esquemas lógicos separados. | Aceptada |
| 3 | 30/09 | Gemini | Generación de código Mermaid para arquitectura monolítica modular | Código con sintaxis de subgraphs y capas | Se detectaron enlaces redundantes entre actores y módulos internos; se corrigió para que todo pase primero por la capa de Presentación Web. | Corregida |
| 4 | 01/10 | Gemini | Generación de script en Python con la librería `diagrams` | Script usando clases no estándar (`diagrams.generic.blank`) para representar la urna | El módulo arrojó error de importación. Se verificó en la documentación oficial de `diagrams.mingrammer.com` y se usaron nodos nativos. | Corregida |
| 5 | 02/10 | Gemini | Alternativa de votación anónima basada en Smart Contracts / Blockchain privada | Implementar un ledger distribuido para registrar cada voto | Se descartó por alta complejidad de despliegue, curva de aprendizaje y nula necesidad técnica para el alcance de un MVP en 1 mes. | Rechazada |

---

## 2. Registro de Interacciones — Lab 08 (ADD, ATAM-lite y Fitness Functions)

Para el dimensionamiento a 25 000 votantes en 8 horas, auditoría externa y fitness functions ejecutables (E1 a E5 y E7):

| # | Etapa | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|---|
| 1 | E1 | 25/10 | Claude 3.5 Sonnet | Prompt IA 1: Definición de escenarios de calidad de 6 partes para 25 000 votantes en 8 h con auditoría externa. | Modelar escenario de rendimiento como *"soportar 25 000 usuarios concurrentes"* y calificar doble voto como (H,H). | **Corrección de concurrencia:** 25 000 en 8 h es una tasa media de 0.87 votos/s; concentrando 18 % en 15 min da un pico de 5 votos/s (~20 req/s), no 25 000 simultáneos. Doble voto se bajó a (H,M) porque ADR-002 ya impone la restricción de unicidad en BD. | **Corregida** |
| 2 | E2 | 26/10 | Claude 3.5 Sonnet | Prompt IA 2: Tácticas arquitectónicas para QA-03 respetando el monolito modular (ADR-001). | Migrar a una arquitectura de microservicios orquestada con Kubernetes para *"escalar horizontalmente"*. | **Rechazo de microservicios con Kubernetes:** La simulación M/G/c demostró que el monolito modular con 3 tácticas soporta holgadamente los 5 votos/s con 54 % de CPU en un solo VPS. Kubernetes viola severamente R-01 (1 mes), R-02 (2 devs) y R-03 (1 VPS). | **Rechazada** |
| 3 | E2 | 26/10 | Claude 3.5 Sonnet | Prompt IA 2 (continuación): Aumentar capacidad de cómputo para soportar el pico. | *"Con solo escalar de 4 a 8 workers de Gunicorn en el VPS el pico queda resuelto"*. | **Verificación cuantitativa:** La simulación M/G/c reveló que con 8 workers el sistema **sigue saturado** (117 % de utilización). El cuello de botella son los bloqueos síncronos en llamadas externas (IdP y SMTP), no la CPU. Se mantuvo 8 workers solo como plan B. | **Corregida** |
| 4 | E2 | 27/10 | Claude 3.5 Sonnet | Prompt IA 2 (continuación): Desacoplamiento de la escritura de votos en hora punta. | Emplear una cola asíncrona de votos (*"aceptar ahora la solicitud y escribir el voto después en BD"*). | **Rechazo de cola asíncrona no durable:** Violaría ADR-002 y QA-01 al confirmar a la interfaz un voto que todavía no ha sido persistido de manera durable en PostgreSQL (riesgo de pérdida ante crash). Lo asíncrono debe ser el comprobante por correo, jamás el voto. | **Rechazada** |
| 5 | E3/E7 | 28/10 | ChatGPT (GPT-4o) | Prompt IA 3: Crítica adversarial ATAM-lite sobre cuellos de botella en persistencia relacional. | Riesgo crítico: *"PostgreSQL colapsará con las escrituras en el pico; agreguen réplicas de lectura y Redis para el padrón"*. | **Refutación de falso positivo:** A 5 votos/s con transacciones de 60 ms, la ocupación del candado exclusivo de escritura es apenas del **30 %**. Las lecturas pesadas ya están en caché de aplicación y una réplica de lectura no alivia las escrituras. Redis añadiría inconsistencia eventual no deseada. | **Rechazada (Falso positivo refutado)** |
| 6 | E4 | 29/10 | Claude 3.5 Sonnet | Tácticas de contingencia ante caída del IdP institucional por 30 min (QA-04). | Usar envío de OTP al correo institucional como mecanismo de contingencia alternativo. | **Detección de falla de modo común:** El correo institucional y el IdP universitario comparten típicamente el mismo proveedor de nube (Google Workspace / M365). Si el IdP cae, el correo también es inaccesible. Se adoptó la mesa presencial del comité con códigos OTP físicos (`OtpComiteSDK`). | **Corregida** |
| 7 | E4 | 29/10 | Claude 3.5 Sonnet | Tácticas de integridad del registro electoral para auditores externos (QA-02). | Implementar una blockchain privada y firma criptográfica asimétrica de cada evento con la clave privada del servidor. | **Evaluación de amenaza:** Si la clave privada reside en el mismo VPS, no protege contra un administrador con acceso root malicioso. La combinación de cadena de hashes SHA-256 local y anclaje periódico externo en canal de auditores ofrece 100 % de detección con costo computacional mínimo (< 0.1 s). | **Rechazada** |
| 8 | E4 | 30/10 | Claude 3.5 Sonnet | Determinación de la frecuencia de anclaje externo de hashes. | *"Basta con publicar únicamente el hash final en el acta electoral al momento del cierre"*. | **Simulación estocástica de ataques:** Anclar únicamente al cierre detecta el 0 % de reescrituras completas de la base de datos realizadas durante el día. La sensibilidad medida mostró que anclar cada 15 min eleva la detección al 92 % general y al 100 % de los eventos ya anclados. | **Corregida** |
| 9 | E5/E7 | 31/10 | Claude 3.5 Sonnet | Definición de contratos en `import-linter` para preservar la arquitectura hexagonal modular. | Contrato estricto: *"votacion.servicio no puede importar votacion.externos"*. | **Verificación en código:** `lint-imports` arrojó `BROKEN` porque en el prototipo `ServicioVotacion` actúa como raíz de composición por defecto instanciando adaptadores. Se redefinió la regla protegiendo estrictamente el dominio, los patrones GoF, padrón y compartido, documentando la deuda técnica de composición. | **Corregida** |

---

## 3. Anexo: Prompts Completos

### Lab 04

#### Prompt 1 (Generación de alternativas)
> Actúa como arquitecto de software senior. Contexto: Sistema VotoEPIS para elección digital de delegados de la EPIS-UNSA. Padrón electoral, voto secreto, conteo automático y actas auditables. Concurrencia pico: ~300 votantes. Restricciones: 2 developers, 1 mes de plazo, 1 único VPS de bajo costo, cumplimiento de la Ley 29733. Propón 3 alternativas de estilo arquitectónico indicando fortalezas, debilidades y qué atributos favorecen.

#### Prompt 2 (Crítica adversarial / Abogado del diablo)
> Actúa como abogado del diablo. Critica duramente la alternativa del Monolito Modular para VotoEPIS en un solo servidor: ¿qué riesgos existen de acoplamiento, fallas en la base de datos y saturación en hora pico? Enumera mitigaciones técnicas concretas.

#### Prompt 3 (Diagrama Mermaid)
> Genera el código Mermaid (`flowchart TD`) para VotoEPIS considerando: actores (Estudiante, Comité, Auditor), monolito con módulos (Autenticación, Padrón, Votación, Escrutinio, Auditoría) y servicios externos (PostgreSQL, Correo Institucional).

#### Prompt 4 (Script de Despliegue)
> Escribe un script en Python usando la librería `diagrams` que modele un despliegue en un VPS Ubuntu con Nginx, Django, PostgreSQL, Grafana y servicios de autenticación externa.

#### Prompt 5 (Mecanismo de Integridad y Secreto)
> ¿Es conveniente utilizar una blockchain ligera o tablas desacopladas con hash SHA-256 para garantizar el secreto del voto y auditoría en un sistema electoral universitario de 1 mes de plazo?

---

### Lab 08

#### Prompt IA 1 (E1: Escenarios y dimensionalidad para 25 000 votantes)
> Actúa como arquitecto de software y analista de rendimiento. Contexto: VotoEPIS escalará a elecciones generales de la UNSA con 25 000 votantes registrados. La elección dura 8 horas ininterrumpidas. Se requiere modelar los escenarios de calidad de 6 partes según Bass et al. para:
> 1. Rendimiento en hora pico y apertura.
> 2. Disponibilidad ante fallas del proveedor de identidad universitario.
> 3. Integridad y auditoría externa independiente.
> Define estímulos, fuentes, entornos, artefactos, respuestas y medidas de respuesta cuantitativas realistas.

#### Prompt IA 2 (E2: Tácticas arquitectónicas de rendimiento bajo restricciones)
> Actúa como arquitecto de software experto en el método ADD. Tenemos el escenario QA-03: en el pico de apertura votan 4 500 personas en 15 minutos (5 votos/s). La arquitectura base es un monolito modular en Django desplegado en un único VPS (4 vCPU, 8 GB RAM). Requisito: el percentil 95 (p95) de emisión de voto debe ser menor o igual a 2 segundos.
> ¿Qué tácticas arquitectónicas concretas permiten garantizar este SLA sin romper el presupuesto ni violar ADR-001 (Monolito) ni ADR-002 (Integridad transaccional del voto)? Evalúa el impacto de: microservicios, aumento de workers, manejo de sesiones, asincronía y caché.

#### Prompt IA 3 (E3/E7: Evaluador adversario ATAM-lite y cuellos de botella en BD)
> Actúa como un evaluador arquitectónico externo implacable bajo el método ATAM. Revisa el diseño propuesto para VotoEPIS con 25 000 votantes sobre un único VPS con PostgreSQL y Django. Encuentra fallas potenciales catastróficas, cuellos de botella en contención de base de datos, riesgos de punto único de falla (SPOF) y trade-offs inaceptables. Sé escéptico y argumenta si PostgreSQL colapsará en escrituras.

#### Prompt IA 4 (E4: Resiliencia ante caída del IdP institucional)
> Contexto VotoEPIS: Durante la jornada electoral de 8 horas, el servidor OIDC institucional de la universidad suele presentar microcortes y una caída conocida de hasta 30 minutos en horas punta. Requisito QA-04: los votantes con sesión activa deben poder seguir emitiendo su voto sin interrupciones (p95 ≤ 2 s) y menos del 5 % de los votantes totales puede quedar insatisfecho al cierre.
> Propón tácticas arquitectónicas de disponibilidad y patrones de resiliencia aplicables en la capa de adaptadores para aislar este fallo externo.

#### Prompt IA 5 (E4: Auditoría externa, cadena de hashes y voto secreto)
> Diseña el mecanismo de auditoría para VotoEPIS que permita a un comité auditor independiente verificar después de la elección que ninguna autoridad ni administrador con privilegios de base de datos haya modificado, insertado o eliminado votos. Restricciones:
> 1. Verificación completa en menos de 10 minutos para 27 000 eventos de log.
> 2. Cumplimiento de la Ley 29733: nadie, ni el auditor, debe poder inferir qué votó cada estudiante relacionando las marcas temporales o secuencias.
