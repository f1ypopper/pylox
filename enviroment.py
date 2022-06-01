class Enviroment:
	def __init__(self, enclosing=None):
		self.enclosing: Enviroment = enclosing
		self.values = {}
	
	def define(self, name, value):
		self.values[name] = value

	def get(self, name):
		if name.lexeme in self.values:
			return self.values.get(name.lexeme)

		if self.enclosing != None: return self.enclosing.get(name)

		raise RuntimeError(name, f"Undefined variable {name.lexeme}.")
	
	def assign(self, name, value):
		if name.lexeme in self.values:
			self.values[name.lexeme] = value
			return 
		
		if self.enclosing != None:
			self.enclosing.assign(name, value)
			return

		raise RuntimeError(name, f"Undefined variable {name.lexeme}.")