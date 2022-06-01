class ReturnException(Exception):
	def __init__(self, value):
		super().__init__("Return")
		self.value = value