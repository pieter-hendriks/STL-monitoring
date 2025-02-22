""" Module defining the BinaryOperationNode:
		abstract base for binary operation nodes in STL AST """
from ....signals import SignalList, Signal, BooleanSignal
from ..node import Node


class BinaryOperationNode(Node):
	""" Abstract class representing a binary operation in STL AST. """

	def __init__(self):
		super().__init__()
		self.resultChildName = 'UNSPECIFIED'
		self.operationName = 'UNSPECIFIED'

		def error(x, y):
			raise NotImplementedError("Abstract base OperationNode.operation was used.")

		self.operation = error

	def processToken(self, token):
		token = str(token)
		if token == '*':
			self.operation = lambda x, y: x * y
			self.resultChildName = 'product'
		elif token == '/':
			self.operation = lambda x, y: x / y
			self.resultChildName = 'quotient'
		elif token == '-':
			self.operation = lambda x, y: x - y
			self.resultChildName = 'difference'
		elif token == '+':
			self.operation = lambda x, y: x + y
			self.resultChildName = 'sum'
		else:
			raise RuntimeError(f"Unknown operation found for BinaryOperationNode: '{token}'")
		self.operationName = token

	def text(self):
		return self.operationName

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		childResults = SignalList(
		    Signal.computeComparableSignals(
		        self.children[0].quantitativeValidate(signals, plot), self.children[1].quantitativeValidate(signals, plot)
		    )
		)
		return self.__operationImplementation(childResults[0], childResults[1])

	def booleanValidate(self, signals: SignalList, plot: bool, booleanize=False) -> BooleanSignal:
		childResults = SignalList(
		    BooleanSignal.computeComparableSignals(
		        self.children[0].booleanValidate(signals, plot, True), self.children[1].booleanValidate(signals, plot, True)
		    )
		)
		x = self.__operationImplementation(childResults[0], childResults[1])
		if booleanize:
			return BooleanSignal.fromSignal(x)
		return x

	def __operationImplementation(self, leftChildSignal: Signal, rightChildSignal: Signal) -> Signal:
		""" Implementation of the binary operations.
		Uses the node's configured operation to compute the correct result. Operation is configured by processToken. """
		# We either work on two booleans or two quantitatives. One and one is non-sensical.
		# A Quantitative signal may contain only boolean values, but that does not make it a Boolean-semantic signal.
		assert isinstance(leftChildSignal, type(rightChildSignal))
		assert type(leftChildSignal) in [Signal, BooleanSignal]
		signalType = type(leftChildSignal)
		ret: Signal = signalType(self.resultChildName)
		for i in range(leftChildSignal.getCheckpointCount()):
			computedValue = self.operation(leftChildSignal.getValue(i), rightChildSignal.getValue(i))
			ret.emplaceCheckpoint(leftChildSignal.getTime(i), computedValue)
		ret.recomputeDerivatives()
		return ret
