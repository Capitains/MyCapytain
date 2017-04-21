#python -m timeit -n 1000 -s "from MyCapytain.common.utils import xmlparser, streamparser" "from MyCapytain.resources.texts.local import Text" "f = open('/home/thibault/dev/capitains/MyCapytain/tests/testing_data/texts/seneca.xml')"  "r = streamparser(f)" "t = Text(resource=r)" "t.getPassage(['780'])"

echo "Dumping data"
python with_pickle.py

echo "Testing on Seneca, Single Simple CapitainsCTSPassage"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1017/phi004/phi1017.phi004.perseus-lat2.xml')"  \
"r = xmlparser(f)" \
"t = CTSText(resource=r)" \
"t.getPassage(['780'])"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = lxml.objectify.makeparser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1017/phi004/phi1017.phi004.perseus-lat2.xml')" \
"r = lxml.objectify.parse(f, X)" \
"t = CTSText(resource=r)" \
"t.getPassage(['780'])"

# We pickle the resource
python -m timeit -n $1 "from MyCapytain.resources.texts.local import CTSText" \
"import pickle" \
"f = open('./pickled.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(['780'])"

echo "Testing range"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.common.reference import Reference" \
"from MyCapytain.resources.texts.local import CTSText" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1017/phi004/phi1017.phi004.perseus-lat2.xml')"  \
"r = xmlparser(f)" \
"t = CTSText(resource=r)" \
"t.getPassage(Reference('1018b-1025'))"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.common.reference import Reference" \
"from MyCapytain.resources.texts.local import CTSText" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = lxml.objectify.makeparser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1017/phi004/phi1017.phi004.perseus-lat2.xml')" \
"r = lxml.objectify.parse(f, X)" \
"t = CTSText(resource=r)" \
"t.getPassage(Reference('1018b-1025'))"

# We pickle the resource
python -m timeit -n $1 "from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"import pickle" \
"f = open('./pickled.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(Reference('1018b-1025'))"

echo "Testing with a deeper architecture"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = xmlparser(f)" \
"t = CTSText(resource=r)" \
"t.getPassage(['1', '5', '2'])"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = lxml.objectify.makeparser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = lxml.objectify.parse(f, X)" \
"t = CTSText(resource=r)" \
"t.getPassage(['1', '5', '2'])"

python -m timeit -n $1 "from MyCapytain.resources.texts.local import CTSText" \
"import pickle" \
"f = open('./pickled2.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(['1', '5', '2'])"

echo "Testing with a deeper architecture at the end"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = xmlparser(f)" \
"t = CTSText(resource=r)" \
"t.getPassage(['12', '5', '2'])"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = lxml.objectify.makeparser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = lxml.objectify.parse(f, X)" \
"t = CTSText(resource=r)" \
"t.getPassage(['12', '5', '2'])"

python -m timeit -n $1 "from MyCapytain.resources.texts.local import CTSText" \
"import pickle" \
"f = open('./pickled2.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(['12', '5', '2'])"

echo "Testing with a deeper architecture with range"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = xmlparser(f)" \
"t = CTSText(resource=r)" \
"t.getPassage(Reference('7.8.1-7.9.1'))"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = lxml.objectify.makeparser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml')"  \
"r = lxml.objectify.parse(f, X)" \
"t = CTSText(resource=r)" \
"t.getPassage(Reference('7.8.1-7.9.1'))"

python -m timeit -n $1 "from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"import pickle" \
"f = open('./pickled2.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(Reference('7.8.1-7.9.1'))"


echo "Testing with complicated XPATH"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/stoa0045/stoa001/stoa0045.stoa001.perseus-lat2.xml')"  \
"r = xmlparser(f)" \
"t = CTSText(resource=r)" \
"t.getPassage(Reference('5.2'))"

python -m timeit -n $1 -s \
"from MyCapytain.common.utils import xmlparser" \
"from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"import lxml.objectify" \
"from lxml.etree import XMLParser" \
"X = lxml.objectify.makeparser()" \
"f = open('/home/thibault/dev/canonicals/canonical-latinLit/data/stoa0045/stoa001/stoa0045.stoa001.perseus-lat2.xml')"  \
"r = lxml.objectify.parse(f, X)" \
"t = CTSText(resource=r)" \
"t.getPassage(Reference('5.2'))"

python -m timeit -n $1 "from MyCapytain.resources.texts.local import CTSText" \
"from MyCapytain.common.reference import Reference" \
"import pickle" \
"f = open('./pickled3.pkl', 'rb')"  \
"t = pickle.load(f)" \
"t.getPassage(Reference('5.2'))"