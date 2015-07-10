# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml

Shared elements for TEI Citation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>
"""

import MyCapytain.common.reference

class Citation(MyCapytain.common.reference.Citation):
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
            regexp="\.".join(["(\\w+)" for dollar in self.refsDecl.find("$")])
        )