# Fitness functions de VotoEPIS (Lab 08, E5)

Son pruebas automáticas que impiden que la arquitectura se degrade sin que nadie lo note. Se ejecutan en cada Pull Request con `.github/workflows/fitness.yml`; si alguna falla, el PR no debería aprobarse.

## Cómo ejecutarlas localmente
```bash
pip install import-linter pytest
PYTHONPATH=src lint-imports          # FF-01 a FF-03 (estructurales)
pytest -v tests/test_fitness.py      # FF-04 a FF-09 (calidad), unos 3 s
```

## Inventario
| ID | Tipo | Qué verifica | Origen | Herramienta | Degradación concreta que detecta |
|---|---|---|---|---|---|
| FF-01 | Estructural | Capas `votacion → padron → compartido`, sin ciclos | ADR-001, ADR-004 | import-linter (`layers`) | Alguien hace que `compartido` o `padron` importen `votacion` (el ciclo que el ADR-004 eliminó) |
| FF-02 | Estructural | El dominio (`dominio`, `estados`, `eventos`), `padron` y `compartido` no importan los SDK externos | ADR-005 (Lab 07) | import-linter (`forbidden`, incluye imports transitivos) | Un «atajo temporal» que llama al SDK de correo o del IdP desde el dominio y salta los adaptadores |
| FF-03 | Estructural | El código refactorizado no depende de `votacion.antes` | Lab 07 | import-linter (`forbidden`) | Reutilizar la versión ingenua (con los olores) desde el código nuevo |
| FF-04 | Calidad (rendimiento) | p95 de «emitir voto» ≤ 2 s con 5 votos/s y utilización ≤ 70 %; el correo sigue siendo asíncrono | QA-03, iteración 1 | pytest + `fitness/rendimiento.py` | Volver a enviar el comprobante de forma síncrona o consultar el IdP en cada solicitud |
| FF-05 | Calidad (disponibilidad) | Con el IdP caído 30 min: p95 de votantes con sesión ≤ 2 s, 0 solicitudes cortadas y ≤ 1 llamada cada 30 s al IdP | QA-04, iteración 2 | pytest + `fitness/disponibilidad.py` | Quitar el circuit breaker o el bulkhead |
| FF-06 | Calidad (disponibilidad) | Con el IdP lento (1 s de mediana), «emitir» sigue cumpliendo los 2 s | S1, iteración 2 | pytest + `fitness/disponibilidad.py` | Unir otra vez los workers de login y de votación |
| FF-07 | Calidad (auditabilidad) | 100 % de alteraciones detectadas sobre eventos anclados; anclaje cada ≤ 15 min; verificación < 10 min; eventos sin datos del voto | QA-02, iteración 3, ADR-002 | pytest + `fitness/auditoria.py` | Espaciar el anclaje, quitar la cadena o agregar la opción o el correo a los eventos |
| FF-08 | Calidad (secreto) | En la exportación mezclada, el acierto por posición es ≤ la tasa base | QA-06, iteración 3 | pytest + `fitness/auditoria.py` | Exportar las papeletas en orden de inserción |
| FF-09 | Calidad (secreto) sobre el **código real** | Ninguna `Papeleta` de `src/` tiene campos del votante | ADR-002 | pytest (introspección de `dataclasses`) | Agregar `votante_id` o `timestamp` a la papeleta «para depurar» |

**Límite honesto:** FF-04 a FF-08 protegen el **modelo** con el que se tomaron las decisiones (las simulaciones de `fitness/`), no un despliegue real. Fallan si alguien cambia una táctica o un supuesto en `fitness/`. Para medir el sistema real hace falta un prototipo con prueba de carga (reto opcional A). FF-09 y FF-01 a FF-03 sí revisan el código de `src/`.

## Prueba de que funcionan: violaciones introducidas a propósito

Se hizo en la rama `demo/violacion-fitness`, se ejecutó, se guardó la salida y luego **se revirtió**.

### 1. Violaciones estructurales
Cambios introducidos:
- En `src/compartido/puertos.py`, línea 3: `from votacion.dominio import Papeleta  # atajo: validar papeletas desde el puerto`
- En `src/votacion/estados.py`: `from votacion.externos import CorreoSDK  # "atajo temporal" para notificar al cerrar`

Salida real de `PYTHONPATH=src lint-imports`:
```text
Analyzed 13 files, 10 dependencies.
-----------------------------------

FF-01 Capas del monolito modular sin ciclos: votacion -> padron -> compartido
(ADR-001, ADR-004) BROKEN
FF-02 El dominio y los patrones no conocen los SDK externos; solo la composicion
(ADR-005, Lab 07) BROKEN
FF-03 El codigo refactorizado no depende de la version ingenua 'antes' (Lab 07) KEPT

Contracts: 1 kept, 2 broken.

compartido is not allowed to import votacion:
- compartido.puertos -> votacion.dominio (l.3)

votacion.estados is not allowed to import votacion.externos:
-   votacion.estados -> votacion.externos (l.13)
```

### 2. Violaciones de calidad
Cambios introducidos:
- En `fitness/rendimiento.py`, variante `tres_tacticas`: `correo_sincrono=True` (alguien «simplifica» quitando el Worker).
- En `src/votacion/servicio.py`, `Papeleta`: se agrega `votante_id: str = ""  # "para depurar duplicados"`.

Salida real de `pytest tests/test_fitness.py -q`:
```text
E       AssertionError: p95=119667 ms excede el presupuesto
E       assert True is False
E           AssertionError: votacion.servicio.Papeleta expone {'votante_id'}
FAILED tests/test_fitness.py::test_ff04_rendimiento_pico_de_apertura - Assert...
FAILED tests/test_fitness.py::test_ff04b_el_correo_del_comprobante_sigue_siendo_asincrono
FAILED tests/test_fitness.py::test_ff09_la_papeleta_no_referencia_al_votante
3 failed, 7 passed
```
Con el correo síncrono, el p95 del pico sube de 229 ms a unos 120 s (el sistema satura).

### 3. Reversión
Con los cambios revertidos: `Contracts: 3 kept, 0 broken.` y `10 passed`. En GitHub Actions, el PR de la rama de demostración sale en **rojo** y el último PR en **verde**. Se deben agregar las capturas.

## Deuda técnica registrada
Una versión más estricta de FF-02 («`votacion.servicio` tampoco importa `votacion.externos`») hoy **falla**, porque `ServicioVotacion` es la raíz de composición del prototipo: crea los SDK por defecto, de forma directa y también a través de `autenticacion`. Se dejó fuera del contrato y se anota como deuda: mover la composición a un módulo de arranque (`votacion/arranque.py`) y entonces endurecer FF-02 (ver bitácora).
