# Olores de código detectados y patrón propuesto — VotoEPIS (Lab 07)

> **BORRADOR del asistente de IA, a revisar por el equipo.** Ejecuten el Prompt IA 1 de la guía con `src/votacion/antes/servicio.py` y `radon-antes.txt`, comparen su resultado con esta tabla y ajusten. Las líneas son de `src/votacion/antes/servicio.py`.

Flujo refactorizado: **emitir un voto secreto** (`docs/design/secuencia-emitir-voto.puml`, Lab 05). Métrica de partida: `emitir_voto` = **C (19)**; promedio del archivo = A (4,69); 130 SLOC.

| # | Olor | Líneas | Patrón propuesto | Principio | Costo | Decisión del equipo / aplicado en |
|---|------|--------|------------------|-----------|-------|-----------------------------------|
| 1 | `if/elif` por medio de autenticación, con bloque duplicado para OIDC y OTP | 57–76 | Strategy + Factory | O (abierto/cerrado), D | Más clases e indirección (3 archivos en vez de 1) | Aceptado — pendiente (E2) |
| 2 | El servicio conoce el formato de cada SDK (`r["ok"]` dict vs. tupla `codigo_http == 200`) | 60–73 | Adapter | D (inversión), I (interfaces pequeñas) | Una clase por SDK | Aceptado — pendiente (E2) |
| 3 | Bloque de reintentos copiado para cada medio (`for intento in range(3)` ×2) | 58–75 | Decorator (ConReintentos) | S, O | Una clase envoltorio; hay que reintentar SOLO ante TimeoutError | Aceptado — pendiente (E4) |
| 4 | Condicionales anidados sobre `eleccion.estado` en emitir_voto y en abrir/cerrar/escrutar/firmar_acta/publicar | 81–88, 108–152 | State | O, L (sustitución) | Una clase por estado (5) y más líneas | Aceptado — pendiente (E3) |
| 5 | El servicio arma a mano la auditoría (6 `eventos.append`) y el comprobante por correo | 78–103 | Observer | S, O | Publicador y suscriptores; hay que cuidar que los eventos no filtren la opción (ADR-002) | Aceptado — pendiente (E4) |
| 6 | Método largo: `emitir_voto` con complejidad ciclomática 19 (C) y 50 líneas | 55–105 | (consecuencia de 1 a 5: no se resuelve con un patrón aparte) | S | — | Aceptado — pendiente (E2–E4) |
| 7 | Propuesta del asistente: `FabricaAutenticadores` como **Singleton** | — | Singleton | — | Estado global; impide inyectar SDK simulados en las pruebas | **Rechazado** |
| 8 | Propuesta del asistente: **Abstract Factory** para "familias" de autenticadores y notificadores | — | Abstract Factory | — | No hay familias de productos relacionados; sería sobreingeniería (patternitis) | **Rechazado** |
| 9 | Propuesta del asistente: **Command** para modelar "voto como acción auditable" | — | Command | — | El voto es irrevocable (sin deshacer ni cola); el Observer ya cubre la auditoría | **Rechazado** |

Lectura honesta: los patrones se justifican por los **cambios previstos** (nuevos medios de autenticación, nuevos interesados en los eventos, nuevos estados), no por sí mismos. Si VotoEPIS solo fuera a tener un medio de autenticación y nunca cambiara, la versión *antes* habría sido razonable.
