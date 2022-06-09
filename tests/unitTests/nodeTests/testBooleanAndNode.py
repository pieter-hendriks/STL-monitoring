import unittest
from unittest.mock import Mock
from stl.signals import BooleanSignal
from stl.tree import AndNode


class AndNodeTest(unittest.TestCase):

	def setUp(self):
		super().setUp()
		self.node = AndNode()
		self.node.children = [Mock(), Mock()]

	def __setInputSignals(self, lhs: BooleanSignal, rhs: BooleanSignal):
		self.node.children[0].booleanValidate.return_value = lhs
		self.node.children[1].booleanValidate.return_value = rhs

	def testBooleanEmptySignal(self):
		# Test boolean semantics
		empty = BooleanSignal("empty")
		nonEmpty = BooleanSignal("nonempty", [0, 1], [0, 1])
		expectedResult = BooleanSignal("and")
		# Test both empty
		self.__setInputSignals(empty, empty)
		self.assertEqual(self.node.booleanValidate(None, None), expectedResult)
		# Test lhs empty
		self.__setInputSignals(empty, nonEmpty)
		self.assertEqual(self.node.booleanValidate(None, None), expectedResult)
		# Test rhs empty
		self.__setInputSignals(nonEmpty, empty)
		self.assertEqual(self.node.booleanValidate(None, None), expectedResult)

	def testBooleanSignal(self):
		# This covers all possible cases for the boolean Signal.
		lhs = BooleanSignal("left", [0, 1, 2, 3], [0, 1, 0, 1])
		rhs = BooleanSignal("right", [0, 1, 2, 3], [1, 0, 0, 1])
		expectedResult = BooleanSignal("and", [0, 1, 2, 3], [0, 0, 0, 1])
		# Test in both directions - though that should be covered already
		self.__setInputSignals(lhs, rhs)
		self.assertEqual(self.node.booleanValidate(None, None), expectedResult)
		self.__setInputSignals(rhs, lhs)
		self.assertEqual(self.node.booleanValidate(None, None), expectedResult)


if __name__ == "__main__":
	unittest.main()
