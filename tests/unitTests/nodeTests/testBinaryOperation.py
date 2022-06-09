import unittest
import unittest.mock as mock
from stl.signals import Signal, BooleanSignal

class BinaryOperationTest(unittest.TestCase):
	def setUp(self):
		self.leftChild: mock.Mock = mock.Mock()
		self.rightChild: mock.Mock = mock.Mock()
		self.node.children = [self.leftChild, self.rightChild]

	def quantitativeValidationTestHelper(self, s1: Signal, s2: Signal, expectedResult: Signal) -> None:
		assert type(s1) == type(s2) == type(expectedResult) == Signal, "Quant semantics uses 'Signal'"
		self.leftChild.reset_mock()
		self.rightChild.reset_mock()
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		nodeResult = self.node.quantitativeValidate(None, None)
		self.assertEqual(expectedResult, nodeResult)
		self.leftChild.quantitativeValidate.assert_called_once_with(None, None)
		self.rightChild.quantitativeValidate.assert_called_once_with(None, None)

	def booleanValidationTestHelper(self, s1: BooleanSignal, s2: BooleanSignal, expectedResult: BooleanSignal) -> None:
		assert type(s1) == type(s2) == type(expectedResult) == BooleanSignal, "Bool semantics uses 'BooleanSignal'"
		self.leftChild.reset_mock()
		self.rightChild.reset_mock()
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		self.assertEqual(expectedResult, self.node.booleanValidate(None, None))
		self.leftChild.booleanValidate.assert_called_once_with(None, None, True)
		self.rightChild.booleanValidate.assert_called_once_with(None, None, True)