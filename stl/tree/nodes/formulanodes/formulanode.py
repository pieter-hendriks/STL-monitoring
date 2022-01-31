from ..node import Node
import numpy as np
from ....utility import PlotHelper
from ....signals import Signal, BooleanSignal

class FormulaNode(Node):  # Abstract class
	def __init__(self):
		super().__init__()

	def text(self) -> str:
		return self.name() + ' [' + str(self.id) + ']'

	def calculatePlotAmount(self) -> int:
		return sum([x.calculatePlotAmount() for x in self.children]) + 1

	def booleanPlot(self, signal: BooleanSignal) -> None:
		PlotHelper().booleanPlot(signal.getTimes(), signal.getValues(), self.text(), 'r-')

	def quantitativePlot(self, signal: Signal) -> None:
		PlotHelper().quantitativePlot(signal.getTimes(), signal.getValues(), self.text(), 'r-')