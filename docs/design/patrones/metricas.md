# Métricas de Complejidad Ciclomática y Análisis de Trade-off — VotoEPIS (Lab 07)

## 1. Comparativa de Complejidad Ciclomática (radon cc)

| Método / Bloque | Antes (condicionales) | Después (patrones) | Mejora / Clasificación |
|---|:---:|:---:|---|
| `ServicioVotacion.emitir_voto` | **19 (C)** | **3 (A)** | Reducción del 84 % en complejidad ciclomática |
| `ServicioVotacion.escrutar` | **7 (B)** | **2 (A)** | Delegado en el patrón State |
| `ServicioVotacion.conteo` | **6 (B)** | **3 (A)** | Simplificado |
| `ServicioVotacion.cerrar` | **5 (A)** | **1 (A)** | Delegado en el patrón State |
| `ServicioVotacion.abrir` | **4 (A)** | **1 (A)** | Delegado en el patrón State |
| **Promedio global del módulo** | **4.69 (A)** | **1.72 (A)** | Disminución drástica de rutas independientes |

## 2. Líneas de Código (SLOC) e Indirección

| Métrica | Antes (`src/votacion/antes/`) | Después (`src/votacion/`) | Variación |
|---|:---:|:---:|:---:|
| Líneas de código ejecutables (SLOC) | 130 | 315 | +142 % (mayor volumen de código) |
| Archivos fuente | 1 (`servicio.py`) | 5 módulos cohesivos | Mayor separación de responsabilidades |
| Métodos a modificar para un nuevo medio de autenticación | 1 (modificar `emitir_voto`) | 0 (solo registrar clase en la fábrica) | Principio Abierto/Cerrado cumplido |
| Cobertura de pruebas | 19 pruebas | 88 pruebas (todas en verde) | Red de seguridad completa |

## 3. Análisis Honesto del Trade-off
El refactor redujo drásticamente el riesgo técnico en el núcleo del sistema electoral: el método crítico `emitir_voto` pasó de una complejidad inaceptable de **19 (C)** a **3 (A)**, eliminando condicionales anidados propensos a regresiones. A cambio de esta flexibilidad y robustez, el número de líneas de código aumentó de 130 a 315 y se introdujo indirección polimórfica que exige al equipo comprender el catálogo GoF.
Si VotoEPIS fuera un script desechable de un solo uso con un único proveedor de correo y sin autenticación multifactor ni asistentes, la versión monolítica inicial habría sido suficiente. Los patrones se justificaron plenamente ante los requerimientos de extensión (nuevos medios de autenticación, observadores de auditoría y guardrails de seguridad).

## 4. Patrones Evaluados y Rechazados
1. **Singleton para `FabricaAutenticadores`:** Rechazado por introducir estado global compartido, lo cual impide paralelizar pruebas e imposibilita inyectar dobles de prueba sin contaminar otros tests.
2. **Abstract Factory:** Rechazado por constituir sobreingeniería (*patternitis*); no existen familias de productos interdependientes que justifiquen una fábrica de fábricas.
3. **Command para el voto:** Rechazado porque en VotoEPIS el sufragio es atómico e irrevocable (no existe operación *undo* ni encolamiento); la auditoría de eventos quedó resuelta de forma más natural y limpia mediante el patrón Observer.
