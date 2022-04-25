""" Implementation of some utility methods for STL """
from typing import Union, List
from .signals import Signal


def getTimeListIntersection(a: List[float], b: List[float]) -> Union[bool, Signal]:
	""" Gets the Boolean Intersection between two sets of times. """
	intersection = [max(a[0], b[0]), min([a[-1], b[-1]])]
	if intersection[0] > intersection[1]:
		return False
	return intersection
