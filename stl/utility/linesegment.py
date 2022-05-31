""" Module containing an implementation of a class representing a LineSegment in a 2D space. """
from typing import Tuple, List
import math
from .point import Point


class LineSegment:
	''' Class representing a LineSegment in a 2D space. '''

	def __init__(self, a: Point, b: Point):
		self.A = a
		self.B = b
		assert self.A != self.B, "Coinciding points do not a line make"

	def intersects(self: 'LineSegment', other: 'LineSegment') -> bool:
		""" Method to check if the line segment X intersects the line segment Y\n
				The edge points are excluded; if the intersection is at either A1==A2 or B1==B2, False is returned."""
		# ACD and BCD must have opposite orientation if the line segments intersect
		# ACD and BCD cannot both be counterclockwise (unless there is no intersection)
		# Analogous for ABC and ABD
		return (
		    Point.inCounterClockWiseOrder(self.A, other.A,
		                                  other.B) != Point.inCounterClockWiseOrder(self.B, other.A, other.B)
		    and Point.inCounterClockWiseOrder(self.A, self.B,
		                                      other.A) != Point.inCounterClockWiseOrder(self.A, self.B, other.B)
		)

	def computeSlope(self: 'LineSegment') -> float:
		""" Compute the slope (derivative) of the line segment """
		return (self.B.y - self.A.y) / (self.B.x - self.A.x)

	def computeIntersectionPoint(self: 'LineSegment', other: 'LineSegment') -> Point:
		""" Compute the point where self and other intersect """
		assert self.intersects(other), "Cannot find an intersection point for two line segments that do not intersect."
		m1, b1 = self.computeLineEquation()
		m2, b2 = other.computeLineEquation()
		# y1 must equal y2 to have an intersection (for line equation y=mx+b)
		# So m1x + b1 == m2x + b2 ==> x = (b2-b1)/(m1-m2)
		x = round((b2-b1) / (m1-m2), 5)
		return Point(x, m1*x + b1)

	def computeLineEquation(self: 'LineSegment') -> Tuple[float, float]:
		""" LineSegment is stored as defined between points A and B.
		 This method computes the equation y = mx + b describing the line. """
		slope = self.computeSlope()  # == m
		offset = self.A.y - (self.A.x * slope)  # == b
		return (slope, offset)

	@classmethod
	def computeIntersectionPoints(
	    self: 'LineSegment.__class__', lhsSegments: List['LineSegment'], rhsSegments: List['LineSegment']
	) -> List[Point]:
		""" Computes the points (pair<time, value>) where self and other intersect.\n
		Returns a list of the intersection points.
		PRECONDITION: All X-coordinates between the lines must be identical.
			This is achieved by pre-processing using Signal.computeCheckpointsForComparableSignals"""
		# Handle all the trivial cases!
		if not lhsSegments or not rhsSegments:
			return []
		# Compute the intersection points!
		index: int = 0
		points: List[Point] = []
		if lhsSegments[0].A == rhsSegments[0].A:
			points.append(lhsSegments[0].A)
		while True:
			if lhsSegments[index].B == rhsSegments[index].B:
				points.append(lhsSegments[index].B)
			if lhsSegments[index].intersects(rhsSegments[index]):
				points.append(lhsSegments[index].computeIntersectionPoint(rhsSegments[index]))
			# Exit after appending for the last segments if we've handled the entire lists
			if index == len(lhsSegments) - 1:
				break
			index += 1
		return points

	def __repr__(self):
		return f"LineSegment(Point({self.A.x}, {self.A.y}), Point({self.B.x}, {self.B.y}))"

	def __str__(self):
		return f"<{{{self.A.x}, {self.A.y}}}, {{{self.B.x}, {self.B.y}}}>"
