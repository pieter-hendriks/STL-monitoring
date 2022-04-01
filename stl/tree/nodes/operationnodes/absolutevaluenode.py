from .operationnode import OperationNode
from ....signals import SignalList, BooleanSignal, Signal, SignalValue
from ....operators import computeAbsoluteValue
import math
from typing import List


class AbsoluteValueNode(OperationNode):

	def __init__(self):
		super().__init__()

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		result = self.children[0].quantitativeValidate(signals, plot)
		newTimestamps: List[float] = []
		for i in range(result.getCheckpointCount() - 1):
			if result.getCheckpoint(i).getValue() * result.getCheckpoint(i + 1).getValue() < 0:
				# If one of the two values is negative, and the other positive,
				# Compute the 0 point between them
				# checkpoint before the zero-point
				cp: SignalValue = result.getCheckpoint(i)
				newTimestamp: float = -cp.getValue() / cp.getDerivative() + cp.getTime()
				assert math.isclose(
				    (newTimestamp - cp.getTime()) * cp.getDerivative() + cp.getValue(), 0, rel_tol=1e-6
				), "Found zero point is not close to 0."
				newTimestamps.append(newTimestamp)

		for t in newTimestamps:
			# Value is always zero, because we've computed timestamps where the value is zero.
			# Derivative is computed later, so we can initialize it to 0 with no problem.
			result.emplaceCheckpoint(t, 0, 0)
		result.recomputeDerivatives()
		result.simplify()
		return computeAbsoluteValue(result)

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		# TODO: Verify correct! I think there isn't an absolute value in Boolean semantics.
		# So just making it a no-op makes sense (except for setting name -- required for test equality)
		result: Signal = self.children[0].booleanValidate(signals, plot)
		result.setName('absolutevalue')
		result.simplify()
		return result

	def text(self) -> str:
		return self.name()