""" File containing an implementation of a point Data Structure. """


# pylint: disable=too-few-public-methods
class Point:
	""" Class representing a Point in a 2D space. """

	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y

	@classmethod
	def inCounterClockWiseOrder(cls, A: 'Point', B: 'Point', C: 'Point') -> bool:
		""" Determine if the points A, B and C are in counter-clockwise order. """
		# If slope of AB < slope of AC, the points are in counter-clockwise order.
		# (B.y-A.y)/(B.x-A.x) < (C.y-A.y)/(C.x-A.x)
		# ==> (B.y-A.y)(C.x-A.x) < (C.y-A.y)(B.x-A.x)
		return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

	def normalize(self) -> None:
		""" Processes the point coordinates to make them compatible with STL operation.
		At this time, this method rounds the time (x-coordinate) to 5 decimal digits."""
		self.x = round(self.x, 5)
