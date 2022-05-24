import unittest
import unittest.mock as mock

from stl.tree import ContentNode
from stl.signals import Signal, BooleanSignal


class ContentNodeTest(unittest.TestCase):

	def setUp(self):
		self.node = ContentNode()
		self.child = mock.Mock()
		self.node.children = [self.child]

	def testSemanticDistribution(self):
		# Content node is the node handling distribution between the two semantics functions.
		# So, here, we need to test that the correct function is called for each semantic option.
		invalidSemantic: str = 'test'
		result: Signal = Signal('test')
		self.child.quantitativeValidate.return_value = result
		self.assertEqual(self.node.validate(None, 'quantitative', False), result)
		self.child.quantitativeValidate.assert_called_once_with(None, False)
		result: BooleanSignal = BooleanSignal('test')
		self.child.booleanValidate.return_value = result
		self.assertEqual(self.node.validate(None, 'boolean', False), result)
		self.child.booleanValidate.assert_called_once_with(None, False)


if __name__ == "__main__":
	unittest.main()