from MyCapytain.resolvers.cts.local import CTSCapitainsLocalResolver
from MyCapytain.resolvers.utils import CollectionDispatcher
from MyCapytain.common.constants import Mimetypes
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection

# We set up a main collection
tic = CtsTextInventoryCollection()
# We register sub collection we want to dispatch to
latin = XmlCtsTextInventoryMetadata("urn:perseus:latinLit", parent=tic)
latin.set_label("Classical Latin", "eng")
farsi = XmlCtsTextInventoryMetadata("urn:perseus:farsiLit", parent=tic)
farsi.set_label("Farsi", "eng")
gc = XmlCtsTextInventoryMetadata("urn:perseus:greekLit", parent=tic)
gc.set_label("Ancient Greek", "eng")
gc.set_label("Grec Ancien", "fre")

# We create the dispatcher with the root collection
dispatcher = CollectionDispatcher(tic)

# And we record function for each given repository
# We could have two function dispatching for the same repository !
@dispatcher.inventory("urn:perseus:latinLit")
def dispatchLatinLit(collection, path=None, **kwargs):
    if collection.id.startswith("urn:cts:latinLit:"):
        return True
    return False

@dispatcher.inventory("urn:perseus:farsiLit")
def dispatchfFarsiLit(collection, path=None, **kwargs):
    if collection.id.startswith("urn:cts:farsiLit:"):
        return True
    return False

@dispatcher.inventory("urn:perseus:greekLit")
def dispatchGreekLit(collection, path=None, **kwargs):
    if collection.id.startswith("urn:cts:greekLit:"):
        return True
    return False

# We set up a resolver which parses local file
NautilusDummy = CTSCapitainsLocalResolver(
    resource=[
        "./tests/testing_data/latinLit2"
    ],
    # We give it the dispatcher
    dispatcher=dispatcher
)

# If we want to read the main repository, we will have all children
all = NautilusDummy.getMetadata()

print(len(all.readableDescendants)) # 25 is the number of edition and translation
print([m.id for m in all.members]) # Direct members are dispatched-in collections
print(
    all["urn:cts:latinLit:phi1294"] == all["urn:perseus:latinLit"]["urn:cts:latinLit:phi1294"]
)  # Is true because they are dispatched this way

try:
    all["urn:perseus:greekLit"]["urn:cts:latinLit:phi1294"]
except KeyError:
    print("But this won't work because the object has been dispatched to latinLit !")

print(len(all["urn:perseus:greekLit"].readableDescendants))  # Is 6 because there is 6 recorded texts in __cts__
print(len(all["urn:perseus:latinLit"].readableDescendants))  # Is 19 because there is 6 recorded texts in __cts__
