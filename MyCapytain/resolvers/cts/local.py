"""

"""
import io
import logging
import os.path
from glob import glob
from math import ceil

from MyCapytain.common.reference._capitains_cts import CtsReference, URN
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.errors import InvalidURN, UnknownObjectError, UndispatchedTextError
from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.resolvers.utils import CollectionDispatcher
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata, XmlCtsTextgroupMetadata, \
    XmlCtsWorkMetadata, XmlCtsCitation, XmlCtsTextMetadata as InventoryText, \
    XmlCtsTranslationMetadata, XmlCtsEditionMetadata, XmlCtsCommentaryMetadata
from MyCapytain.resources.prototypes.cts.inventory import CtsEditionMetadata, CtsTextgroupMetadata, CtsWorkMetadata, \
    CtsCommentaryMetadata, CtsTextInventoryCollection, CtsTranslationMetadata, CtsTextInventoryMetadata
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText


__all__ = [
    "CtsCapitainsLocalResolver"
]


class CtsCapitainsLocalResolver(Resolver):
    """ XML Folder Based resolver. CtsTextMetadata and metadata resolver based on local directories

    :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
    :type resource: [str]
    :param name: Key used to differentiate Repository and thus enabling different repo to be used
    :type name: str
    :param logger: Logging object
    :type logger: logging

    :cvar TEXT_CLASS: CtsTextMetadata Class [not instantiated] to be used to parse Texts. Can be changed to support Cache for example
    :type TEXT_CLASS: class
    :cvar DEFAULT_PAGE: Default Page to show
    :cvar PER_PAGE: Tuple representing the minimal number of texts returned, the default number and the maximum number of texts returned


    """
    CLASSES = {
        "text": CapitainsCtsText,
        "edition": XmlCtsEditionMetadata,
        "translation": XmlCtsTranslationMetadata,
        "commentary": XmlCtsCommentaryMetadata,
        "work": XmlCtsWorkMetadata,
        "textgroup": XmlCtsTextgroupMetadata,
        "inventory": XmlCtsTextInventoryMetadata,
        "inventory_collection": CtsTextInventoryCollection,
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
        return self.inventory.readableDescendants

    def __init__(self, resource, name=None, logger=None, dispatcher=None, autoparse=True):
        """ Initiate the XMLResolver
        """
        self.classes = {}
        self.classes.update(type(self).CLASSES)

        if dispatcher is None:
            inventory_collection = self.classes["inventory_collection"](identifier="defaultTic")
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

    def _parse_textgroup_wrapper(self, cts_file):
        """ Wraps with a Try/Except the textgroup parsing from a cts file

        :param cts_file: Path to the CTS File
        :type cts_file: str
        :return: CtsTextgroupMetadata
        """
        try:
            return self._parse_textgroup(cts_file)
        except Exception as E:
            self.logger.error("Error parsing %s ", cts_file)
            if self.RAISE_ON_GENERIC_PARSING_ERROR:
                raise E

    def _parse_textgroup(self, cts_file):
        """ Parses a textgroup from a cts file

        :param cts_file: Path to the CTS File
        :type cts_file: str
        :return: CtsTextgroupMetadata and Current file
        """
        with io.open(cts_file) as __xml__:
            return self.classes["textgroup"].parse(
                resource=__xml__
            ), cts_file

    def _parse_work_wrapper(self, cts_file, textgroup):
        """ Wraps with a Try/Except the Work parsing from a cts file

        :param cts_file: Path to the CTS File
        :type cts_file: str
        :param textgroup: Textgroup to which the Work is a part of
        :type textgroup: CtsTextgroupMetadata
        :return: Parsed Work and the Texts, as well as the current file directory
        """
        try:
            return self._parse_work(cts_file, textgroup)
        except Exception as E:
            self.logger.error("Error parsing %s ", cts_file)
            if self.RAISE_ON_GENERIC_PARSING_ERROR:
                raise E

    def _parse_work(self, cts_file, textgroup):
        """ Parses a work from a cts file

        :param cts_file: Path to the CTS File
        :type cts_file: str
        :param textgroup: Textgroup to which the Work is a part of
        :type textgroup: CtsTextgroupMetadata
        :return: Parsed Work and the Texts, as well as the current file directory
        """
        with io.open(cts_file) as __xml__:
            work, texts = self.classes["work"].parse(
                resource=__xml__,
                parent=textgroup,
                _with_children=True
            )

        return work, texts, os.path.dirname(cts_file)

    def _parse_text(self, text, directory):
        """ Complete the TextMetadata object with its citation scheme by parsing the original text

        :param text: Text Metadata collection
        :type text: XmlCtsTextMetadata
        :param directory: Directory in which the metadata was found and where the text file should be
        :type directory: str
        :returns: True if all went well
        :rtype: bool
        """
        text_id, text_metadata = text.id, text
        text_metadata.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
            directory=directory,
            textgroup=text_metadata.urn.textgroup,
            work=text_metadata.urn.work,
            version=text_metadata.urn.version
        )
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

    def _dispatch(self, textgroup, directory):
        """ Run the dispatcher over a textgroup.

        :param textgroup: Textgroup object that needs to be dispatched
        :param directory: Directory in which the textgroup was found
        """
        if textgroup.id in self.dispatcher.collection:
            self.dispatcher.collection[textgroup.id].update(textgroup)
        else:
            self.dispatcher.dispatch(textgroup, path=directory)

        for work_urn, work in textgroup.works.items():
            if work_urn in self.dispatcher.collection[textgroup.id].works:
                self.dispatcher.collection[work_urn].update(work)

    def _dispatch_container(self, textgroup, directory):
        """ Run the dispatcher over a textgroup within a try/except block

        .. note:: This extraction allows to change the dispatch routine \
            without having to care for the error dispatching

        :param textgroup: Textgroup object that needs to be dispatched
        :param directory: Directory in which the textgroup was found
        """
        try:
            self._dispatch(textgroup, directory)
        except UndispatchedTextError as E:
            self.logger.error("Error dispatching %s ", directory)
            if self.RAISE_ON_UNDISPATCHED is True:
                raise E

    def _clean_invalids(self, invalids):
        """ Optionally remove texts that were found to be invalid

        :param invalids: List of text identifiers
        :type invalids: [CtsTextMetadata]
        """
        pass

    def parse(self, resource):
        """ Parse a list of directories and reads it into a collection

        :param resource: List of folders
        :return: An inventory resource and a list of CtsTextMetadata metadata-objects
        """
        textgroups = []
        texts = []
        invalids = []

        for folder in resource:
            cts_files = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for cts_file in cts_files:
                textgroup, cts_file = self._parse_textgroup_wrapper(cts_file)
                textgroups.append((textgroup, cts_file))

        for textgroup, cts_textgroup_file in textgroups:
            cts_work_files = glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(cts_textgroup_file)))

            for cts_work_file in cts_work_files:
                _, parsed_texts, directory = self._parse_work_wrapper(cts_work_file, textgroup)
                texts.extend([(text, directory) for text in parsed_texts])

        for text, directory in texts:
            # If text_id is not none, the text parsing errored
            if not self._parse_text(text, directory):
                invalids.append(text)

        # Dispatching routine
        for textgroup, textgroup_path in textgroups:
            self._dispatch_container(textgroup, textgroup_path)

        # Clean invalids if there was a need
        self._clean_invalids(invalids)

        self.inventory = self.dispatcher.collection
        return self.inventory

    def __getText__(self, urn):
        """ Returns a CtsTextMetadata object
        :param urn: URN of a text to retrieve
        :type urn: str, URN
        :return: Textual resource and metadata
        :rtype: (CapitainsCtsText, InventoryText)
        """
        if not isinstance(urn, URN):
            urn = URN(urn)
        if len(urn) != 5:
            if len(urn) == 4:
                urn, reference = urn.upTo(URN.WORK), str(urn.reference)
                urn = [
                    t.id
                    for t in self.texts
                    if t.id.startswith(str(urn)) and isinstance(t, CtsEditionMetadata)
                ]
                if len(urn) > 0:
                    urn = URN(urn[0])
                else:
                    raise UnknownObjectError
            else:
                raise InvalidURN

        text = self.inventory[str(urn)]

        if os.path.isfile(text.path):
            with io.open(text.path) as __xml__:
                resource = self.classes["text"](urn=urn, resource=self.xmlparse(__xml__))
        else:
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
        __PART = None
        if urn is not None:
            if isinstance(urn, URN):
                _urn = urn
            else:
                _urn = URN(urn)
            __PART = [None, None, URN.NAMESPACE, URN.TEXTGROUP, URN.WORK, URN.VERSION, URN.COMPLETE][len(_urn)]

        matches = [
            text
            for text in self.texts
            if
            (lang is None or (lang is not None and lang == text.lang)) and
            (urn is None or (urn is not None and text.urn.upTo(__PART) == urn)) and
            (text.citation is not None) and
            (
                category not in ["edition", "translation", "commentary"] or
                (category in ["edition", "translation", "commentary"] and category.lower() == text.subtype.lower())
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
        page = page or CtsCapitainsLocalResolver.DEFAULT_PAGE
        limit = limit or CtsCapitainsLocalResolver.PER_PAGE[1]

        if limit < CtsCapitainsLocalResolver.PER_PAGE[0] or limit > CtsCapitainsLocalResolver.PER_PAGE[2]:
            limit = CtsCapitainsLocalResolver.PER_PAGE[1]

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
        inv_names = [text.parent.parent.parent.id for text in texts]
        if len(set(inv_names)) == 1:
            inventory = self.classes["inventory"](name=inv_names[0])
        else:
            inventory = self.classes["inventory"]()

        # For each text we found using the filter
        for text in texts:
            tg_urn = str(text.parent.parent.urn)
            wk_urn = str(text.parent.urn)
            txt_urn = str(text.urn)
            # If we need to generate a textgroup object
            if tg_urn not in inventory.textgroups:
                self.classes["textgroup"](urn=tg_urn, parent=inventory)
            # If we need to generate a work object
            if wk_urn not in inventory.textgroups[tg_urn].works:
                self.classes["work"](urn=wk_urn, parent=inventory.textgroups[tg_urn])

            if isinstance(text, CtsEditionMetadata):
                x = self.classes["edition"](urn=txt_urn, parent=inventory.textgroups[tg_urn].works[wk_urn])
                x.citation = text.citation
            elif isinstance(text, CtsTranslationMetadata):
                x = self.classes["translation"](urn=txt_urn, parent=inventory.textgroups[tg_urn].works[wk_urn], lang=text.lang)
                x.citation = text.citation
            elif isinstance(text, CtsCommentaryMetadata):
                x = self.classes["commentary"](urn=txt_urn, parent=inventory.textgroups[tg_urn].works[wk_urn], lang=text.lang)
                x.citation = text.citation

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
            passage.set_metadata_from_collection(text_metadata)
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
