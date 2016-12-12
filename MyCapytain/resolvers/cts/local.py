"""

"""
import io

from MyCapytain.common.utils import xmlparser
from MyCapytain.resources.collections.cts import TextInventory, TextGroup, Work, Citation
from MyCapytain.resources.texts.locals.tei import Text
from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.errors import InvalidURN
from MyCapytain.common.reference import URN
from glob import glob
import os.path
from math import ceil
import logging


class CTSCapitainsLocalResolver(Resolver):
    """ XML Folder Based resolver.

    :param resource: Resource should be a list of folders retaining data as Capitains Guidelines Repositories
    :type resource: [str]
    :param name: Key used to differentiate Repository and thus enabling different repo to be used
    :type name: str
    :param logger: Logging object
    :type logger: logging

    :cvar TEXT_CLASS: Text Class [not instantiated] to be used to parse Texts. Can be changed to support Cache for example
    :type TEXT_CLASS: class
    :cvar DEFAULT_PAGE: Default Page to show
    :cvar PER_PAGE: Tuple representing the minimal number of texts returned, the default number and the maximum number of texts returned


    """
    TEXT_CLASS = Text
    DEFAULT_PAGE = 1
    PER_PAGE = (1, 10, 100) # Min, Default, Mainvex,

    @property
    def inventory(self):
        return self.__inventory__

    @property
    def texts(self):
        return self.__texts__

    def __init__(self, resource, name=None, logger=None):
        """ Initiate the XMLResolver
        """
        self.__inventory__ = TextInventory()
        self.__texts__ = []
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
        """ Parse a list of directories ans
        :param resource: List of folders
        :param cache: Auto cache the results
        :return: An inventory resource and a list of Text metadata-objects
        """
        for folder in resource:
            textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=folder))
            for __cts__ in textgroups:
                try:
                    with io.open(__cts__) as __xml__:
                        textgroup = TextGroup(
                            resource=__xml__
                        )
                        str_urn = str(textgroup.urn)
                    if str_urn in self.inventory.textgroups:
                        self.inventory.textgroups[str_urn].update(textgroup)
                    else:
                        self.inventory.textgroups[str_urn] = textgroup

                    for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                        with io.open(__subcts__) as __xml__:
                            work = Work(
                                resource=__xml__,
                                parents=[self.inventory.textgroups[str_urn]]
                            )
                            work_urn = str(work.urn)
                            if work_urn in self.inventory.textgroups[str_urn].works:
                                self.inventory.textgroups[str_urn].works[work_urn].update(work)
                            else:
                                self.inventory.textgroups[str_urn].works[work_urn] = work

                        for __textkey__ in work.texts:
                            __text__ = self.inventory.textgroups[str_urn].works[work_urn].texts[__textkey__]
                            __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                                directory=os.path.dirname(__subcts__),
                                textgroup=__text__.urn.textgroup,
                                work=__text__.urn.work,
                                version=__text__.urn.version
                            )
                            if os.path.isfile(__text__.path):
                                try:
                                    with io.open(__text__.path) as f:
                                        t = Text(resource=self.xmlparse(f))
                                        cites = list()
                                        for cite in [c for c in t.citation][::-1]:
                                            if len(cites) >= 1:
                                                cites.append(Citation(
                                                    xpath=cite.xpath.replace("'", '"'),
                                                    scope=cite.scope.replace("'", '"'),
                                                    name=cite.name,
                                                    child=cites[-1]
                                                ))
                                            else:
                                                cites.append(Citation(
                                                    xpath=cite.xpath.replace("'", '"'),
                                                    scope=cite.scope.replace("'", '"'),
                                                    name=cite.name
                                                ))
                                    __text__.citation = cites[-1]
                                    self.logger.info("%s has been parsed ", __text__.path)
                                    if __text__.citation:
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
                except Exception as E:
                    self.logger.error("Error parsing %s ", __cts__)

        return self.inventory, self.texts

    def __getText__(self, urn):
        """ Returns a Text object
        :param urn: URN of a text to retrieve
        :type urn: str, URN
        :return: Textual resource and metadata
        :rtype: (text.Text, inventory.Text)
        """
        if not isinstance(urn, URN):
            urn = URN(urn)
        if len(urn) != 5:
            raise InvalidURN

        text = self.inventory[str(urn)]
        with io.open(text.path) as __xml__:
            resource = self.TEXT_CLASS(urn=urn, resource=self.xmlparse(__xml__))

        return resource, text

    def __getCapabilities__(self,
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
        :rtype: ([Text], int, int)
        """
        __PART = None
        if urn is not None:
            _urn = URN(urn)
            __PART = [None, None, URN.NAMESPACE, URN.TEXTGROUP, URN.WORK, URN.VERSION, URN.COMPLETE][len(_urn)]

        matches = [
            text
            for text in self.__texts__
            if (lang is None or (lang is not None and lang == text.lang)) and
            (urn is None or (urn is not None and text.urn.upTo(__PART) == urn)) and
            (text.citation is not None) and
            (category not in ["edition", "translation"] or (category in ["edition", "translation"] and category.lower() == text.subtype.lower()))
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
        page = page or CTSCapitainsLocalResolver.DEFAULT_PAGE
        limit = limit or CTSCapitainsLocalResolver.PER_PAGE[1]

        if limit < CTSCapitainsLocalResolver.PER_PAGE[0] or limit > CTSCapitainsLocalResolver.PER_PAGE[2]:
            limit = CTSCapitainsLocalResolver.PER_PAGE[1]

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
        return self.__getCapabilities__(urn=objectId)[0]

    def getPassage(self, textId, subreference=None, prevnext=False, metadata=False):
        return self.__getText__(textId).getPassage(Reference(subreference))

