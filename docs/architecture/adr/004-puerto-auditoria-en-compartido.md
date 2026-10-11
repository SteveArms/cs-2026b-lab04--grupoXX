# ADR-004: Definir el puerto RegistroAuditoria en el paquete compartido

Estado: Aceptado
Fecha: 2026-10-07
Decisores: Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando

## Contexto
Votación y Escrutinio deben registrar eventos auditables inmutables (QA-01, RF-07). Auditoría, a su vez, inspecciona los resultados de Escrutinio (QA-02). En el borrador aparecía una llamada directa de Votación a Auditoría, lo que inducía una dependencia cíclica violando el ADR-001 y la regla C4.

## Alternativas consideradas
1. Permitir dependencia bidireccional directa: Acopla los módulos y destruye el aislamiento de Votación.
2. Definir el puerto RegistroAuditoria en compartido: Votación y Escrutinio consumen el puerto; Auditoría lo implementa.
3. Message broker asíncrono (RabbitMQ): Excede el presupuesto y hardware del único VPS (R-03).

## Decisión
Usaremos la alternativa 2. El puerto RegistroAuditoria se ubica en el paquete compartido, eliminando ciclos entre paquetes.

## Consecuencias
Positivas: Cumple la regla C4; Votación queda aislada de la persistencia de Auditoría.
Negativas: Se debe gobernar el paquete compartido para no acumular lógica innecesaria.
