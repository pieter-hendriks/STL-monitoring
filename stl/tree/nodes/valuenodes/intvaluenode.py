from .valuenode import ValueNode
class IntValueNode(ValueNode):
	def __init__(self):
		super().__init__()

	def processToken(self, token: str) -> None:
		if token == '-':
			self.sign *= -1
			return
		self.value = self.sign * int(str(token))