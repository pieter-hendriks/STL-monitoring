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
		return signals.getByName(self.signalName)

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		return signals.getByName(self.signalName)

	def text(self) -> str:
		return 'Signal: ' + self.signalName