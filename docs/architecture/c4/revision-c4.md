# Revisión de Diagramas con la Lista Oficial de C4 y Auditoría IA — VotoEPIS

## 1. Verificación con el Checklist Oficial (c4model.com)

| Grupo | Pregunta de revisión | Contexto | Contenedores | Componentes | Dinámico | Despliegue | Evidencia en el modelo |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| **General** | ¿Tiene título claro y describe el tipo y alcance? | Sí | Sí | Sí | Sí | Sí | Generado en el encabezado de cada vista (`System Context`, `Container`, `Component`, `Dynamic`, `Deployment`). |
| **General** | ¿Incluye leyenda comprensible? | Sí | Sí | Sí | Sí | Sí | Macro `SHOW_LEGEND(true)` presente en las 5 vistas exportadas. |
| **Elementos** | ¿Cada elemento tiene nombre, tipo y descripción? | Sí | Sí | Sí | Sí | Sí | Todos los elementos declaran nombre, estereotipo C4 y resumen de responsabilidad. |
| **Elementos** | ¿Los contenedores, componentes y nodos indican tecnología? | N/A | Sí | Sí | Sí | Sí | Se especifica `Python / Django`, `PostgreSQL 16`, `Django app`, `Ubuntu 24.04 LTS`, `Docker 27`. |
| **Relaciones** | ¿Cada flecha tiene una etiqueta con verbo de intención? | Sí | Sí | Sí | Sí | Sí | Se usan verbos concretos (`Emite su voto`, `Verifica habilitación`, `Guarda papeleta`), evitando frases vagas. |
| **Relaciones** | ¿Se indica protocolo o tecnología en las interacciones entre contenedores/sistemas? | Sí | Sí | Sí | Sí | Sí | Se especifica `HTTPS`, `HTTPS/JSON (REST)`, `OpenID Connect / HTTPS`, `SQL/TCP` y `SMTP`. |

## 2. Hallazgos del Asistente de IA (Prompt IA 2) y Verificación del Equipo

| Vista | Hallazgo reportado por la IA | Verificación del equipo |
|---|---|---|
| **Contexto** | "Falta indicar el protocolo o tecnología en las flechas entre las personas (Estudiante, Comité, Auditor) y el sistema VotoEPIS." | **Falso positivo rechazado:** En el Nivel 1 (Contexto) el diagrama está dirigido también a público no técnico; la lista oficial de C4 no exige detallar protocolos de interfaz de usuario en las interacciones humanas de nivel 1. |
| **Componentes** | "Las relaciones internas entre módulos (por ejemplo, Votación a Padrón) no indican protocolo de red como HTTP o gRPC." | **Falso positivo rechazado:** La IA asumió que los componentes se comunican por red. Al ser un monolito modular en Django (ADR-001), las llamadas entre componentes son invocaciones a interfaces Python en memoria dentro del mismo proceso. |
| **Despliegue** | "No se especificaba la versión del motor de base de datos PostgreSQL en el contenedor." | **Aceptado y corregido:** Se actualizó la tecnología del contenedor `db` a `PostgreSQL 16` para precisar la especificación en Contenedores y Despliegue. |
| **Todas** | "Todas las vistas cuentan con título, descripción, leyenda y verbos de acción claros." | **Correcto (cumple):** Verificado en los archivos exportados. |
