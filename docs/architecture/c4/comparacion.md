## Vista dinámica de C4 vs. diagrama de secuencia UML (flujo "emitir un voto secreto")

La secuencia UML del Lab 05 muestra el detalle que necesita el developer: líneas de vida de clases, nombres de operaciones (regla C1), los fragmentos alt/opt para los casos de error (elección no abierta, voto duplicado), los retornos y el límite de la transacción atómica. La vista dinámica de C4 omite eso: solo muestra los pasos numerados entre componentes, contenedores y sistemas externos del camino feliz, sin ramas ni retornos. Sirve al equipo técnico, a operaciones y a quien quiera entender el recorrido sin leer clases; la secuencia sirve a quien va a programar y a probar. Además, la vista dinámica sale del mismo modelo que las demás, por lo que no se desactualiza si cambia el nombre de un componente.

<!-- E6 completará la comparación escritura a mano vs. modelo exportado -->
