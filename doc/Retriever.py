from MyCapytain.retrievers.cts5 import HttpCtsRetriever

# We set up a retriever which communicates with an API available in Leipzig
retriever = HttpCtsRetriever("http://cts.dh.uni-leipzig.de/api/cts/")
# We require a passage : passage is now a Passage object
passage = retriever.getPassage("urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
# Passage is now equal to the string content of http://cts.dh.uni-leipzig.de/api/cts/?request=GetPassage&urn=urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1
print(passage)

"""
<GetPassage><request><requestName>GetPassage</requestName><requestUrn>urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1</requestUrn></request>
<reply><urn>urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1</urn><passage><TEI>
<text n="urn:cts:latinLit:phi1294.phi002.perseus-lat2" xml:id="stoa0045.stoa0"><body>
<div type="edition" n="urn:cts:latinLit:phi1294.phi002.perseus-lat2" xml:lang="lat">
<div type="textpart" subtype="book" n="1"><div type="textpart" subtype="poem" n="1">
<head>I</head>
<l n="1">Hic est quem legis ille, quem requiris, </l>
<l n="2">Toto notus in orbe Martialis </l>
<l n="3">Argutis epigrammaton libellis: <pb/></l>
<l n="4">Cui, lector studiose, quod dedisti </l>
<l n="5">Viventi decus atque sentienti, </l>
<l n="6">Rari post cineres habent poetae. </l>
</div></div></div></body></text></TEI></passage></reply>
"""