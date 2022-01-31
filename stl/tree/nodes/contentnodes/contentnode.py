from ..node import Node
import matplotlib.pyplot as plt
from ....utility import cm2inch, PlotHelper
from ....signals import SignalList
from typing import Union

class ContentNode(Node):
	def __init__(self):
		super().__init__()

	def validate(self, signals: SignalList, semantic: str = 'quantitative', plot: bool = False) -> Union[bool, float]:
		assert semantic in ['boolean', 'quantitative']
		if plot:  # Create subplots if necessary
			plotAmount = self.calculatePlotAmount()
			PlotHelper().createSubplots(plotAmount)
			result = self.children[0].validate(signals, semantic, True)
			PlotHelper().show()
			return result
		else:
			result = self.children[0].validate(signals, semantic, False)
			return result
