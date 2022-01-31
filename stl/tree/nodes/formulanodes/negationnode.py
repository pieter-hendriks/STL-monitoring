from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList
class NegationNode(FormulaNode):
	def __init__(self):
		super().__init__()

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		result = self.children[0].booleanValidate(signals, plot)
		print(result.getTimes())
		print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
		temp = BooleanSignal(f"Negation({result.getName()}", result.getTimes(), [0 if x == 1 else 1 for x in result.getValues()])
		if plot:
			self.booleanPlot(temp)
		return temp

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result = self.children[0].quantitativeValidate(signals, plot)
		temp = Signal(f'Negation({result.getName()})', result.getTimes(), [-x for x in result.getValues()], [-x for x in result.getDerivatives()])
		if plot:
			self.quantitativePlot(temp)
		return temp