# ADR-006: Tácticas de Rendimiento para el Pico de Apertura (QA-03)

- **Estado:** Aceptado
- **Fecha:** 2026-10-27
- **Decisores:** Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando

## Contexto
Para 25 000 votantes en 8 h, el pico de apertura concentra 4 500 votantes en 15 min (5 votos/s). Sin tácticas, la API se satura (utilización > 100 %) y el p95 supera los 16.8 s, violando QA-03 (p95 <= 2 s). Restricción: un único VPS de bajo costo (R-03).

## Alternativas consideradas
1. Migrar a microservicios con Kubernetes: Rechazado (viola R-01 y R-03; costo y complejidad excesivos).
2. Escalar a 8 workers (segundo VPS): Duplica el costo mensual; se guarda como plan de contingencia B.
3. Tres tácticas combinadas sobre el monolito modular: Sesión firmada de 15 min, envío de comprobante asíncrono y caché en memoria de opciones de la elección.

## Decisión
Adoptamos la alternativa 3. Validar el token solo al iniciar sesión reduce llamadas externas; el correo se procesa en segundo plano sin bloquear el hilo HTTP; y las opciones se leen de caché.

## Evidencia y Consecuencias
- **Evidencia:** Simulación M/G/c reduce el p95 en el pico de 16.8 s a 122 ms con 54 % de utilización de CPU.
- **Trade-off aceptado:** Una inhabilitación de último minuto en el padrón puede demorar hasta 15 min en surtir efecto si el alumno ya inició sesión. Se acepta porque el padrón se congela en estado ABIERTA.
