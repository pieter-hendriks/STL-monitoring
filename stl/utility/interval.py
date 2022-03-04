from numbers import Number

class Interval:
	def __init__(self, a: Number, b: Number):
		assert isinstance(a, Number) and isinstance(b, Number), "A and B must both be Numbers when used in Interval"
		self.lowerLimit = a
		self.upperLimit = b
	
	def getLower(self) -> float:
		""" Get the lower limit of the interval. """
		return self.lowerLimit

	def getUpper(self) -> float:
		""" Get the upper limit of the interval. """
		return self.upperLimit
		
	@classmethod
	def computeIntersection(cls, lhs: 'Interval', rhs: 'Interval') -> 'Interval':
		""" Compute the intersection between the two intervals.\n\nFor intervals [a, b] and [c,d], this is [max(a,c), min(b,d)]."""
		return Interval(
			max(lhs.getLower(), rhs.getLower()),
			min(lhs.getUpper(), rhs.getUpper())
		)

	def contains(self, value: float, closed: bool = True) -> bool:
		""" Checks if the value is in the interval (closed): lower <= value <= upper """
		if closed:
			return self.getLower() <= value <= self.getUpper()
		return self.getLower() <= value < self.getUpper()
	
	def isSingular(self) -> bool:
		""" Checks if the Interval is singular (upper == lower)"""
		return self.getLower() == self.getUpper()

	def __eq__(self, other: 'Interval') -> bool:
		if not isinstance(other, Interval):
			return super().__eq__(other)
		return self.lowerLimit == other.lowerLimit and self.upperLimit == other.upperLimit
	
	def __str__(self) -> str:
		return self.__repr__()

	def __repr__(self) -> str:
		return f"Interval({self.lowerLimit}, {self.upperLimit})"

	def __add__(self, c: Number) -> 'Interval':
		return Interval(self.lowerLimit + c, self.upperLimit + c)

	def __sub__(self, c: Number) -> 'Interval':
		return Interval(self.lowerLimit - c, self.upperLimit - c)

	def __mult__(self, c: Number) -> 'Interval':
		return Interval(self.lowerLimit * c, self.upperLimit * c)

	def __truediv__(self, c: Number) -> 'Interval':
		return Interval(self.lowerLimit / c, self.upperLimit / c)
	