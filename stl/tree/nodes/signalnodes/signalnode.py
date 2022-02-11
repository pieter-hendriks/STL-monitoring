from ..node import Node
import warnings
import pandas as pd
from ....signals import SignalList, Signal, BooleanSignal
from typing import Union

class SignalNode(Node):
	def __init__(self):
		super().__init__()
		self.signalName = None

	def processToken(self, token: str) -> None:
		self.signalName = str(token)

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		signal = signals.getByName(self.signalName)
		if type(signal) != BooleanSignal:
			# Should be only other option
			assert type(signal) == Signal
			signal = BooleanSignal.fromSignal(signal)
		return signal

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		signal = signals.getByName(self.signalName)
		if type(signal) != Signal:
			# Should be only other option
			assert type(signal) == BooleanSignal
			signal = Signal.fromBooleanSignal(signal)
			# The boolean signal doesn't use derivatives, so we must initialize them in the quantitative signal
			signal.recomputeDerivatives() 
		return signal

	def text(self) -> str:
		return 'Signal: ' + self.signalName