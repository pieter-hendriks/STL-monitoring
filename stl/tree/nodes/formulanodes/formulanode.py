""" Formula Node implementation """
from ..node import Node
from ....utility import PlotHelper
from ....signals import Signal, BooleanSignal


class FormulaNode(Node):  # Abstract class
	""" Class for containing nodes used in STL formulas. """

	def text(self) -> str:
		return self.name() + ' [' + str(self.id) + ']'

	def calculatePlotAmount(self) -> int:
		return sum([x.calculatePlotAmount() for x in self.children]) + 1

	def booleanPlot(self, plot: bool, signal: BooleanSignal) -> None:
		""" Plot for boolean semantics """
		if plot:
			PlotHelper().booleanPlot(signal.getTimes(), signal.getValues(), self.text(), 'r-')

	def quantitativePlot(self, plot: bool, signal: Signal) -> None:
		""" Plot for quantitative semantics"""
		if plot:
			PlotHelper().quantitativePlot(signal.getTimes(), signal.getValues(), self.text(), 'r-')
