""" Implementation for a SignalNode. """
from ..node import Node
from ....signals import SignalList, Signal, BooleanSignal


class SignalNode(Node):
	""" Class representing a Signal from an STL formula in as an AST node. """

	def __init__(self):
		super().__init__()
		self.signalName = None

	def processToken(self, token: str) -> None:
		self.signalName = str(token)

	def booleanValidate(self, signals: SignalList, plot: bool, booleanize=False) -> BooleanSignal:
		signal = signals.getByName(self.signalName)
		if booleanize:
			return BooleanSignal.fromSignal(signal)
		return signal

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		signal = signals.getByName(self.signalName)
		if isinstance(signal, BooleanSignal):
			signal = Signal.fromBooleanSignal(signal)
			signal.recomputeDerivatives()
		return signal

	def text(self) -> str:
		return 'Signal: ' + self.signalName
