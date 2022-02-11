from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList
class NegationNode(FormulaNode):
	def __init__(self):
		super().__init__()

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		childResult = self.children[0].booleanValidate(signals, plot)
		result = BooleanSignal("negation", childResult.getTimes(), [0 if x == 1 else 1 for x in childResult.getValues()])
		if plot:
			self.booleanPlot(result)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result = self.children[0].quantitativeValidate(signals, plot)
		temp = Signal('negation', result.getTimes(), [-x for x in result.getValues()], [-x for x in result.getDerivatives()])
		if plot:
			self.quantitativePlot(temp)
		return temp