import unittest
from stl.tree import FloatValueNode
from stl.signals import Signal, SignalList, BooleanSignal
from typing import Iterable
class FloatValueNodeTest(unittest.TestCase):
	def setUp(self):
		pass	

	def testNegativeZeroValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['-', '0']
		# Create the node and read tokens
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testFractionalZeroValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['0', '.', '0']
		# Create the node and read tokens
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testNegativeFractionalZeroValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['-', '0', '.', '0']
		# Create the node and read tokens
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testZeroValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['0']
		# Create the node and read tokens
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testWholePositiveValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['123']
		# Create the node and read tokens
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [123], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [1], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testFractionalPositiveValue(self):
		# Str because that's the data type the node gets
		values: str = ['123', '.', '456']
		# Create the node and read tokens
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [123.456], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [1], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testWholeNegativeValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['-', '123']
		# Create the node and read token
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [-123], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testFractionalNegativeValue(self):
		# Str because that's the data type the node gets
		values: Iterable[str] = ['-', '123', '.', '456']
		# Create the node and read token
		node: FloatValueNode = FloatValueNode()
		for value in values:
			node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0], [-123.456], [0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		expectedSignal = BooleanSignal("BooleanValueNodeSignal", [0], [0], [0])
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)




if __name__ == "__main__":
	unittest.main()