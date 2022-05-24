""" Implementation of the test for the absolute value operation """

from stl.signals import Signal
from stl.operators import computeAbsoluteValue
import unittest


class AbsoluteValueTest(unittest.TestCase):
	""" Test cases for absolute value operation. 
	Quantitative Semantics Only.
	The operation function shouldn't be called in Boolean semantics."""

	def setUp(self) -> None:
		super().setUp()

	def testEmptySignal(self):
		empty = Signal("empty")
		expectedResult = Signal("absolutevalue")
		self.assertEqual(computeAbsoluteValue(empty), expectedResult)

	def testPositiveSignal(self):
		signal = Signal("in", [0, 1, 2, 3, 4], [0, 5, 8, 1234, 2], [5, 3, 1226, -1232, 0])
		expectedResult = Signal("absolutevalue", [0, 1, 2, 3, 4], [0, 5, 8, 1234, 2], [5, 3, 1226, -1232, 0])
		self.assertEqual(computeAbsoluteValue(signal), expectedResult)

	def testNegativeSignal(self):
		signal = Signal("in", [0, 1, 2, 3, 4], [0, -5, -8, -1234, -2], [-5, -3, -1226, 1232, 0])
		expectedResult = Signal("absolutevalue", [0, 1, 2, 3, 4], [0, 5, 8, 1234, 2], [5, 3, 1226, -1232, 0])
		self.assertEqual(computeAbsoluteValue(signal), expectedResult)

	def testAlternatingSignal(self):
		signal = Signal("in", [0, 1, 2, 4], [-1, 1, -1, 1], [-2, 2, -2, 0])
		expectedResult = Signal("absolutevalue", [0, 1, 2, 4], [1, 1, 1, 1], [0, 0, 0, 0])
		self.assertEqual(computeAbsoluteValue(signal), expectedResult)


if __name__ == "__main__":
	unittest.main()