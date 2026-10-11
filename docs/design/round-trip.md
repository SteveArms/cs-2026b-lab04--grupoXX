# Comparación Round-Trip — VotoEPIS (clases.puml vs pyreverse)

| # | Diferencia observada | Causa técnica | Acción tomada |
|---|----------------------|---------------|---------------|
| 1 | Composición Eleccion-Opcion y Eleccion-Papeleta no aparece como rombo negro; se muestra como atributo de lista. | pyreverse no deduce composición a partir de `list[T]`. | Ninguna en diagrama: limitación de herramienta. Se mantiene el diseño. |
| 2 | Ausencia de multiplicidades cardinales (ej. 2..* en opciones). | El sistema de tipos de Python no expresa límites numéricos de negocio. | Se añadieron guardas en el método `abrir()` de Eleccion para validar `len(opciones) >= 2`. |
| 3 | Participacion y Papeleta muestran `estudiante_id` y `eleccion_id` como UUID, no como flechas asociativas. | Desacoplamiento modular explícito para evitar dependencias circulares en memoria. | Aceptable: respalda el ADR-002 (no vincular identidad con papeleta). |
| 4 | Interfaces aparecen como clases convencionales. | Python no tiene interfaces nativas; usa herencia de `abc.ABC`. | Aceptable en Python; documentado. |
| 5 | Nombres en snake_case frente a camelCase de UML. | Convención PEP 8 de Python. | Aceptable: equivalencia 1:1 verificada (Regla C5). |
| 6 | Excepciones EleccionNoAbierta y VotoDuplicado presentes en código pero no en el diagrama original. | Refinamiento de implementación para soportar las ramas alternativas del diagrama de secuencia. | Se documenta como soporte del flujo de error. |
