from loxcallable import LoxCallable
from enviroment import Enviroment
from returnexecption import ReturnException

class LoxFunction(LoxCallable):
	def __init__(self, declaration, closure):
		self.declaration = declaration
		self.closure = closure	

	def arity(self):
		return len(self.declaration.params)

	def call(self, interpreter, arguments):
		environment = Enviroment(self.closure)
		for i in range(0, len(self.declaration.params)):
			environment.define(self.declaration.params[i].lexeme, arguments[i])
		try:	
			interpreter.executeBlock(self.declaration.body, environment)
		except ReturnException as returnValue:
			return returnValue.value
		return None

	def bind(self, instance):
		environment = Enviroment(self.closure)
		environment.define("this", instance)
		return LoxFunction(self.declaration, environment)

	def __str__(self):
		return f"<fn {self.declaration.name.lexeme}>"