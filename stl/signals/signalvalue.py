""" Implementation of a Signal Value """
from typing import List
import warnings
import math


class SignalValue:
	""" Data container class for signal values
	A signal is a collection of these, sorted by self.timestamp (ascending) """

	def __init__(self, time: float, value: float, derivative: float = None) -> None:
		self.timestamp: float = float(time)
		self.value: float = float(value)
		self.derivative: float = float(derivative)
		if derivative is None:
			warnings.warn("SignalValue is auto-assigning derivative = 0 where it was None.")
			self.derivative = 0

	def getTime(self) -> float:
		""" Return the SignalValue's timestamp """
		return self.timestamp

	def getValue(self) -> float:
		""" Return the SignalValue's value """
		return self.value

	def getDerivative(self) -> float:
		""" Return the SignalValue's derivative """
		return self.derivative

	def copy(self) -> float:
		""" Return a copy of the SignalValue.
		Used to avoid having references to the same SV in
		multiple Signals. This would cause problems when changes to the Signal occur,
		since they would also be made in different Signals the SV is a part of. """
		return SignalValue(self.timestamp, self.value, self.derivative)

	# WARNING: Using this on a checkpoint that is inside a SortedList will lead to hard to find buggy behaviour.
	# It is imperative that this function only be used before the checkpointed is inserted in a SortedList, as the
	# SortedList uses the timestamp attribute of the SignalValue class as the key to sort by.
	def setTime(self, v: float) -> None:
		"""
		Sets the timestamp for the SignalValue instance.
		This method must not be used when the checkpoint has been inserted in a container that sorts by the timestamp.
		"""
		self.timestamp = float(v)

	def setValue(self, v: float) -> None:
		""" Change the value for this SV """
		self.value = float(v)

	def setDerivative(self, v: float) -> None:
		""" Change the derivative for this SV """
		self.derivative = float(v)

	def __str__(self) -> str:
		return f"SignalValue<T={self.timestamp},V={self.value},D={self.derivative}>"

	def __repr__(self) -> str:
		return f"SignalValue({self.timestamp.__repr__()}, {self.value.__repr__()}, {self.derivative.__repr__()})"

	def __eq__(self, other: 'SignalValue') -> bool:
		if type(other) is not type(self):
			super().__eq__(other)
		return (
		    math.isclose(self.timestamp, other.timestamp, rel_tol=1e-7)
		    and math.isclose(self.value, other.value, rel_tol=1e-7)
		    and math.isclose(self.derivative, other.derivative, rel_tol=1e-7)
		)

	def oldFormat(self) -> List[List[float]]:
		""" Conver the SV to the old format; [[times], [values], [derivatives]] """
		return [[self.getTime()], [self.getValue()], [self.getDerivative()]]
