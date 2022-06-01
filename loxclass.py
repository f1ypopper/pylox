from loxcallable import LoxCallable
from loxinstance import LoxInstance

class LoxClass(LoxCallable):
	def __init__(self, name, methods):
		self.name = name
		self.methods = methods

	def call(self, interpreter, arguments):
		instance = LoxInstance(self)	
		return instance

	def arity(self):
		return 0

	def findMethod(self, name):
		if name in self.methods:
			return self.methods.get(name)
		return None

	def __str__(self) -> str:
		return self.name
	
