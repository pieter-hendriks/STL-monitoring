

import unittest
import unittest.mock as mock
from stl.signals import SignalList, Signal, BooleanSignal
from stl.tree import AbsoluteValueNode
from .helpers import getCosSignal

class AbsoluteValueNodeTest(unittest.TestCase):
	def setUp(self):
		# Node doesn't need to read input so isn't method dependent
		self.node: AbsoluteValueNode = AbsoluteValueNode()
		self.childMock = mock.Mock()
		self.node.children = [self.childMock]
	
	def testEmptySignal(self):
		# Test return for quant validate
		emptySignal: Signal = Signal()
		self.childMock.quantitativeValidate.return_value = emptySignal
		self.assertEqual(emptySignal, self.node.quantitativeValidate(None, None))
		# Test return for bool validate
		emptySignal = BooleanSignal()
		self.childMock.booleanValidate.return_value = emptySignal
		self.assertEqual(emptySignal, self.node.booleanValidate(None, None))

	def testPositiveConstantSignal(self):
		# Positive signal should remain unchanged.
		posSignal: Signal = Signal('testsignal', [0, 1], [5, 5], [0, 0])
		self.childMock.quantitativeValidate.return_value = posSignal
		self.assertEqual(posSignal, self.node.quantitativeValidate(None, None))
		# Boolean signal should remain unchanged.
		posSignal = BooleanSignal.fromSignal(posSignal)
		self.childMock.booleanValidate.return_value = posSignal
		self.assertEqual(posSignal, self.node.booleanValidate(None, None))

	def testPositiveVariableSignal(self):
		# Positive signal should remain unchanged
		posSignal: Signal = Signal('testsignal', [0, 1, 2], [3, 5, 7], [2, 2, 0])
		self.childMock.quantitativeValidate.return_value = posSignal
		self.assertEqual(posSignal, self.node.quantitativeValidate(None, None))

		# Boolean signal should remain unchanged
		posSignal = BooleanSignal.fromSignal(posSignal)
		self.childMock.booleanValidate.return_value = posSignal
		self.assertEqual(posSignal, self.node.booleanValidate(None, None))

	def testNegativeConstantSignal(self):
		# Negative signal should be inverted
		negSignal: Signal = Signal('testsignal', [0, 1, 2], [-1, -1, -1], [0, 0, 0])
		self.childMock.quantitativeValidate.return_value = negSignal
		resSignal: Signal = Signal('testsignal', [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.assertEqual(resSignal, self.node.quantitativeValidate(None, None))

		# Boolean signal should remain unchanged
		negSignal = BooleanSignal.fromSignal(negSignal)
		self.childMock.booleanValidate.return_value = negSignal
		self.assertEqual(negSignal, self.node.booleanValidate(None, None))

	def testNegativeVariableSignal(self):
		# Negative signal should be inverted, derivatives need to be recomputed if signal isn't constant
		negSignal: Signal = Signal('testsignal', [0, 1, 2], [-1, -3, -4], [-2, -1, 0])
		resSignal: Signal = Signal("testsignal", [0, 1, 2], [1, 3, 4], [2, 1, 0])
		self.childMock.quantitativeValidate.return_value = negSignal
		self.assertEqual(resSignal, self.node.quantitativeValidate(None, None))

		# Derivate recomputation may result in negative derivatives where previously there was a positive derivative.
		negSignal = Signal('testsignal', [0,1,2], [-5, -4, -6], [1, -2, 0])
		resSignal = Signal('testsignal', [0,1,2], [5, 4, 6], [-1, 2, 0])
		self.childMock.quantitativeValidate.return_value = negSignal
		self.assertEqual(resSignal, self.node.quantitativeValidate(None, None))

		# Boolean signal should remain unchanged
		negSignal = BooleanSignal.fromSignal(negSignal)
		self.childMock.booleanValidate.return_value = negSignal
		self.assertEqual(negSignal, self.node.booleanValidate(None, None))

	def testCosSignal(self):
		# Quantitative cosine signal
		cosSignal: Signal = Signal('testsignal', [0,1,2,3,4,5,6], [1, -1, 1, -1, 1, -1, 1], [-2, 2, -2, 2, -2, 2, 0])
		self.childMock.quantitativeValidate.return_value = cosSignal
		resSignal: Signal = Signal('testsignal', [0,1,2,3,4,5,6], [1, 1, 1, 1, 1, 1, 1], [0,0,0,0,0,0,0])
		self.assertEqual(resSignal, self.node.quantitativeValidate(None, None))

		# Boolean cosine signal; all bool should remain unchanged
		cosSignal = BooleanSignal("testsignal", [0,1,2,3,4,5,6], [1, 0, 1, 0, 1, 0, 1], [0,0,0,0,0,0,0])
		self.childMock.booleanValidate.return_value = cosSignal
		self.assertEqual(cosSignal, self.node.booleanValidate(None, None))
		


if __name__ == "__main__":
	unittest.main()