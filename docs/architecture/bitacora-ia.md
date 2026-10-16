# Bitácora de uso de IA — Lab 06 VotoEPIS (modelo C4)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 16/10/2026 | Claude | Prompt IA 1: borrador de `workspace.dsl` a partir del inventario, los ADR-001/002/003 y `despliegue.py` | DSL con 3 personas, el sistema, 2 externos, 3 contenedores, 6 componentes y las vistas de contexto, contenedores, componentes y dinámica | Se verificó que solo use tecnologías de los ADR y que los componentes coincidan con `paquetes.puml`. `structurizr validate` sin errores en las cuatro etapas | Aceptada con ajustes |
| 2 | 16/10/2026 | Claude | Misma conversación: decidir los contenedores (E2) | 3 contenedores: aplicación web, API Django y PostgreSQL | Se justifica la web separada (corre en el navegador del usuario; la guía pide 3 o más contenedores). Se rechazó Nginx y Docker Compose como contenedores (infraestructura, E5) y Redis/Celery (no figuran en los ADR) | Aceptada con ajustes |
| 3 | 16/10/2026 | Claude y Structurizr CLI | Exportar el DSL a C4-PlantUML y Mermaid | Etiquetar los sistemas externos con `"Externo"` y un estilo gris | `validate` sin errores. En Mermaid los externos salen grises; en C4-PlantUML la etiqueta se pierde (`$tags=""`) y salen del mismo azul que VotoEPIS | Aceptada con limitación documentada |
| 4 | 16/10/2026 | Claude | Comparar los componentes C4 con `docs/design/paquetes.puml` y la arquitectura del Lab 04 | 6 componentes con las dependencias de `paquetes.puml`; señaló que `arquitectura.mmd` y el README conservan `Votacion -->\|registra eventos\| Auditoria` | Esa flecha forma el ciclo `votacion → auditoria → escrutinio → votacion`, que el ADR-004 dice haber eliminado con el puerto `RegistroAuditoria` en `compartido`. Se corrigió el Mermaid del Lab 04 (artefacto equivocado) | Corregida |
| 5 | 16/10/2026 | Claude y Structurizr CLI | Vista dinámica "Emitir voto" a partir de `secuencia-emitir-voto.puml` | 6 pasos: web → Votación → Padrón → BD, Votación → BD, Votación → puerto compartido y Votación → correo | Cada paso corresponde a una relación ya declarada en el modelo (si no, `validate` falla). Se omitieron a propósito las ramas de error, los retornos y la transacción, y se documentó en `comparacion.md` | Aceptada |

## Detalle de las correcciones

### Entrada 4 — Contradicción entre `arquitectura.mmd` y el ADR-004 (E3)
- **Qué propuso la IA:** modelar los 6 componentes de la API con las mismas dependencias que `paquetes.puml`, y señaló la flecha `Votacion -->|registra eventos| Auditoria` que seguía en `arquitectura.mmd` y en el README.
- **Qué verificamos:** esa flecha crea la dependencia `votacion → auditoria`; junto con `auditoria → escrutinio → votacion` forma un ciclo, que el ADR-004 dice haber eliminado. El modelo C4 no la tiene: Votación usa el puerto y Auditoría lo implementa.
- **Corrección:** se cambió `Votacion -->|registra eventos| Auditoria` por `Auditoria -->|lee acta y hash| Escrutinio` en `arquitectura.mmd` y en el README, y se regeneró `arquitectura.png`.

### Entrada 3 — Etiqueta `Externo` en la exportación PlantUML (E2)
- **Qué verificamos:** el exportador de C4-PlantUML descarta la etiqueta (`$tags=""`), por lo que los externos no se distinguen por color en el PNG.
- **Corrección:** no se cambió el modelo; la etiqueta se mantiene en el DSL. Se documenta la limitación y se indica que la versión Mermaid sí muestra los externos en gris.

### Entrada 2 — Contenedor web separado del monolito (E2)
- **Qué verificamos:** en el Lab 04 la capa de presentación estaba dentro del monolito. Se separó como contenedor porque es código que corre en el navegador del usuario.
- **Corrección:** se rechazaron Nginx y Docker Compose como contenedores y no se agregó Redis ni Celery, que no figuran en los ADR.

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
