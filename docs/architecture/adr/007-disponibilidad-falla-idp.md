# ADR-007: Tácticas de Disponibilidad ante Caídas del Proveedor de Identidad (QA-04)

- **Estado:** Aceptado
- **Fecha:** 2026-10-28
- **Decisores:** Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando

## Contexto
El proveedor de identidad institucional puede sufrir caídas de hasta 30 minutos en hora punta. Durante ese lapso, los estudiantes con sesión abierta deben seguir votando normalmente (p95 <= 2 s) y debe evitarse sobrecargar al servidor externo caído.

## Alternativas consideradas
1. Reintentos ciegos continuos: Empeora la situación saturando los workers locales y bombardeando al IdP.
2. Usar correo institucional como segundo factor de respaldo: Falla de modo común (ambos dependen de Google Workspace).
3. Circuit Breaker + Bulkhead + Mesa de contingencia con códigos OTP físicos emitidos por el comité.

## Decisión
Adoptamos la alternativa 3. Un Circuit Breaker (umbral de 3 fallos, pausa de 30 s) corta llamadas inútiles; un Bulkhead asigna un grupo exclusivo de workers para login aislando el flujo de sufragio; y el comité entrega códigos OTP presenciales a quienes no tengan sesión activa.

## Evidencia y Consecuencias
- **Evidencia:** La simulación reduce llamadas al IdP caído de 1 411 a 59; votantes con sesión mantienen p95 de 139 ms; los alumnos sin votar al cierre caen de 465 (25 %) a 12 (0.6 %).
- **Trade-off:** Requiere presencia física de miembros del comité electoral durante la jornada para validar carnés universitarios si el IdP colapsa.
