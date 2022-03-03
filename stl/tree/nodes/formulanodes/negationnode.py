from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList
from ....operators import computeNot

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
		childResult: Signal = self.children[0].quantitativeValidate(signals, plot)
		myResult: Signal = computeNot(childResult)
		myResult.setName("negation")
		if plot:
			self.quantitativePlot(myResult)
		return myResult