class Point:
	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y
	
	@classmethod
	def inCounterClockWiseOrder(cls, A: 'Point', B: 'Point', C: 'Point') -> bool:
		""" Determine if the points A, B and C are in counter-clockwise order. """
		# If slope of AB < slope of AC, the points are in counter-clockwise order.
		# (B.y-A.y)/(B.x-A.x) < (C.y-A.y)/(C.x-A.x)
		# ==> (B.y-A.y)(C.x-A.x) < (C.y-A.y)(B.x-A.x) 
		return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)