# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI Citation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""

from MyCapytain.common.utils import NS, Mimetypes, normalize, xmlparser, \
    nested_set, nested_ordered_dictionary
from MyCapytain.resources.prototypes.text import InteractiveTextualNode

from lxml.etree import tostring
from six import text_type as str


class TEIResource(InteractiveTextualNode):
    """ TEI Resource

    """
    def __init__(self, resource, **kwargs):
        super(TEIResource, self).__init__(**kwargs)
        self.resource = xmlparser(resource)

    def __str__(self):
        """ Text based representation of the passage
    
        :rtype: basestring
        :returns: XML of the passage in string form 
        """
        return self.export(output=Mimetypes.XML.Std)

    def export(self, output=Mimetypes.PLAINTEXT, exclude=None, _preformatted=False):
        """ Text content of the passage

        :param output: Mimetype (From MyCapytian.common.utils.Mimetypes) to output
        :type output: str
        :param exclude: Remove some nodes from text
        :type exclude: list
        :param _preformatted: This parameter is used when export loops on itself
        :type _preformatted: booln
        :rtype: basestring
        :returns: Text of the xml node

        :Example:
            >>>    P = Passage(resource='<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')
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
            """ Exports the whole resource as a LXML object
            """
            return self.resource

        elif output == Mimetypes.XML.Std:
            """ Exports the whole resource formatted as XML but as string object
            """
            return tostring(self.resource, encoding=str)

        elif output == Mimetypes.PYTHON.NestedDict:
            """ Exports the whole resource into a NestedDict
            """
            reffs = self.getReffs(level=len(self.citation))
            text = nested_ordered_dictionary()
            for reff in reffs:
                _r = reff.split(".")
                nested_set(text, _r, self.getPassage(_r, simple=True).export(
                    Mimetypes.PLAINTEXT,
                    exclude=exclude,
                    _preformatted=True
                ))
            return text

        elif output == Mimetypes.PLAINTEXT:
            return normalize(
                " ".join(
                    [
                        element
                        for element
                        in self.resource.xpath(
                            ".//descendant-or-self::text(){}".format(exclude),
                            namespaces=NS,
                            smart_strings=False
                        )
                    ]
                )
            )

    @property
    def xml(self):
        """ XML Representation of the Passage

        :rtype: lxml.etree._Element
        :returns: XML element representing the passage
        """
        return self.resource