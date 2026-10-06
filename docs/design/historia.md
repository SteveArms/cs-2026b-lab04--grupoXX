# Historia de usuario crítica — VotoEPIS

HU-03: Como estudiante votante de la EPIS, quiero emitir mi voto de forma secreta
       para elegir a mis delegados sin que nadie sepa por quién voté.

Trazabilidad: RF-03, RF-04 · QA-01, QA-03 · ADR-001, ADR-002

Criterios de aceptación:
- CA-1: Dado una elección ABIERTA y un estudiante habilitado que aún no votó,
  cuando selecciona una opción y confirma, entonces el sistema registra una papeleta
  anónima, registra su participación y le muestra un código de comprobante que
  no revela su opción.
- CA-2: Dado un estudiante que ya votó en la elección, cuando intenta votar otra vez
  (otra pestaña o dispositivo), entonces el sistema rechaza el voto, no modifica la
  urna y registra el intento en auditoría.
- CA-3: Dado una elección que no está ABIERTA, cuando el estudiante intenta votar,
  entonces el sistema rechaza el voto y registra el intento en auditoría.
- CA-4: Dado que emití mi voto, cuando solicito una copia del comprobante por correo,
  entonces el sistema envía la constancia asíncronamente a través del servicio externo.