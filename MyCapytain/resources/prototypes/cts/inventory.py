# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.cts.inventory
   :synopsis: Prototypes for repository/inventory Collection CTS objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""
from __future__ import unicode_literals
from six import text_type

from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import make_xml_node
from MyCapytain.common.constants import NAMESPACES, Mimetypes
from MyCapytain.errors import InvalidURN
from collections import defaultdict
from copy import deepcopy

from rdflib import RDF, Literal, URIRef
from rdflib.collection import Collection as RDFLibCollection
from rdflib.namespace import DC


class PrototypeCTSCollection(Collection):
    """ Resource represents any resource from the inventory

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :cvar CTSMODEL: String Representation of the type of collection
    """
    CTSMODEL = "CTSCollection"
    DC_TITLE_KEY = None
    CTS_PROPERTIES = []

    def __init__(self, identifier="", resource=None):
        super(PrototypeCTSCollection, self).__init__(identifier)

        if hasattr(type(self), "CTSMODEL"):
            self.graph.set((self.asNode(), RDF.type, NAMESPACES.CTS.term(self.CTSMODEL)))
            self.graph.set((self.asNode(), NAMESPACES.CTS.isA, NAMESPACES.CTS.term(self.CTSMODEL)))

        self.resource = None
        self.__urn__ = ""
        if resource is not None:
            self.setResource(resource)

    @property
    def urn(self):
        return self.__urn__

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        elif self.resource is None:
            # Not totally true
            return hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn
        return hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn and self.resource == other.resource

    def setResource(self, resource):
        """ Set the object property resource

        :param resource: Resource representing the PrototypeTextInventory
        :type resource: Any
        :rtype: Any
        :returns: Input resource
        """
        self.resource = resource
        self.parse(resource)
        return self.resource

    def parse(self, resource):
        """ Parse the object resource

        :param resource: Resource representing the PrototypeTextInventory
        :type resource: Any
        :rtype: List
        """
        raise NotImplementedError()

    def set_cts_property(self, property, value, lang=None):
        if not isinstance(value, Literal):
            value = Literal(value, lang=lang)
        property = NAMESPACES.CTS.term(property)

        if property == self.DC_TITLE_KEY:
            self.set_label(value, lang)

        self.graph.add(
            (self.metadata, property, value)
        )

    def __namespaces_header__(self):
        nm = self.graph.namespace_manager
        bindings = {}
        for predicate in set(self.graph.predicates()):
            prefix, namespace, name = nm.compute_qname(predicate)
            if prefix != "":
                bindings["xmlns:" + prefix] = str(URIRef(namespace))
            else:
                bindings["xmlns"] = str(URIRef(namespace))

        return bindings

    def __xml_export_generic__(self, attrs, namespaces=False, lines="\n"):
        if namespaces is True:
            attrs.update(self.__namespaces_header__())

        strings = [make_xml_node(self.graph, self.TYPE_URI, close=False, attributes=attrs)]

        #additional = [make_xml_node(self.graph, NAMESPACES.CTS.extra)]
        for pred in self.CTS_PROPERTIES:
            for obj in self.graph.objects(self.metadata, pred):
                strings.append(
                    make_xml_node(
                        self.graph, pred, attributes={"xml:lang": obj.language}, text=str(obj), complete=True
                    )
                )

        #c = RDFLibCollection(self.graph, self.asNode())
        #additional.append(c.graph.serialize(format="xml").decode())
        #additional.append(make_xml_node(self.graph, NAMESPACES.CTS.extra, close=True))
        #strings = strings + additional

        for object in self.members:
            strings.append(object.export(Mimetypes.XML.CTS, namespaces=False))

        strings.append(make_xml_node(self.graph, self.TYPE_URI, close=True))

        return lines.join(strings)


