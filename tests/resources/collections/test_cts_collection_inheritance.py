from unittest import TestCase
from MyCapytain.resources.collections.cts import TextInventory, TextGroup, Work, Edition

with open("tests/testing_data/examples/getcapabilities.seneca.xml") as f:
    SENECA = f.read()


class TestCollectionCTSInheritance(TestCase):
    def test_types(self):
        TI = TextInventory.parse(resource=SENECA)
        self.assertCountEqual(
            [type(descendant) for descendant in TI.descendants],
            [TextGroup] + [Work]*10 + [Edition]*10,
            "Descendant should be correctly parsed into correct types"
        )
        self.assertCountEqual(
            [type(descendant) for descendant in TI.readableDescendants],
            [Work]*0 + [Edition]*10,
            "Descendant should be correctly parsed into correct types and filtered when readable"
        )

    def test_title(self):
        TI = TextInventory.parse(resource=SENECA)
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
