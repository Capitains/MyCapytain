# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI Citation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""

import MyCapytain.common.reference
from MyCapytain.common.utils import NS, Mimetypes, normalize
import MyCapytain.resources.prototypes.text

from lxml.etree import tostring
from six import text_type as str


class Passage(MyCapytain.resources.prototypes.text.Passage):
    def __str__(self):
        """ Text based representation of the passage
    
        :rtype: basestring
        :returns: XML of the passage in string form 
        """
        return self.export(output=Mimetypes.XML)

    def export(self, output=Mimetypes.PLAINTEXT, exclude=None):
        """ Text content of the passage

        :param output: Mimetype (From MyCapytian.common.utils.Mimetypes) to output
        :type output: str
        :param exclude: Remove some nodes from text
        :type exclude: List
        :rtype: basestring
        :returns: Text of the xml node

        :Example:
            >>>    P = Passage(resource='<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')
            >>>    P.export(output=Mimetypes.PLAINTEXT) == "Ibis hello b ab excusso missus in astra sago. "
            >>>    P.export(output=Mimetypes.PLAINTEXT, exclude=[]) == "Ibis hello b ab excusso missus in astra sago. "


        """
        if output == Mimetypes.ETREE:
            return self.resource
        elif output == Mimetypes.XML:
            return tostring(self.resource, encoding=str)
        elif output == Mimetypes.PLAINTEXT:
            if exclude is None:
                exclude = self.default_exclude
            else:
                exclude = "[{0}]".format(
                    " and ".join(
                        "not(./ancestor-or-self::{0})".format(excluded)
                        for excluded in exclude
                    )
                )

            return MyCapytain.common.utils.normalize(
                " ".join(
                    [
                        element
                        for element
                        in self.resource.xpath(
                        ".//descendant-or-self::text()" + exclude,
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