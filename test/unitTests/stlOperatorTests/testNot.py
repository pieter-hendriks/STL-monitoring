""" Implementation of the test for the absolute value operation """

from stl.signals import Signal
from stl.operators import computeNot
import unittest


class NotTest(unittest.TestCase):
	""" Test cases for absolute value operation. 
	Quantitative Semantics Only.
	The operation function shouldn't be called in Boolean semantics."""

	def setUp(self) -> None:
		super().setUp()

	def testEmptySignal(self):
		empty = Signal("empty")
		expectedResult = Signal("not")
		self.assertEqual(computeNot(empty), expectedResult)

	def testPositiveSignal(self):
		signal = Signal("in", [0, 1, 2, 3, 4], [0, 5, 8, 1234, 2], [5, 3, 1226, -1232, 0])
		expectedResult = Signal("not", [0, 1, 2, 3, 4], [0, -5, -8, -1234, -2], [-5, -3, -1226, 1232, 0])
		self.assertEqual(computeNot(signal), expectedResult)

	def testNegativeSignal(self):
		signal = Signal("in", [0, 1, 2, 3, 4], [0, -5, -8, -1234, -2], [-5, -3, -1226, 1232, 0])
		expectedResult = Signal("not", [0, 1, 2, 3, 4], [0, 5, 8, 1234, 2], [5, 3, 1226, -1232, 0])
		self.assertEqual(computeNot(signal), expectedResult)

	def testAlternatingSignal(self):
		signal = Signal("in", [0, 1, 2, 3], [-1, 1, -1, 1], [2, -2, 2, 0])
		expectedResult = Signal("not", [0, 1, 2, 3], [1, -1, 1, -1], [-2, 2, -2, 0])
		self.assertEqual(computeNot(signal), expectedResult)


if __name__ == "__main__":
	unittest.main()