# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI XmlCtsCitation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""
from lxml.etree import tostring

from MyCapytain.common.constants import Mimetypes, XPATH_NAMESPACES
from MyCapytain.common.utils import xmlparser, nested_ordered_dictionary, nested_set, normalize
from MyCapytain.resources.prototypes.text import InteractiveTextualNode


class TEIResource(InteractiveTextualNode):
    """ TEI Encoded Resource

    :param resource: XML Resource that needs to be parsed into a CapitainsCtsPassage/CtsTextMetadata
    :type resource: Union[str,_Element]
    :cvar EXPORT_TO: List of exportable supported formats
    :cvar DEFAULT_EXPORT: Default export (Plain/CtsTextMetadata)
    """
    EXPORT_TO = [
        Mimetypes.PYTHON.ETREE, Mimetypes.XML.Std,
        Mimetypes.PYTHON.NestedDict, Mimetypes.PLAINTEXT, Mimetypes.XML.TEI
    ]
    DEFAULT_EXPORT = Mimetypes.PLAINTEXT
    PLAINTEXT_STRING_JOIN = " "

    def __init__(self, resource, **kwargs):
        super(TEIResource, self).__init__(**kwargs)
        self.resource = xmlparser(resource)
        self.__plaintext_string_join__ = ""+self.PLAINTEXT_STRING_JOIN

    @property
    def plaintext_string_join(self):
        """ String used to join xml node's texts in export
        """
        return self.__plaintext_string_join__

    @plaintext_string_join.setter
    def plaintext_string_join(self, value):
        """ Set the value for string join

        :param value: Default string value to use for join at export for plaintext
        :type value: str
        :return:
        """
        self.__plaintext_string_join__ = value

    def __str__(self):
        """ CtsTextMetadata based representation of the passage

        :rtype: basestring
        :returns: XML of the passage in string form
        """
        return self.export(output=Mimetypes.XML.Std)

    def __export__(self, output=Mimetypes.PLAINTEXT, exclude=None, _preformatted=False):
        """ CtsTextMetadata content of the passage

        :param output: Mimetype (From MyCapytian.common.utils.Mimetypes) to output
        :type output: str
        :param exclude: Remove some nodes from text
        :type exclude: list
        :param _preformatted: This parameter is used when export loops on itself
        :type _preformatted: boolean
        :rtype: basestring
        :returns: CtsTextMetadata of the xml node

        :Example:
            >>>    P = CapitainsCtsPassage(resource='<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')
            >>>    P.export(output=Mimetypes.PLAINTEXT) == "Ibis hello b ab excusso missus in astra sago. "
            >>>    P.export(output=Mimetypes.PLAINTEXT, exclude=[]) == "Ibis hello b ab excusso missus in astra sago. "


        """
        if exclude is None:
            exclude = self.default_exclude

        if len(exclude) > 0 and _preformatted is False:
            exclude = "[{0}]".format(
                " and ".join(
                    "not(./ancestor-or-self::{0})".format(excluded)
                    for excluded in exclude
                )
            )
        elif _preformatted is False:
            exclude = ""

        if output == Mimetypes.PYTHON.ETREE:
            # Exports the whole resource as a LXML object
            return self.resource

        elif output == Mimetypes.XML.Std or output == Mimetypes.XML.TEI:
            # Exports the whole resource formatted as XML but as string object
            return tostring(self.resource, encoding=str)

        elif output == Mimetypes.PYTHON.NestedDict:
            # Exports the whole resource into a NestedDict
            reffs = self.getReffs(level=len(self.citation))
            text = nested_ordered_dictionary()
            for reff in reffs:
                _r = reff.split(".")
                nested_set(text, _r, self.getTextualNode(_r).export(
                    Mimetypes.PLAINTEXT,
                    exclude=exclude,
                    _preformatted=True
                ))
            return text

        elif output == Mimetypes.PLAINTEXT:
            # Exports to string
            return normalize(
                self.plaintext_string_join.join(
                    [
                        element
                        for element
                        in self.resource.xpath(
                            ".//descendant-or-self::text(){}".format(exclude),
                            namespaces=XPATH_NAMESPACES,
                            smart_strings=False
                        )
                    ]
                )
            )

    @property
    def xml(self):
        """ XML Representation of the CapitainsCtsPassage

        :rtype: lxml.etree._Element
        :returns: XML element representing the passage
        """
        return self.resource