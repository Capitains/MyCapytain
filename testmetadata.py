"""
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.constants import NAMESPACES, Mimetypes, GRAPH

a = Metadata()
a.add(NAMESPACES.CTS.groupname, "Martial", "eng")
a.add(NAMESPACES.CTS.groupname, "Martialis", "lat")
a.get(NAMESPACES.CTS.groupname)

b = Metadata()
b.add(NAMESPACES.CTS.groupname, "Vergil", "eng")
b.add(NAMESPACES.CTS.groupname, "Vergilius", "lat")

print(
    a[NAMESPACES.CTS.groupname, "eng"],
    a[NAMESPACES.CTS.groupname, "lat"],
    a.get(NAMESPACES.CTS.groupname, "eng"),
    a.get(NAMESPACES.CTS.groupname, "lat"),
    a.get(NAMESPACES.CTS.groupname)
)

from MyCapytain.resources.prototypes.metadata import Collection
import json
from pprint import pprint

a = Collection("urn:cts")
#pprint(json.loads(a.graph.serialize(format="json-ld").decode()))
print(a.id)

b = Collection("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
#pprint(json.loads(a.graph.serialize(format="json-ld", auto_compact=True).decode()))
print(b.id)
print(b.metadata["http://w3id.org/dts-ontology/model"])
#print(a.graph.serialize(format="json-ld", auto_compact=True).decode())
b.set_label("Martial's Epigrammata", "eng")
print(b.export(Mimetypes.JSON.LD).decode())
"""
# WHAO, SUCH SEXYNESS
"""
from rdflib import Graph, URIRef, RDFS, Literal
from MyCapytain.common.constants import NAMESPACES

a = URIRef("urn:cts:latinLit:phi1294.phi002")
b = URIRef("urn:cts:latinLit:phi1294.phi002")
g = Graph()
g.bind("", NAMESPACES.CTS)
g.add((a, RDFS.label, Literal("Epigrammata", lang="lat")))
g.add((b, RDFS.label, Literal("Epigrammata", lang="eng")))
g.add((b, NAMESPACES.CTS.groupname, Literal("Epigrammata", lang="eng")))
print(g.serialize(format="xml", decl=False).decode())
"""

from MyCapytain.common.constants import NAMESPACES, Mimetypes
from MyCapytain.common.reference import Citation
from MyCapytain.resources.prototypes.cts.inventory import PrototypeTextInventory, PrototypeTextGroup, \
    PrototypeWork, PrototypeEdition

a = PrototypeTextInventory(name="superFreak")

b = PrototypeTextGroup(urn="urn:cts:latinLit:phi1294")
b.set_cts_property("groupname", "Martial", "eng")
b.set_cts_property("groupname", "Martialis", "lat")
a.textgroups[b.id] = b

c = PrototypeWork(urn="urn:cts:latinLit:phi1294.phi002")
c.set_cts_property("title", "Epigrams", "eng")
c.set_cts_property("title", "Epigrammata", "lat")
b.works[c.id] = c

d = PrototypeEdition(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
d.set_cts_property("label", "Epigrams [Ed 1978]", "eng")
d.set_cts_property("description", "Some wonderful edition", "eng")
c.texts[d.id] = d
d.citation = Citation(name="book", scope="/tei:TEI/tei:text/tei:body/tei:div", xpath="/tei:div[@n='?']")
d.citation.child = Citation(name="poem", scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']", xpath="/tei:div[@n='?']")

e = PrototypeWork(urn="urn:cts:latinLit:phi1294.phi002")
e.set_cts_property("title", "Epigrammes", "fre")

print(a.export(Mimetypes.XML.CTS))
