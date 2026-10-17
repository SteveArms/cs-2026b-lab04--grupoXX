# Bitácora de uso de IA — VotoEPIS (Laboratorio 06: Modelo C4)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 13/10 | Gemini | Prompt IA 1: Generar borrador de `workspace.dsl` a partir de `inventario.md` y `ADR-001` | Modeló "Docker Compose" y "Nginx" como contenedores dentro de `votoepis` | Confundió contenedor C4 con infraestructura. Se movieron a `deploymentNode` en la vista de despliegue (E5). | Corregida |
| 2 | 13/10 | Gemini | Prompt IA 1: Sistemas externos de VotoEPIS en el nivel de Contexto | Agregó un "Sistema Académico UNSA" conectado por base de datos para leer el padrón | Contradice la restricción R-05 (`drivers.md`): no hay acceso a BD externas; el comité carga el padrón (RF-01). Se eliminó. | Rechazada |
| 3 | 14/10 | Gemini | Modelar relaciones entre componentes de la API en `workspace.dsl` | Puso una relación directa de `votacion` a `auditoria` y otra de `auditoria` a `escrutinio` | Creaba dependencia cíclica. Se ajustó para que `votacion` y `escrutinio` usen el componente `compartido` (`RegistroAuditoria`), coherente con `paquetes.puml` y ADR-004. | Corregida |
| 4 | 15/10 | Gemini | Prompt IA 2: Auditar las 5 vistas exportadas con el checklist oficial de C4 | Señaló como error que faltaba protocolo HTTP/gRPC entre los componentes internos de la API | Falso positivo: en un monolito modular las llamadas entre componentes son en memoria, no por red. Se documentó en `revision-c4.md`. | Rechazada (Falso positivo) |
| 5 | 16/10 | Gemini | Prompt IA 3: Explicar el diagrama de contexto en máximo 120 palabras sin jerga técnica | Mencionó términos técnicos como "API REST", "OAuth2/OIDC" y "hash SHA-256" | Se reescribió en lenguaje llano para el comité y estudiantes (114 palabras), verificando fidelidad con el modelo. | Corregida |

## Anexo: Prompts principales utilizados

### Prompt 1 (Borrador Structurizr DSL):
> Actúa como arquitecto de software experto en el modelo C4 y en Structurizr DSL. Contexto: sistema VotoEPIS, monolito modular en Python/Django y PostgreSQL desplegado en un único VPS Ubuntu con Docker Compose (ADR-001, R-03). Escribe un workspace de Structurizr DSL con personas, el sistema, sus contenedores, los 6 componentes de la API (coherentes con paquetes.puml), sistemas externos con etiqueta "Externo" y las 5 vistas (systemContext, container, component, dynamic y deployment). Usa `!identifiers hierarchical`.

### Prompt 2 (Auditor C4):
> Actúa como revisor de diagramas de arquitectura. Evalúa las 5 vistas de VotoEPIS exportadas desde Structurizr DSL aplicando la lista de revisión oficial de c4model.com (general, elementos y relaciones). Responde en una tabla indicando vista, criterio, si cumple o no, evidencia y corrección sugerida.

### Prompt 3 (Explicación para público no técnico):
> Explica el diagrama de contexto de VotoEPIS a un miembro del comité electoral estudiantil que no es técnico, en máximo 120 palabras: qué hace el sistema, quiénes lo usan y de qué servicios externos depende. Evita toda jerga técnica.
