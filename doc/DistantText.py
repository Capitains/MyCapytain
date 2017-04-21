from MyCapytain.retrievers.cts5 import HttpCtsRetriever
from MyCapytain.resources.texts.remote.cts import CTSText

# We set up a retriever which communicates with an API available in Leipzig
retriever = HttpCtsRetriever("http://cts.dh.uni-leipzig.de/api/cts/")

# Given that we have other examples that shows how to work with text,
# we will focus here on playing with the graph functionality of texts implementations.
# We are gonna retrieve a text passage and the retrieve all its siblings in different fashion#
# The main point is to find all children of the same parent.
# The use case could be the following : some one want to retrieve the full text around a citation
# To enhance the display a little.

# We will work with the line 7 of poem 39 of book 4 of Martial's Epigrammata
# The text is urn:cts:latinLit:phi1294.phi002.perseus-lat2
text = CTSText(retriever=retriever, urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2")

# We retrieve up the passage
target = text.getTextualNode(subreference="4.39.7")
print(target.text)
"""
Nec quae Callaico linuntur auro,
"""

# The parent way :
# - get to the parent,
# - retrieve each node,
# - print only the one which are not target

parent = target.parent
for node in parent.children:
    if node.id != target.id:
        print("{}\t{}".format(node.id, node.text))
    else:
        print("------Original Node-----------")

"""
4.39.1	Argenti genus omne comparasti,
4.39.2	Et solus veteres Myronos artes,
4.39.3	Solus Praxitelus manum Scopaeque,
4.39.4	Solus Phidiaci toreuma caeli,
4.39.5	Solus Mentoreos habes labores.
4.39.6	Nec desunt tibi vera Gratiana,
------Original Node-----------
4.39.8	Nec mensis anaglypta de paternis.
4.39.9	Argentum tamen inter omne miror
4.39.10	Quare non habeas, Charine, purum.
"""

print("\n\nSecond Method\n\n")

# We are gonna do another way this time :
# - get the previous until we change parent
# - get the next until we change parent

parentId = node.parentId
# Deal with the previous ones
current = target.prev
while current.parentId == parentId:
    print("{}\t{}".format(current.id, current.text))
    current = current.prev

print("------Original Node-----------")

# Deal with the next ones
current = target.next
while current.parentId == parentId:
    print("{}\t{}".format(current.id, current.text))
    current = current.next
"""
4.39.6	Nec desunt tibi vera Gratiana,
4.39.5	Solus Mentoreos habes labores.
4.39.4	Solus Phidiaci toreuma caeli,
4.39.3	Solus Praxitelus manum Scopaeque,
4.39.2	Et solus veteres Myronos artes,
4.39.1	Argenti genus omne comparasti,
------Original Node-----------
4.39.8	Nec mensis anaglypta de paternis.
4.39.9	Argentum tamen inter omne miror
4.39.10	Quare non habeas, Charine, purum.

"""