# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI Citation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""

import MyCapytain.common.reference
import MyCapytain.common.utils
import MyCapytain.resources.proto.text

from lxml.etree import _Element, tostring
from builtins import range, object
from six import text_type as str


def childOrNone(liste):
    if len(liste) > 0:
        return liste[-1]
    else:
        return None


class Citation(MyCapytain.common.reference.Citation):
    """ Implementation of Citation for TEI markup

    .. automethod:: __str__
    
    """
    def __str__(self):
        """ Returns a string refsDecl version of the object 

        :Example:
            >>>    a = Citation(name="book", xpath="/tei:TEI/tei:body/tei:text/tei:div", scope="/tei:div[@n=\"1\"]")
            >>>    str(a) == \"\"\"<tei:refsDecl n='book' xpath='/tei:TEI/tei:body/tei:text/tei:div' scope='/tei:div[@n=\"1\"]'>
            >>>         <tei:p>This Citation extracts Book from the text</tei:p>
            >>>    </tei:refsDecl>\"\"\"
        """
        if self.refsDecl is None:
            return ""

        label = ""
        if self.name is not None:
            label = self.name

        return "<tei:cRefPattern n=\"{label}\" matchPattern=\"{regexp}\" replacementPattern=\"#xpath({refsDecl})\">" \
               "<tei:p>This pointer pattern extracts {label}</tei:p></tei:cRefPattern>".format(
                   refsDecl=self.refsDecl,
                   label=label,
                   regexp="\.".join(["(\w+)" for i in range(0, self.refsDecl.count("$"))])
               )

    @staticmethod
    def ingest(resource, xpath=".//tei:cRefPattern"):
        """ Ingest a resource and store data in its instance

        :param resource: XML node cRefPattern or list of them in ASC hierarchy order (deepest to highest, eg. lines to poem to book)
        :type resource: lxml.etree._Element
        :param xpath: XPath to use to retrieve citation
        :type xpath: str

        :returns: A citation object
        :rtype: Citation
        """
        if len(resource) == 0 and isinstance(resource, list):
            return None
        elif isinstance(resource, list):
            resource = resource[0]
        elif not isinstance(resource, _Element):
            return None

        resource = resource.xpath(xpath, namespaces=MyCapytain.common.utils.NS)
        resources = []

        for x in range(0, len(resource)):
            resources.append(
                Citation(
                    name=resource[x].get("n"),
                    refsDecl=resource[x].get("replacementPattern")[7:-1],
                    child=childOrNone(resources)
                )
            )

        return resources[-1]


class Passage(MyCapytain.resources.proto.text.Passage):
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
                        namespaces=MyCapytain.common.utils.NS
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
