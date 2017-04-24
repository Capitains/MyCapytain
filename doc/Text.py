#  We import the correct classes from the local module
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText
from MyCapytain.common.constants import Mimetypes, XPATH_NAMESPACES
from lxml.etree import tostring

#  We open a file
with open("./tests/testing_data/examples/text.martial.xml") as f:
    # We initiate a Text object giving the IO instance to resource argument
    text = CapitainsCtsText(resource=f)

# Text objects have a citation property
#  len(Citation(...)) gives the depth of the citation scheme
# in the case of this sample, this would be 3 (Book, Poem, Line)
for ref in text.getReffs(level=len(text.citation)):
    # We retrieve a Passage object for each reference that we find
    # We can pass the reference many way, including in the form of a list of strings
    # We use the _simple parameter to get a fairly simple object
    # Simple makes a straight object that has only the targeted node inside of it
    psg = text.getTextualNode(subreference=ref, simple=True)
    # We print the passage from which we retrieve <note> nodes
    print("\t".join([ref, psg.export(Mimetypes.PLAINTEXT, exclude=["tei:note"])]))

"""
You'll print something like the following :

    1.pr.1	Spero me secutum in libellis meis tale temperamen-
    1.pr.2	tum, ut de illis queri non possit quisquis de se bene
    1.pr.3	senserit, cum salva infimarum quoque personarum re-
    1.pr.4	verentia ludant; quae adeo antiquis auctoribus defuit, ut
    1.pr.5	nominibus non tantum veris abusi sint, sed et magnis.
    1.pr.6	Mihi fama vilius constet et probetur in me novissimum

"""

# It is possible that what you're interested in is a little more complex
# Like for example, getting a specific text sample with a specific reference
# In TEI !

#  We open another such as Cicero's texts !
with open("./tests/testing_data/examples/text.cicero.xml") as f:
    # We initiate a Text object giving the IO instance to resource argument
    text = CapitainsCtsText(resource=f)
    # We are specifically interest in the portion 28-30
    # Note that we won't use 28-30 as cross passage reference won't work properly
    p28_29 = text.getTextualNode("28-29")

    # And we want to be able to work with the xml
    # To be injected in a third party API for lemmatization purposes
    xml = p28_29.export(Mimetypes.XML.Std)
    print("XML of 28-29")
    print(xml)
    print("------------")

    # But what we really want to do, is suppress the note from the XML.
    # So we export to an LXML Object
    document = p28_29.export(Mimetypes.PYTHON.ETREE)
    # We remove some XML
    for element in document.xpath("//tei:note", namespaces=XPATH_NAMESPACES):
        element.getparent().remove(element)
    # And we print using LXML constants
    print("Clean XML of 28-29")
    print(tostring(document, encoding=str))
    print("------------")

