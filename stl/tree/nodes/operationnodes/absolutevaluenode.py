""" Implementation of node representing ABS operation in STL formula """
import math
from typing import List

from ..node import Node
from ....signals import SignalList, BooleanSignal, Signal, SignalValue
from ....operators import computeAbsoluteValue


class AbsoluteValueNode(Node):
	""" AST tree node representing the STL operation ABS """

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
		return computeAbsoluteValue(result)

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		result: Signal = self.children[0].booleanValidate(signals, plot)
		result.setName('absolutevalue')
		return result

	def text(self) -> str:
		return self.name()
