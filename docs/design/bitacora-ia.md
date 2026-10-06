# Bitácora de Uso de IA — Entrega E1

- **Fecha:** Octubre 2026
- **Herramienta:** Asistente IA
- **Objetivo:** Generar el diagrama de clases del dominio y diseño para la HU-03 (Votación secreta).

### Prompt utilizado:
> Actúa como diseñador de software orientado a objetos.
> Contexto: módulos Padrón y Votación de VotoEPIS, arquitectura monolito modular en Python/Django bajo arquitectura hexagonal (ADR-001: puertos y adaptadores para integraciones externas). Por ADR-002, el registro de participación (quién votó) y la papeleta (qué se votó) deben estar estrictamente desacoplados sin relación directa entre sí para garantizar el voto secreto (Ley 29733).
> Requisitos del diagrama:
> 1. Mínimo 6 clases, 1 interfaz como puerto hacia servicio externo, 1 enumeración.
> 2. Atributos con tipo y visibilidad, métodos/operaciones en las clases principales.
> 3. Multiplicidades explícitas en ambos extremos de todas las asociaciones.
> 4. Relaciones de composición, asociación, realización y dependencia correctamente tipadas en PlantUML.