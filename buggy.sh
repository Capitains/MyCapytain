
python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import Text" \
"from MyCapytain.common.reference import Reference" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = XMLParser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = lxml.objectify.parse(f, X)" \
"t = Text(resource=r)" \
"t.getPassage(Reference('7.8.1-7.9.1'))" \
"print(len(t.getPassage(Reference('7.8.1-7.9.1'))))"

python -m timeit -n $1 "from MyCapytain.resources.texts.local import Text" \
"from MyCapytain.common.reference import Reference" \
"import pickle" \
"f = open('./pickled2.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(Reference('7.8.1-7.9.1'))" \
"print(len(t.getPassage(Reference('7.8.1-7.9.1'))))"
