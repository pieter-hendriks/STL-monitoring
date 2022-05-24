""" Implementation of the Comparison Operator Node

This is a class that implements generic functionality for
all comparison operations based on the tokens read. """
from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList


class ComparisonOperatorNode(FormulaNode):
	""" Class implementing the comparison operator functionality.
	Implements all binary comparison STL operations, which is used depends on token."""
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
		""" Set the node's functionality based on token. """
		assert self.filter is None
		assert self.operation is None
		self.filter = str(token)
		self.operation = ComparisonOperatorNode.OPERATORS[self.filter]

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		lhs: BooleanSignal = self.children[0].booleanValidate(signals, plot)
		rhs: BooleanSignal = self.children[1].booleanValidate(signals, plot)
		result: BooleanSignal = BooleanSignal('comparison')
		assert isinstance(lhs, BooleanSignal), "Input to boolean validate should always be BooleanSignal instances."
		assert isinstance(rhs, BooleanSignal), "Input to boolean validate should always be BooleanSignal instances."
		lhs, rhs = BooleanSignal.computeComparableSignals(lhs, rhs)
		for i in range(lhs.getCheckpointCount()):
			comparisonResult = self.operation(lhs.getValue(i), rhs.getValue(i))
			result.emplaceCheckpoint(lhs.getTime(i), comparisonResult)
		self.booleanPlot(plot, result)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		lhs: Signal = self.children[0].quantitativeValidate(signals, plot)
		rhs: Signal = self.children[1].quantitativeValidate(signals, plot)
		result: Signal = Signal('comparison')
		assert isinstance(lhs, Signal) and not isinstance(lhs, BooleanSignal)
		assert isinstance(rhs, Signal) and not isinstance(rhs, BooleanSignal)
		lhs, rhs = Signal.computeComparableSignals(lhs, rhs)
		for i in range(lhs.getCheckpointCount()):
			comparisonResult = self.operation(lhs.getValue(i), rhs.getValue(i))
			result.emplaceCheckpoint(lhs.getTime(i), comparisonResult, None)
		result.recomputeDerivatives()
		self.quantitativePlot(plot, signals)
		return result

	def text(self) -> str:
		return 'BooleanFilter' + ' [' + str(self.id) + ']: ' + self.filter
