import unittest
import unittest.mock as mock
from stl.tree import UntilNode
from stl.signals import Signal, BooleanSignal
from .helpers import getCosSignal
from stl.utility import Interval
from .testUntilNode import UntilNodeSetup

class EventuallyOperationTest(UntilNodeSetup):
	def setUp(self):
		super().setUp()
		self.node: UntilNode = UntilNode()
		self.leftSignalChild: mock.Mock = mock.Mock()
		self.intervalLowerBoundChild: mock.Mock = mock.Mock()
		self.intervalUpperBoundChild: mock.Mock = mock.Mock()
		self.rightSignalChild: mock.Mock = mock.Mock()
		self.node.children = [self.leftSignalChild, self.intervalLowerBoundChild, self.intervalUpperBoundChild, self.rightSignalChild]

	def __eventuallyHelper(self, lowerBound, upperBound):
		# In these cases, we have a 3-child operation. A static TRUE Signal is created in the node to act as leftSignalChild.
		self.node.children = [self.intervalLowerBoundChild, self.intervalUpperBoundChild, self.rightSignalChild]
		self.setInterval(lowerBound, upperBound)

	def __quantitativeEventuallyHelper(self, lowerBound: float, upperBound: float, signal: Signal, method: str):
		self.__eventuallyHelper(lowerBound, upperBound, signal)
		self.rightSignalChild.quantitativeValidate.return_value = signal
		generatedDummyTrue = Signal("DummyTrueSignal", signal.getTimes(), [1] * signal.getCheckpointCount(), [0] * signal.getCheckpointCount())
		with mock.patch.object(self.node, method, return_value=Signal()) as mymock:
			self.node.quantitativeValidate(None, None)
			self.rightSignalChild.quantitativeValidate.assert_called_once_with(None, None)
			self.intervalLowerBoundChild.quantitativeValidate.assert_called_once_with(None, None)
			self.intervalUpperBoundChild.quantitativeValidate.assert_called_once_with(None, None)
			mymock.assert_called_once_with(signal.getCheckpointCount(), [generatedDummyTrue, signal], Interval(lowerBound, upperBound))
		self.resetMocks()

	def __booleanEventuallyHelper(self, lowerBound: float, upperBound: float, signal: Signal):
		self.__eventuallyHelper(lowerBound, upperBound)
		self.rightSignalChild.booleanValidate.return_value = signal
		generatedDummyTrue = BooleanSignal("DummyTrueSignal", signal.getTimes(), [1] * signal.getCheckpointCount(), [0] * signal.getCheckpointCount())
		with mock.patch.object(self.node, 'booleanValidationImplementation', return_value=BooleanSignal()) as mymock:
			self.node.booleanValidate(None, None)
			self.rightSignalChild.booleanValidate.assert_called_once_with(None, None)
			self.intervalLowerBoundChild.booleanValidate.assert_called_once_with(None, None)
			self.intervalUpperBoundChild.booleanValidate.assert_called_once_with(None, None)
			mymock.assert_called_once_with(signal.getCheckpointCount(), [generatedDummyTrue, signal], Interval(0, 24))
	def testEventuallyShortAlgorithm(self):
		testSignal = getCosSignal(20, booleanSignal=False)
		self.node.useShortAlgorithm()
		self.__quantitativeEventuallyHelper(0, 24, testSignal, 'shortAlgorithm')

	def testEventuallyLongAlgorithm(self):
		testSignal = getCosSignal(20, booleanSignal=False)
		self.node.useLongAlgorithm()
		self.__quantitativeEventuallyHelper(0, 24, testSignal, 'longAlgorithm')

	def testEventuallyBoolean(self):
		testSignal = getCosSignal(20, booleanSignal=False)
		self.node.useLongAlgorithm()
		self.__booleanEventuallyHelper(0, 24, testSignal)