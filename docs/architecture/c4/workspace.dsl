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
            api = container "API VotoEPIS" "Monolito modular que implementa los casos de uso mediante una API REST." "Python / Django" {

                // ===== [E3] Componentes (= paquetes de docs/design/paquetes.puml) =====
                autenticacion = component "Módulo Autenticación" "Inicia sesión con el correo institucional y verifica que el estudiante esté en el padrón." "Django app"
                padron = component "Módulo Padrón" "Administra el padrón electoral y el registro de participación." "Django app"
                votacion = component "Módulo Votación" "Registra la papeleta anónima y controla el voto único por estudiante." "Django app"
                escrutinio = component "Módulo Escrutinio" "Cuenta los votos y genera los resultados y el acta." "Django app"
                auditoria = component "Módulo Auditoría" "Registra eventos y permite la verificación independiente del conteo." "Django app"
                compartido = component "Puertos compartidos" "Define interfaces comunes, como el puerto RegistroAuditoria." "Python"
            }

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

        // --- [E3] Relaciones de nivel 3 (idénticas a las dependencias de paquetes.puml) ---
        votoepis.web -> votoepis.api.autenticacion "Inicia sesión" "HTTPS/JSON"
        votoepis.web -> votoepis.api.padron "Carga y consulta el padrón" "HTTPS/JSON"
        votoepis.web -> votoepis.api.votacion "Emite el voto" "HTTPS/JSON"
        votoepis.web -> votoepis.api.escrutinio "Solicita el escrutinio y los resultados" "HTTPS/JSON"
        votoepis.web -> votoepis.api.auditoria "Descarga el acta y las papeletas anónimas" "HTTPS/JSON"

        votoepis.api.autenticacion -> votoepis.api.padron "Verifica que el correo esté habilitado"
        votoepis.api.votacion -> votoepis.api.padron "Verifica y registra la participación"
        votoepis.api.votacion -> votoepis.api.compartido "Registra eventos (puerto RegistroAuditoria)"
        votoepis.api.escrutinio -> votoepis.api.votacion "Lee las papeletas"
        votoepis.api.escrutinio -> votoepis.api.compartido "Registra eventos (puerto RegistroAuditoria)"
        votoepis.api.auditoria -> votoepis.api.escrutinio "Lee resultados y hash del acta"
        votoepis.api.auditoria -> votoepis.api.compartido "Implementa el puerto RegistroAuditoria"

        votoepis.api.autenticacion -> idp "Autentica al estudiante" "OpenID Connect / HTTPS"
        votoepis.api.votacion -> correo "Envía el comprobante (opcional)" "SMTP"

        votoepis.api.padron -> votoepis.db "Lee y escribe (esquema padron)" "SQL"
        votoepis.api.votacion -> votoepis.db "Guarda papeletas anónimas (esquema urna)" "SQL"
        votoepis.api.escrutinio -> votoepis.db "Guarda resultados y acta" "SQL"
        votoepis.api.auditoria -> votoepis.db "Lee y escribe (esquema auditoria)" "SQL"
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

        // ===== [E3] Nivel 3 =====
        component votoepis.api "Componentes" "Nivel 3: módulos de la API." {
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
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }
}
