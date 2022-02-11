from .formulanode import FormulaNode
import numpy
from ....signals import Signal, BooleanSignal, SignalList

class QuantitativeSignalNode(FormulaNode):
	def __init__(self):
		super().__init__()

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		raise RuntimeError("I don 't think this node is used.")
		raise RuntimeError("Is this ever required? It seems non-sensical.")
		result: BooleanSignal = self.children[0].booleanValidate(signals, plot)
		if plot:
			self.booleanPlot(result)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		raise RuntimeError("I don 't think this node is used.")
		result: Signal = self.children[0].quantitativeValidate(signals, plot)
		if plot:
			self.quantitativePlot(result)
		return result  # signal represented as an instance of Signal

	def text(self):
		return self.name() + ' [' + str(self.id) + ']'