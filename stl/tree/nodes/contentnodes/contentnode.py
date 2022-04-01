from ..node import Node
from ....utility import PlotHelper
from ....signals import SignalList, Signal


class ContentNode(Node):

	def __init__(self):
		super().__init__()

	def validate(
	    self, signals: SignalList, semantic: str = 'quantitative', plot: bool = False
	) -> Signal:
		assert semantic in ['boolean', 'quantitative']
		# Create subplots
		if plot:
			plotAmount = self.calculatePlotAmount()
			PlotHelper().createSubplots(plotAmount)
		# Make sure we use the correct child functions based on current semantics
		if semantic == 'quantitative':
			result = self.children[0].quantitativeValidate(signals, plot)
		elif semantic == 'boolean':
			result = self.children[0].booleanValidate(signals, plot)
		else:
			raise RuntimeError(f"Unknown semantic specified: {semantic}")
		# Show the plots if we generated any
		if plot:
			PlotHelper().show()
		# Return the result
		return result
