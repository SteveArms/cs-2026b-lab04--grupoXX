workspace "VotoEPIS" "Modelo C4 de la plataforma de elección digital de delegados estudiantiles de la EPIS-UNSA" {

    !identifiers hierarchical

    model {

        // ===== [E1] Personas, sistema y sistemas externos =====
        estudiante = person "Estudiante votante" "Estudiante habilitado de la EPIS que emite un voto secreto."
        comite = person "Comité electoral" "Administra el padrón y las elecciones, realiza el escrutinio y firma el acta."
        auditor = person "Auditor" "Verifica de forma independiente el conteo de la elección."
        votoepis = softwareSystem "VotoEPIS" "Permite votar de forma secreta y verificable en las elecciones de delegados."

        idp = softwareSystem "Proveedor de identidad institucional" "Autentica a los estudiantes con su correo institucional." "Externo"
        correo = softwareSystem "Servicio de correo" "Entrega los comprobantes de participación." "Externo"

        // --- [E1] Relaciones de nivel 1 (verbo de intención) ---
        estudiante -> votoepis "Emite su voto secreto"
        comite -> votoepis "Administra elecciones, realiza el escrutinio y firma el acta"
        auditor -> votoepis "Verifica el conteo de forma independiente"
        votoepis -> idp "Autentica a los estudiantes" "HTTPS"
        votoepis -> correo "Envía comprobantes de participación" "SMTP"
    }

    views {

        // ===== [E1] Nivel 1 =====
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS y su entorno." {
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
        }
    }
}
