from MyCapytain.resources.texts.local import Text
import pickle
import lxml.objectify
from lxml.etree import XMLParser
X = XMLParser()
Z = lxml.objectify.makeparser()

canonical = '../../canonicals/canonical-latinLit'

f = open(canonical + '/data/phi1017/phi004/phi1017.phi004.perseus-lat2.xml')
r = lxml.objectify.parse(f, Z )
t = Text(resource=r)
with open("pickled.pkl", "wb") as p:
    pickle.dump(t, p)

f = open(canonical + '/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')
r = lxml.objectify.parse(f, Z )
t = Text(resource=r)
with open("pickled2.pkl", "wb") as p:
    pickle.dump(t, p)

f = open(canonical + '/data/stoa0045/stoa001/stoa0045.stoa001.perseus-lat2.xml')
r = lxml.objectify.parse(f, Z )
t = Text(resource=r)
with open("pickled3.pkl", "wb") as p:
    pickle.dump(t, p)

f = open(canonical + '/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')
r = lxml.objectify.parse(f, Z )
with open("pickled4.pkl", "wb") as p:
    pickle.dump(r, p)