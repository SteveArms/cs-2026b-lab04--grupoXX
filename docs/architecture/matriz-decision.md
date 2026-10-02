# Matriz de decisión — VotoEPIS

## Alternativas
- **A. Monolito en capas:** una sola aplicación desplegada en un servidor, organizada en presentación, lógica de negocio y acceso a datos. Una sola base de datos compartida.
- **B. Monolito modular:** un solo despliegue dividido en módulos de dominio (Autenticación, Padrón, Votación, Escrutinio, Auditoría) que se comunican solo por interfaces públicas; esquema de BD separado por módulo.
- **C. Microservicios:** servicios independientes (padrón, votación, escrutinio, auditoría) con su propia base de datos, un API Gateway y un broker de eventos.

## Criterios y pesos (deben sumar 100 %)
| Criterio                 | Peso  | Justificación (driver relacionado)                                                        |
|--------------------------|-------|-------------------------------------------------------------------------------------------|
| Seguridad e integridad   | 30 %  | QA-01: atributo crítico; el aislamiento del módulo de votos y de la urna es central       |
| Tiempo de entrega        | 20 %  | R-01: el MVP debe estar en producción en 1 mes                                            |
| Costo operativo          | 15 %  | R-03: un solo VPS de bajo costo                                                           |
| Simplicidad operativa    | 15 %  | R-02: 3 developers sin equipo de DevOps                                                   |
| Auditabilidad            | 10 %  | QA-02 / RF-07: el conteo debe poder verificarse de forma independiente                    |
| Modificabilidad          | 10 %  | RF-08: cambios futuros (nuevas elecciones, reglas) sin afectar otros módulos              |
| **Total**                | 100 % |                                                                                           |

## Matriz (puntaje 1 = muy malo … 5 = excelente)
| Criterio (peso)               | A. Capas | B. Monolito modular | C. Microservicios |
|-------------------------------|:--------:|:-------------------:|:-----------------:|
| Seguridad e integridad (30 %) | 3        | 5                   | 3                 |
| Tiempo de entrega (20 %)      | 5        | 4                   | 2                 |
| Costo operativo (15 %)        | 5        | 5                   | 2                 |
| Simplicidad operativa (15 %)  | 5        | 4                   | 1                 |
| Auditabilidad (10 %)          | 3        | 5                   | 3                 |
| Modificabilidad (10 %)        | 2        | 4                   | 5                 |
| **Total ponderado**           | **3,90** | **4,55**            | **2,55**          |

Total ponderado = Σ (peso × puntaje).
- A: 0,30×3 + 0,20×5 + 0,15×5 + 0,15×5 + 0,10×3 + 0,10×2 = 3,90
- B: 0,30×5 + 0,20×4 + 0,15×5 + 0,15×4 + 0,10×5 + 0,10×4 = 4,55
- C: 0,30×3 + 0,20×2 + 0,15×2 + 0,15×1 + 0,10×3 + 0,10×5 = 2,55

## Justificación de puntajes clave
- **Seguridad/integridad:** B permite esquemas separados (`padron`, `urna`, `auditoria`) y un módulo de votación aislado sin la superficie de red extra de C. C multiplica endpoints y comunicación entre servicios, lo que amplía la superficie de ataque; A comparte todo en un solo esquema acoplado.
- **Auditabilidad:** B tiene un módulo dedicado de auditoría/actas con fronteras claras.

## Afirmación incorrecta de la IA detectada
<Completar con el caso real de la bitácora, ej.: la IA recomendó microservicios "por escalabilidad" y propuso Kubernetes; se rechazó porque excede R-01 (1 mes), R-02 y R-03, y la carga (~300 votantes concurrentes) no lo justifica.>

## Conclusión
Elegimos **B. Monolito modular** (4,55) porque cumple el plazo de 1 mes con un equipo de 3 developers y un solo VPS, y permite aislar el módulo de votación para proteger la integridad y el secreto del voto. La decisión final la tomó el equipo. Ver [ADR-001](adr/001-estilo-arquitectonico.md).