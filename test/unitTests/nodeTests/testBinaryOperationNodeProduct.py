import unittest
import unittest.mock as mock

from stl.tree import BinaryOperationNode
from .testBinaryOperation import BinaryOperationTest
from stl.signals import Signal, BooleanSignal

class BinaryOperationNodeProductTest(BinaryOperationTest):
	def setUp(self):
		self.node: BinaryOperationNode = BinaryOperationNode()
		super().setUp()
		self.node.processToken("*")

	def testEmptyEmptyMultiplication(self):
		# Empty signal should return empty signal - name should always be 'product'
		s1: Signal = Signal()
		s2: Signal = Signal('test', [0], [0], [0])
		result: Signal = Signal('product')
		self.quantitativeValidationTestHelper(s1, s1, result)
		self.quantitativeValidationTestHelper(s1, s2, result)
		self.quantitativeValidationTestHelper(s2, s1, result)
		s1 = BooleanSignal()
		s2 = BooleanSignal('test', [0], [0], [0])
		result = BooleanSignal('product')
		self.booleanValidationTestHelper(s1, s1, result)
		self.booleanValidationTestHelper(s1, s2, result)
		self.booleanValidationTestHelper(s2, s1, result)

	def testPosPosMultiplication(self):
		s1: Signal = Signal('s1', [0, 1], [4, 5], [1, 0])
		s2: Signal = Signal('s2', [0, 1], [1, 2], [1, 0])
		# Name is given inside product node as well - string change might break this.
		# Probably prudent to enable this using a variable instead, but this works for now.
		# TODO: Add a variable 'productResultSignalName' or something similar (also for other operations)
		rs: Signal = Signal('product', [0, 1], [4, 10], [6, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)

		# Test the boolean semantics of pos-pos
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal("product", [0, 1], [1, 1], [0, 0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	# By swapping operand order, this also covers NegPosMultiplication
	def testPosNegMultiplication(self):
		s1: Signal = Signal('s1', [0, 1], [4, 5], [1, 0])
		s2: Signal = Signal('s2', [0, 1], [-1, -2], [-1, 0])
		# Name is given inside product node as well - string change might break this.
		# Probably prudent to enable this using a variable instead, but this works for now.
		# TODO: Add a variable 'productResultSignalName' or something similar (also for other operations)
		rs: Signal = Signal('product', [0, 1], [-4, -10], [-6, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)

		# BooleanSignal test: should just be Falsey values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal("product", [0, 1], [0, 0], [0, 0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testNegNegMultiplication(self):
		s1: Signal = Signal('s1', [0, 1], [-4, -5], [-1, 0])
		s2: Signal = Signal('s2', [0, 1], [-1, -2], [-1, 0])
		# Name is given inside product node as well - string change might break this.
		# Probably prudent to enable this using a variable instead, but this works for now.
		# TODO: Add a variable 'productResultSignalName' or something similar (also for other operations)
		rs: Signal = Signal('product', [0, 1], [4, 10], [6, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)

		# BooleanSignal test: should just be Falsey values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal("product", [0, 1], [0, 0], [0, 0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)
	

if __name__ == "__main__":
	unittest.main()