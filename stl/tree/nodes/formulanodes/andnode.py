""" Node representing the AND operation in STL formulas """
from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList

from ....operators import computeAnd


class AndNode(FormulaNode):
	""" Node class for the AND operation in STL """

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result: Signal = Signal('and')
		lhs: Signal = self.children[0].quantitativeValidate(signals, plot)
		rhs: Signal = self.children[1].quantitativeValidate(signals, plot)
		result = computeAnd(lhs, rhs)
		self.quantitativePlot(plot, result)
		result.recomputeDerivatives()
		return result

	def booleanValidate(self, signals: SignalList, plot: bool, booleanize=False) -> BooleanSignal:
		lhs: BooleanSignal = self.children[0].booleanValidate(signals, plot, True)
		rhs: BooleanSignal = self.children[1].booleanValidate(signals, plot, True)
		result: BooleanSignal = BooleanSignal('and')
		lhs, rhs = BooleanSignal.computeComparableSignals(lhs, rhs)
		for i in range(lhs.getCheckpointCount()):
			value = lhs.getValue(i) and rhs.getValue(i)
			result.emplaceCheckpoint(lhs.getTime(i), value)
		self.booleanPlot(plot, result)
		result.recomputeDerivatives()
		return result
