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


# def getSortedMergedListNoDuplicates(*args) -> List:
# 	""" Merge all parameters (iterables) into a single, sorted list with no duplicate elements. """
# 	ret: List = []
# 	# For each passed in list, put the entries in the combined list.
# 	for arg in args:
# 		assert isinstance(arg, Iterable), "Can't merge non-iterables!"
# 		if arg:
# 			ret.extend(arg)
# 	ret = sorted(ret)
# 	# Dict maintains insertion order and filters out duplicates
# 	# Turn back to list to output as a list
# 	return list(dict.fromkeys(ret))
