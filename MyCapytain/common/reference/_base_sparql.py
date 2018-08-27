from rdflib import BNode

from MyCapytain.common.constants import get_graph, RDF_NAMESPACES
from MyCapytain.common.reference._base import CitationSet, BaseCitation


class BaseSparqlCitationSet(CitationSet):
    def __init__(self, children=None, _bnode_id=None):
        self.__graph__ = get_graph()
        self.__node__ = BNode(_bnode_id)
        super(BaseSparqlCitationSet, self).__init__(children=children)

    @property
    def graph(self):
        return self.__graph__

    def asNode(self):
        return self.__node__

    @property
    def children(self):
        """ Children of a citation

        :rtype: [BaseCitation]
        """
        return super(BaseSparqlCitationSet, self).children

    @children.setter
    def children(self, val):
        super(BaseSparqlCitationSet, self).children = val
        for child in self._children:
            self.graph.add(
                (self.asNode(), RDF_NAMESPACES.CAPITAINS.citation, child.asNode())
            )


class BaseSparqlCitation(BaseSparqlCitationSet, BaseCitation):
    """ Helper class that deals with Citation in the graph
    """
    CITELABEL_TERM = RDF_NAMESPACES.CAPITAINS.citeLabel

    def __init__(self, name=None, children=None, root=None, _bnode_id=None):
        self.__graph__ = get_graph()
        self.__node__ = BNode(_bnode_id)
        super(BaseSparqlCitation, self).__init__(name=name, children=children, root=root)

    @property
    def graph(self):
        return self.__graph__

    def asNode(self):
        return self.__node__

    @property
    def name(self):
        """ Type of the citation represented

        :rtype: str
        :example: Book, Chapter, Textpart, Section, Poem...
        """
        return super(BaseSparqlCitation, self).name

    @name.setter
    def name(self, val):
        super(BaseSparqlCitation, self).name = val
        self.graph.add(
            (self.asNode(), self.CITELABEL_TERM, val)
        )
