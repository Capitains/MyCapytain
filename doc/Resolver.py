from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever
from MyCapytain.common.constants import Mimetypes, XPATH_NAMESPACES

# We set up a resolver which communicates with an API available in Leipzig
resolver = HttpCtsResolver(HttpCtsRetriever("http://cts.dh.uni-leipzig.de/api/cts/"))
# We require a passage : passage is now a Passage object
# This is an entry from the Smith Myth Dictionary
# The inner methods will resolve to the URI http://cts.dh.uni-leipzig.de/api/cts/?request=GetPassage&urn=urn:cts:pdlrefwk:viaf88890045.003.perseus-eng1:A.abaeus_1
# And parse it into interactive objects
passage = resolver.getTextualNode("urn:cts:pdlrefwk:viaf88890045.003.perseus-eng1", "A.abaeus_1")
# We need an export as plaintext
print(passage.export(
    output=Mimetypes.PLAINTEXT
))
"""
    Abaeus ( Ἀβαῖος ), a surname of Apollo
     derived from the town of Abae in Phocis, where the god had a rich temple. (Hesych. s. v.
     Ἄβαι ; Hdt. 8.33 ; Paus. 10.35.1 , &c.) [ L.S ]
"""
# We want to find bibliographic information in the passage of this dictionary
# We need an export as LXML ETREE object to perform XPath
print(
    passage.export(
        output=Mimetypes.PYTHON.ETREE
    ).xpath(".//tei:bibl/text()", namespaces=XPATH_NAMESPACES, magic_string=False)
)
["Hdt. 8.33", "Paus. 10.35.1"]