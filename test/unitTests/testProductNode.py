import unittest
import unittest.mock as mock
from stl.tree import BinaryOperationNode
from stl.signals import Signal, BooleanSignal



	# While tempting to test signals with non-matching timestamps (to verify they work correctly)
	# that shouldn't be happening here. Non-matching timestamps are handled by getPunctualIntersection,
	# so adding those would be a part of unit-testing punctualIntersection - not ProductNode.

# TODO: Split this file into ProductNodeTest and DivisionNodeTest
# OR merge with SumNodeTest to create BinaryOperationNodeTest
# Current hierarchy doesn't reflect current situation.

class ProductNodeTest(unittest.TestCase):
	def setUp(self):
		self.node: BinaryOperationNode = BinaryOperationNode()
		self.leftChild = mock.Mock()
		self.rightChild = mock.Mock()
		self.node.children = [self.leftChild, self.rightChild]

	def testEmptyEmptyMultiplication(self):
		self.node.processToken("*") # Create a multiplication BinaryOperationNode
		self.assertEqual(self.node.operatorName, "*")
		s1: Signal = Signal()
		s2: Signal = Signal()
		s1b: BooleanSignal = BooleanSignal()
		s2b: BooleanSignal = BooleanSignal()
		self.leftChild.quantitativeValidate.return_value = s1
		self.leftChild.booleanValidate.return_value = s1b
		self.rightChild.quantitativeValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s1b
		# Empty signals multiplied should be the empty signal, both in quant and bool semantics
		self.assertEqual(self.node.quantitativeValidate(None, None), Signal('product'))
		self.assertEqual(self.node.booleanValidate(None, None), BooleanSignal('product'))

	def testPosPosMultiplication(self):
		self.node.processToken("*") # Create a multiplication BinaryOperationNode
		self.assertEqual(self.node.operatorName, "*")

		s1: Signal = Signal('s1', [0, 1], [4, 5], [1, 0])
		s2: Signal = Signal('s2', [0, 1], [1, 2], [1, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		# Name is given inside product node as well - string change might break this.
		# Probably prudent to enable this using a variable instead, but this works for now.
		# TODO: Add a variable 'productResultSignalName' or something similar (also for other operations)
		rs: Signal = Signal('product', [0, 1], [4, 10], [6, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Product should be equal if operands are swapped
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# Test the boolean semantics of pos-pos
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal("product", [0, 1], [1, 1], [0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Product should be equal if operands are swapped
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))

	# By swapping operand order, this also covers NegPosMultiplication
	def testPosNegMultiplication(self):
		self.node.processToken("*") # Create a multiplication ProductNode
		self.assertEqual(self.node.operatorName, "*")

		s1: Signal = Signal('s1', [0, 1], [4, 5], [1, 0])
		s2: Signal = Signal('s2', [0, 1], [-1, -2], [-1, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		# Name is given inside product node as well - string change might break this.
		# Probably prudent to enable this using a variable instead, but this works for now.
		# TODO: Add a variable 'productResultSignalName' or something similar (also for other operations)
		rs: Signal = Signal('product', [0, 1], [-4, -10], [-6, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Product should be equal if operands are swapped
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# BooleanSignal test: should just be Falsey values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal("product", [0, 1], [0, 0], [0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Product should be equal if operands are swapped
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))

	def testNegNegMultiplication(self):
		self.node.processToken("*") # Create a multiplication ProductNode
		self.assertEqual(self.node.operatorName, "*")

		s1: Signal = Signal('s1', [0, 1], [-4, -5], [-1, 0])
		s2: Signal = Signal('s2', [0, 1], [-1, -2], [-1, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		# Name is given inside product node as well - string change might break this.
		# Probably prudent to enable this using a variable instead, but this works for now.
		# TODO: Add a variable 'productResultSignalName' or something similar (also for other operations)
		rs: Signal = Signal('product', [0, 1], [4, 10], [6, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Product should be equal if operands are swapped
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# BooleanSignal test: should just be Falsey values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal("product", [0, 1], [0, 0], [0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Product should be equal if operands are swapped
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))
	
	def testPosPosDivision(self):
		self.node.processToken("/")
		self.assertEqual(self.node.operatorName, "/")
		s1: Signal = Signal("s1", [0, 1, 2], [4, 5, 6], [1, 1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [2, 1, 4], [-1, 3, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('product', [0, 1, 2], [2, 5, 1.5], [3, -3.5, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Division order change changes the results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		rs = Signal('product', [0, 1, 2], [0.5, 0.2, 2/3], [-0.3, 2/3-0.2, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# BooleanSignal test: should just be Truthy values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal("product", [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Since all values in pos-pos are truthy (that is, 1), operand swap doesn't change anything.
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		
	def testPosNegDivision(self):
		self.node.processToken("/")
		self.assertEqual(self.node.operatorName, "/")
		s1: Signal = Signal("s1", [0, 1, 2], [4, 6, 8], [2, 2, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -3, -4], [-1, -1, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('product', [0, 1, 2], [-2, -2, -2], [0, 0, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Division order change changes the results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		rs = Signal('product', [0, 1, 2], [-0.5, -0.5, -0.5], [0, 0, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# test Boolean variant as well
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		with self.assertRaises(ZeroDivisionError):
			self.node.booleanValidate(None, None)
		# Swap the operands
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		rs = BooleanSignal('product', [0, 1, 2], [0, 0, 0], [0, 0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))

	def testNegNegDivision(self):
		self.node.processToken("/")
		self.assertEqual(self.node.operatorName, "/")
		s1: Signal = Signal("s1", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -4, -6], [-2, -2, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('product', [0, 1, 2], [0.5, 0.5, 0.5], [0, 0, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Division order changes results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		rs = Signal('product', [0, 1, 2], [2, 2, 2], [0, 0, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Test Boolean Variant - both Signals are negative values, so get converted to False (0)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		# Divide by False (which is 0) results in error
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		with self.assertRaises(ZeroDivisionError):
			self.node.booleanValidate(None, None)
		# Divide by False (which is 0) results in error
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		with self.assertRaises(ZeroDivisionError):
			self.node.booleanValidate(None, None)



if __name__ == "__main__":
	unittest.main()