import warnings
class SignalValue:
	# Data container class for signal values
	# A signal is a collection of these, sorted by self.timestamp (ascending)
	def __init__(self, time: float, value: float, derivative: float = None) -> None:
		self.timestamp: float = float(time)
		self.value: float = float(value)
		self.derivative: float = float(derivative)
		if derivative is None:
			warnings.warn("SignalValue is auto-assigning derivative = 0 where it was None.")
			self.derivative = 0

	def getTime(self) -> float:
		return self.timestamp

	def getValue(self) -> float:
		return self.value

	def getDerivative(self) -> float:
		return self.derivative
	
	def setTime(self, v: float) -> None:
		raise NotImplementedError("Modifying time would require re-sorting the SignalValue list. This operation is unsupported.")
	
	def setValue(self, v: float) -> None:
		self.value = float(v)
	
	def setDerivative(self, v:float) -> None:
		self.derivative = float(v)
	
	def __str__(self):
		return f"SignalValue<T={self.timestamp},V={self.value},D={self.derivative}>"
	def __repr__(self):
		return f"SignalValue({self.timestamp.__repr__()}, {self.value.__repr__()}, {self.derivative.__repr__()})"

	def __eq__(self, other: 'SignalValue'):
		return self.timestamp == other.timestamp and self.value == other.value and self.derivative == other.derivative

	def oldFormat(self):
		return [[self.getTime()], [self.getValue()], [self.getDerivative()]]
