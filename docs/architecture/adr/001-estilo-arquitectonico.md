# ADR-001: Adoptar un monolito modular para el MVP de VotoEPIS

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: <Integrante 1>, <Integrante 2>, <Integrante 3>

## Contexto
VotoEPIS debe estar en producción en 1 mes (R-01) con 3 developers de Python/Django (R-02) y un único VPS (R-03). El atributo crítico es la seguridad e integridad del voto (QA-01), con conteo verificable (QA-02) y desempeño p95 ≤ 3 s con 300 votantes concurrentes (QA-03). Debe proteger datos del padrón (R-04).

## Alternativas consideradas
1. Monolito en capas (3,90): simple y rápido, pero comparte esquema y lógica entre padrón y votos, debilitando el aislamiento requerido por QA-01.
2. Microservicios (2,55): mayor independencia, pero excede el plazo (R-01), el equipo (R-02) y el presupuesto (R-03), y amplía la superficie de ataque.
3. Monolito modular (4,55): elegido.

## Decisión
Usaremos un monolito modular en Django con cinco módulos (Autenticación, Padrón, Votación, Escrutinio, Auditoría). Los módulos se comunican solo por interfaces públicas (servicios de aplicación) y cada uno tiene su propio esquema en PostgreSQL. Las integraciones externas se implementan como adaptadores.

## Consecuencias
- Positivas: un solo despliegue y bajo costo; entrega dentro de 1 mes; el módulo de Votación queda aislado, lo que favorece QA-01 y QA-02; los módulos pueden extraerse a servicios si la carga lo exige.
- Negativas / riesgos: el equipo debe respetar los límites entre módulos (se usará import-linter en la CI); una falla grave afecta a todo el sistema, por lo que se requieren pruebas y respaldos previos a la jornada.