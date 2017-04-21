from MyCapytain.resolvers.cts.api import HttpCTSResolver
from MyCapytain.retrievers.cts5 import CtsHttpRetriever
from MyCapytain.common.constants import Mimetypes

# We set up a resolver which communicates with an API available in Leipzig
resolver = HttpCTSResolver(CtsHttpRetriever("http://cts.dh.uni-leipzig.de/api/cts/"))
# We require some metadata information
textMetadata = resolver.getMetadata("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
# Texts in CTS Metadata have one interesting property : its citation scheme.
# XmlCtsCitation are embedded objects that carries information about how a text can be quoted, what depth it has
print(type(textMetadata), [citation.name for citation in textMetadata.citation])
# Now, we want to retrieve the first line of poem seventy two of the second book
passage = resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="2.72.1")
# And we want to have its content exported to plain text and have the siblings of this passage (previous and next line)
print(passage.export(Mimetypes.PLAINTEXT), passage.siblingsId)
poemsInBook3 = resolver.getReffs("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="3")
print(poemsInBook3)
