from .point import Point
from typing import Tuple
import math

class LineSegment:
	def __init__(self, a: Point, b: Point):
		self.A = a
		self.B = b

	def intersects(self, other: 'LineSegment') -> bool:
		""" Method to check if the line segment X intersects the line segment Y\n
				Implementation does not count a point on the line as an intersection."""
		# ACD and BCD must have opposite orientation if the line segments intersect - ACD and BCD cannot both be counterclockwise.
		# Analogous for ABC and ABD
		return (Point.inCounterClockWiseOrder(self.A, other.A, other.B) != Point.inCounterClockWiseOrder(self.B, other.A, other.B) 
					and Point.inCounterClockWiseOrder(self.A, self.B, other.A) != Point.inCounterClockWiseOrder(self.A, self.B, other.B))

	def computeSlope(self) -> float:
		""" Compute the slope (derivative) of the line segment """
		return (self.B.y - self.A.y) / (self.B.x - self.A.x)

	def getIntersectionPoint(self, other: 'LineSegment') -> Point:
		""" Compute the point where self and other intersect """
		assert self.intersects(other), "Cannot find an intersection point for two line segments that do not intersect."
		m1, b1 = self.computeLineEquation()
		m2, b2 = other.computeLineEquation()
		# y1 must equal y2 to have an intersection (for line equation y=mx+b)
		# So m1x + b1 == m2x + b2 ==> x = (b2-b1)/(m1-m2)
		x = (b2 - b1) / (m1 - m2)
		assert math.isclose(m1 * x + b1, m2 * x + b2, rel_tol=1e-05), f"Failed to find an intersection! Computed y-values do not match."
		return Point(x, m1 * x + b1)

		
	def computeLineEquation(self) -> Tuple[float, float]:
		""" LineSegment is stored as defined between points A and B. This method computes the equation y = mx + b describing the line. """
		slope = self.computeSlope() # == m
		offset = self.A.y - (self.A.x * slope) # == b
		return (slope, offset)
