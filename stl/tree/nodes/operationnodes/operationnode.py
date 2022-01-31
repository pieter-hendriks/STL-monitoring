from ..node import Node
class OperationNode(Node):  # Abstract class
	def __init__(self):
		super().__init__()

	def text(self):
		return "ABSTRACT OPERATION NODE"


