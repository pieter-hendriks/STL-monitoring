from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList
class AndNode(FormulaNode):
	def __init__(self):
		super().__init__()

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result: Signal = Signal('and')
		lhs: Signal; rhs: Signal
		lhs, rhs = self.children[0].quantitativeValidate(signals, plot), self.children[1].quantitativeValidate(signals, plot)
		result = Signal.computeAnd(lhs, rhs)
		if plot:
			self.quantitativePlot(result)
		result.recomputeDerivatives()
		return result

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		lhs: Signal; rhs: Signal
		lhs, rhs = self.children[0].booleanValidate(signals, plot), self.children[1].booleanValidate(signals, plot)
		result: Signal = BooleanSignal('and')
		lhs, rhs = SignalList(Signal.computeComparableSignals(lhs, rhs))
		for i in range(lhs.getCheckpointCount()):
			value = lhs.getValue(i) and rhs.getValue(i)
			result.emplaceCheckpoint(lhs.getTime(i), value)
		if plot:
			self.booleanPlot(result)
		result.recomputeDerivatives()
		return result
		
