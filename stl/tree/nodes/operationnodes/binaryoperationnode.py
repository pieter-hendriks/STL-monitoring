from turtle import left
from .operationnode import OperationNode
from ....signals import SignalList, Signal, BooleanSignal
from typing import Union

class BinaryOperationNode(OperationNode):
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
		return self.operatorName

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		childResults = SignalList(Signal.computeComparableSignals(self.children[0].quantitativeValidate(signals, plot), self.children[1].quantitativeValidate(signals, plot)))
		return self.__operationImplementation(childResults[0], childResults[1])

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		childResults = SignalList(Signal.computeComparableSignals(self.children[0].booleanValidate(signals, plot), self.children[1].booleanValidate(signals, plot)))
		assert type(childResults[0]) == BooleanSignal
		return self.__operationImplementation(childResults[0], childResults[1])
		
	def __operationImplementation(self, leftChildSignal: Union[Signal, BooleanSignal], rightChildSignal: Union[Signal, BooleanSignal]) -> Union[Signal, BooleanSignal]:
		# We either work on two booleans or two quantitatives. One and one is non-sensical.
		# A Quantitative signal may contain only boolean values, but that does not make it a Boolean-semantic signal.
		assert type(leftChildSignal) == type(rightChildSignal) 
		assert type(leftChildSignal) in [Signal, BooleanSignal]
		returnType = type(leftChildSignal)
		ret: Union[Signal, BooleanSignal] = returnType(self.resultChildName)
		for i in range(leftChildSignal.getCheckpointCount()):
			computedValue = self.operation(leftChildSignal.getValue(i), rightChildSignal.getValue(i))
			ret.emplaceCheckpoint(leftChildSignal.getTime(i), computedValue)
		ret.recomputeDerivatives()
		return ret