# Inventario de elementos — VotoEPIS (modelo C4)

| Elemento | Tipo C4 | Origen |
|----------|---------|--------|
| Estudiante votante | Persona | drivers.md (RF-02, RF-03) — Lab 04 |
| Comité electoral | Persona | drivers.md (RF-01, RF-05, RF-06, RF-08) — Lab 04 |
| Auditor | Persona | drivers.md (RF-07, QA-02) — Lab 04 |
| VotoEPIS | Sistema de software | Caso (README) |
| Proveedor de identidad del correo institucional | Sistema externo | ADR-003 y arquitectura.mmd (IDP) — Lab 04 |
| Servicio de correo | Sistema externo | arquitectura.mmd (MAIL) — Lab 04; NotificadorCorreo en clases.puml — Lab 05 |
| Aplicación web de votación | Contenedor | arquitectura.mmd (capa de presentación) y despliegue.py (dispositivo del usuario) — Lab 04 |
| API VotoEPIS | Contenedor | ADR-001 (monolito modular Django) y despliegue.py — Lab 04 |
| Base de datos | Contenedor | ADR-001 y ADR-002 (PostgreSQL, un esquema por módulo) — Lab 04 |
| Módulos Autenticación, Padrón, Votación, Escrutinio, Auditoría y Puertos compartidos | Componente (de la API) | paquetes.puml — Lab 05 |
| Flujo "emitir un voto secreto" | Vista dinámica | secuencia-emitir-voto.puml — Lab 05 |

Notas
- Nginx, Docker Compose y Grafana (de despliegue.py) son **infraestructura**: se modelan como nodos en la vista de despliegue (E5), no como contenedores C4.
- El padrón lo carga el comité (RF-01); no se modela un sistema académico externo porque R-05 indica que no se accede a bases de otros sistemas. 🔶 Si su Lab 04 decidió otra cosa, agréguenlo como sistema externo.
