"""Notional system architecture."""
from diagrams import Cluster, Diagram
from diagrams.gcp.network import FirewallRules, LoadBalancing
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet, StatefulSet
from diagrams.k8s.podconfig import Secret
from diagrams.k8s.network import Service
from diagrams.k8s.storage import PersistentVolume, PersistentVolumeClaim, StorageClass
from diagrams.onprem.client import Client


with Diagram("TRM Exercise", show=False):
    with Cluster("GKE"):

        with Cluster("App Namespace"):
            # Resources
            app_dep = Deployment("App Deployment")
            app_rs = ReplicaSet("App ReplicaSet")
            app_replica_set_count = 3
            app_pods = [Pod("App Pod") for pod in range(0, app_replica_set_count, 1)]
            app_secret = Secret("App Secret\n(contains DB credentials & host)")
            app_svc = Service("App Service")
            app_lb = LoadBalancing("App LB")
            app_fw = FirewallRules("Firewall")

            # Relationships
            app_dep >> app_rs >> app_pods << app_svc << app_lb << app_fw
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

    with Cluster("Overview"):
        # General overview of system flow
        Client("client") >> FirewallRules("allowed source network") >> LoadBalancing(
            "App LB"
        ) >> Service("App Service") >> Pod("App Pod") >> Service(
            "Pgpool Service"
        ) >> Pod(
            "Pgpool Pod"
        ) >> Service(
            "DB Service"
        ) >> Pod(
            "DB Pod"
        )
