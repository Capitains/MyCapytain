from unittest import TestCase
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText
from MyCapytain.common.constants import Mimetypes
from lxml import etree


class TestAdHoc(TestCase):
    """ This is a series of tests drawn from issues on other repositories and third parties use of the code.

    """
    def test_passage_extraction_fail_when_reffs_are_found(self):
        """ This issues is drawn from https://github.com/PerseusDL/canonical-latinLit/issues/226
        """
        with open("tests/testing_data/texts/extraction_issue.xml") as text:
            interactive_text = CapitainsCtsText(resource=etree.parse(text).getroot())
            reffs = interactive_text.getReffs(level=len(interactive_text.citation))
            passages = []
            # The failing passage was 5.1
            for reff in reffs:
                try:
                    passages.append(interactive_text.getTextualNode(reff))
                except IndexError:
                    raise Exception("Unable to extract %s " % reff)

            plaintext = [r.export(Mimetypes.PLAINTEXT, exclude=["tei:note"]).strip() for r in passages]
            self.assertIn(
                "NUNC et praedictos et regni sorte sequentes", plaintext,
                "The text of 5.1 should be in plaintext"
            )
