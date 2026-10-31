workspace "VotoEPIS" "Modelo C4 de VotoEPIS escalado tras ADD (Lab 08)" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Votante habilitado de la universidad [QA-01, QA-03, QA-06]."
        comite = person "Comité electoral" "Administra padrón, contingencias y firma el acta [QA-04, QA-08]."
        auditor = person "Auditor externo" "Verifica conteo y anclajes criptográficos independientes [QA-02]."

        votoepis = softwareSystem "VotoEPIS" "Sistema de votación electrónica segura y auditable [QA-01..QA-08]." {
            web = container "Aplicación web de votación" "PWA responsive con sesión local de 15 min [QA-03, QA-04]." "HTML5 / React / PWA" "Web Browser"
            api = container "API VotoEPIS" "Monolito modular en Django con Bulkhead y Circuit Breaker [QA-01, QA-03, QA-04]." "Python / Django" {
                autenticacion = component "Módulo Autenticación" "Autenticación OIDC con Circuit Breaker y fallback OTP [QA-04]." "Django app"
                padron = component "Módulo Padrón" "Valida habilitación y unicidad de participación [QA-01, QA-03]." "Django app"
                votacion = component "Módulo Votación" "Urna anónima y lógica de emisión desacoplada [QA-01, QA-06]." "Django app"
                escrutinio = component "Módulo Escrutinio" "Cómputo automatizado y exportación mezclada [QA-02, QA-06]." "Django app"
                auditoria = component "Módulo Auditoría" "Cadena de hashes SHA-256 y anclaje cada 15 min [QA-02]." "Django app"
                compartido = component "Puertos compartidos" "Interfaces públicas y RegistroAuditoria [ADR-004]." "Python"
            }
            cache = container "Caché de consultas" "Almacena opciones de elección y sesiones activas [QA-03]." "Redis / Memoria"
            outbox = container "Worker / Outbox" "Despacho asíncrono de comprobantes por correo [QA-03]." "Celery / Python"
            db = container "Base de datos" "PostgreSQL con esquemas aislados y candado de escritura [QA-01, QA-02]." "PostgreSQL 16" "Database"
        }

        idp = softwareSystem "Proveedor de identidad institucional" "Autentica credenciales universitarias vía OIDC [QA-04]." "Externo"
        correo = softwareSystem "Servicio de correo" "Envío de comprobantes de voto en segundo plano [QA-03]." "Externo"
        portal_anclaje = softwareSystem "Portal externo de anclaje" "Publicación periódica de hashes para auditoría pública [QA-02]." "Externo"

        // Relaciones Nivel 1
        estudiante -> votoepis "Emite voto secreto [QA-01, QA-03]"
        comite -> votoepis "Gestiona elecciones y contingencias [QA-04, QA-08]"
        auditor -> votoepis "Audita cadena y recuento independiente [QA-02]"
        votoepis -> idp "Valida credenciales [QA-04]" "HTTPS/OIDC"
        votoepis -> correo "Envía comprobantes [QA-03]" "SMTP"
        votoepis -> portal_anclaje "Publica anclas cada 15 min [QA-02]" "HTTPS/REST"

        // Relaciones Nivel 2
        estudiante -> votoepis.web "Usa navegador o celular [QA-03]" "HTTPS"
        comite -> votoepis.web "Monitorea y atiende contingencias [QA-04]" "HTTPS"
        auditor -> votoepis.web "Descarga exportación anónima [QA-02]" "HTTPS"
        votoepis.web -> votoepis.api "Llamadas REST con token de sesión [QA-03]" "HTTPS/JSON"
        votoepis.api -> votoepis.cache "Lee catálogo y valida sesión [QA-03]" "TCP/Memory"
        votoepis.api -> votoepis.db "Transacción atómica de voto [QA-01]" "SQL/TCP"
        votoepis.api -> votoepis.outbox "Encola comprobantes en outbox [QA-03]" "SQL/TCP"
        votoepis.outbox -> correo "Despacha correos sin bloquear al votante [QA-03]" "SMTP"
        votoepis.api -> idp "Autenticación protegida con Circuit Breaker [QA-04]" "HTTPS/OIDC"
        votoepis.api -> portal_anclaje "Envía hash acumulado cada 15 min [QA-02]" "HTTPS/JSON"

        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Dispositivo del votante" "" "Android / iOS / Navegador web" {
                containerInstance votoepis.web
            }
            deploymentNode "VPS único en la nube" "Ubuntu 24.04 LTS, 4 vCPU, 8 GB RAM (R-03)" "Servidor VPS" {
                deploymentNode "Docker Compose" "" "Docker Engine" {
                    containerInstance votoepis.api
                    containerInstance votoepis.cache
                    containerInstance votoepis.outbox
                    containerInstance votoepis.db
                }
            }
        }
    }

    views {
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS 2.0 y su entorno." {
            include *
            autolayout lr
        }

        container votoepis "Contenedores" "Nivel 2: Contenedores tras refactor ADD (Lab 08)." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Database" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
