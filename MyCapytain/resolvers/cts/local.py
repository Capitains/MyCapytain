"""

"""
import io
import logging
import os.path
from glob import glob
from math import ceil

from MyCapytain.common.reference import URN, Reference
from MyCapytain.common.utils import xmlparser
from MyCapytain.errors import InvalidURN, UnknownObjectError, UndispatchedTextError
from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.resolvers.utils import CollectionDispatcher
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata, XmlCtsTextgroupMetadata, XmlCtsWorkMetadata, XmlCtsCitation, XmlCtsTextMetadata as InventoryText, \
    XmlCtsTranslationMetadata, XmlCtsEditionMetadata, XmlCtsCommentaryMetadata
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText


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
    TEXT_CLASS = CapitainsCtsText
    DEFAULT_PAGE = 1
    PER_PAGE = (1, 10, 100)  # Min, Default, Mainvex,
    RAISE_ON_UNDISPATCHED = False

    @property
    def inventory(self):
        return self.__inventory__

    @property
    def texts(self):
        return self.inventory.readableDescendants

    def __init__(self, resource, name=None, logger=None, dispatcher=None):
        """ Initiate the XMLResolver
        """
        if dispatcher is None:
            inventory_collection = CtsTextInventoryCollection(identifier="defaultTic")
            ti = XmlCtsTextInventoryMetadata("default")
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

        self.TEXT_CLASS = type(self).TEXT_CLASS
        self.works = []

        self.parse(resource)

    def xmlparse(self, file):
        """ Parse a XML file
        :param file: Opened File
        :return: Tree
        """
        return xmlparser(file)

    def parse(self, resource):
        """ Parse a list of directories and reades it into a collection

        :param resource: List of folders
        :return: An inventory resource and a list of CtsTextMetadata metadata-objects
        """
        for folder in resource:
            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                try:
                    with io.open(__cts__) as __xml__:
                        textgroup = XmlCtsTextgroupMetadata.parse(
                            resource=__xml__
                        )
                        tg_urn = str(textgroup.urn)
                    if tg_urn in self.inventory:
                        self.inventory[tg_urn].update(textgroup)
                    else:
                        self.dispatcher.dispatch(textgroup, path=__cts__)

                    for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                        with io.open(__subcts__) as __xml__:
                            work = XmlCtsWorkMetadata.parse(
                                resource=__xml__,
                                parent=self.inventory[tg_urn]
                            )
                            work_urn = str(work.urn)
                            if work_urn in self.inventory[tg_urn].works:
                                self.inventory[work_urn].update(work)

                        for __textkey__ in work.texts:
                            __text__ = self.inventory[__textkey__]
                            __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                                directory=os.path.dirname(__subcts__),
                                textgroup=__text__.urn.textgroup,
                                work=__text__.urn.work,
                                version=__text__.urn.version
                            )
                            if os.path.isfile(__text__.path):
                                try:
                                    with io.open(__text__.path) as f:
                                        t = CapitainsCtsText(resource=self.xmlparse(f))
                                        cites = list()
                                        for cite in [c for c in t.citation][::-1]:
                                            if len(cites) >= 1:
                                                cites.append(XmlCtsCitation(
                                                    xpath=cite.xpath.replace("'", '"'),
                                                    scope=cite.scope.replace("'", '"'),
                                                    name=cite.name,
                                                    child=cites[-1]
                                                ))
                                            else:
                                                cites.append(XmlCtsCitation(
                                                    xpath=cite.xpath.replace("'", '"'),
                                                    scope=cite.scope.replace("'", '"'),
                                                    name=cite.name
                                                ))
                                        del t
                                    __text__.citation = cites[-1]
                                    self.logger.info("%s has been parsed ", __text__.path)
                                    if __text__.citation.isEmpty() is False:
                                        self.texts.append(__text__)
                                    else:
                                        self.logger.error("%s has no passages", __text__.path)
                                except Exception:
                                    self.logger.error(
                                        "%s does not accept parsing at some level (most probably citation) ",
                                        __text__.path
                                    )
                            else:
                                self.logger.error("%s is not present", __text__.path)
                except UndispatchedTextError as E:
                    self.logger.error("Error dispatching %s ", __cts__)
                    if self.RAISE_ON_UNDISPATCHED is True:
                        raise E
                except Exception as E:
                    self.logger.error("Error parsing %s ", __cts__)

        return self.inventory, self.texts

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
                    if t.id.startswith(str(urn)) and isinstance(t, XmlCtsEditionMetadata)
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
                resource = self.TEXT_CLASS(urn=urn, resource=self.xmlparse(__xml__))
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
            inventory = XmlCtsTextInventoryMetadata(name=inv_names[0])
        else:
            inventory = XmlCtsTextInventoryMetadata()
        # For each text we found using the filter
        for text in texts:
            tg_urn = str(text.parent.parent.urn)
            wk_urn = str(text.parent.urn)
            txt_urn = str(text.urn)
            # If we need to generate a textgroup object
            if tg_urn not in inventory.textgroups:
                XmlCtsTextgroupMetadata(urn=tg_urn, parent=inventory)
            # If we need to generate a work object
            if wk_urn not in inventory.textgroups[tg_urn].works:
                XmlCtsWorkMetadata(urn=wk_urn, parent=inventory.textgroups[tg_urn])

            if isinstance(text, XmlCtsEditionMetadata):
                x = XmlCtsEditionMetadata(urn=txt_urn, parent=inventory.textgroups[tg_urn].works[wk_urn])
                x.citation = text.citation
            elif isinstance(text, XmlCtsTranslationMetadata):
                x = XmlCtsTranslationMetadata(urn=txt_urn, parent=inventory.textgroups[tg_urn].works[wk_urn], lang=text.lang)
                x.citation = text.citation
            elif isinstance(text, XmlCtsCommentaryMetadata):
                x = XmlCtsCommentaryMetadata(urn=txt_urn, parent=inventory.textgroups[tg_urn].works[wk_urn], lang=text.lang)
                x.citation = text.citation

        return inventory[objectId]

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :param prevnext: Retrieve graph representing previous and next passage
        :type prevnext: boolean
        :param metadata: Retrieve metadata about the passage and the text
        :type metadata: boolean
        :return: CapitainsCtsPassage
        :rtype: CapitainsCtsPassage
        """
        text, text_metadata = self.__getText__(textId)
        if subreference is not None:
            subreference = Reference(subreference)
        passage = text.getTextualNode(subreference)
        if metadata:
            passage.set_metadata_from_collection(text_metadata)
        return passage

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :return: Tuple of references
        :rtype: (str, str)
        """
        text, inventory = self.__getText__(textId)
        passage = text.getTextualNode(Reference(subreference))
        return passage.siblingsId

    def getReffs(self, textId, level=1, subreference=None):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param level: Depth for retrieval
        :type level: int
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :return: List of references
        :rtype: [str]
        """
        passage, inventory = self.__getText__(textId)
        if subreference:
            passage = passage.getTextualNode(subreference)
        return passage.getReffs(level=level, subreference=subreference)
