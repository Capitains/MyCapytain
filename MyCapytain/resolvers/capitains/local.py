"""

"""
import io
import logging
import os.path
from glob import glob
from math import ceil
from collections import defaultdict

from MyCapytain.common.reference._capitains_cts import CtsReference
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.errors import UnknownObjectError, UndispatchedTextError
from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.resolvers.utils import CollectionDispatcher
from MyCapytain.resources.collections.capitains import XmlCapitainsCollectionMetadata, \
    XmlCapitainsReadableMetadata
from MyCapytain.resources.collections.cts import XmlCtsCitation
from MyCapytain.resources.prototypes.capitains.collection import CapitainsCollectionMetadata
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText


__all__ = [
    "XmlCapitainsLocalResolver"
]


class XmlCapitainsLocalResolver(Resolver):
    """ XML Folder Based resolver. CapitainsReadableMetadata and metadata resolver based on local directories

    :param resource: Resource should be a list of folders retaining data as Capitains 3.0 Guidelines Repositories
    :type resource: [str]
    :param name: Key used to differentiate Repository and thus enabling different repo to be used
    :type name: str
    :param logger: Logging object
    :type logger: logging

    :cvar TEXT_CLASS: CapitainsReadableMetadata Class [not instantiated] to be used to parse Texts. Can be changed to support Cache for example
    :type TEXT_CLASS: class
    :cvar DEFAULT_PAGE: Default Page to show
    :cvar PER_PAGE: Tuple representing the minimal number of texts returned, the default number and the maximum number of texts returned


    """
    CLASSES = {
        "text": CapitainsCtsText,
        "edition": XmlCapitainsReadableMetadata,
        "translation": XmlCapitainsReadableMetadata,
        "commentary": XmlCapitainsReadableMetadata,
        "work": XmlCapitainsCollectionMetadata,
        "textgroup": XmlCapitainsCollectionMetadata,
        "inventory": XmlCapitainsCollectionMetadata,
        "inventory_collection": XmlCapitainsCollectionMetadata,
        "citation": XmlCtsCitation
    }

    DEFAULT_PAGE = 1
    PER_PAGE = (1, 10, 100)  # Min, Default, Mainvex,
    RAISE_ON_UNDISPATCHED = False
    RAISE_ON_GENERIC_PARSING_ERROR = True

    @property
    def inventory(self):
        return self.__inventory__

    @inventory.setter
    def inventory(self, value):
        self.__inventory__ = value

    @property
    def texts(self):
        """ returns all readable texts

        :return: Readable descendants
        :rtype: {str: CapitainsReadableMetadata}
        """
        # Changed to a dictionary to match with the return type for XmlCapitainsCollectionMetadata.texts
        return {text.id: text for text in self.inventory.readableDescendants}

    def __init__(self, resource, name=None, logger=None, dispatcher=None, autoparse=True):
        """ Initiate the XMLResolver
        """
        self.classes = {}
        self.classes.update(type(self).CLASSES)

        if dispatcher is None:
            inventory_collection = self.classes["inventory_collection"](urn="defaultTic")
            ti = self.classes["inventory"]("default")
            ti.parent = inventory_collection
            ti.set_label("Default collection", "eng")
            self.dispatcher = CollectionDispatcher(inventory_collection)
        else:
            self.dispatcher = dispatcher
        self.__inventory__ = self.dispatcher.collection
        self.name = name

        self.logger = logger
        if not logger:
            self.logger = logging.getLogger(name)

        if not name:
            self.name = "repository"

        self.works = []

        if autoparse:
            self.parse(resource)

    def xmlparse(self, file):
        """ Parse a XML file
        :param file: Opened File
        :return: Tree
        """
        return xmlparser(file)

    def read(self, identifier, path):
        """ Retrieve and parse a text given an identifier

        :param identifier: Identifier of the text
        :type identifier: str
        :param path: Path of the text
        :type path: str
        :return: Parsed Text
        :rtype: CapitainsCtsText
        """
        with open(path) as f:
            o = self.classes["text"](urn=identifier, resource=self.xmlparse(f))
        return o

    def _parse_collection_wrapper(self, metadata_file, collection=None):
        """ Wraps with a Try/Except the Work parsing from a cts file

        :param metadata_file: Path to the metadata File
        :type metadata_file: str
        :param collection: Collection to which the collection belongs
        :type collection: CapitainsCollectionMetadata
        :return: Parsed Collection and the Texts, as well as the current file directory
        """
        try:
            return self._parse_collection(metadata_file, collection)
        except Exception as E:
            self.logger.error("Error parsing %s ", metadata_file)
            if self.RAISE_ON_GENERIC_PARSING_ERROR:
                raise E

    def _parse_collection(self, metadata_file, collection=None):
        """ Parses a work from a cts file

        :param metadata_file: Path to the CTS File
        :type metadata_file: str
        :param collection: Collection to which the Work is a part of
        :type collection: CapitainsCollectionMetadata
        :return: Parsed Collection and the Texts, as well as the current file directory
        """
        with io.open(metadata_file) as __xml__:
            work, children = self.classes["work"].parse(
                resource=__xml__,
                parent=collection,
                _with_children=True
            )

        return work, children, os.path.dirname(metadata_file)

    def _parse_text(self, text):
        """ Complete the TextMetadata object with its citation scheme by parsing the original text

        :param text: Text Metadata collection
        :type text: XmlCapitainsReadableMetadata
        :returns: True if all went well
        :rtype: bool
        """
        text_id, text_metadata = text.id, text
        if os.path.isfile(text_metadata.path):
            try:
                text = self.read(text_id, path=text_metadata.path)
                cites = list()
                for cite in [c for c in text.citation][::-1]:
                    if len(cites) >= 1:
                        cites.append(self.classes["citation"](
                            xpath=cite.xpath.replace("'", '"'),
                            scope=cite.scope.replace("'", '"'),
                            name=cite.name,
                            child=cites[-1]
                        ))
                    else:
                        cites.append(self.classes["citation"](
                            xpath=cite.xpath.replace("'", '"'),
                            scope=cite.scope.replace("'", '"'),
                            name=cite.name
                        ))
                del text
                text_metadata.citation = cites[-1]
                self.logger.info("%s has been parsed ", text_metadata.path)
                if not text_metadata.citation.is_set():
                    self.logger.error("%s has no passages", text_metadata.path)
                    return False
                return True
            except Exception:
                self.logger.error(
                    "%s does not accept parsing at some level (most probably citation) ",
                    text_metadata.path
                )
                return False
        else:
            self.logger.error("%s is not present", text_metadata.path)
            return False

    def _dispatch(self, collection, directory):
        """ Run the dispatcher over a textgroup.

        :param collection: Collection object that needs to be dispatched
        :param directory: Directory in which the Collection was found
        """
        if collection.id in self.dispatcher.collection:
            self.dispatcher.collection[collection.id].update(collection)
        else:
            self.dispatcher.dispatch(collection, path=directory)

        for sub_coll_id, sub_coll in collection.collections.items():
            if sub_coll_id in self.dispatcher.collection[collection.id].collections:
                self.dispatcher.collection[sub_coll_id].update(sub_coll)

    def _dispatch_container(self, collection, directory):
        """ Run the dispatcher over a collection within a try/except block

        .. note:: This extraction allows to change the dispatch routine \
            without having to care for the error dispatching

        :param collection: Collection object that needs to be dispatched
        :param directory: Directory in which the Collection was found
        """
        try:
            self._dispatch(collection, directory)
        except UndispatchedTextError as E:
            self.logger.error("Error dispatching %s ", directory)
            if self.RAISE_ON_UNDISPATCHED is True:
                raise E

    def _clean_invalids(self, invalids):
        """ Optionally remove texts that were found to be invalid

        :param invalids: List of text identifiers
        :type invalids: [CapitainsReadableMetadata]
        """
        pass

    def parse(self, resource):
        """ Parse a list of directories and reads it into a collection

        :param resource: List of folders
        :return: An inventory resource and a list of CapitainsReadableMetadata metadata-objects
        """
        id_to_coll = dict()
        members = dict()
        parents = dict()
        invalids = []

        for folder in resource:
            metadata_files = glob("{base_folder}/data/**/__capitains__.xml".format(base_folder=folder), recursive=True)
            for metadata_file in metadata_files:
                collection, children, rel_dir = self._parse_collection_wrapper(metadata_file)
                collection.path = os.path.normpath(metadata_file)
                id_to_coll[collection.id] = collection
                members[collection.id] = [child.id for child in children]

                for child in children:
                    if child.id not in parents:
                        parents.update({child.id: [collection]})
                    else:
                        parents[child.id].append(collection)
                    if child.readable is True:
                        child.path = os.path.normpath(os.path.join(rel_dir, child.path))
                        id_to_coll[child.id] = child

        for k, v in id_to_coll.items():
            if k in parents:
                for parent in parents[k]:
                    v.parent = parent
            if v.readable is False:
                v.children.update({ident: id_to_coll[ident] for ident in members[k]})
            else:
                # If text_id is not none, the text parsing errored
                if not self._parse_text(v):
                    invalids.append(v)

        # Dispatching routine
        # The sorting is required to make sure that the top-level collections are dispatched first.
        for collection in sorted(id_to_coll, key=lambda x: x in parents.keys()):
            if id_to_coll[collection].readable is False:
                self._dispatch_container(id_to_coll[collection], os.path.dirname(id_to_coll[collection].path))

        # Clean invalids if there was a need
        self._clean_invalids(invalids)

        self.inventory = self.dispatcher.collection
        return self.inventory

    def __getText__(self, identifier):
        """ Returns a XmlCapitainsReadableMetadata object
        :param identifier: URN of a text to retrieve
        :type identifier: str, URN
        :return: Textual resource and metadata
        :rtype: (CapitainsCtsText, XmlCapitainsReadableMetadata)
        """
        # This will raise an UnknownCollection error if the identifier does not exist in the collection
        # I assume that this is the desired outcome. If not, we can do a try/except here.
        temp_text = self.inventory[str(identifier)]
        if temp_text.readable:
            text = temp_text
        else:
            # Perhaps there is a better exception to raise here?
            raise(UnknownObjectError('{} is not a readable object'.format(str(identifier))))

        if os.path.isfile(text.path):
            with io.open(text.path) as __xml__:
                resource = self.classes["text"](urn=identifier, resource=self.xmlparse(__xml__))
        else:
            # Passing None to the functions that call __getText__ results in a not very helpful AttributeError
            # A more informative error should be raised here.
            resource = None
            self.logger.warning('The file {} is mentioned in the metadata but does not exist'.format(text.path))

        return resource, text

    def __getTextMetadata__(self,
                            urn=None, page=None, limit=None,
                            lang=None, category=None, pagination=False
                            ):
        """ Retrieve a slice of the inventory filtered by given arguments
        :param urn: Partial URN to use to filter out resources
        :type urn: str
        :param page: Page to show
        :type page: int
        :param limit: Item Per Page
        :type limit: int
        :param inventory: Inventory name
        :type inventory: str
        :param lang: Language to filter on
        :type lang: str
        :param category: Type of elements to show
        :type category: str
        :param pagination: Activate pagination
        :type pagination: bool
        :return: ([Matches], Page, Count)
        :rtype: ([CtsTextMetadata], int, int)
        """
        if urn is not None:
            collection = self.inventory[urn].readableDescendants or [self.inventory[urn]]
        else:
            collection = self.inventory.readableDescendants

        matches = [
            text
            for text in collection
            if
            (lang is None or (lang is not None and lang == text.lang)) and
            (text.citation is not None) and
            # I am not sure that this categorization is useful since the type is not longer a strictly controlled
            # vocabulary.
            # It might be possible if the resolver built a list of the types as it was ingesting the texts and then
            # checked to see if the category parameter is a member of this list.
            (
                category not in ["cts:edition", "cts:translation", "cts:commentary"] or
                (category in ["cts:edition", "cts:translation", "cts:commentary"]
                 and category.lower() == text.subtype.lower())
            )
        ]
        if pagination:
            start_index, end_index, page, count = type(self).pagination(page, limit, len(matches))
        else:
            start_index, end_index, page, count = None, None, 0, len(matches)

        return matches[start_index:end_index], page, count

    @staticmethod
    def pagination(page, limit, length):
        """ Help for pagination
        :param page: Provided Page
        :param limit: Number of item to show
        :param length: Length of the list to paginate
        :return: (Start Index, End Index, Page Number, Item Count)
        """
        realpage = page
        page = page or XmlCapitainsLocalResolver.DEFAULT_PAGE
        limit = limit or XmlCapitainsLocalResolver.PER_PAGE[1]

        if limit < XmlCapitainsLocalResolver.PER_PAGE[0] or limit > XmlCapitainsLocalResolver.PER_PAGE[2]:
            limit = XmlCapitainsLocalResolver.PER_PAGE[1]

        page = (page - 1) * limit

        if page > length:
            realpage = int(ceil(length / limit))
            page = limit * (realpage - 1)
            count = length - 1
        elif limit - 1 + page < length:
            count = limit - 1 + page
        else:
            count = length - 1

        return page, count + 1, realpage, count - page + 1

    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param objectId: Object Identifier to filter on
        :type objectId: str
        :param filters: Kwargs parameters.
        :type filters: dict
        :return: Collection
        """
        if objectId is None:
            return self.inventory
        elif objectId in self.inventory.children.keys():
            return self.inventory[objectId]
        texts, _, _ = self.__getTextMetadata__(urn=objectId)

        # We store inventory names and if there is only one we recreate the inventory
        inv_names = [text.parents[-2].id for text in texts]
        if len(set(inv_names)) == 1:
            inventory = self.classes["inventory"](urn=inv_names[0])
        else:
            inventory = self.classes["inventory"]()

        # For each text we found using the filter
        for text in texts:
            # Generate any ancestor collections for the text
            reversed_parents = text.parents[::-1][2:]
            parent = inventory
            for ancestor in reversed_parents:
                coll_urn = str(ancestor.urn)
                if coll_urn not in parent.collections:
                    self.classes["work"](urn=coll_urn, parent=parent)
                parent = parent.collections[coll_urn]
                parent.path = ancestor.path
                parent.children.update(ancestor.children)

            x = self.classes["edition"](urn=str(text.urn), parent=parent, lang=text.lang)
            x.citation = text.citation
            x.path = text.path

        return inventory[objectId]

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage CtsReference
        :type subreference: str
        :param prevnext: Retrieve graph representing previous and next passage
        :type prevnext: boolean
        :param metadata: Retrieve metadata about the passage and the text
        :type metadata: boolean
        :return: CapitainsCtsPassage
        :rtype: CapitainsCtsPassage
        """
        text, text_metadata = self.__getText__(textId)
        if subreference is not None and not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)
        passage = text.getTextualNode(subreference)
        if metadata:
            passage._metadata = text_metadata.metadata
        return passage

    def getSiblings(self, textId, subreference: CtsReference):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage CtsReference
        :type subreference: str
        :return: Tuple of references
        :rtype: (str, str)
        """
        text, inventory = self.__getText__(textId)
        if not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)
        passage = text.getTextualNode(subreference)
        return passage.siblingsId

    def getReffs(self, textId, level=1, subreference=None):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param level: Depth for retrieval
        :type level: int
        :param subreference: CapitainsCtsPassage CtsReference
        :type subreference: str
        :return: List of references
        :rtype: [str]
        """
        passage, inventory = self.__getText__(textId)
        if subreference:
            passage = passage.getTextualNode(subreference)
        return passage.getReffs(level=level, subreference=subreference)
