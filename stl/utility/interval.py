from numbers import Number

class Interval:
	def __init__(self, a: Number, b: Number):
		assert isinstance(a, Number) and isinstance(b, Number), "A and B must both be Numbers when used in Interval"
		self.lowerLimit = a
		self.upperLimit = b
	
	def getLower(self) -> float:
		return self.lowerLimit

	def getUpper(self) -> float:
		return self.upperLimit