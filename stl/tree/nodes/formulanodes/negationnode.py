""" Node used to represent the Negation operation in STL AST """
from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList
from ....operators import computeNot


class NegationNode(FormulaNode):
	""" Node representing Negation operation in STL formula. """

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		childResult = self.children[0].booleanValidate(signals, plot)
		result = BooleanSignal("negation", childResult.getTimes(), [0 if x == 1 else 1 for x in childResult.getValues()])
		self.booleanPlot(plot, result)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		childResult: Signal = self.children[0].quantitativeValidate(signals, plot)
		result: Signal = computeNot(childResult)
		result.setName("negation")
		self.quantitativePlot(plot, result)
		return result
