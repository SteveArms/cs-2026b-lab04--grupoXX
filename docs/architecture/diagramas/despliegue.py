from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.generic.device import Mobile
from diagrams.onprem.network import Nginx, Internet
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Grafana

graph_attr = {"fontsize": "18", "bgcolor": "white", "pad": "0.3"}

with Diagram("VotoEPIS - Vista de despliegue", filename="img/despliegue",
             show=False, direction="LR", graph_attr=graph_attr, outformat="png"):
    
    votantes = Users("Estudiantes,\nComite y Auditor")
    dispositivo = Mobile("Navegador Web\n(Movil o Desktop)")
    idp_externo = Internet("Correo institucional\n(Identity Provider)")
    correo_notif = Internet("Servicio de correo\n(Actas y comprobantes)")

    with Cluster("Servidor en la nube (VPS Ubuntu)"):
        proxy = Nginx("Nginx\n(Reverse Proxy / HTTPS)")
        
        with Cluster("Monolito Modular"):
            app = Django("Django Core\n(5 modulos desacoplados)")
            
        db = PostgreSQL("PostgreSQL\n(schemas: padron, urna, auditoria)")
        monitoreo = Grafana("Grafana / Logs")

    votantes >> dispositivo >> Edge(label="HTTPS") >> proxy >> app
    app >> Edge(label="SQL interno") >> db
    app >> Edge(label="OAuth2 / OIDC", style="dashed") >> idp_externo
    app >> Edge(label="SMTP / REST", style="dashed") >> correo_notif
    app >> Edge(label="Metricas", style="dotted") >> monitoreo
