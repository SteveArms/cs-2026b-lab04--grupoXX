# ADR-002: Separar registro de participación y urna con papeleta anónima

- Estado: Aceptado
- Fecha: 2026-10-01
- Decisores: <Integrante 1>, <Integrante 2>, <Integrante 3>

## Contexto
El sistema debe garantizar un voto por estudiante (RF-03, QA-01) y voto secreto (RF-04), y permitir conteo verificable de forma independiente (RF-07, QA-02). La normativa de datos personales (R-04) exige no vincular innecesariamente identidad y voto.

## Alternativas consideradas
1. Una sola tabla `votos(estudiante_id, candidato_id)`: simple, pero rompe el secreto del voto porque cualquiera con acceso a la BD ve quién votó por quién.
2. Separar `padron.participacion(estudiante_id, ya_voto)` de `urna.papeleta(id_aleatorio, opcion)` sin ninguna clave que los relacione, escritos en una misma transacción atómica.
3. Voto cifrado extremo a extremo con pruebas criptográficas: máximo nivel de verificabilidad, pero muy complejo para 1 mes y 3 developers (R-01, R-02).

## Decisión
Usaremos la alternativa 2. Al votar, en una sola transacción se (a) marca `ya_voto = true` con restricción única por estudiante y elección, y (b) inserta una papeleta con identificador aleatorio y sin referencia al estudiante ni marca de tiempo precisa. Al cierre, las papeletas se mezclan, se exportan de forma anónima y se publica el hash SHA-256 del archivo en el acta para que el auditor recalcule el conteo.

## Consecuencias
- Positivas: se impide el voto doble por restricción a nivel de BD (QA-01); el secreto se protege por diseño; el auditor puede reconstruir el conteo (QA-02); complejidad asumible para el equipo.
- Negativas / riesgos: no ofrece verificabilidad criptográfica de extremo a extremo (el votante no puede comprobar matemáticamente que su voto se contó); un administrador con acceso total a la BD y a los registros de servidor podría intentar correlacionar por tiempos, mitigado con la mezcla y la omisión de marcas de tiempo, pero no eliminado.