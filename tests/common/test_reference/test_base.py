import unittest

from MyCapytain.common.reference import NodeId


class TestNodeId(unittest.TestCase):
    def test_setup(self):
        """ Ensure basic properties works """
        n = NodeId(children=["1", "b", "d"])
        self.assertEqual(n.childIds, ["1", "b", "d"])
        self.assertEqual(n.lastId, "d")
        self.assertEqual(n.firstId, "1")
        self.assertEqual(n.depth, None)
        self.assertEqual(n.parentId, None)
        self.assertEqual(n.id, None)
        self.assertEqual(n.prevId, None)
        self.assertEqual(n.nextId, None)
        self.assertEqual(n.siblingsId, (None, None))

        n = NodeId(parent="1", identifier="1.1")
        self.assertEqual(n.parentId, "1")
        self.assertEqual(n.id, "1.1")

        n = NodeId(siblings=("1", "1.1"), depth=5)
        self.assertEqual(n.prevId, "1")
        self.assertEqual(n.nextId, "1.1")
        self.assertEqual(n.childIds, [])
        self.assertEqual(n.firstId, None)
        self.assertEqual(n.lastId, None)
        self.assertEqual(n.siblingsId, ("1", "1.1"))
        self.assertEqual(n.depth, 5)