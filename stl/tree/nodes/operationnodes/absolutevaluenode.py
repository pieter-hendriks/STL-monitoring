from .operationnode import OperationNode
from numbers import Number
from ....signals import SignalList, BooleanSignal, Signal
import warnings

class AbsoluteValueNode(OperationNode):
	def __init__(self):
		super().__init__()

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result = self.children[0].quantitativeValidate(signals, plot)
		result.computeAbsoluteValue()
		return result

	def booleanValidate(self, signals:SignalList, plot: bool) -> BooleanSignal:
		# TODO: Verify correct! I think there isn't an absolute value in Boolean semantics, technically,
		# So just making it a no-op makes sense.
		return self.children[0].booleanValidate(signals, plot)

	def text(self) -> str:
		return self.name()