from MyCapytain.common.constants import Mimetypes
from MyCapytain.common.base import Exportable


class Sentence(Exportable):
    """ This class represent a Sentence

    :param content: Content of the sentence
    """
    # EXPORT_TO is a list of Mimetype the object is capable to export to
    EXPORT_TO = [
        Mimetypes.PLAINTEXT, Mimetypes.XML.Std
    ]
    DEFAULT_EXPORT = Mimetypes.PLAINTEXT

    def __init__(self, content):
        self.content = content

    def __export__(self, output=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        if output == Mimetypes.PLAINTEXT:
            return self.content
        elif output == Mimetypes.XML.Std:
            return "<sentence>{}</sentence>".format(self.content)


class TEISentence(Sentence):
    """ This class represent a Sentence but adds some exportable accepted output

    :param content: Content of the sentence
    """
    EXPORT_TO = [
        Mimetypes.JSON.Std
    ]

    def __export__(self, output=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        if output == Mimetypes.JSON.Std:
            return {"http://www.tei-c.org/ns/1.0/sentence": self.content}
        elif output == Mimetypes.XML.Std:
            return "<sentence xmlns=\"http://www.tei-c.org/ns/1.0\">{}</sentence>".format(self.content)


s = Sentence("I love Martial's Epigrammatas")
print(s.export(Mimetypes.PLAINTEXT))
# I love Martial's Epigrammatas
print(s.export())  # Defaults to PLAINTEXT
# I love Martial's Epigrammatas
print(s.export(Mimetypes.XML.Std))
# <sentence>I love Martial's Epigrammatas</sentence>

tei = TEISentence("I love Martial's Epigrammatas")
print(tei.export(Mimetypes.PLAINTEXT))
# I love Martial's Epigrammatas
print(tei.export())  # Defaults to PLAINTEXT
# I love Martial's Epigrammatas
print(tei.export(Mimetypes.JSON.Std))
# {"http://www.tei-c.org/ns/1.0/sentence": I love Martial's Epigrammatas}
print(tei.export(Mimetypes.XML.Std))  # Has been rewritten by TEISentence
# <sentence xmlns="http://www.tei-c.org/ns/1.0">I love Martial's Epigrammatas</sentence>
try:
    print(tei.export(Mimetypes.XML.RDF))
except NotImplementedError as error:
    print(error)
# Raise the error and prints "Mimetype application/rdf+xml has not been implemented for this resource"
