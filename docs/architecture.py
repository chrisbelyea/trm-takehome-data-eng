"""Notional system architecture."""
from diagrams import Cluster, Diagram
from diagrams.gcp.network import FirewallRules, LoadBalancing
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet, StatefulSet
from diagrams.k8s.podconfig import Secret
from diagrams.k8s.network import Ingress, Service
from diagrams.k8s.storage import PersistentVolume, PersistentVolumeClaim, StorageClass
from diagrams.onprem.client import Client


with Diagram("TRM Exercise Detail", show=False):
    with Cluster("GCP"):
        # Resources
        app_lb_ext = LoadBalancing("App LB (HTTP/external)")
        app_lb_int = LoadBalancing("App LB (TCP/internal)")
        app_ingress_ext = Ingress("App Ingress (external)")
        app_fw = FirewallRules("Firewall")

        with Cluster("GKE"):

            with Cluster("App Namespace"):
                # Resources
                app_dep = Deployment("App Deployment")
                app_rs = ReplicaSet("App ReplicaSet")
                app_replica_set_count = 3
                app_pods = [
                    Pod("App Pod") for pod in range(0, app_replica_set_count, 1)
                ]
                app_secret = Secret("App Secret\n(contains DB credentials & host)")
                app_svc_ext = Service("App Service (external)")
                app_svc_int = Service("App Service (internal)")

                # Relationships
                app_dep >> app_rs >> app_pods << app_svc_ext << app_ingress_ext << app_lb_ext << app_fw
                # app_pods << app_svc_int << app_lb_int << app_fw
                app_secret << app_dep

            with Cluster("DB Namespace"):
                # Pgpool
                # Resources
                pgpool_dep = Deployment("Pgpool Deployment")
                pgpool_rs = ReplicaSet("Pgpool ReplicaSet")
                pgpool_replica_set_count = 1
                pgpool_pods = [
                    Pod("Pgpool Pod") for pod in range(0, pgpool_replica_set_count, 1)
                ]
                pgpool_svc = Service("Pgpool Service")

                # Relationships
                pgpool_dep >> pgpool_rs >> pgpool_pods << pgpool_svc

                # PostgreSQL
                # Resources
                db_sset = StatefulSet("PostgreSQL StatefulSet")
                db_stateful_set_count = 3
                db_svc = Service("DB Service")
                sc = StorageClass("Storage Class (SSD)")

                db_pods = []
                for _ in range(db_stateful_set_count):
                    db_pod = Pod("DB Pod")
                    db_pvc = PersistentVolumeClaim("DB PVC")
                    db_pv = PersistentVolume("DB PV")
                    # Relationships
                    sc << db_pv << db_pvc << db_pod >> db_sset
                    db_pods.append(db_pod << db_svc)

        # Relationships
        app_pods << app_svc_int << app_lb_int << app_fw
        # app_pods >> pgpool_svc  # Not rendered since the diagram is busy enough

with Diagram("TRM Exercise Overview", show=False):
    # General overview of system flow

    # Resources
    external_client = Client("external client")
    vpc_client = Client("vpc client")
    app_svc_ext = Service("App Service (external)")
    app_svc_int = Service("App Service (internal)")
    app_lb_ext = LoadBalancing("App LB (HTTP/external)")
    app_lb_int = LoadBalancing("App LB (TCP/internal)")
    app_ingress_ext = Ingress("App Ingress (external)")
    app_fw = FirewallRules("Firewall")
    app_pod = Pod("App Pods")
    pgpool_svc = Service("Pgpool Service")
    pgpool_pod = Pod("Pgpool Pod")
    db_svc = Service("DB Service")
    db_pod = Pod("DB Pods")

    # Relationships
    external_client >> app_fw >> app_ingress_ext >> app_lb_ext >> app_svc_ext >> app_pod
    vpc_client >> app_fw >> app_lb_int >> app_svc_int >> app_pod
    app_pod >> pgpool_svc >> pgpool_pod >> db_svc >> db_pod
