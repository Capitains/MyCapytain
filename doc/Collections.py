from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.resources.collections.cts import TextInventory
from MyCapytain.common.constants import Mimetypes
from pprint import pprint

"""
In order to have a real life example,
we are gonna query for data in the Leipzig CTS API
We are gonna query for metadata about Seneca who
is represented by urn:cts:latinLit:stoa0255

To retrieve data, we are gonna make a GetMetadata query
to the CTS Retriever.
"""
retriever = CTS("http://cts.dh.uni-leipzig.de/api/cts/")
# We store the response (Pure XML String)
response = retriever.getMetadata(objectId="urn:cts:latinLit:stoa0255")

"""
From here, we actually have the necessary data, we can now
play with collections. TextInventory is the main collection type that is needed to
parse the whole response.
"""
inventory = TextInventory(resource=response)
# What we are gonna do is print the title of each descendant :
for descendant in inventory.descendants:
    print(descendant.title["default"])

"""
You should see in there things such as
-   "Seneca, Lucius Annaeus" (The TextGroup or main object)
-   "de Ira" (The Work object)
-   "de Ira, Moral essays Vol 2" (The Edition specific Title)

We can now see other functions, such as the export to JSON DTS.
CTS Collection have a uniquely feature built in : they allow for
accessing an item using its key as if it were a dictionary :
The identifier of a De Ira is urn:cts:latinLit:stoa0255.stoa0110
"""
deIra = inventory["urn:cts:latinLit:stoa0255.stoa010"]
pprint(deIra.export(output=Mimetypes.JSON.DTS.Std))
# you should see a DTS representation of the work

"""
What we might want to do is to browse metadata about seneca's De Ira
Remember that CTSCollections have a parents attribute !
"""
for descAsc in deIra.descendants + [deIra] + deIra.parents:
    # We filter out Textgroup which has an empty Metadata value
    if not isinstance(descAsc, TextInventory):
        print(
            descAsc.metadata.export(output=Mimetypes.JSON.Std)
        )
"""
And of course, we can simply export deIra to CTS XML format
"""
print(deIra.export(Mimetypes.XML.CTS))