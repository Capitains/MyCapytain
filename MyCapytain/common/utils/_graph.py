from collections import defaultdict

from rdflib import Graph, BNode
from rdflib.namespace import NamespaceManager


class Subgraph(object):
    """ Utility class to generate subgraph around one or more items

    :param
    """
    def __init__(self, bindings: dict = None):
        self.graph = Graph()
        self.graph.namespace_manager = NamespaceManager(self.graph)
        for prefix, namespace in bindings.items():
            self.graph.namespace_manager.bind(prefix, namespace)

        self.downwards = defaultdict(lambda: True)
        self.updwards = defaultdict(lambda: True)

    def graphiter(self, graph, target, ascendants=0, descendants=1):
        """ Iter on a graph to finds object connected

        :param graph: Graph to serialize
        :type graph: Graph
        :param target: Node to iterate over
        :type target: Node
        :param ascendants: Number of level to iter over upwards (-1 = No Limit)
        :param descendants: Number of level to iter over downwards (-1 = No limit)
        :return:
        """

        asc = 0 + ascendants
        if asc != 0:
            asc -= 1

        desc = 0 + descendants
        if desc != 0:
            desc -= 1

        t = str(target)

        if descendants != 0 and self.downwards[t] is True:
            self.downwards[t] = False
            for pred, obj in graph.predicate_objects(target):
                if desc == 0 and isinstance(obj, BNode):
                    continue
                self.add((target, pred, obj))

                # Retrieve triples about the object
                if desc != 0 and self.downwards[str(obj)] is True:
                    self.graphiter(graph, target=obj, ascendants=0, descendants=desc)

        if ascendants != 0 and self.updwards[t] is True:
            self.updwards[t] = False
            for s, p in graph.subject_predicates(object=target):
                if desc == 0 and isinstance(s, BNode):
                    continue
                self.add((s, p, target))

                # Retrieve triples about the parent as object
                if asc != 0 and self.updwards[str(s)] is True:
                    self.graphiter(graph, target=s, ascendants=asc, descendants=0)

    def serialize(self, *args, **kwargs):
        return self.graph.serialize(*args, **kwargs)

    def add(self, *args, **kwargs):
        self.graph.add(*args, **kwargs)


def expand_namespace(nsmap, string):
    """ If the string starts with a known prefix in nsmap, replace it by full URI

    :param nsmap: Dictionary of prefix -> uri of namespace
    :param string: String in which to replace the namespace
    :return: Expanded string with no namespace
    """
    for ns in nsmap:
        if isinstance(string, str) and isinstance(ns, str) and string.startswith(ns+":"):
            return string.replace(ns+":", nsmap[ns])
    return string