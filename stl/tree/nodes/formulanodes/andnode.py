from .formulanode import FormulaNode
from stl.stlUtils import getPunctualIntersection, calculate_and_or
from ....signals import Signal, BooleanSignal, SignalList
class AndNode(FormulaNode):
	def __init__(self):
		super().__init__()

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result: SignalList = SignalList()
		lhs: Signal; rhs: Signal
		lhs, rhs = self.children[0].quantitativeValidate(signals, plot), self.children[1].quantitativeValidate(signals, plot)
		result = calculate_and_or(lhs, rhs, 'and')
		if plot:
			self.quantitativePlot(result)
		return result

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		lhs: Signal; rhs: Signal
		lhs, rhs = self.children[0].booleanValidate(signals, plot), self.children[1].booleanValidate(signals, plot)
		result: Signal = BooleanSignal()
		intersectedChildResults = getPunctualIntersection(lhs, rhs, semantic='boolean')
		lhs, rhs = intersectedChildResults[0], intersectedChildResults[1]
		for i in range(lhs.getCheckpointCount()):
			value = lhs.getValue(i) and rhs.getValue(i)
			result.emplaceCheckpoint(lhs.getTime(i), value)
		if plot:
			self.booleanPlot(result)
		return result
