"""

"""
import io
import logging
import os.path
from glob import glob
from math import ceil

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
from MyCapytain.common.constants import RDF_NAMESPACES
from typing import Dict, List, Union


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
        "Text": CapitainsCtsText,
        "ReadableCollection": XmlCapitainsReadableMetadata,
        "Collection": XmlCapitainsCollectionMetadata,
        "citation": XmlCtsCitation
    }

    DEFAULT_PAGE = 1
    PER_PAGE = (1, 10, 100)  # Min, Default, Mainvex,
    RAISE_ON_UNDISPATCHED = False
    RAISE_ON_GENERIC_PARSING_ERROR = True

    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, value):
        self._inventory = value

    @property
    def texts(self) -> Dict[str, XmlCapitainsReadableMetadata]:
        """ returns all readable texts

        :return: Readable descendants
        :rtype: {str: CapitainsReadableMetadata}
        """
        # Changed to a dictionary to match with the return type for XmlCapitainsCollectionMetadata.texts
        texts = {}
        for s in self.children.values():
            for v in s:
                c = self.id_to_coll[v]
                if c.readable:
                    texts[v] = c
        return texts

    def __init__(self, resource, name=None, logger=None, autoparse=True):
        """ Initiate the XMLResolver
        """
        super(XmlCapitainsLocalResolver, self).__init__()
        self.classes = {}
        self.classes.update(type(self).CLASSES)

        self._inventory = self.classes["Collection"](name or "defaultTic", resolver=self)
        self.add_collection(self._inventory.id, self._inventory)
        self.name = name

        self.logger = logger
        if not logger:
            self.logger = logging.getLogger(name)

        if not name:
            self.name = "repository"

        if autoparse:
            self.parse(resource)

    def xmlparse(self, file):
        """ Parse a XML file
        :param file: Opened File
        :return: Tree
        """
        return xmlparser(file)

    def read(self, identifier: str, path: str) -> CapitainsCtsText:
        """ Retrieve and parse a text given an identifier

        :param identifier: Identifier of the text
        :type identifier: str
        :param path: Path of the text
        :type path: str
        :return: Parsed Text
        :rtype: CapitainsCtsText
        """
        with open(path) as f:
            o = self.classes["Text"](urn=identifier, resource=self.xmlparse(f))
        return o

    def _parse_collection_wrapper(self, metadata_file: str, collection: XmlCapitainsCollectionMetadata=None):
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

    def _parse_collection(self, metadata_file: str, collection: XmlCapitainsCollectionMetadata=None)\
            -> (XmlCapitainsCollectionMetadata,
                List[Union[XmlCapitainsCollectionMetadata, XmlCapitainsReadableMetadata]],
                str):
        """ Parses a work from a cts file

        :param metadata_file: Path to the CTS File
        :type metadata_file: str
        :param collection: Collection to which the Work is a part of
        :type collection: CapitainsCollectionMetadata
        :return: Parsed Collection and the Texts, as well as the current file directory
        """
        with io.open(metadata_file) as _xml:
            work, children = self.classes["Collection"].parse(
                resource=_xml,
                parent=collection,
                _with_children=True,
                resolver=self
            )

        return work, children, os.path.dirname(metadata_file)

    def _parse_text(self, text: XmlCapitainsReadableMetadata) -> bool:
        """ Complete the TextMetadata object with its citation scheme by parsing the original text
        Note that this still uses guidelines 2.0 (i.e., CTS) citation system

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

    def _clean_invalids(self, invalids: List[XmlCapitainsReadableMetadata]):
        """ Optionally remove texts that were found to be invalid

        :param invalids: List of text identifiers
        :type invalids: [CapitainsReadableMetadata]
        """
        pass

    def parse(self, resource: List[str]) -> XmlCapitainsCollectionMetadata:
        """ Parse a list of directories and reads it into a collection

        :param resource: List of folders
        :return: An inventory resource and a list of CapitainsReadableMetadata metadata-objects
        """
        invalids = []

        for folder in resource:
            metadata_files = glob("{base_folder}/data/**/__capitains__.xml".format(base_folder=folder), recursive=True)
            for metadata_file in metadata_files:
                collection, children, rel_dir = self._parse_collection_wrapper(metadata_file)
                collection.path = os.path.normpath(metadata_file)
                # Setting up relationships in the resolver is in the parse methods of the collection objects
                # Moving the relationship building there means that XML files parsed without a resolver will also have these relationships.
                # This assumes that the resolver will never ingest anything that doesn't parse xml files
                # self.add_collection(collection.id, collection)

                for child in children:
                    child.path = os.path.normpath(os.path.join(rel_dir, child.path))
                    # self.add_parent(child.id, collection.id)
                    child.metadata.add(RDF_NAMESPACES.CAPITAINS.parent, collection.id)
                    """if child.id in self.id_to_coll and not child.readable:
                        self.id_to_coll[child.id].update(child)
                    else:
                        self.add_collection(child.id, child)"""
                    if child.readable:
                        if not self._parse_text(child):
                            invalids.append(child)

        for coll_id, collection in self.id_to_coll.items():
            if coll_id not in self.parents and coll_id != self.inventory.id:
                self.add_parent(coll_id, self.inventory.id)

        # Clean invalids if there was a need
        self._clean_invalids(invalids)

        return self.inventory

    def _get_text(self, identifier: str) -> (Union[CapitainsCtsText, None], XmlCapitainsReadableMetadata):
        """ Returns a XmlCapitainsReadableMetadata object
        :param identifier: URN of a text to retrieve
        :type identifier: str, URN
        :return: Textual resource and metadata
        :rtype: (CapitainsCtsText, XmlCapitainsReadableMetadata)
        """
        # This will raise an UnknownCollection error if the identifier does not exist in the collection
        # I assume that this is the desired outcome. If not, we can do a try/except here.
        if not isinstance(identifier, str):
            identifier = str(identifier)
        try:
            text = self.texts[identifier]
        except KeyError:
            # Perhaps there is a better exception to raise here?
            raise(UnknownObjectError('{} is not a readable object'.format(str(identifier))))

        if os.path.isfile(text.path):
            with io.open(text.path) as _xml:
                resource = self.classes["Text"](urn=identifier, resource=self.xmlparse(_xml))
        else:
            # Passing None to the functions that call __getText__ results in a not very helpful AttributeError
            # A more informative error should be raised here.
            resource = None
            self.logger.warning('The file {} is mentioned in the metadata but does not exist'.format(text.path))

        return resource, text

    def _get_text_metadata(self,
                           id: str=None, page: int=None, limit: int=None,
                           lang: str=None, pagination: bool=False
                           ) -> (List[XmlCapitainsReadableMetadata], int, int):
        """ Retrieve a slice of the inventory filtered by given arguments
        :param id: identifier to use to filter out resources
        :param page: Page to show
        :param limit: Item Per Page
        :param lang: Language to filter on
        :param pagination: Activate pagination
        :return: ([Matches], Page, Count)
        """
        if id:
            collection = {id: self.id_to_coll[id]}
            if not collection[id].readable:
                collection = collection[id].readableDescendants
        else:
            collection = self.texts

        matches = [
            text
            for text in collection.values()
            if
            (lang is None or (lang is not None and lang == text.lang)) and
            (text.citation is not None)
        ]
        if pagination:
            start_index, end_index, page, count = type(self).pagination(page, limit, len(matches))
        else:
            start_index, end_index, page, count = None, None, 0, len(matches)

        return matches[start_index:end_index], page, count

    @staticmethod
    def pagination(page: int, limit: int, length: int) -> (int, int, int, int):
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

    def getMetadata(self, objectId: str=None, **filters) -> Union[XmlCapitainsReadableMetadata, XmlCapitainsCollectionMetadata]:
        """ Request metadata about a text or a collection

        :param objectId: Object Identifier to filter on
        :type objectId: str
        :param filters: Kwargs parameters.
        :type filters: dict
        :return: Collection
        """
        if objectId is None:
            return self.inventory
        return self.id_to_coll[objectId]

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
        text, text_metadata = self._get_text(textId)
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
        text, inventory = self._get_text(textId)
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
        passage, inventory = self._get_text(textId)
        if subreference:
            passage = passage.getTextualNode(subreference)
        return passage.getReffs(level=level, subreference=subreference)
