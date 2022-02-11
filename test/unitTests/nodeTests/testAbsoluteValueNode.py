import unittest
import unittest.mock as mock
from .testUnaryOperation import UnaryOperationTest
from stl.signals import SignalList, Signal, BooleanSignal
from stl.tree import AbsoluteValueNode
from .helpers import getCosSignal

class AbsoluteValueNodeTest(UnaryOperationTest):
	def setUp(self):
		# Node doesn't need to read input so isn't method dependent
		self.node: AbsoluteValueNode = AbsoluteValueNode()
		super().setUp()

	def testEmptySignal(self):
		# Empty signals remain empty
		emptySignal: Signal = Signal()
		self.quantitativeValidationTestHelper(emptySignal, emptySignal)
		emptySignal = BooleanSignal()
		self.booleanValidationTestHelper(emptySignal, emptySignal)

	def testPositiveConstantSignal(self):
		# Positive signals remain unchanged
		posSignal: Signal = Signal('testsignal', [0, 1], [5, 5], [0, 0])
		self.quantitativeValidationTestHelper(posSignal, posSignal)
		posSignal = BooleanSignal.fromSignal(posSignal)
		self.booleanValidationTestHelper(posSignal, posSignal)

	def testPositiveVariableSignal(self):
		# Positive signals remain unchanged
		posSignal: Signal = Signal('testsignal', [0, 1, 2], [3, 5, 7], [2, 2, 0])
		self.quantitativeValidationTestHelper(posSignal, posSignal)
		posSignal = BooleanSignal.fromSignal(posSignal)
		self.booleanValidationTestHelper(posSignal, posSignal)

	def testNegativeConstantSignal(self):
		# Negative signal should be inverted
		negSignal: Signal = Signal('testsignal', [0, 1, 2], [-1, -1, -1], [0, 0, 0])
		resSignal: Signal = Signal('testsignal', [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.quantitativeValidationTestHelper(negSignal, resSignal)
		# Boolean signal should remain unchanged
		negSignal = BooleanSignal.fromSignal(negSignal)
		self.booleanValidationTestHelper(negSignal, negSignal)

	def testNegativeVariableSignal(self):
		# Negative signal should be inverted, derivatives need to be recomputed if signal isn't constant
		negSignal: Signal = Signal('testsignal', [0, 1, 2], [-1, -3, -4], [-2, -1, 0])
		resSignal: Signal = Signal("testsignal", [0, 1, 2], [1, 3, 4], [2, 1, 0])
		self.quantitativeValidationTestHelper(negSignal, resSignal)
		
		# Derivate recomputation may result in negative derivatives where previously there was a positive derivative.
		negSignal = Signal('testsignal', [0,1,2], [-5, -4, -6], [1, -2, 0])
		resSignal = Signal('testsignal', [0,1,2], [5, 4, 6], [-1, 2, 0])
		self.quantitativeValidationTestHelper(negSignal, resSignal)

		# Boolean signal should remain unchanged
		negSignal = BooleanSignal.fromSignal(negSignal)
		self.booleanValidationTestHelper(negSignal, negSignal)

	def testCosSignal(self):
		# Alternating [1, -1]-signal (~=cosine) should become constant
		cosSignal: Signal = Signal('testsignal', [0,1,2,3,4,5,6], [1, -1, 1, -1, 1, -1, 1], [-2, 2, -2, 2, -2, 2, 0])
		resSignal: Signal = Signal('testsignal', [0,1,2,3,4,5,6], [1, 1, 1, 1, 1, 1, 1], [0,0,0,0,0,0,0])
		self.quantitativeValidationTestHelper(cosSignal, resSignal)

		# Boolean cosine signal; all bool should remain unchanged
		cosSignal = BooleanSignal("testsignal", [0,1,2,3,4,5,6], [1, 0, 1, 0, 1, 0, 1], [0,0,0,0,0,0,0])
		self.booleanValidationTestHelper(cosSignal, cosSignal)
		


if __name__ == "__main__":
	unittest.main()