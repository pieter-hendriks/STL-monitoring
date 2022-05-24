from stl.signals import Signal, BooleanSignal
from stl.operators import computeAnd
import unittest


class AndTest(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()

	def testQuantitativeEmptySignal(self):
		# Test quantitative semantics
		empty = Signal("empty")
		nonEmpty = Signal("nonempty", [0, 1], [0, 1], [1, 0])
		expectedResult = Signal("and")
		# Test both empty
		self.assertEqual(computeAnd(empty, empty), expectedResult)
		# Test lhs empty
		self.assertEqual(computeAnd(empty, nonEmpty), expectedResult)
		# Test rhs empty
		self.assertEqual(computeAnd(nonEmpty, empty), expectedResult)

	def testQuantitativeSimpleSignal(self):
		lhs = Signal("left", [0, 1, 2], [0, 1, -1], [1, -2, 0])
		rhs = Signal("right", [0, 1, 2], [1, 0, -2], [-1, -2, 0])
		expectedResult = Signal("and", [0, 0.5, 1, 2], [0, 0.5, 0, -2], [1, -1, -2, 0])
		# Test in both directions
		self.assertEqual(computeAnd(lhs, rhs), expectedResult)
		self.assertEqual(computeAnd(rhs, lhs), expectedResult)

	def testQuantitativeSimpleNegativeSignal(self):
		lhs = Signal("left", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		rhs = Signal("right", [0, 1, 2], [-3, -2, -1], [1, 1, 0])
		expectedResult = Signal("and", [0, 1, 2], [-3, -2, -3], [1, -1, 0])
		# Test in both directions
		self.assertEqual(computeAnd(lhs, rhs), expectedResult)
		self.assertEqual(computeAnd(rhs, lhs), expectedResult)

	def testQuantitativeSimplePositiveSignal(self):
		lhs = Signal("left", [0, 1, 2], [1, 2, 3], [1, 1, 0])
		rhs = Signal("right", [0, 1, 2], [3, 2, 1], [-1, -1, 0])
		expectedResult = Signal("and", [0, 1, 2], [1, 2, 1], [1, -1, 0])
		# Test in both directions
		self.assertEqual(computeAnd(lhs, rhs), expectedResult)
		self.assertEqual(computeAnd(rhs, lhs), expectedResult)

	def testSmallSignal(self):
		inputSignal: Signal = Signal('test', [0, 1, 2, 3, 4, 5], [-1, -1, 1, -1, -1, -1], [0, 2, -2, 0, 0, 0])
		result = computeAnd(inputSignal, inputSignal)
		inputSignal.setName('and')
		self.assertEqual(inputSignal, result)

		inputSignal: Signal = Signal('test', [0, 1, 2, 3, 4, 5], [1, -1, 1, -1, 1, -1], [-2, 2, -2, 2, -2, 0])
		result = computeAnd(inputSignal, inputSignal)
		inputSignal.setName('and')
		self.assertEqual(inputSignal, result)

		input1: Signal = Signal('test', [0, 1, 2, 3, 4, 5], [1, -1, 1, -1, 1, -1], [-2, 2, -2, 2, -2, 0])
		input2: Signal = Signal('test', [0, 1, 2, 3, 4, 5], [-1, 1, -1, 1, -1, 1], [2, -2, 2, -2, 2, 0])
		result = computeAnd(input1, input2)
		expRes = Signal(
		    'and', [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], [-1, 0, -1, 0, -1, 0, -1, 0, -1, 0, -1],
		    [2, -2, 2, -2, 2, -2, 2, -2, 2, -2, 0]
		)
		self.assertEqual(expRes, result)


if __name__ == "__main__":
	unittest.main()