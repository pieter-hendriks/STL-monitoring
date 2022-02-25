from typing import List
from ..signalvalue import SignalValue
from ...utility import Interval
import math
import warnings

def getValues(self) -> List[float]:
	""" Get the values for the signal. """
	return [x.getValue() for x in self.checkpoints]

def getTimes(self) -> List[float]:
	""" Get the times for the signal. """
	return [x.getTime() for x in self.checkpoints]

def getDerivatives(self) -> List[float]:
	""" Get the derivatives for the signal. """
	return [x.getDerivative() for x in self.checkpoints]

def getCheckpointCount(self) -> int:
	""" Get the size of the checkpoint list for the signal. """
	return len(self.checkpoints)

def getCheckpoints(self) -> List[SignalValue]:
	""" Get the list of checkpoints for the signal. """
	return self.checkpoints

def getName(self) -> str:
	""" Get the name for the signal. """
	return self.name

def setName(self, name: str) -> None:
	""" Set the Signal's name attribute. """
	self.name = name

def getLargestTime(self) -> float:
	""" Return the value of the largest timestamp """
	# Returns the checkpoint in self.checkpoints with c.getTime() largest
	return self.checkpoints[-1].getTime()

def getTime(self, index: int) -> float:
	"""Return the timestamp of the signal checkpoint at the specified index"""
	return self.checkpoints[index].getTime()

def getValue(self, index: int) -> float:
	"""Return the value of the signal checkpoint at the specified index"""
	#assert abs(index) < len(self.checkpoints), f"{abs(index)} >= {len(self.checkpoints)}. Access non-existent index."
	return self.checkpoints[index].getValue()

def getDerivative(self, index: int) -> float:
	"""Return the derivative of the signal checkpoint at the specified index"""
	#assert abs(index) < len(self.checkpoints), f"{abs(index)} >= {len(self.checkpoints)}. Access non-existent index."
	return self.checkpoints[index].getDerivative()

def getCheckpoint(self, index: int) -> SignalValue:
	"""Return the signal checkpoint at the specified index"""
	#assert abs(index) < len(self.checkpoints), f"{abs(index)} >= {len(self.checkpoints)}. Access non-existent index."
	return self.checkpoints[index]

def setValue(self, index: int, value: float) -> None:
	""" Set the value for the checkpoint at index. """
	self.checkpoints[index].setValue(value)

def setDerivative(self, index: int, derivative: float) -> None:
	""" Set the derivative for the checkpoint at index. """
	self.checkpoints[index].setDerivative(derivative)

def getDefinedTimeInterval(self) -> Interval:
	""" Returns the Interval of time over which this Signal is defined -- starts at the first sample point, ends at the last. """
	# Checkpoints are sorted by time, so we can just get this by index.
	return Interval(self.getTime(0), self.getTime(-1))


def popCheckpoint(self) -> SignalValue:
	"""Pop the last element from the chekcpoint list and return it"""
	return self.checkpoints.pop()

def addCheckpoint(self, sv: SignalValue) -> None:
	"""Add a checkpoint to the signal. Insertion location is determined by the SignalValue's timestamp"""
	if sv.getTime() in self.getTimes():
		assert math.isclose(sv.getValue(), self.getValue(self.computeIndexForTime(sv.getTime())), rel_tol=1e-7), "Ensure that we attempt to add identical checkpoints only. These can be safely dropped, others can't."
		return
	if sv.getTime() != int(sv.getTime()):
		time = sv.getTime()
	# Use the emplace method to make a copy
	# If we simply .add(sv) we reference the same object. This may cause issues in e.g. the derivative computations.
	self.emplaceCheckpoint(sv.getTime(), sv.getValue(), sv.getDerivative())
	#self.checkpoints.add(sv.copy())

# Similar to addCheckpoint, but creates the SignalValue internally
def emplaceCheckpoint(self, time: float, value: float, derivative: float = None) -> None:
	"""Add a (constructed) checkpoint to the signal. Insertion location is determined by the timestamp"""
	# if derivative is None:
	# 	warnings.warn("Replaced None derivative with 0. Ensure this is correct behaviour.")
	if time in self.getTimes():
		assert math.isclose(value, self.getValue(self.computeIndexForTime(time)), rel_tol=1e-7), "Ensure that we attempt to add identical checkpoints only. These can be safely dropped, others can't."
		return
	self.checkpoints.add(SignalValue(time, value, derivative if derivative is not None else 0))

def isEmpty(self) -> bool:
	""" Checks if the Signal is empty (i.e. contains no sample points)."""
	return self.getCheckpointCount() == 0

def isSingular(self) -> bool:
	""" Returns if the signal is defined by a single sample point. """
	return self.getCheckpointCount() == 1



