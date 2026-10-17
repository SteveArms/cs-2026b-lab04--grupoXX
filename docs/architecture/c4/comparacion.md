# Comparación de Vistas y Herramientas — VotoEPIS (Lab 06)

## 1. Vista Dinámica C4 vs. Diagrama de Secuencia UML (E4)
La secuencia UML (`secuencia-emitir-voto.puml`) muestra el detalle algorítmico completo en 22 pasos: incluye nombres exactos de métodos (`estaAbierta()`, `existeParticipacion()`), fragmentos condicionales de error (`alt` para elección cerrada o intento de voto duplicado), envíos opcionales (`opt`), mensajes de retorno y el bloque de transacción atómica del ADR-002. La vista dinámica C4 (`EmitirVoto`) omite esas ramificaciones y resume el "camino feliz" en 6 interacciones de alto nivel entre contenedores y componentes. La vista dinámica sirve para explicar el flujo rápidamente al comité electoral, docentes o nuevos integrantes; la secuencia UML sirve a los desarrolladores para programar y escribir pruebas unitarias.

## 2. Diagramación a mano (C4-PlantUML) vs. Modelado único exportado (Structurizr DSL) (E6)

| Criterio | C4-PlantUML escrito a mano (`contexto-manual.puml`) | Modelo único en Structurizr DSL (`workspace.dsl`) |
|---|---|---|
| **Tiempo invertido** | Rápido para un único diagrama aislado (~5 min), pero lento cuando se deben crear y mantener 5 vistas distintas porque obliga a repetir definiciones. | Requiere ~15 min iniciales para declarar el modelo completo, pero las 5 vistas se exportan en segundos sin repetir elementos. |
| **Errores encontrados** | Riesgo de inconsistencias de nombres o descripciones entre archivos `.puml` separados y olvido de leyendas o etiquetas si no se revisa manualmente. | El comando `structurizr validate` verifica automáticamente identificadores inexistentes, tipos inválidos y garantiza que toda flecha en una vista exista en el modelo. |
| **Impacto si mañana cambia el nombre de un contenedor** | Habría que abrir y editar manualmente los archivos de Contenedores, Componentes, Vista Dinámica y Despliegue, corriendo el riesgo de olvidar alguno. | Se cambia el nombre en una sola línea dentro del bloque `model` de `workspace.dsl` y, al exportar, las vistas se actualizan de forma consistente. |
