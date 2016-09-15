from MyCapytain.resources.texts.local import Text
import pickle
import lxml.objectify
from lxml.etree import XMLParser
X = XMLParser()

f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1017/phi004/phi1017.phi004.perseus-lat2.xml')
r = lxml.objectify.parse(f, X)
t = Text(resource=r)
with open("pickled.pkl", "wb") as p:
    pickle.dump(t, p)

f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')
r = lxml.objectify.parse(f, X)
t = Text(resource=r)
with open("pickled2.pkl", "wb") as p:
    pickle.dump(t, p)

f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/stoa0045/stoa001/stoa0045.stoa001.perseus-lat2.xml')
r = lxml.objectify.parse(f, X)
t = Text(resource=r)
with open("pickled3.pkl", "wb") as p:
    pickle.dump(t, p)