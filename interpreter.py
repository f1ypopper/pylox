from enviroment import Enviroment
from expr import *
from loxcallable import LoxCallable
from loxclass import LoxClass
from loxfunction import LoxFunction
from loxinstance import LoxInstance
from stmt import Block, Class, Expression, Function, If, Print, Return, Var, While
from token_type import *
from tokens import Token
from globals import Clock
from returnexecption import ReturnException

class Interpreter:
	def __init__(self):
		self.globals = Enviroment()
		self.environment = self.globals
		self.globals.define("clock", Clock())

	def interpret(self, statements, lox):
		try:
			for statement in statements:
				self.execute(statement)
		except RuntimeError as error:
			lox.runtimeError(error)			

	def visitLiteralExpr(self, expr:Literal):
		return expr.value
	
	def visitGroupingExpr(self, expr: Grouping):
		return self.evaluate(expr.expression)

	def visitUnaryExpr(self, expr: Unary):
		right = self.evaluate(expr.right)

		if expr.operator.token_type == BANG:
			return not self.isTruthy(right)

		if expr.operator.token_type == MINUS:
			return -float(right)

		return None

	def visitWhileStmt(self, stmt: While):
		while self.isTruthy(self.evaluate(stmt.condition)):
			self.execute(stmt.body)
		return None

	def visitBinaryExpr(self, expr: Binary):
		left = self.evaluate(expr.left)
		right = self.evaluate(expr.right)

		operator = expr.operator.token_type

		if operator == GREATER:
			self.checkNumberOperands(expr.operator, left, right)
			return float(left) > float(right)

		if operator == GREATER_EQUAL:
			self.checkNumberOperands(expr.operator, left, right)
			return float(left) >= float(right)

		if operator == LESS:
			self.checkNumberOperands(expr.operator, left, right)
			return float(left) < float(right)
		
		if operator == LESS_EQUAL:
			self.checkNumberOperands(expr.operator, left, right)
			return float(left) <= float(right)

		if operator == BANG_EQUAL: return not self.isEqual(left, right)
		if operator == EQUAL_EQUAL: return self.isEqual(left, right)

		if operator == MINUS:
			self.checkNumberOperand(expr.operator, right)
			return float(left) - float(right)
		
		if operator == PLUS:
			if(type(left) == float and type(right) == float):
				return float(left) + float(right)

			if(type(left) == str and type(right) == str):
				return str(left) + str(right)

			raise RuntimeError(expr.operator, "Operator must be two numbers or two strings.")

		if operator == SLASH:
			self.checkNumberOperands(expr.operator, left, right)
			return float(left) / float(right)

		if operator == STAR:
			self.checkNumberOperands(expr.operator, left, right)
			return float(left) * float(right)

		return None

	def visitExpressionStmt(self, stmt: Expression):
		self.evaluate(stmt.expression)
		return None

	def visitPrintStmt(self, stmt: Print):
		value = self.evaluate(stmt.expression)
		print(self.stringify(value))
		return None

	def visitReturnStmt(self, stmt: Return):
		value = None
		if stmt.value != None: value = self.evaluate(stmt.value)
		raise ReturnException(value)

	def visitVarStmt(self, stmt: Var):
		value = None
		if stmt.initializer != None:
			value = self.evaluate(stmt.initializer)
		self.environment.define(stmt.name.lexeme, value)
		return None

	def visitVariableExpr(self, expr: Variable):
		return self.environment.get(expr.name)	

	def visitAssignExpr(self, expr: Assign):
		value = self.evaluate(expr.value)
		self.environment.assign(expr.name, value)
		return value

	def visitCallExpr(self, expr: Call):
		callee = self.evaluate(expr.callee)
		arguments = []
		for argument in expr.arguments:
			arguments.append(self.evaluate(argument))
		if not isinstance(callee, LoxCallable):
			raise RuntimeError(expr.paren, "Can only call functions and classes.")
		function = callee
		if len(arguments) != function.arity():
			raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
		return function.call(self, arguments)

	def visitGetExpr(self, expr: Get):
		obj = self.evaluate(expr.object)
		if isinstance(obj, LoxInstance):
			return obj.get(expr.name)
		raise RuntimeError(expr.name, "Only instances have properties.")

	def visitBlockStmt(self, stmt:Block):
		self.executeBlock(stmt.statements, Enviroment(self.environment))
		return None

	def visitIfStmt(self, stmt:If):
		if self.isTruthy(self.evaluate(stmt.condition)):
			self.execute(stmt.thenBranch)
		elif stmt.elseBranch != None:
			self.execute(stmt.elseBranch)

		return None

	def visitFunctionStmt(self, stmt: Function):
		function = LoxFunction(stmt, self.environment)
		self.environment.define(stmt.name.lexeme, function)
		return None

	def visitClassStmt(self, stmt: Class):
		self.environment.define(stmt.name.lexeme, None)
		methods = {}
		for method in stmt.methods:
			function = LoxFunction(method, self.environment)
			methods[method.name.lexeme] = function
		
		klass = LoxClass(stmt.name.lexeme, methods)

		self.environment.assign(stmt.name, klass)
		return None

	def visitLogicalExpr(self, expr: Logical):
		left = self.evaluate(expr.left)
		if expr.operator.token_type == OR:
			if self.isTruthy(left): return left
		else:
			if not self.isTruthy(left): return left
		return self.evaluate(expr.right)

	def visitSetExpr(self, expr: Set):
		obj = self.evaluate(expr.object)
		if not isinstance(obj, LoxInstance):
			raise RuntimeError(expr.name, "Only instances have fields.")
		value = self.evaluate(expr.value)
		obj.set(expr.name, value) 
		return value

	def visitThisExpr(self, expr: This):
		return self.lookupVariable(expr.keyword, expr)

	def executeBlock(self, statements, enviroment):
		previous = self.environment
		try:
			self.environment = enviroment
			for statement in statements:
				self.execute(statement)
		finally:
			self.environment = previous

	def evaluate(self, expr):
		return expr.accept(self)
	
	def execute(self, stmt):
		stmt.accept(self)
	
	def isTruthy(self, object):
		if object == None : return False
		if type(object) == bool: return bool(object)
		return True

	def isEqual(self, a, b):
		if a == None and b == None: return True
		if a == None: return False	
		return a == b
	
	def checkNumberOperand(self, operator: Token, operand):
		if type(operand) == float: return
		raise RuntimeError(operator, "Operand must be a number")
	
	def checkNumberOperands(self, operator: Token, left, right):
		if type(left) == float and type(right) == float: return
		raise RuntimeError(operator, "Operands must be numbers.")
	
	def stringify(self, object):
		if object == None: return "nil"

		if type(object) == float:
			text = str(object)
			if text.endswith(".0"):
				text = text[0: len(text) - 2]	
			return text
		
		return str(object)