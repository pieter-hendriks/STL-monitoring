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
	
	def __eq__(self, other: 'Interval') -> bool:
		if not isinstance(other, Interval):
			return super().__eq__(other)
		return self.lowerLimit == other.lowerLimit and self.upperLimit == other.upperLimit
	
	def __str__(self) -> str:
		return self.__repr__()

	def __repr__(self) -> str:
		return f"Interval({self.lowerLimit}, {self.upperLimit})"

	def __add__(self, const: Number) -> 'Interval':
		return Interval(self.lowerLimit + const, self.upperLimit + const)

	def __sub__(self, const: Number) -> 'Interval':
		return Interval(self.lowerLimit - const, self.upperLimit + const)

	def __mult__(self, const: Number) -> 'Interval':
		return Interval(self.lowerLimit * const, self.upperLimit + const)

	def __div__(self, const: Number) -> 'Interval':
		return Interval(self.lowerLimit / const, self.upperLimit + const)