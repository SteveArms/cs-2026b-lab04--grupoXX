# Bitácora de uso de IA — Lab 07 VotoEPIS (patrones de diseño)

> **Borrador:** las filas describen lo que produjo el asistente (Claude) mientras se preparó este material y lo que se verificó con pytest/radon. Reemplacen `<fecha>` y adapten la columna *Herramienta*, la redacción y los prompts a sus interacciones reales. La guía exige **5 o más interacciones** y que **al menos una sea una corrección detectada por las pruebas**; la fila 5 documenta una brecha de pruebas detectada por mutación manual (no por una prueba en rojo): si quieren, provoquen y documenten un caso real propio.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | <fecha> | Claude | Prompt IA 1: detector de olores sobre `antes/servicio.py` + salida de radon | 9 olores con patrón, principio y costo (6 aceptados como problema real, 3 propuestas de patrón rechazadas) | Se contrastó con la lectura del código y con radon: `emitir_voto` = C (19). Se rechazaron Singleton, Abstract Factory y Command | 3 aceptadas, 3 rechazadas |
| 2 | <fecha> | Claude | Generar la versión ingenua del flujo crítico y 19 pruebas de caracterización | `antes/servicio.py`, `externos.py` (SDK simulados) y `test_comportamiento.py` | `pytest`: 19 passed. Se revisó que las pruebas verifican comportamiento observable (estado, eventos, excepciones) y que ninguna llama a servicios reales | Aceptada |
| 3 | <fecha> | Claude | Prompt IA 2: aplicar SOLO Strategy + Adapter + Factory, sin cambiar el comportamiento observable | `autenticacion.py` (puerto, 2 adaptadores, fábrica) y `servicio.py` usando la fábrica | `pytest`: 44 passed (las mismas 19 pruebas sobre antes y después). `emitir_voto`: C(19) → C(14). La prueba `test_open_closed_nuevo_medio...` agrega un medio sin tocar el servicio | Aceptada |
| 4 | <fecha> | Claude | Refactor del ciclo de vida de la elección a State | `estados.py` (clase base que prohíbe todo + 5 estados) y delegación en el servicio | `pytest`: 72 passed (25 casos de transición inválida/válida). Corrección: el servicio seguía comparando `eleccion.estado != "ABIERTA"`; se reemplazó por `admite_votos` del estado | Corregida |

## Anexo: prompts completos
<pegar aquí el texto exacto de cada prompt usado, uno por entrada>
