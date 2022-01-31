import re 
from typing import Container, Tuple
from math import ceil
# Converts the given value from cm to inches
def cm2inch(value: float) -> float:
	return value / 2.54

# Computes the coordinates of the point where two lines intersect
def line_intersection(line1: Container, line2: Container) -> Tuple[float, float]:
	xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
	ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

	def det(a: Tuple, b: Tuple):
		return a[0] * b[1] - a[1] * b[0]

	div = det(xdiff, ydiff)
	if div == 0:
		raise Exception('lines do not intersect')

	d = (det(*line1), det(*line2))
	x = det(d, xdiff) / div
	y = det(d, ydiff) / div
	return x, y

def countOccurences(text: str, pattern: str) -> int:
	return len(re.findall(re.escape(pattern), text))

def binarySearch(item: object, container: Container, fn = lambda x: x) -> Tuple[int, object]:
	divisor = 2
	middle = ceil(len(container) / divisor)
	while fn(container[middle]) != item:
		divisor *= 2
		if fn(container[middle]) > item:
			middle -= ceil(len(container) / divisor)
		else:
			middle += ceil(len(container) / divisor)
	return middle, container[middle]