import re 
from typing import Container, Tuple
from math import ceil
# Converts the given value from cm to inches
def cm2inch(value: float) -> float:
	return value / 2.54

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