from architectures.core import Graph, Cluster, Group, Node, Edge
from architectures.themes import Default, Clean

from architectures.providers.azure.data import DataFactory, DataLake, AzureDatabricks, AnalysisService, AzureSynapseAnalytics
from architectures.providers.azure.ai import PowerBi

theme = Clean(graph_attr_overrides={"ranksep": "2"}, cluster_attr_overrides={"bgcolor": "whitesmoke"}, node_attr_overrides={"color": "whitesmoke"})

with Graph("my architecture", theme=theme, show=True):
    with Group() as inputs:
        unstructured_data = Node("Logs Files and Media (Unstructured)")
        structured_data = Node("Business and Custom Apps (Structured)")

    with Cluster("Ingest") as ingest:
        data_factory = DataFactory("Azure Data Factory")

    with Cluster("Store") as store:
        data_lake = DataLake("Data Lake")

    with Cluster("Prep and train") as train:
        databricks = AzureDatabricks("Azure Databricks")

    with Group():
        with Cluster("Model") as model:
            analysis_services = AnalysisService("Azure Analysis Services")
            synapse_analytics = AzureSynapseAnalytics("Azure Synapse Analytics")

        with Cluster("Serve") as serve:
            power_bi = PowerBi("Power BI")

    Edge([unstructured_data, structured_data], ingest)
    Edge(ingest, store)
    Edge(store, train)
    Edge(store, model)
    Edge(analysis_services, serve)
    Edge(train, serve)
    Edge(synapse_analytics, train, dir="both")
    Edge(synapse_analytics, analysis_services, style="invis")