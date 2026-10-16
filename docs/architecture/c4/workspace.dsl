workspace "VotoEPIS" "Modelo C4 de la plataforma de elección digital de delegados estudiantiles de la EPIS-UNSA" {

    !identifiers hierarchical

    model {

        // ===== [E1] Personas, sistema y sistemas externos =====
        estudiante = person "Estudiante votante" "Estudiante habilitado de la EPIS que emite un voto secreto."
        comite = person "Comité electoral" "Administra el padrón y las elecciones, realiza el escrutinio y firma el acta."
        auditor = person "Auditor" "Verifica de forma independiente el conteo de la elección."
        votoepis = softwareSystem "VotoEPIS" "Permite votar de forma secreta y verificable en las elecciones de delegados." {
            // ===== [E2] Contenedores =====
            web = container "Aplicación web de votación" "Interfaz para votantes, comité y auditor desde celular o PC." "HTML / CSS / JavaScript (web responsive)" "Web Browser"
            api = container "API VotoEPIS" "Monolito modular que implementa los casos de uso mediante una API REST." "Python / Django"

            db = container "Base de datos" "Padrón, participación, papeletas anónimas, resultados y auditoría (un esquema por módulo)." "PostgreSQL" "Database"
        }

        idp = softwareSystem "Proveedor de identidad institucional" "Autentica a los estudiantes con su correo institucional." "Externo"
        correo = softwareSystem "Servicio de correo" "Entrega los comprobantes de participación." "Externo"

        // --- [E1] Relaciones de nivel 1 (verbo de intención) ---
        estudiante -> votoepis "Emite su voto secreto"
        comite -> votoepis "Administra elecciones, realiza el escrutinio y firma el acta"
        auditor -> votoepis "Verifica el conteo de forma independiente"
        votoepis -> idp "Autentica a los estudiantes" "HTTPS"
        votoepis -> correo "Envía comprobantes de participación" "SMTP"

        // --- [E2] Relaciones de nivel 2 (verbo + protocolo) ---
        estudiante -> votoepis.web "Emite su voto" "HTTPS"
        comite -> votoepis.web "Administra elecciones y firma el acta" "HTTPS"
        auditor -> votoepis.web "Descarga papeletas anónimas y acta" "HTTPS"
        votoepis.web -> votoepis.api "Envía solicitudes" "HTTPS/JSON (REST)"
        votoepis.api -> votoepis.db "Lee y escribe" "SQL/TCP"
        votoepis.api -> idp "Autentica a los estudiantes" "OpenID Connect / HTTPS"
        votoepis.api -> correo "Envía comprobantes" "SMTP"
    }

    views {

        // ===== [E1] Nivel 1 =====
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS y su entorno." {
            include *
            autolayout lr
        }

        // ===== [E2] Nivel 2 =====
        container votoepis "Contenedores" "Nivel 2: contenedores de VotoEPIS." {
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
