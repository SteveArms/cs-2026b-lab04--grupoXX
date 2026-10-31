# ADR-008: Tácticas de Auditabilidad Externa y Preservación del Secreto (QA-02, QA-06)

- **Estado:** Aceptado
- **Fecha:** 2026-10-29
- **Decisores:** Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando

## Contexto
La elección general requiere verificación independiente por auditores externos (QA-02: detectar 100 % de alteraciones en <= 10 min) garantizando que nadie pueda correlacionar el orden de votación con el voto emitido (QA-06).

## Alternativas consideradas
1. Blockchain privada distribuida: Inviable para 1 mes; sobrecosto operativo que viola R-01 y R-03.
2. Publicar un hash único solo al cierre: Detecta 0 % de reescrituras completas de la base de datos realizadas durante la jornada por un administrador malicioso.
3. Cadena de hashes SHA-256 + Anclaje periódico externo cada 15 min + Exportación con mezcla aleatoria criptográfica (shuffle).

## Decisión
Adoptamos la alternativa 3. Cada evento se encadena mediante hash con el anterior. Cada 15 min se publica el hash acumulado en un canal externo no alterable (portal público / correo de auditores). Las papeletas se exportan sin timestamp y con orden aleatorio.

## Evidencia y Consecuencias
- **Evidencia:** El prototipo detecta el 100 % de alteraciones sobre eventos ya anclados; la tasa de adivinación del voto cae de 100 % a la tasa base estocástica (37 % - 46 %).
- **Trade-off:** Obliga a mantener sincronizado el cronómetro de anclaje cada 15 min con el auditor.
