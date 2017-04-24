from unittest import TestCase
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata, XmlCtsTextgroupMetadata, XmlCtsWorkMetadata, XmlCtsEditionMetadata, XmlCtsTranslationMetadata
from MyCapytain.resources.prototypes.cts.inventory import CtsTextgroupMetadata

with open("tests/testing_data/examples/getcapabilities.seneca.xml") as f:
    SENECA = f.read()


class TestCollectionCtsInheritance(TestCase):
    def test_types(self):
        TI = XmlCtsTextInventoryMetadata.parse(resource=SENECA)
        self.assertCountEqual(
            [type(descendant) for descendant in TI.descendants],
            [XmlCtsTextgroupMetadata] + [XmlCtsWorkMetadata] * 10 + [XmlCtsEditionMetadata] * 10,
            "Descendant should be correctly parsed into correct types"
        )
        self.assertCountEqual(
            [type(descendant) for descendant in TI.readableDescendants],
            [XmlCtsWorkMetadata] * 0 + [XmlCtsEditionMetadata] * 10,
            "Descendant should be correctly parsed into correct types and filtered when readable"
        )

    def test_title(self):
        TI = XmlCtsTextInventoryMetadata.parse(resource=SENECA)
        self.assertCountEqual(
            [str(descendant.get_label()) for descendant in TI.descendants],
            ["Seneca, Lucius Annaeus", "de Ira", "de Vita Beata", "de consolatione ad Helviam", "de Constantia",
             "de Tranquilitate Animi", "de Brevitate Vitae", "de consolatione ad Polybium",
             "de consolatione ad Marciam", "de Providentia", "de Otio Sapientis", "de Ira, Moral essays Vol 2",
             "de Vita Beata, Moral essays Vol 2", "de consolatione ad Helviam, Moral essays Vol 2",
             "de Constantia, Moral essays Vol 2", "de Tranquilitate Animi, Moral essays Vol 2",
             "de Brevitate Vitae, Moral essays Vol 2", "de consolatione ad Polybium, Moral essays Vol 2",
             "de consolatione ad Marciam, Moral essays Vol 2", "de Providentia, Moral essays Vol 2",
             "de Otio Sapientis, Moral essays Vol 2"],
            "Title should be computed correctly : default should be set"
        )

    def test_new_object(self):
        """ When creating an object with same urn, we should retrieve the same metadata"""
        TI = XmlCtsTextInventoryMetadata.parse(resource=SENECA)
        a = TI["urn:cts:latinLit:stoa0255.stoa012.perseus-lat2"].metadata
        b = (CtsTextgroupMetadata("urn:cts:latinLit:stoa0255")).metadata