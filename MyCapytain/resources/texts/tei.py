# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI Citation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""

import MyCapytain.common.reference
from lxml.etree import _Element
from builtins import range, object


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

        child = ""
        if isinstance(self.child, Citation):
            child=str(self.child)

        label = ""
        if self.name is not None:
            label = self.name

        return "<tei:cRefPattern n=\"{label}\" matchPattern=\"{regexp}\" replacementPattern=\"#xpath({refsDecl})\"><tei:p>This pointer pattern extracts {label}</tei:p></tei:cRefPattern>".format(
            refsDecl=self.refsDecl,
            label=label,
            regexp="\.".join(["(\w+)" for i in range(0, self.refsDecl.count("$"))])
        )

    def ingest(self, resource):
        """ Ingest a resource and store data in its instance

        :param resource: XML node cRefPattern or list of them in ASC hierarchy order (deepest to highest, eg. lines to poem to book)
        :type resource: lxml.etre._Element
        """
        resources = []
        if isinstance(resource, _Element):
            resource = [resource]

        for x in range(0,len(resource)):
            resources.append(
                self.__class__(
                    name=resource[x].get("n"),
                    refsDecl=resource[x].get("replacementPattern")[7:-1],
                    child=childOrNone(resources)
                )
            )
        self.name = resources[-1].name
        self.refsDecl = resources[-1].refsDecl
        self.child = resources[-1].child



