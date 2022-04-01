from .formulanode import FormulaNode
import numpy
from ....signals import Signal, BooleanSignal, SignalList


class QuantitativeSignalNode(FormulaNode):

	def __init__(self):
		super().__init__()

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		result: BooleanSignal = self.children[0].booleanValidate(signals, plot)
		if plot:
			self.booleanPlot(result)
		result.simplify()
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result: Signal = self.children[0].quantitativeValidate(signals, plot)
		if plot:
			self.quantitativePlot(result)
		result.simplify()
		return result

	def text(self):
		return self.name() + ' [' + str(self.id) + ']'