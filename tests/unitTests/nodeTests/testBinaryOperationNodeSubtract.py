import unittest
import unittest.mock as mock
from .testBinaryOperation import BinaryOperationTest
from stl.signals import Signal, BooleanSignal
from stl.tree import BinaryOperationNode

class BinaryOperationNodeSubtractTest(BinaryOperationTest):
	def setUp(self):
		self.node: BinaryOperationNode = BinaryOperationNode()
		super().setUp()
		self.node.processToken('-')
	
	def testEmptyDifference(self):
		s1: Signal = Signal()
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s1
		# Empty signal difference should return empty signal
		self.assertEqual(Signal('difference'), self.node.quantitativeValidate(None, None))
		s1 = BooleanSignal()
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s1
		# Empty signal difference should return empty signal
		self.assertEqual(BooleanSignal('difference'), self.node.booleanValidate(None, None))

	def testPosPosDifference(self):
		s1: Signal = Signal("s1", [0, 1, 2], [4, 5, 6], [1, 1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [2, 1, 4], [-1, 3, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('difference', [0, 1, 2], [2, 4, 2], [2, -2, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# difference is operand order dependent
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		rs = Signal('difference', [0,1,2], [-2, -4, -2], [-2, 2, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# BooleanSignal test: should just be Truthy values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal("difference", [0, 1, 2], [0,0,0], [0, 0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Since all values in pos-pos are truthy (that is, 1), operand swap doesn't change anything.
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		
	def testPosNegDifference(self):
		s1: Signal = Signal("s1", [0, 1, 2], [4, 6, 8], [2, 2, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -3, -4], [-1, -1, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('difference', [0, 1, 2], [6, 9, 12], [3, 3, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Operand order change changes the results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		rs = Signal("difference", [0,1,2], [-6, -9, -12], [-3, -3, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# test Boolean variant as well
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal('difference', [0,1,2], [1,1,1], [0,0,0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Swap the operands, result should be the same
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		rs = BooleanSignal('difference', [0, 1, 2], [0, 0, 0], [0, 0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))

	def testNegNegDifference(self):
		s1: Signal = Signal("s1", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -4, -6], [-2, -2, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('difference', [0, 1, 2], [1, 2, 3], [1, 1, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# difference operand order impacts results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		rs = Signal("difference", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# Test Boolean Variant - both Signals are negative values, so get converted to False (0)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		# Then we expect all false differences
		rs = BooleanSignal('difference', [0,1,2], [0,0,0], [0,0,0])
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Signals should be equal, so result should be too!
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))


if __name__ == "__main__":
	unittest.main()