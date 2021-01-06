import contextvars
import os
import uuid
from pathlib import Path

from graphviz import Digraph

from architectures.themes import Default

__graph = contextvars.ContextVar("graph")
__cluster = contextvars.ContextVar("cluster")
__node = contextvars.ContextVar("node")

def get_graph():
    try:
        return __graph.get()
    except LookupError:
        return None


def set_graph(graph):
    __graph.set(graph)


def get_cluster():
    try:
        return __cluster.get()
    except LookupError:
        return None


def set_node(node):
    __node.set(node)

def get_node():
    try:
        return __node.get()
    except LookupError:
        return None


def set_cluster(cluster):
    __cluster.set(cluster)


def wrap_text(text, max_length=16):
    """
    Wraps a labels text for a node if it exceeds a certain length
    """
    # Set a minimum word wrap length
    if max_length < 12:
        max_length = 12

    # Implement word wrap
    if len(text) > max_length:
        words = text.split()
        new_text = ""
        if len(words) > 1:
            temp_text = ""
            for word in words:
                test_text = temp_text + " " + word
                if len(test_text) < max_length:
                    new_text = new_text + " " + word
                    temp_text = test_text
                else:
                    new_text = new_text + "\n" + word
                    temp_text = word
        return new_text
    else:
        return text

def get_cluster_node(cluster):
    """
    Takes a cluster object and finds the most central node in the cluster for doing cluster to cluster connections.
    """
    node_dict = get_node()
    center_node_index = round(len(node_dict[cluster])/2) - 1
    node = node_dict[cluster][center_node_index]
    return node


