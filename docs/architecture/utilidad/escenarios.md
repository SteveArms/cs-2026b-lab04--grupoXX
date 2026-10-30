# Árbol de utilidad: escenarios priorizados de VotoEPIS (Lab 08, E1)

**Escenario de crecimiento (Tabla 11, caso 5):** la elección se extiende a toda la universidad. Votan **25 000 estudiantes en 8 horas** y hay **auditoría externa**. Los atributos críticos son la integridad, la disponibilidad y la auditabilidad.
**Restricciones vigentes** (`drivers.md`): 1 mes de plazo (R-01), el mismo equipo (R-02), un solo VPS (R-03), la Ley 29733 (R-04) y el monolito modular del ADR-001.

Diagrama: `arbol.dot` → `arbol.png` (`dot -Tpng arbol.dot -o arbol.png`).

## De dónde salen los números de carga

| Dato | Valor | Origen |
|---|---|---|
| Promedio de la jornada | 25 000 / (8 × 3 600 s) = **0,87 votos/s** | Escenario de crecimiento |
| Pico de apertura | 18 % del padrón (≈ 4 500 votantes) en los primeros 15 min = **5 votos/s** | 🔶 Supuesto: correo masivo del comité a las 08:00. Ajustarlo si el comité tiene datos de la elección anterior |
| Solicitudes por votante | 4: login OIDC, ver papeleta, emitir voto y ver comprobante, es decir, **20 solicitudes/s** en el pico | Flujo de `secuencia-emitir-voto.puml` (Lab 05) |

> ⚠️ 25 000 votantes en 8 horas **no** son 25 000 usuarios concurrentes. Es un promedio menor a 1 voto/s, con picos de unos 5 votos/s. Esta es la corrección más importante que se hizo al borrador de la IA (bitácora, entrada 1).

## Escenarios de seis partes

Los IDs QA-01 a QA-03 son los mismos del Lab 04. Se **actualizan** sus medidas al nuevo tamaño y desde QA-04 son escenarios nuevos.

| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida | (I, D) |
|---|---|---|---|---|---|---|---|---|
| QA-03 | Rendimiento | 4 500 votantes tras el correo de apertura | Inician sesión y votan en los primeros 15 min (5 votos/s) | Jornada, pico de apertura, 1 VPS | API (monolito modular) | Registra el voto y muestra el comprobante | **p95 de "emitir voto" ≤ 2 s** | **(H,H)** |
| QA-04 | Disponibilidad | Proveedor de identidad institucional (OIDC) | No responde durante 30 min | Hora punta (2 votos/s) | Módulo Autenticación y API | Los votantes con sesión siguen votando; los demás reciben un aviso claro y una alternativa | Con sesión: **p95 ≤ 2 s y 0 solicitudes cortadas**. **≤ 5 %** de los afectados sin votar al cierre. **≤ 1 llamada cada 30 s** al IdP caído | **(H,H)** |
| QA-05 | Disponibilidad | Sistema operativo o proceso | El VPS o el proceso de la API se reinicia | Jornada en curso | VPS, API y PostgreSQL | El servicio vuelve sin intervención manual | Servicio en **≤ 5 min**; **0 votos confirmados perdidos** (RPO = 0) | (H,M) |
| QA-01 | Seguridad (integridad) | Votante autenticado | Envía su voto 2 veces a la vez (doble clic o dos dispositivos) | Pico de apertura | Módulo Votación y BD | Acepta solo uno y registra el intento | **0 votos duplicados** en 1 000 pares concurrentes; **participaciones = papeletas** | (H,M) |
| QA-06 | Seguridad (secreto) | Quien conoce el orden en que votaron (admin, observador) | Intenta deducir el voto de un votante por la posición de su papeleta | Exportación al auditor y BD | Urna y exportación | No puede deducir más que adivinando | **Acierto ≤ tasa base** (la opción más votada, 🔶 46 %) | (H,M) |
| QA-02 | Seguridad (auditabilidad) | Auditor externo | Recibe la exportación anónima, el registro de auditoría y el acta | Después del cierre | Escrutinio y Auditoría | Recalcula el conteo y verifica que el registro no fue alterado | **Diferencia = 0 votos**; **100 %** de alteraciones detectadas (modificar, borrar, reordenar o reescribir eventos ya anclados); verificación **≤ 10 min** | (H,M) |
| QA-07 | Modificabilidad | Comité / universidad | Pide un medio de autenticación nuevo (p. ej., DNIe) | Desarrollo, entre elecciones | `autenticacion.py` (Lab 07) | Se agrega como estrategia nueva | **≤ 2 días-persona** y **0 líneas cambiadas** en `ServicioVotacion` | (M,L) |
| QA-08 | Modificabilidad | Comité de otra facultad | Configura su propia elección (padrón, opciones, ventana) | Operación normal | Padrón y Votación | Se configura desde la administración | **≤ 30 min**, **sin desplegar código** | (M,M) |

