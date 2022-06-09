""" Helper methods for STL functionality. """
from typing import List, Union


# Converts the given value from cm to inches
def cm2inch(value: float) -> float:
	""" Conversion function from centimeters to inches. """
	return value / 2.54


def getTimeListIntersection(a: List[float], b: List[float]) -> Union[bool, List[float]]:
	""" Gets the Boolean Intersection between two sets of times. """
	intersection = [max(a[0], b[0]), min([a[-1], b[-1]])]
	if intersection[0] > intersection[1]:
		return False
	return intersection
