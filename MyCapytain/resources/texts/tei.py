# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI Citation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""

import MyCapytain.common.reference
import MyCapytain.common.utils
import MyCapytain.resources.prototypes.text

from lxml.etree import tostring
from six import text_type as str


class Passage(MyCapytain.resources.prototypes.text.Passage):
    def __str__(self):
        """ Text based representation of the passage
    
        :rtype: basestring
        :returns: XML of the passage in string form 
        """
        return tostring(self.resource, encoding=str)

    def text(self, exclude=None):
        """ Text content of the passage

        :param exclude: Remove some nodes from text
        :type exclude: List
        :rtype: basestring
        :returns: Text of the xml node
        :Example:
            >>>    P = Passage(resource='<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')
            >>>    P.text == "Ibis hello b ab excusso missus in astra sago. "
            >>>    P.text(exclude=["note"]) == "Ibis hello b ab excusso missus in astra sago. "


        """

        if exclude is None:
            exclude = ""
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
                        namespaces=MyCapytain.common.utils.NS,
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
