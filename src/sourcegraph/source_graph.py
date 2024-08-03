import networkx as nx
import matplotlib.pyplot as plt
from .utils import repo_to_graph, get_all_dependent_functions


class Sourcegraph:
    def __init__(self, repository_url: str) -> None:
        """
        Initialize the Sourcegraph instance with a repository URL.

        Args:
            repository_url (str): The URL of the repository to analyze.
        """
        self.node_data = None
        self.repository_url = repository_url
        self.graph: nx.Graph = None

    def run(self):
        """
        Fetch the repository data and build the graph.

        This method calls the `repo_to_graph` function to generate a graph representation
        of the repository and stores the node data.
        """
        self.graph = repo_to_graph(self.repository_url)
        self.node_data = self.graph.nodes(data=True)

    @property
    def get_functions_and_classes(self):
        """
        Get a list of nodes (functions and classes) in the graph.

        Returns:
            list: A list of node identifiers.
        """
        return list(self.graph.nodes())

    @property
    def n_nodes(self):
        """
        Get the number of nodes in the graph.

        Returns:
            int: The number of nodes in the graph.
        """
        return self.graph.number_of_nodes()

    def get_node_property(self, node_name):
        """
        Get properties of a specific node.

        Args:
            node_name (str): The name of the node to retrieve properties for.

        Returns:
            dict: The properties of the specified node.
        """
        return self.node_data[node_name]

    def get_dependencies(self, starting_object):
        """
        Get all dependencies for a starting object.

        Args:
            starting_object (str): The node from which to find dependencies.

        Returns:
            list: A list of nodes that are dependent on the starting object.
        """
        return get_all_dependent_functions(self.graph, starting_object)

    def plot(self, layout='random_layout'):
        """
        Plot the graph using a random layout.

        This method generates a plot of the graph with node labels showing their names
        and types. The plot is displayed using matplotlib.
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        nx_layout = getattr(nx, layout)
        pos = nx_layout(self.graph)
        node_labels = {node: f"{data['name']} ({data['type']})" for node, data in self.node_data}
        nx.draw(self.graph, pos, with_labels=True, labels=node_labels, node_size=3000, node_color='skyblue',
                font_size=10, font_weight='bold', edge_color='gray', ax=ax)
        plt.show()
