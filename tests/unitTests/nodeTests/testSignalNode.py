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
		with self.assertRaisesRegex(RuntimeError, "Signal with name 'notfound' not found."):
				node.booleanValidate(SignalList(), None)
		with self.assertRaisesRegex(RuntimeError, "Signal with name 'notfound' not found."):
				node.quantitativeValidate(SignalList(), None)

	def testEmptySignal(self):
		# Create node to test
		node: SignalNode = SignalNode()
		node.processToken("empty")
		# Test both Boolean and Non-Boolean empty signals.
		for emptySignal in [BooleanSignal("empty"), Signal("empty")]:
			# Boolean validation should return boolean empty signal no matter what input
			self.assertEqual(BooleanSignal("empty"), node.booleanValidate(SignalList([emptySignal]), None, True))
			# Quant validation should return quant empty signal no matter what input
			self.assertEqual(Signal("empty"), node.quantitativeValidate(SignalList([emptySignal]), None))
		self.assertNotEqual(BooleanSignal("empty"), Signal("empty"))

	def testBooleanSignal(self):
		# Create node to test
		node: SignalNode = SignalNode()
		node.processToken("cos")
		# Create signal to test with
		cosSignal = getCosSignal(10, name='cos', booleanSignal = True)
		# The returned signal must be equal to the signal we created as input
		self.assertEqual(cosSignal, node.booleanValidate(SignalList([cosSignal]), None))
		# Type conversion must applied when necessary
		self.assertEqual(Signal.fromBooleanSignal(cosSignal), node.quantitativeValidate(SignalList([cosSignal]), None))


	def testNonBooleanSignal(self):
		# Create node to test
		node: SignalNode = SignalNode()
		node.processToken("cos")
		# Create signal to test with
		cosSignal = getCosSignal(10, name='cos', booleanSignal = False)
		if cosSignal.getName() != 'cos':
			raise RuntimeError(f"{cosSignal.getName()}")
		# The returned signal must be equal to the signal we created as input
		self.assertEqual(cosSignal, node.quantitativeValidate(SignalList([cosSignal]), None))
		# And booleanized version thereof in case of boolean evaluation
		# booleanize must be explicitly set; BooleanSignal supports non-boolean values to allow for time intervals
		# to be specified using Signals (for consistency, though this was a somewhat weird design decision we've made.)
		self.assertEqual(BooleanSignal.fromSignal(cosSignal), node.booleanValidate(SignalList([cosSignal]), None, booleanize=True))






if __name__ == "__main__":
	unittest.main()