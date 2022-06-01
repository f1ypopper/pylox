from loxcallable import LoxCallable
import time

class Clock(LoxCallable):
	def __init__(self):
		pass

	def arity(self):
		return 0
	
	def call(self, interpreter, arguments):
		return time.time()

	def toString(self):
		return "<native fn>"