class Graph():
    """
    Create and set default settings for a graph and its clusters, nodes, and edges.
    """
    def __init__(self, name, output_file_name="", output_file_format="png", theme=None, show=True):
        """
        :param str name: The name of the graph.
        :param str output_file_name: The name of the file that will be output.
        :param str output_file_format: The format of the output file.
        :param theme: The base theme to apply to the graph and its clusters, nodes, and edges.
        :param bool show: Flag used to determine whether or not the graph will render.
        """

        # Set graph and output file name
        self.name = name
        if not output_file_name:
            output_file_name = "-".join(self.name.split()).lower()
        self.output_file_name = output_file_name
        self.output_file_format = output_file_format

        # Create the graph
        # Support for multiple engines can be added later by adding in the engine argument passed from the class
        self.dot = Digraph(name=self.name, filename=self.output_file_name)

        # Set the theme
        if theme is None:
            self.theme = Default()
        else:
            self.theme = theme

        # Set global graph attributes
        self.dot.graph_attr.update(self.theme.graph_attrs)
        self.dot.graph_attr["label"] = self.name

        # Set global node attributes
        self.dot.node_attr.update(self.theme.node_attrs)

        # Set global edge attributes
        self.dot.edge_attr.update(self.theme.edge_attrs)

        # Set option to show architecture diagram
        self.show = show

    def __str__(self):
        return str(self.dot)

    def __enter__(self):
        set_graph(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.render()
        # Remove the graphviz file leaving only the image.
        os.remove(self.output_file_name)
        set_graph(None)

    def node(self, node_id, label, **attrs):
        """
        Create a node.
        """
        self.dot.node(node_id, label=label, **attrs)

    def edge(self, tail_node, head_node, **attrs):
        """
        Connect nodes with edges.
        """
        self.dot.edge(tail_node.node_id, head_node.node_id, **attrs)

    def subgraph(self, dot):
        """
        Create a subgraph.
        """
        self.dot.subgraph(dot)

    def render(self):
        """
        Generate an output file.
        """
        self.dot.render(format=self.output_file_format, view=self.show, quiet=True)

class Cluster():
    """
    Create a cluster.
    """
    __background_colors = ("#FFFFFF", "#FFFFFF")

    def __init__(self, label="cluster", background_colors=False, **attrs):
        """
        :param label: Label for the cluster.
        :param background_colors: Flag for adding background colors to clusters.
        """

        # Set the cluster label
        self.label = label

        # Set the cluster name
        self.name = "cluster_" + self.label

        # Create cluster
        self.dot = Digraph(self.name)

        # Set global graph and cluster context
        self._graph = get_graph()
        if self._graph is None:
            raise EnvironmentError("No global graph object found.  A cluster must be part of a graphs context.")
        self._cluster = get_cluster()

        # Set cluster attributes based on the theme using copy to ensure the objects are independent
        self.dot.graph_attr.update(self._graph.theme.cluster_attrs)

        # Override any values directly passed from the object
        self.dot.graph_attr.update(attrs)

        # Update cluster label
        self.dot.graph_attr["label"] = self.label

        # Set cluster depth to allow for logic based on the nesting of clusters
        self.depth = self._cluster.depth + 1 if self._cluster else 0
        color_index = self.depth % len(self.__background_colors)

        # Set the background colors
        # Update this functionality to be something that is passed from a theme
        if background_colors:
            self.dot.graph_attr["bgcolor"] = self.__background_colors[color_index]


    def __enter__(self):
        set_cluster(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._cluster:
            self._cluster.subgraph(self.dot)
        else:
            self._graph.subgraph(self.dot)
        set_cluster(self._cluster)

    def node(self, node_id: str, label: str, **attrs) -> None:
        """
        Create a node.
        """
        self.dot.node(node_id, label=label, **attrs)

    def subgraph(self, dot=Digraph):
        """
        Create a subgraph
        """
        self.dot.subgraph(dot)

    @staticmethod
    def _rand_id():
        """
        Generate a random hex number.
        """
        return uuid.uuid4().hex


class Group(Cluster):
    """
    Creates a special type of group used only or organizing nodes.
    """
    __background_colors = ("#FFFFFF", "#FFFFFF")
    
    def __init__(self, label="group", background_colors=False, **attrs):
        """
        :param label
        :param background_colors
        """

        # Set the cluster label
        self.label = self._rand_id()

        # Set the cluster name
        self.name = "cluster_" + self.label

        # Create cluster
        self.dot = Digraph(self.name)

        # Set global graph and cluster context
        self._graph = get_graph()
        if self._graph is None:
            raise EnvironmentError("No global graph object found.  A cluster must be part of a graphs context.")
        self._cluster = get_cluster()

        # Update cluster label
        self.dot.graph_attr["style"] = "invis"

        # Set cluster depth to allow for logic based on the nesting of clusters
        self.depth = self._cluster.depth + 1 if self._cluster else 0
        color_index = self.depth % len(self.__background_colors)

        # Set the background colors
        # Update this functionality to be something that is passed from a theme
        if background_colors:
            self.dot.graph_attr["bgcolor"] = self.__background_colors[color_index]
    

class Node():
    """
    Create a node.  This can be a standard node or a node representing a service from a provider.
    """

    _provider = None
    _service_type = None

    _icon_dir = None
    _icon = None
    
    _default_label = None # To be used later for all providers using automated script

    def __init__(self, label="", **attrs):
        """
        :param str label: Label for a node.
        """
        # Generate an ID used to uniquely identify a node
        self._id = self._rand_id()

        # Set the label
        self.label = label

        # Get global graph and cluster context to ensure the node is part of the graph and/or cluster
        self._graph = get_graph()
        if self._graph is None:
            raise EnvironmentError("No global graph object found.  A cluster must be part of a graphs context.")
        self._cluster = get_cluster()

        # Auto-wrap labels
        if self._cluster is not None:
            self.label = wrap_text(self.label, len(self._cluster.label))
        else:
            self.label = wrap_text(self.label)

        # Set node attributes based on the theme using copy to ensure the objects are independent
        self.node_attrs = self._graph.theme.node_attrs.copy()

        # Override any values directly passed from the object
        self.node_attrs.update(attrs)

        # Add attributes specific for when provider service nodes are used.
        if self._icon:
            padding = 0.4 * (self.label.count('\n'))
            self.node_attrs["height"] = str(float(self.node_attrs['height']) + padding)
            self.node_attrs["image"] = self._load_icon()

        # If a node is in the cluster context, add it to cluster.
        if self._cluster:
            self._cluster.node(self._id, self.label, **self.node_attrs)
        else:
            self._graph.node(self._id, self.label, **self.node_attrs)

        node_dict = get_node()
        if node_dict is None:
            # Creates the initial node dictionary if one does not exist
            node_dict = {self._cluster: [self]}
            set_node(node_dict)
        elif self._cluster not in node_dict:
            # Adds a new cluster key and value to the node dictionary
            node_dict.update({self._cluster: [self]})
        else:
            # Updates an existing cluster value in the node dictionary
            node_list = node_dict[self._cluster]
            node_list.append(self)
            node_dict.update({self._cluster: node_list})
            set_node(node_dict)

    @property
    def node_id(self):
        return self._id

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex

    def _load_icon(self):
        basedir = Path(os.path.abspath(os.path.dirname(__file__)))
        return os.path.join(basedir.parent.parent, self._icon_dir, self._icon)

class Edge():
    """
    Creates an edge between two nodes
    """

    def __init__(self, start_node, end_node, **attrs,):
        """
        :param start_node: The origin cluster, group, or node object.
        :param end_node: The destination cluster, group, or node object.
        :param attrs: Other edge attributes.
        """

        # Set the start and end node
        self.start_node = start_node
        self.end_node = end_node

        # Get global graph and cluster context to ensure the node is part of the graph and/or cluster
        self._graph = get_graph()
        if self._graph is None:
            raise EnvironmentError("No global graph object found.  A cluster must be part of a graphs context.")

        # Set edge attributes based on the theme using copy to ensure the objects are independent
        self.edge_attrs = self._graph.theme.edge_attrs.copy()

        # Override any attributes directly passed from the object
        self.edge_attrs.update(attrs)

        # Add single start and end node objects to a list
        if type(self.start_node) is not list:
            self.start_node = [self.start_node] 
        
        if type(self.end_node) is not list:
            self.end_node = [self.end_node]

        start_node_list = self.start_node
        end_node_list = self.end_node

        # For each start node passed
        for current_start_node in start_node_list:

            # And For each end node passed
            for current_end_node in end_node_list:

                # Make all of the connections based on whether or not the object is a node, cluster, or group
                if isinstance(current_start_node, Node) and isinstance(current_end_node, Node):
                    self.start_node = current_start_node
                    self.end_node = current_end_node
                    self.edge_attrs.update({"ltail": "", "lhead": ""})
                elif isinstance(current_start_node, Node) and isinstance(current_end_node, (Cluster, Group)):
                    cluster = current_end_node
                    self.start_node = current_start_node
                    self.end_node = get_cluster_node(current_end_node)
                    self.edge_attrs.update({"lhead": cluster.name})
                elif isinstance(current_start_node, (Cluster, Group)) and isinstance(current_end_node, Node):
                    cluster = current_start_node
                    self.start_node = get_cluster_node(current_start_node)
                    self.end_node = current_end_node
                    self.edge_attrs.update({"ltail": cluster.name})
                elif isinstance(current_start_node, (Cluster, Group)) and isinstance(current_end_node, (Cluster, Group)):
                    start_cluster = current_start_node
                    end_cluster = current_end_node
                    self.start_node = get_cluster_node(current_start_node)
                    self.end_node = get_cluster_node(current_end_node)
                    self.edge_attrs.update({"ltail": start_cluster.name, "lhead": end_cluster.name})
                else:
                    if not isinstance(self.start_node, (Cluster, Group, Node)) or isinstance(self.end_node, (Cluster, Group, Node)):
                        raise TypeError("Values passed for start node and end node must be Cluster, Group, or Node objects.")

                self._graph.edge(self.start_node, self.end_node, **self.edge_attrs)

class Flow():
    """
    Another method of connecting nodes by allowing users to define a flow as a list
    """
    def __init__(self, nodes, **attrs):
        """
        :param nodes: A list of nodes to be used to create the flow.
        """
        
        self.nodes = nodes

        if not isinstance(self.nodes, list):
            raise TypeError("Flow only accepts a single list of Cluster, Group, or Node objects.")

        self.node_count = len(self.nodes)

        # Get global graph and cluster context to ensure the node is part of the graph and/or cluster
        self._graph = get_graph()
        if self._graph is None:
            raise EnvironmentError("No global graph object found.  A cluster must be part of a graphs context.")

        # Set edge attributes based on the theme using copy to ensure the objects are independent
        self.edge_attrs = self._graph.theme.edge_attrs.copy()

        # Override any attributes directly passed from the object
        self.edge_attrs.update(attrs)

        # Ensure there is more than one node passed to the list
        if self.node_count > 1:

            # For each node
            for i in range(self.node_count):

                # If the node is not the last node in the list
                if i < self.node_count - 1:

                    # Set the start and end node values
                    self.start_node = self.nodes[i]
                    self.end_node = self.nodes[i + 1]

                    # Make all of the connections based on whether or not the object is a node, cluster, or group
                    if isinstance(self.start_node, Node) and isinstance(self.end_node, Node):
                        self.edge_attrs.update({"ltail": "", "lhead": ""})
                    elif isinstance(self.start_node, Node) and isinstance(self.end_node, (Cluster, Group)):
                        cluster = self.end_node
                        self.end_node = get_cluster_node(self.end_node)
                        self.edge_attrs.update({"lhead": cluster.name})
                    elif isinstance(self.start_node, (Cluster, Group)) and isinstance(self.end_node, Node):
                        cluster = self.start_node
                        self.start_node = get_cluster_node(self.start_node)
                        self.edge_attrs.update({"ltail": cluster.name})
                    elif isinstance(current_start_node, (Cluster, Group)) and isinstance(current_end_node, (Cluster, Group)):
                        start_cluster = self.start_node
                        end_cluster = self.end_node
                        self.start_node = get_cluster_node(self.start_node)
                        self.end_node = get_cluster_node(self.end_node)
                        self.edge_attrs.update({"ltail": start_cluster.name, "lhead": end_cluster.name})
                    else:
                        if not isinstance(self.start_node, (Cluster, Group, Node)) or not isinstance(self.end_node, (Cluster, Group, Node)):
                            raise TypeError("Values passed for start node and end node must be Cluster, Group, or Node objects.")
                
                    self._graph.edge(self.start_node, self.end_node, **self.edge_attrs)
        else:
            # Let the user know that the list must contain more than one item
            raise Exception('More than one node must be passed in the list to use the Flow object')
