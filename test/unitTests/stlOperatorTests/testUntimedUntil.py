""" Test cases for the untimed until operation.
This only exists in the efficient algorithm implementation. """

import unittest
from stl.signals import Signal
from stl.operators import computeUntimedUntil


class UntimedUntilTest(unittest.TestCase):
	""" Implementation of the Untimed Until tests. """

	def setUp(self) -> None:
		return super().setUp()

	def testEmptySignal(self):
		empty = Signal()
		nonEmpty = Signal('t', [0, 1], [0, 1], [1, 0])
		expectedResult = Signal("untimedUntil")

		self.assertEqual(computeUntimedUntil(empty, empty), expectedResult)
		self.assertEqual(computeUntimedUntil(empty, nonEmpty), expectedResult)
		self.assertEqual(computeUntimedUntil(nonEmpty, empty), expectedResult)

	def testSimpleSignal(self) -> None:
		inputSignal: Signal = Signal('test', [0, 1], [0, 1], [1, 0])
		expectedResult = Signal("untimedUntil", [0, 1], [0, 1], [1, 0])
		self.assertEqual(computeUntimedUntil(inputSignal, inputSignal), expectedResult)

		inputSignal: Signal = Signal('test', [0, 1], [-1, 1], [2, 0])
		expectedResult = Signal("untimedUntil", [0, 1], [-1, 1], [2, 0])
		self.assertEqual(computeUntimedUntil(inputSignal, inputSignal), expectedResult)

	def testSmallSignal(self) -> None:
		lhs = Signal("left", [0, 1, 2, 3, 4], [2, 7, 5, 4, -1], [5, -2, -1, -5, 0])
		rhs = Signal("right", [0, 1, 2, 3, 4], [-1, -1, -1, 1, 1], [0, 0, 2, 0, 0])
		expectedResult = Signal("untimedUntil", [0, 1, 2, 3, 3.6, 4], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0])
		self.assertEqual(computeUntimedUntil(lhs, rhs), expectedResult)
		rhs = Signal("right", [0, 1, 2, 3, 4], [-1, -1, -1, 4, 1], [0, 0, 2, 0, 0])
		expectedResult = Signal("untimedUntil", [0, 1, 2, 3, 4], [2, 4, 4, 4, 1], [2, 0, 0, -3, 0])
		self.assertEqual(computeUntimedUntil(lhs, rhs), expectedResult)
		lhs = Signal("left", [0, 1, 2, 3, 4], [-2, -7, -5, -4, -1], [5, -2, -1, -5, 0])
		expectedResult = Signal("untimedUntil", [0, 1, 2, 3, 4], [-2, -7, -5, -4, 1], [-5, 2, 1, 5, 0])
		self.assertEqual(computeUntimedUntil(lhs, rhs), expectedResult)
		lhs = Signal("left", [0, 1, 2, 3, 4], [-2, -7, -5, -4, -12], [5, -2, -1, -5, 0])
		expectedResult = Signal("untimedUntil", [0, 1, 2, 3, 4], [-2, -7, -5, -4, 1], [-5, 2, 1, 5, 0])
		self.assertEqual(computeUntimedUntil(lhs, rhs), expectedResult)