from ..signalvalue import SignalValue
from typing import List

def shift(self, offset: float) -> 'Signal': # type: ignore (unsupported annotation)
	"""Take the current timestamps, subtract offset"""
	cp: SignalValue
	newCheckpoints: List[SignalValue] = []
	for cp in self.checkpoints:
		newCheckpoints.append(SignalValue(cp.getTime() + offset, cp.getValue(), cp.getDerivative()))
	return self.fromCheckpoints(f"{self.name}_shift", newCheckpoints)

def merge(self, other: 'Signal') -> None: # type: ignore
	""" Takes all checkpoints from other and merges them into self.\n
	Requires that the timestamps are not equal for all checkpoints where the checkpoints are not identical. """
	assert all([cp.getTime() not in self.getTimes() or self.getCheckpoint(self.computeIndexForTime(cp.getTime())) == cp for cp in other.getTimes()])
	for cp in other.getCheckpoints():
		self.addCheckpoint(cp)


def recomputeDerivatives(self):
	"""Re-compute the derivatives part of each SignalValue, to make sure it matches the current values."""
	if self.checkpoints: # no-op if empty list
		for i in range(len(self.checkpoints) - 1):
			valueDiff = self.checkpoints[i+1].getValue() - self.checkpoints[i].getValue()
			timeDiff = self.checkpoints[i+1].getTime() - self.checkpoints[i].getTime()
			if timeDiff == 0:
				assert False, "This shouldn't be possible - means we have a double time entry."
			self.checkpoints[i].setDerivative(valueDiff / timeDiff)
			if self.checkpoints[i+1].getValue() - self.checkpoints[i].getValue() != 0 and self.checkpoints[i].getDerivative() == 0:
				assert False, "wtf"
		self.checkpoints[-1].setDerivative(0)