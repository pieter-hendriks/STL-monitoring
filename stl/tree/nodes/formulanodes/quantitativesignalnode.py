""" Quantitative Signal Node for STL formulas """
from .formulanode import FormulaNode
from ....signals import Signal, BooleanSignal, SignalList


class QuantitativeSignalNode(FormulaNode):
	""" Node in STL ASTs representing quantitative Signal. """

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		result: BooleanSignal = self.children[0].booleanValidate(signals, plot)
		self.booleanPlot(plot, result)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result: Signal = self.children[0].quantitativeValidate(signals, plot)
		self.quantitativePlot(plot, result)
		return result

	def text(self):
		return self.name() + ' [' + str(self.id) + ']'
