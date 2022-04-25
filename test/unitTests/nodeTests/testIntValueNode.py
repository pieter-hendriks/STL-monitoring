import unittest
from stl.tree import IntValueNode
from stl.signals import Signal


class IntValueNodeTest(unittest.TestCase):

	def setUp(self):
		pass

	def testZeroValue(self):
		# Str because that's the data type the node gets
		value: str = '0'
		# Create the node and read token
		node: IntValueNode = IntValueNode()
		node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0, float('inf')], [0, 0], [0, 0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testPositiveValue(self):
		# Str because that's the data type the node gets
		value: str = '123'
		# Create the node and read token
		node: IntValueNode = IntValueNode()
		node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0, float('inf')], [123, 123], [0, 0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)

	def testNegativeValue(self):
		# Str because that's the data type the node gets
		value: str = '123'
		# Create the node and read token
		node: IntValueNode = IntValueNode()
		node.processToken("-")
		node.processToken(value)
		# Create expected result and compare the two
		expectedSignal: Signal = Signal("ValueNodeSignal", [0, float('inf')], [-123, -123], [0, 0])
		self.assertEqual(node.quantitativeValidate(None, None), expectedSignal)
		self.assertEqual(node.booleanValidate(None, None), expectedSignal)


if __name__ == "__main__":
	unittest.main()