# VotoEPIS — Laboratorio 04: Fundamentos de Arquitectura de Software
**Construcción de Software · EPIS - UNSA · Semestre 2026-B**

## Integrantes y Roles
| Nombre | Rol en el laboratorio |
|---|---|
| Cuno Cahuari Armando Steven | Analista de Requisitos, Matriz y Diagramador Mermaid (E1, E2, E3, E4) |
| Quiñonez Delgado Aarón Fernando | Ingeniero de Modelado, Despliegue y Decisiones (E5, E6, E7, E8) |

## Caso VotoEPIS
Plataforma web para la elección digital de delegados estudiantiles de la Escuela Profesional de Ingeniería de Sistemas (EPIS - UNSA). Facilita la carga de padrones, sufragio seguro y anónimo, escrutinio automático y auditoría independiente mediante actas con hash criptográfico. Su atributo de calidad crítico es **Seguridad e Integridad**: garantía estricta de un solo voto por estudiante, secreto inviolable y trazabilidad verificable. El MVP debe operar en producción en 1 mes sobre un único VPS.

## Arquitectura Elegida (Monolito Modular)
```mermaid
flowchart TD
Estudiante["Estudiante votante"]
Comite["Comite electoral"]
Auditor["Auditor"]

subgraph VotoEPIS ["VotoEPIS - Monolito modular (un solo despliegue)"]
    Presentacion["Capa de presentacion: web responsive + API REST"]
    Autenticacion["Autenticacion y sesiones"]
    Padron["Padron electoral"]
    Votacion["Votacion (urna anonima)"]
    Escrutinio["Escrutinio y resultados"]
    Auditoria["Auditoria y actas"]
    Infraestructura["Capa de infraestructura: repositorios y adaptadores"]
end

DB[("PostgreSQL\n(schemas: padron, urna, auditoria)")]
CorreoId["Correo institucional\n(proveedor de identidad)"]
CorreoNotif["Servicio de correo\n(comprobantes y actas)"]

Estudiante --> Presentacion
Comite --> Presentacion
Auditor --> Presentacion

Presentacion --> Autenticacion & Padron & Votacion & Escrutinio & Auditoria
Votacion -->|verifica habilitacion| Padron
Escrutinio -->|lee papeletas| Votacion
Votacion -->|registra eventos| Auditoria

Padron & Votacion & Escrutinio & Auditoria --> Infraestructura
Infraestructura --> DB & CorreoId & CorreoNotif
```

## Artefactos del Repositorio
- [Drivers arquitectónicos y escenarios de calidad](docs/architecture/drivers.md)
- [Matriz de decisión ponderada](docs/architecture/matriz-decision.md)
- [Decisiones de Arquitectura (ADR)](docs/architecture/adr/)
- [Alternativa descartada en PlantUML](docs/architecture/diagramas/alternativa.puml)
- [Script de vista de despliegue](docs/architecture/diagramas/despliegue.py)
- [Bitácora crítica de uso de IA](docs/architecture/bitacora-ia.md)

## Reflexión sobre el uso de la IA (Uso Crítico)
Los asistentes de IA aceleraron significativamente la redacción de sintaxis en Diagram as Code y la generación de escenarios de prueba. No obstante, se evidenció un fuerte sesgo inicial hacia soluciones complejas (microservicios y Kubernetes), incompatibles con el plazo de 1 mes y el hardware acordado. La verificación humana contrastando documentación oficial y restricciones de presupuesto evitó sobreingeniería, demostrando que la IA funciona como herramienta de apoyo heurístico, pero la toma de decisiones arquitectónicas recae enteramente en el equipo.

## Diseño UML (Lab 05)

Diseño detallado de la historia crítica **HU-03: emitir un voto secreto**, coherente con la arquitectura de monolito modular (ADR-001) y la preservación del voto secreto (ADR-002).

### Máquina de estados de la Elección
```mermaid
stateDiagram-v2
    [*] --> CONFIGURADA : configurar()
    CONFIGURADA --> ABIERTA : abrir() [2 o más opciones]
    ABIERTA --> CERRADA : cerrar() [hora actual igual o posterior al fin]
    CERRADA --> ESCRUTADA : escrutar() [papeletas = participaciones]
    ESCRUTADA --> ESCRUTADA : firmarActa()
    note left of ESCRUTADA
        firmarActa() no cambia el estado:
        solo marca actaFirmada = true
    end note
    ESCRUTADA --> PUBLICADA : publicar() [acta firmada]
    PUBLICADA --> [*]
```

### Índice de Artefactos de Diseño
| Entregable | Archivo de Código Fuente | Diagrama Renderizado |
|---|---|---|
| **E1: Clases de Dominio** | [`clases.puml`](docs/design/clases.puml) | [Ver Imagen](docs/design/img/clases-votacion.png) |
| **E2: Secuencia (Flujo Crítico)** | [`secuencia-emitir-voto.puml`](docs/design/secuencia-emitir-voto.puml) | [Ver Imagen](docs/design/img/secuencia-emitir-voto.png) |
| **E3: Estados de Elección** | [`estados-eleccion.mmd`](docs/design/estados-eleccion.mmd) | Renderizado en GitHub |
| **E4: Proceso de Escrutinio** | [`actividades-escrutinio-acta.puml`](docs/design/actividades-escrutinio-acta.puml) | [Ver Imagen](docs/design/img/actividades-escrutinio-acta.png) |
| **E5: Paquetes Modulares** | [`paquetes.puml`](docs/design/paquetes.puml) | [Ver Imagen](docs/design/img/paquetes.png) |
| **E6: Round-Trip Engineering** | [`round-trip.md`](docs/design/round-trip.md) | [Clases Pyreverse](docs/design/img/classes_votoepis.png) |
| **E7: Auditoría C1-C5** | [`consistencia.md`](docs/design/consistencia.md) | [Bitácora de IA](docs/design/bitacora-ia.md) |
| **Arquitectura: Nuevo ADR** | [`ADR-004`](docs/architecture/adr/004-puerto-auditoria-en-compartido.md) | — |
