from .formulanode import FormulaNode
from numbers import Number
import warnings
import numpy
from ....signals import Signal, BooleanSignal, SignalList


class ComparisonOperatorNode(FormulaNode):
	OPERATORS = {
	    '=': lambda x, y: int(x == y),
	    '!=': lambda x, y: int(x != y),
	    '>=': lambda x, y: int(x >= y),
	    '<=': lambda x, y: int(x <= y),
	    '>': lambda x, y: int(x > y),
	    '<': lambda x, y: int(x < y)
	}

	def __init__(self) -> None:
		super().__init__()
		self.filter = None
		self.operation = None

	def processToken(self, token: str) -> None:
		assert self.filter == self.operation == None, "Only one token can be processed by a node. Re-defining the operation is not supported."
		self.filter = str(token)
		self.operation = ComparisonOperatorNode.OPERATORS[self.filter]

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		lhs = self.children[0].booleanValidate(signals, plot)
		rhs = self.children[1].booleanValidate(signals, plot)
		result: BooleanSignal = BooleanSignal('comparison')
		assert type(lhs) == type(
		    rhs
		) == BooleanSignal, "Input the boolean validate should always be BooleanSignal instances."
		# We can't have intermediate equalities in BooleanSignals, so we don't have to perform this step
		lhs, rhs = BooleanSignal.computeComparableSignals(lhs, rhs)
		for i in range(lhs.getCheckpointCount()):
			comparisonResult = self.operation(lhs.getValue(i), rhs.getValue(i))
			result.emplaceCheckpoint(lhs.getTime(i), comparisonResult)
		result.simplify()
		if plot:
			self.booleanPlot(result)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		lhs = self.children[0].quantitativeValidate(signals, plot)
		rhs = self.children[1].quantitativeValidate(signals, plot)
		result: Signal = Signal('comparison')
		assert type(lhs) == type(rhs) == Signal
		lhs, rhs = Signal.computeComparableSignals(lhs, rhs)
		for i in range(lhs.getCheckpointCount()):
			comparisonResult = self.operation(lhs.getValue(i), rhs.getValue(i))
			result.emplaceCheckpoint(lhs.getTime(i), comparisonResult, None)
		result.recomputeDerivatives()
		result.simplify()
		if plot:
			self.quantitativePlot(signals)
		return result

	def text(self) -> str:
		return 'BooleanFilter' + ' [' + str(self.id) + ']: ' + self.filter
