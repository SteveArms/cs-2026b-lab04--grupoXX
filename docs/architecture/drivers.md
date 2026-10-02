# Drivers arquitectónicos — VotoEPIS

Elección digital de delegados estudiantiles de la EPIS-UNSA.
Actores: estudiante votante, comité electoral, auditor.

## 1. Requisitos funcionales clave
| ID    | Requisito                                                                 | Actor             | Prioridad |
|-------|---------------------------------------------------------------------------|-------------------|-----------|
| RF-01 | El comité carga y administra el padrón electoral (estudiantes habilitados) | Comité electoral  | Alta      |
| RF-02 | El estudiante se autentica con su correo institucional                     | Estudiante votante| Alta      |
| RF-03 | El estudiante habilitado emite un único voto por elección                  | Estudiante votante| Alta      |
| RF-04 | El sistema garantiza el secreto del voto (no se vincula voto con votante)  | Estudiante votante| Alta      |
| RF-05 | El sistema realiza el conteo automático al cierre de la votación           | Comité electoral  | Alta      |
| RF-06 | El comité publica resultados y el acta de escrutinio                       | Comité electoral  | Alta      |
| RF-07 | El auditor verifica el conteo de forma independiente                       | Auditor           | Alta      |
| RF-08 | El comité registra listas/candidatos y abre/cierra la votación             | Comité electoral  | Media     |

## 2. Atributos de calidad (ordenados por prioridad)
1. **Seguridad e integridad** — atributo crítico: un voto por estudiante, voto secreto y resultados no alterables; sin esto la elección pierde legitimidad.
2. **Auditabilidad (trazabilidad / responsabilidad, dentro de Seguridad en ISO/IEC 25010:2023)** — el conteo debe poder verificarse de forma independiente.
3. **Fiabilidad (disponibilidad)** — la votación ocurre en una ventana corta; una caída invalida la jornada.
4. **Eficiencia de desempeño** — hay picos de votantes al abrir y antes del cierre.
5. **Capacidad de interacción** — el votante debe poder votar desde celular sin capacitación.

## 3. Restricciones
| ID   | Tipo        | Restricción                                                                                   |
|------|-------------|-----------------------------------------------------------------------------------------------|
| R-01 | Plazo       | MVP en producción en 1 mes                                                                     |
| R-02 | Equipo      | 3 developers con experiencia en Python/Django y PostgreSQL 🔶 (ajustar a lo que realmente dominan) |
| R-03 | Presupuesto | Un solo servidor (VPS) de bajo costo; cualquier servicio de pago debe justificarse             |
| R-04 | Normativa   | Ley 29733 de protección de datos personales (padrón con datos de estudiantes)                  |
| R-05 | Tecnología  | Acceso con correo institucional; no se accede a bases de datos de otros sistemas 🔶            |

## 4. Escenarios de atributos de calidad
| ID    | Atributo                | Fuente                       | Estímulo                                                        | Entorno                                        | Artefacto            | Respuesta                                                                                  | Medida                                                         |
|-------|-------------------------|------------------------------|-----------------------------------------------------------------|------------------------------------------------|----------------------|--------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| QA-01 | Seguridad e integridad  | Estudiante votante autenticado| Envía su voto dos veces (doble clic o dos dispositivos a la vez) | Jornada electoral, 300 votantes concurrentes    | Módulo Votación      | Acepta solo el primer voto, rechaza el segundo y registra el intento en auditoría          | 0 votos duplicados en 1000 intentos concurrentes de prueba; 100 % de intentos registrados |
| QA-02 | Auditabilidad           | Auditor                      | Recalcula el conteo con el archivo público de papeletas anónimas | Cierre de votación, operación normal            | Módulo Escrutinio    | El conteo independiente coincide con el oficial y el hash del archivo coincide con el del acta | Diferencia = 0 votos; verificación completa en ≤ 5 min        |
| QA-03 | Eficiencia de desempeño | 300 estudiantes votantes     | Emiten su voto en simultáneo                                    | Apertura de votación (pico), red universitaria | Módulo Votación (API)| Registra el voto y muestra el comprobante                                                  | p95 del tiempo de respuesta ≤ 3 s                              |