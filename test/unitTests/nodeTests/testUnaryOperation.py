import unittest
import unittest.mock as mock
from stl.signals import Signal, BooleanSignal


class UnaryOperationTest(unittest.TestCase):

	def setUp(self):
		self.child: mock.Mock = mock.Mock()
		self.node.children = [self.child]

	def quantitativeValidationTestHelper(self, s1: Signal, expectedResult: Signal) -> None:
		assert type(s1) == type(expectedResult) == Signal, "Quant semantics uses 'Signal'"
		self.child.reset_mock()
		self.child.quantitativeValidate.return_value = s1
		self.assertEqual(expectedResult, self.node.quantitativeValidate(None, None))
		self.child.quantitativeValidate.assert_called_once_with(None, None)

	def booleanValidationTestHelper(self, s1: BooleanSignal, expectedResult: BooleanSignal) -> None:
		assert type(s1) == type(expectedResult) == BooleanSignal, "Bool semantics uses 'BooleanSignal'"
		self.child.reset_mock()
		self.child.booleanValidate.return_value = s1
		self.assertEqual(expectedResult, self.node.booleanValidate(None, None))
		self.child.booleanValidate.assert_called_once_with(None, None)