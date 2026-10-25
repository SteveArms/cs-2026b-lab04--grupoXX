# ADR-005: Refactorización hacia Patrones de Diseño en el Flujo Crítico de VotoEPIS

- **Estado:** Aceptado
- **Fecha:** 2026-10-23
- **Decisores:** Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando

## Contexto
El flujo crítico `emitir_voto` de VotoEPIS presentaba una complejidad ciclomática de **19 (C)** y 50 líneas concentradas en un método monolítico propenso a regresiones. Agregar un nuevo medio de autenticación o suscriptores de auditoría requería alterar la lógica transaccional sensible, violando el principio Abierto/Cerrado. Asimismo, se requería incorporar un asistente de consulta reglamentaria con IA sin permitir que participe en el conteo ni emita respuestas sesgadas.

## Alternativas consideradas
1. **Mantener condicionales estructurados (versión antes):** Simple para un prototipo, pero de altísimo riesgo ante cambios normativos o nuevos proveedores de identidad.
2. **Aplicar patrones GoF justificados por olores de código:** Strategy + Adapter + Factory para autenticación; Decorator para reintentos y caché; State para el ciclo de vida electoral; Observer para auditoría desacoplada; Chain of Responsibility para guardrails de IA.
3. **Adopción masiva de patrones (Patternitis):** Uso de Singleton para fábricas, Abstract Factory y Command para cada voto.

## Decisión
Adoptamos la alternativa 2. Se rechazan explícitamente Singleton (evita estado global que arruina pruebas unitarias), Abstract Factory (innecesaria al no haber familias interdependientes) y Command (el voto es atómico e irrevocable, sin necesidad de undo).

## Consecuencias
- **Positivas:** Reducción de complejidad ciclomática de 19 (C) a 3 (A); nuevos medios de autenticación se registran sin alterar el servicio; el asistente de IA queda completamente aislado y validado antes de llegar al usuario; 88 pruebas automatizadas garantizan ausencia de regresiones.
- **Negativas / riesgos:** Incremento de líneas de código de 130 a 315 e introducción de indirección polimórfica que exige al equipo dominar el catálogo GoF.
