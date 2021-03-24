"""Notional system architecture."""
from diagrams import Diagram
from diagrams.gcp.compute import GKE

with Diagram("TRM Exercise", show=False):
    GKE("GKE")