class PrototypeText(PrototypeCTSCollection):
    """ Represents a CTS PrototypeText

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :param urn: Identifier of the PrototypeText
    :type urn: str
    :param parents: Item parents of the current collection
    :type parents: [PrototypeCTSCollection]
    :param subtype: Subtype of the object (Edition, Translation)
    :type subtype: str

    :ivar urn: URN Identifier
    :type urn: URN
    :ivar parents: List of ancestors, from parent to furthest
    """

    DC_TITLE_KEY = NAMESPACES.CTS.term("label")
    EXPORT_TO = [Mimetypes.XML.CTS]
    CTS_PROPERTIES = [NAMESPACES.CTS.label, NAMESPACES.CTS.description]

    def __init__(self, urn="", resource=None, parents=None, subtype="Edition"):
        self.subtype = subtype
        super(PrototypeText, self).__init__(identifier=str(urn))
        self.resource = None
        self.citation = None
        self.__urn__ = URN(urn)
        self.docname = None
        self.parents = list()
        self.validate = None

        if parents is not None:
            self.parents = parents
            self.lang = self.parents[0].lang

        if resource is not None:
            self.setResource(resource)

    @property
    def lang(self):
        return str(self.graph.value(self.asNode(), DC.language))

    @lang.setter
    def lang(self, lang):
        self.graph.set((self.asNode(), DC.language, Literal(lang)))

    @property
    def readable(self):
        return True

    @property
    def members(self):
        return []

    @property
    def descendants(self):
        return []

    def translations(self, key=None):
        """ Get translations in given language

        :param key: Language ISO Code to filter on
        :return:
        """
        return self.parents[0].getLang(key)

    def editions(self):
        """ Get all editions of the texts

        :return: List of editions
        :rtype: [PrototypeText]
        """
        return [
                self.parents[0].texts[urn]
                for urn in self.parents[0].texts
                if self.parents[0].texts[urn].subtype == "Edition"
            ]

    def __export__(self, output=None, domain="", namespaces=True, lines="\n"):
        """ Create a {output} version of the Text

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS:
            attrs = {"urn": self.id}
            if namespaces is True:
                attrs.update(self.__namespaces_header__())

            strings = [make_xml_node(self.graph, self.TYPE_URI, close=False, attributes=attrs)]

            # additional = [make_xml_node(self.graph, NAMESPACES.CTS.extra)]
            for pred in self.CTS_PROPERTIES:
                for obj in self.graph.objects(self.metadata, pred):
                    strings.append(
                        make_xml_node(
                            self.graph, pred, attributes={"xml:lang": obj.language}, text=str(obj), complete=True
                        )
                    )

            # Citation !
            strings.append(
                # Online
                make_xml_node(
                    self.graph, NAMESPACES.CTS.term("online"), complete=True,
                    # Citation Mapping
                    innerXML=make_xml_node(
                        self.graph, NAMESPACES.CTS.term("citationMapping"), complete=True,
                        innerXML=self.citation.export(Mimetypes.XML.CTS)
                    )
                )
            )
            strings.append(make_xml_node(self.graph, self.TYPE_URI, close=True))

            return lines.join(strings)


class PrototypeEdition(PrototypeText):
    """ Represents a CTS Edition

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :param urn: Identifier of the PrototypeText
    :type urn: str
    :param parents: Item parents of the current collection
    :type parents: [PrototypeCTSCollection]
    """
    TYPE_URI = NAMESPACES.CTS.term("edition")

    def __init__(self, urn=None, resource=None, parents=None):
        super(PrototypeEdition, self).__init__(urn=urn, resource=resource, parents=parents, subtype="Edition")


class PrototypeTranslation(PrototypeText):
    """ Represents a CTS Translation

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :param urn: Identifier of the PrototypeText
    :type urn: str
    :param parents: Item parents of the current collection
    :type parents: [PrototypeCTSCollection]
    """
    TYPE_URI = NAMESPACES.CTS.term("translation")

    def __init__(self, urn=None, resource=None, parents=None):
        super(PrototypeTranslation, self).__init__(urn=urn, resource=resource, parents=parents, subtype="Translation")


class PrototypeWork(PrototypeCTSCollection):
    """ Represents a CTS PrototypeWork

    CTS PrototypeWork can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :param urn: Identifier of the PrototypeWork
    :type urn: str
    :param parents: List of parents for current object
    :type parents: Tuple.<PrototypeTextInventory>

    :ivar urn: URN Identifier
    :type urn: URN
    :ivar parents: List of ancestors, from parent to furthest
    """

    DC_TITLE_KEY = NAMESPACES.CTS.term("title")
    TYPE_URI = NAMESPACES.CTS.term("work")
    EXPORT_TO = [Mimetypes.XML.CTS]
    CTS_PROPERTIES = [NAMESPACES.CTS.term("title")]

    def __init__(self, resource=None, urn=None, parents=None):
        super(PrototypeWork, self).__init__(identifier=str(urn))
        self.__urn__ = URN(urn)
        self.texts = defaultdict(PrototypeText)
        self.parents = list()

        if parents is not None:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    @property
    def lang(self):
        return [str(x) for x in self.graph.objects(self.asNode(), DC.language)]

    @lang.setter
    def lang(self, lang):
        self.graph.add((self.asNode(), DC.language, Literal(lang)))

    def update(self, other):
        """ Merge two Work Objects.

        - Original (left Object) keeps his parent.
        - Added document overwrite text if it already exists

        :param other: Work object
        :type other: PrototypeWork
        :return: Work Object
        :rtype Work:
        """
        if not isinstance(other, PrototypeWork):
            raise TypeError("Cannot add %s to PrototypeWork" % type(other))
        elif self.urn != other.urn:
            raise InvalidURN("Cannot add PrototypeWork %s to PrototypeWork %s " % (self.urn, other.urn))

        parents = [self] + self.parents
        for urn, text in other.texts.items():
            self.texts[urn] = deepcopy(text)
            self.texts[urn].parents = parents
            self.texts[urn].resource = None

        return self

    def getLang(self, key=None):
        """ Find a translation with given language

        :param key: Language to find
        :type key: text_type
        :rtype: [PrototypeText]
        :returns: List of availables translations
        """
        if key is not None:
            return [self.texts[urn] for urn in self.texts if self.texts[urn].subtype == "Translation" and self.texts[urn].lang == key]
        else:
            return [self.texts[urn] for urn in self.texts if self.texts[urn].subtype == "Translation"]

    def __len__(self):
        """ Get the number of text in the PrototypeWork

        :return: Number of texts available in the inventory
        """
        return len(self.texts)

    @property
    def members(self):
        return list(self.texts.values())

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the Work

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS:
            attrs = {"urn": self.id}
            return self.__xml_export_generic__(attrs, namespaces=False)


class PrototypeTextGroup(PrototypeCTSCollection):
    """ Represents a CTS Textgroup

    CTS PrototypeTextGroup can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :param urn: Identifier of the PrototypeTextGroup
    :type urn: str
    :param parents: List of parents for current object
    :type parents: Tuple.<PrototypeTextInventory>

    :ivar urn: URN Identifier
    :type urn: URN
    :ivar parents: List of ancestors, from parent to furthest
    """
    DC_TITLE_KEY = NAMESPACES.CTS.term("groupname")
    TYPE_URI = NAMESPACES.CTS.term("textgroup")
    EXPORT_TO = [Mimetypes.XML.CTS]
    CTS_PROPERTIES = [NAMESPACES.CTS.groupname]

    @property
    def members(self):
        return list(self.works.values())

    def __init__(self, urn="", resource=None, parents=None):
        super(PrototypeTextGroup, self).__init__(identifier=str(urn))
        self.__urn__ = URN(urn)
        self.resource = None
        self.works = defaultdict(PrototypeWork)
        self.parents = list()

        if parents:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def update(self, other):
        """ Merge two Textgroup Objects.

        - Original (left Object) keeps his parent.
        - Added document merges with work if it already exists

        :param other: Textgroup object
        :type other: PrototypeTextGroup
        :return: Textgroup Object
        :rtype: PrototypeTextGroup
        """
        if not isinstance(other, PrototypeTextGroup):
            raise TypeError("Cannot add %s to PrototypeTextGroup" % type(other))
        elif str(self.urn) != str(other.urn):
            raise InvalidURN("Cannot add PrototypeTextGroup %s to PrototypeTextGroup %s " % (self.urn, other.urn))

        parents = [self] + self.parents
        for urn, work in other.works.items():
            if urn in self.works:
                self.works[urn].update(deepcopy(work))
            else:
                self.works[urn] = deepcopy(work)
            self.works[urn].parents = parents
            self.works[urn].resource = None

        return self

    def __len__(self):
        """ Get the number of text in the Textgroup

        :return: Number of texts available in the inventory
        """
        return len([
            text
            for work in self.works.values()
            for text in work.texts.values()
        ])

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the TextGroup

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS:
            attrs = {"urn": self.id}
            return self.__xml_export_generic__(attrs, namespaces=False)


class PrototypeTextInventory(PrototypeCTSCollection):
    """ Initiate a PrototypeTextInventory resource

    :param resource: Resource representing the PrototypeTextInventory
    :type resource: Any
    :param id: Identifier of the PrototypeTextInventory
    :type id: str
    """
    DC_TITLE_KEY = NAMESPACES.CTS.term("name")
    TYPE_URI = NAMESPACES.CTS.term("TextInventory")
    EXPORT_TO = [Mimetypes.XML.CTS]

    @property
    def members(self):
        return list(self.textgroups.values())

    def __init__(self, resource=None, name="defaultInventory"):
        super(PrototypeTextInventory, self).__init__(identifier=name)
        self.resource = None
        self.textgroups = defaultdict(PrototypeTextGroup)
        self.parents = list()
        if resource is not None:
            self.setResource(resource)

    def __len__(self):
        """ Get the number of text in the Inventory

        :return: Number of texts available in the inventory
        """
        return len([
            text
            for tg in self.textgroups.values()
            for work in tg.works.values()
            for text in work.texts.values()
        ])

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the PrototypeTextInventory

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :param namespaces: List namespaces in main node
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS:
            attrs = {}
            if self.id:
                attrs["tiid"] = self.id

            return self.__xml_export_generic__(attrs, namespaces=namespaces)
