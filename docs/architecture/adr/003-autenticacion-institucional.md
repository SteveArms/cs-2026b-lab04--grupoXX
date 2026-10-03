# ADR-003: Autenticar con el correo institucional mediante un proveedor de identidad externo

- Estado: Aceptado
- Fecha: 2026-10-02
- Decisores: <Integrante 1>, <Integrante 2>, <Integrante 3>

## Contexto
Solo los estudiantes del padrón pueden votar (RF-01, RF-02). El acceso debe hacerse con el correo institucional (R-05), con un equipo pequeño y 1 mes de plazo (R-01, R-02). Almacenar contraseñas propias aumentaría el riesgo para QA-01 y las obligaciones de R-04.

## Alternativas consideradas
1. Usuarios y contraseñas propios en VotoEPIS: control total, pero el equipo debe custodiar credenciales y construir recuperación de cuenta.
2. Inicio de sesión con el proveedor de identidad del correo institucional (OAuth2/OpenID Connect), validando que el correo esté en el padrón: no se guardan contraseñas. 🔶 Verificar con la universidad que el proveedor lo permita y qué datos entrega.

## Decisión
Usaremos autenticación delegada al proveedor de identidad del correo institucional. Tras el inicio de sesión, el módulo Autenticación verifica que el correo exista en el padrón habilitado y crea una sesión de corta duración.

## Consecuencias
- Positivas: no se almacenan contraseñas; menos código de seguridad propio; identidad alineada con el padrón.
- Negativas / riesgos: dependencia de un servicio externo (si falla, nadie puede votar), mitigado con pruebas previas y un plan de contingencia acordado con el comité; requiere autorización de la institución para registrar la aplicación.