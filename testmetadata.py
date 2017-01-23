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

"""
a = PrototypeTextInventory(name="superFreak")

b = PrototypeTextGroup(urn="urn:cts:latinLit:phi1294", parent=a)
b.set_cts_property("groupname", "Martial", "eng")
b.set_cts_property("groupname", "Martialis", "lat")

c = PrototypeWork(urn="urn:cts:latinLit:phi1294.phi002", parent=b)
c.set_cts_property("title", "Epigrams", "eng")
c.set_cts_property("title", "Epigrammata", "lat")

d = PrototypeEdition(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2", parent=c)
d.set_cts_property("label", "Epigrams [Ed 1978]", "eng")
d.set_cts_property("description", "Some wonderful edition", "eng")
d.citation = Citation(name="book", scope="/tei:TEI/tei:text/tei:body/tei:div", xpath="/tei:div[@n='?']")
d.citation.child = Citation(name="poem", scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']", xpath="/tei:div[@n='?']")

e = PrototypeWork(urn="urn:cts:latinLit:phi1294.phi002")
e.set_cts_property("title", "Epigrammes", "fre")
e.set_cts_property("title", "Epigrammes", "fre")
c.update(e)
"""

from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.common.constants import Mimetypes
from MyCapytain.resources.collections.cts import TextInventory
c = CTS("http://cts.perseids.org/api/cts/")

a = TextInventory.parse(resource=c.getCapabilities(urn="urn:cts:latinLit:phi0959"))

print(a["urn:cts:latinLit:phi0959.phi005"].get_label())
print(a["urn:cts:latinLit:phi0959.phi005"].get_label("eng"))
#with open("tests/testing_data/cts/getCapabilities.xml") as f:
#    a = TextInventory.parse(resource=f)
#from pprint import pprint
#pprint(a.export(Mimetypes.JSON.DTS.Std))
#from json import dump
#with open("./inv", "w") as f:
#    dump(a["urn:cts:latinLit:phi0959.phi005"].export(Mimetypes.JSON.DTS.Std), f)
#print(a["urn:cts:latinLit:phi0959.phi005"].export(Mimetypes.JSON.LD).decode())
#print(a.export(Mimetypes.XML.RDF).decode())
#print(a.export(Mimetypes.XML.CTS))