## Por qué cada calificación

- **QA-03 (H,H):** si el pico tumba la API, los estudiantes abandonan y la participación baja, lo que afecta la legitimidad. Es difícil porque el VPS es único (R-03) y los workers de Django son síncronos.
- **QA-04 (H,H):** el ADR-003 ya decía que «si [el IdP] falla, nadie puede votar». Es el único punto de falla que el equipo **no controla**, y la contingencia depende del comité.
- **QA-05 (H,M):** es importante, pero PostgreSQL con commit síncrono y un `systemd`/Docker con reinicio automático ya lo cubren en gran parte (se verificará en E5).
- **QA-01 (H,M):** es el atributo crítico, pero el ADR-002 ya lo resuelve con una restricción única en la BD dentro de la misma transacción. Falta **verificarlo** a escala, no rediseñarlo.
- **QA-06 (H,M):** hay riesgo por el orden de inserción, que ya se reconoce en el ADR-002.
- **QA-02 (H,M):** la auditoría **externa** es nueva. Hoy el registro de auditoría es una tabla común que cualquier administrador puede editar sin dejar rastro.
- **QA-07 (M,L):** el Lab 07 ya lo resolvió con Strategy + Factory. La prueba `test_open_closed_nuevo_medio_sin_modificar_el_servicio` lo demuestra.
- **QA-08 (M,M):** el escenario de crecimiento no exige elecciones simultáneas por facultad; queda para después.

**Escenarios que guían las iteraciones de ADD:** QA-03 → QA-04 → QA-02 (más QA-06). QA-01 y QA-05 se cubrirán con fitness functions en E5.

## Correcciones a la propuesta de la IA (Prompt IA 1)

| La IA propuso | El equipo decidió | Por qué |
|---|---|---|
| «Soportar **25 000 usuarios concurrentes**» | QA-03 con **5 votos/s** en el pico | 25 000 en 8 h son 0,87 votos/s en promedio. Confundir total con concurrencia lleva a sobredimensionar (por ejemplo, a microservicios) |
| QA-01 (doble voto) como **(H,H)** | **(H,M)** | La restricción única del ADR-002 ya existe; la dificultad está en verificarla, no en construirla |
| «El voto debe ser **secreto**» (sin medida) | QA-06 con **acierto ≤ tasa base** | La guía prohíbe medidas como «seguro» o «rápido» |

## Lista de verificación (E1)
- [x] 4 atributos: rendimiento, disponibilidad, seguridad y modificabilidad.
- [x] 8 escenarios (≥ 6), todos con medida numérica. Ninguno dice «rápido», «seguro» ni «fácil».
- [x] Al menos un (H,H) o (H,M) por atributo crítico: integridad (QA-01), disponibilidad (QA-04 y QA-05) y auditabilidad (QA-02).
- [x] Al menos una calificación de la IA corregida y justificada (QA-01).
