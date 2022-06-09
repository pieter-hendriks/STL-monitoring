""" Test the untimed always operation """

from stl.signals import Signal
from stl.operators import computeUntimedAlways
import unittest


class UntimedAlwaysTest(unittest.TestCase):
	""" Implementation of the test cases for UntimedAlways """

	def setUp(self) -> None:
		super().setUp()

	def testQuantitativeEmptySignal(self):
		signal = Signal()
		expectedResult = Signal("untimedAlways")
		# Test empty both
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testSimpleSignal(self):
		signal = Signal('test', [0, 1], [0, 1], [1, 0])
		expectedResult = Signal('untimedAlways', [0, 1], [0, 1], [1, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testConstantResultSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [2, 7, 5, 4, -1], [5, -2, -1, -5, 0])
		expectedResult = Signal('untimedAlways', [0, 1, 2, 3, 4], [-1, -1, -1, -1, -1], [0, 0, 0, 0, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testVariableResultSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [2, -7, 5, 4, -1], [5, -9, 12, -5, 0])
		expectedResult = Signal('untimedAlways', [0, 1, 1.5, 2, 3, 4], [-7, -7, -1, -1, -1, -1], [0, 12, 0, 0, 0, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testPositiveConstantResultSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [2, 7, 5, 4, 1], [5, -2, -1, -3, 0])
		expectedResult = Signal('untimedAlways', [0, 1, 2, 3, 4], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testPositiveVariableResultSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [2, 7, 5, 4, 8], [5, -2, -1, 4, 0])
		expectedResult = Signal('untimedAlways', [0, 0.4, 1, 2, 3, 4], [2, 4, 4, 4, 4, 8], [5, 0, 0, 0, 4, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testNegativeVariableResultSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [-2, -7, -5, -4, -1], [-5, 2, 1, -3, 0])
		expectedResult = Signal('untimedAlways', [0, 1, 2, 3, 4], [-7, -7, -5, -4, -1], [0, 2, 1, 3, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)

	def testNegativeConstantResultSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [-1, -2, -4, -5, -7], [-1, -2, -1, -2, 0])
		expectedResult = Signal('untimedAlways', [0, 1, 2, 3, 4], [-7, -7, -7, -7, -7], [0, 0, 0, 0, 0])
		self.assertEqual(computeUntimedAlways(signal), expectedResult)


if __name__ == "__main__":
	unittest.main()