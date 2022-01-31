import unittest

from stl.signals import SignalList, Signal, BooleanSignal
from .helpers import getCosSignal, getShiftedCosSignal
from stl.tree import SignalNode

# SignalNode is a node on the tree returning a given signal name from the signal list.

class SignalNodeTest(unittest.TestCase):
	def setUp(self):
		pass

	def signalNotFoundTest(self):
		node: SignalNode = SignalNode()
		node.processToken('notfound')
		# In case of signal with specified name not in list, we expect a runtime failure
		# TODO: Determine if more appropriate (non-failing) error handling is desired. This suffices for now, though.
		with self.assertRaisesRegex(RuntimeError, "Signal with name '.*' not found."):
				node.booleanValidate(SignalList(), None)
		with self.assertRaisesRegex(RuntimeError, "Signal with name '.*' not found."):
				node.quantitativeValidate(SignalList(), None)
	
	def testEmptySignal(self):
		# Create node to test
		node: SignalNode = SignalNode()
		node.processToken("empty")
		# Test both Boolean and Non-Boolean empty signals. 
		for emptySignal in [BooleanSignal("empty"), Signal("empty")]:
			self.assertEqual(emptySignal, node.booleanValidate(SignalList([emptySignal]), None))
			self.assertEqual(emptySignal, node.quantitativeValidate(SignalList([emptySignal]), None))

	def testBooleanSignal(self):
		# Create node to test
		node: SignalNode = SignalNode()
		node.processToken("cos")
		# Create signal to test with
		cosSignal = getCosSignal(10, name='cos', booleanSignal = True)
		if cosSignal.getName() != 'cos':
			raise RuntimeError("FUCK")
		# The returned signal must be equal to the signal we created as input
		self.assertEqual(cosSignal, node.booleanValidate(SignalList([cosSignal]), None))
		self.assertEqual(cosSignal, node.quantitativeValidate(SignalList([cosSignal]), None))


	def testNonBooleanSignal(self):
		# Create node to test
		node: SignalNode = SignalNode()
		node.processToken("cos")
		# Create signal to test with
		cosSignal = getCosSignal(10, name='cos', booleanSignal = False)
		if cosSignal.getName() != 'cos':
			raise RuntimeError(f"{cosSignal.getName()}")
		# The returned signal must be equal to the signal we created as input
		self.assertEqual(cosSignal, node.booleanValidate(SignalList([cosSignal]), None))
		self.assertEqual(cosSignal, node.quantitativeValidate(SignalList([cosSignal]), None))



		


if __name__ == "__main__":
	unittest.main()