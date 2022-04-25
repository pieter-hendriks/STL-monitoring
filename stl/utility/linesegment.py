""" Module containing an implementation of a class representing a LineSegment in a 2D space. """
from typing import Tuple, List, Union
import math
from .point import Point


class LineSegment:
	''' Class representing a LineSegment in a 2D space. '''

	def __init__(self, a: Point, b: Point):
		self.A = a
		self.B = b
		assert self.A != self.B, "Coinciding points do not a line make"

	def intersects(self, other: 'LineSegment') -> bool:
		""" Method to check if the line segment X intersects the line segment Y\n
				Implementation does not count a point on the line as an intersection."""
		# ACD and BCD must have opposite orientation if the line segments intersect
		# ACD and BCD cannot both be counterclockwise (unless there is no intersection)
		# Analogous for ABC and ABD
		return (
		    Point.inCounterClockWiseOrder(self.A, other.A,
		                                  other.B) != Point.inCounterClockWiseOrder(self.B, other.A, other.B)
		    and Point.inCounterClockWiseOrder(self.A, self.B,
		                                      other.A) != Point.inCounterClockWiseOrder(self.A, self.B, other.B)
		)

	def computeSlope(self) -> float:
		""" Compute the slope (derivative) of the line segment """
		return (self.B.y - self.A.y) / (self.B.x - self.A.x)

	def computeIntersectionPoint(self, other: 'LineSegment') -> Point:
		""" Compute the point where self and other intersect """
		assert self.intersects(other), "Cannot find an intersection point for two line segments that do not intersect."
		m1, b1 = self.computeLineEquation()
		m2, b2 = other.computeLineEquation()
		# y1 must equal y2 to have an intersection (for line equation y=mx+b)
		# So m1x + b1 == m2x + b2 ==> x = (b2-b1)/(m1-m2)
		x = (b2-b1) / (m1-m2)

		assert math.isclose(
		    m1*x + b1, m2*x + b2, rel_tol=1e-7
		), "Failed to find an intersection! Computed y-values do not match."
		return Point(x, m1*x + b1)

	def computeLineEquation(self) -> Tuple[float, float]:
		""" LineSegment is stored as defined between points A and B.
		 This method computes the equation y = mx + b describing the line. """
		slope = self.computeSlope()  # == m
		offset = self.A.y - (self.A.x * slope)  # == b
		return (slope, offset)

	@classmethod
	def computeIntersectionPoints(
	    cls, lhsSegments: Union[List['LineSegment'], 'LineSegment'], rhsSegments: Union[List['LineSegment'],
	                                                                                    'LineSegment']
	) -> List[Point]:
		""" Computes the points (pair<time, value>) where self and other intersect.\n
		Returns a list of the intersection points. """
		# Handle all the trivial cases!
		if isinstance(lhsSegments, LineSegment):
			assert isinstance(rhsSegments, LineSegment), "Must be same type."
			if not lhsSegments.intersects(rhsSegments):
				return []
			return lhsSegments.computeIntersectionPoint(rhsSegments)

		assert isinstance(lhsSegments, list) and isinstance(rhsSegments, list)
		if not lhsSegments or not rhsSegments:
			return []
		assert isinstance(lhsSegments[0], LineSegment) and isinstance(rhsSegments[0], LineSegment)
		# Compute the intersection points!
		lhsIndex: int = 0
		rhsIndex: int = 0
		points: List[Point] = []
		while True:
			if lhsSegments[lhsIndex].intersects(rhsSegments[rhsIndex]):
				points.append(lhsSegments[lhsIndex].computeIntersectionPoint(rhsSegments[rhsIndex]))
			# Exit after appending for the last segments if we've handled the entire lists
			if lhsIndex == len(lhsSegments) - 1 and rhsIndex == len(rhsSegments) - 1:
				break
			# Increment the correct counter - the one where the next time value is smallest.
			if lhsIndex >= len(lhsSegments) - 1:
				rhsIndex += 1
			elif (rhsIndex >= len(rhsSegments) - 1 or lhsSegments[lhsIndex + 1].B.x <= rhsSegments[rhsIndex + 1].B.x):
				lhsIndex += 1
			else:
				rhsIndex += 1
		return points

	def __repr__(self):
		return f"LineSegment(Point({self.A.x}, {self.A.y}), Point({self.B.x}, {self.B.y}))"

	def __str__(self):
		return f"<{{{self.A.x}, {self.A.y}}}, {{{self.B.x}, {self.B.y}}}>"
