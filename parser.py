import constantly
from loxinstance import LoxInstance
from stmt import Block, Class, Expression, Function, If, Print, Return, Var, While
from tokens import Token
from token_type import *
from expr import Assign, Binary, Call, Get, Logical, Set, This, Unary, Literal, Grouping, Variable 
from plox import Plox

class ParserError(Exception):
	pass

class Parser:
	def __init__(self, tokens, parser_error):
		self.tokens = tokens
		self.current = 0
		self.parser_error = parser_error

	def parse(self):
		statements = []
		while not self.isAtEnd():
			statements.append(self.declaration())
		return statements

	def declaration(self):
		try:
			if self.match(CLASS): return self.classDeclaration()
			if self.match(FUN): return self.function("function")
			if self.match(VAR): return self.varDeclaration()
			return self.statement()
		except ParserError as error:
			self.synchronize()
			return None

	def classDeclaration(self):
		name = self.consume(IDENTIFIER, "Expect class name.")
		self.consume(LEFT_BRACE, "Expect '{' before class body.")
		methods = []
		while not self.check(RIGHT_BRACE) and not self.isAtEnd() :
			methods.append(self.function("method"))
		self.consume(RIGHT_BRACE, "Expect '}' after class body.")
		return Class(name, methods)

	def function(self, kind):
		name = self.consume(IDENTIFIER, f"Expect {kind} name.")
		self.consume(LEFT_PAREN, f"Expect '(' after {kind} name.")
		parameters = []
		if not self.check(RIGHT_PAREN):
			parameters.append(self.consume(IDENTIFIER, "Expect parameter name."))
			while self.match(COMMA):
				if len(parameters) >= 255:
					self.parser_error(self.peek(), "Can't have more than 255 parameters.")	
				parameters.append(self.consume(IDENTIFIER, "Expect parameter name."))
		self.consume(RIGHT_PAREN, "Expect ')' after parameters.")
		self.consume(LEFT_BRACE, "Expect '{' before "+kind+" body.")
		body = self.block()
		return Function(name, parameters, body)

	def varDeclaration(self):
		name = self.consume(IDENTIFIER, "Expect variable name.")
		initializer = None
		if self.match(EQUAL):
			initializer = self.expression()
		self.consume(SEMICOLON, "Expect ';' after variable declaration.")
		return Var(name, initializer)

	def statement(self):
		if self.match(IF): return self.ifStatement()
		if self.match(PRINT): return self.printStatement()
		if self.match(RETURN): return self.returnStatement()
		if self.match(WHILE): return self.whileStatement()
		if self.match(FOR): return self.forStatement()
		if self.match(LEFT_BRACE): return Block(self.block())
		return self.expressionStatement()

	def forStatement(self):
		self.consume(LEFT_PAREN, "Expect '(' after 'for'.")
		initializer = None
		if self.match(SEMICOLON):
			initializer = None
		elif self.match(VAR):
			initializer = self.varDeclaration()
		else:
			initializer = self.expressionStatement()
		condition = None
		if not self.check(SEMICOLON):
			condition = self.expression()
		self.consume(SEMICOLON, "Expect ';' after loop condition.")
		increment = None
		if not self.check(RIGHT_PAREN):
			increment = self.expression()
		self.consume(RIGHT_PAREN, "Expect ')' after for clauses.")
		body = self.statement()

		if increment != None:
			body = Block([body, Expression(increment)])
		
		if condition == None: 
			condition = Literal(True)
		body = While(condition, body)
		
		if initializer != None:
			body = Block([initializer, body])
		return body

	def whileStatement(self):
		self.consume(LEFT_PAREN, "Expect '(' after 'while'.")
		condition = self.expression()
		self.consume(RIGHT_PAREN, "Expect ')' after condition.")
		body = self.statement()
		return While(condition, body)

	def ifStatement(self):
		self.consume(LEFT_PAREN, "Expect '(' after 'if'.")
		condition = self.expression()
		self.consume(RIGHT_PAREN, "Expect ')' after if condition.")
		thenBranch = self.statement()
		elseBranch = None
		if self.match(ELSE):
			elseBranch = self.statement()
		return If(condition, thenBranch, elseBranch)

	def printStatement(self):
		value = self.expression()
		self.consume(SEMICOLON, "Expect ';' after value.")
		return Print(value)

	def returnStatement(self):
		keyword = self.previous()
		value = None
		if not self.check(SEMICOLON):
			value = self.expression()
		self.consume(SEMICOLON, "Expect ';' after return value.")
		return Return(keyword, value)

	def expressionStatement(self):
		expr = self.expression()
		self.consume(SEMICOLON, "Expect ';' after expression.")
		return Expression(expr)

	def block(self):
		statements = []
		while (not self.check(RIGHT_BRACE) and not self.isAtEnd()):
			statements.append(self.declaration())
		self.consume(RIGHT_BRACE, "Expect '}' after block.")
		return statements

	def expression(self):
		return self.assignment()

	def assignment(self):
		expr = self.orstmt()
		if self.match(EQUAL):
			equals = self.previous()
			value = self.assignment()
			if type(expr) == Variable:
				name = expr.name
				return Assign(name, value)
			elif isinstance(expr, LoxInstance):
				get = expr
				return Set(get.object, get.name, value)

			self.error(equals, "Invalid assignment target.")

		return expr 

	def orstmt(self):
		expr = self.andstmt()
		while self.match(OR):
			operator = self.previous()
			right = self.andstmt()
			expr = Logical(expr, operator, right)
		return expr
	
	def andstmt(self):
		expr = self.equality()
		while self.match(AND):
			operator = self.previous()
			right = self.equality()
			expr = Logical(expr, operator, right)
		return expr

	def equality(self):
		expr = self.comparison()

		while (self.match(BANG_EQUAL, EQUAL_EQUAL)):
			operator = self.previous()
			right = self.comparsion()
			expr = Binary(expr, operator, right)

		return expr

	def comparison(self):
		expr = self.term()
		while(self.match(GREATER, GREATER_EQUAL, LESS, LESS_EQUAL)):
			operator = self.previous()
			right = self.term()
			expr = Binary(expr, operator, right)	
		return expr

	def term(self):
		expr = self.factor()
		while self.match(MINUS, PLUS):
			operator = self.previous()
			right = self.factor()
			expr = Binary(expr, operator, right)
		return expr

	def factor(self):
		expr = self.unary()
		while self.match(SLASH, STAR):
			operator = self.previous()
			right = self.unary()
			expr = Binary(expr, operator, right)
		return expr

	def unary(self):
		if self.match(BANG, MINUS):
			operator = self.previous()
			right = self.unary()
			return Unary(operator, right)
		return self.call()

	def call(self):
		expr = self.primary()

		while True:
			if self.match(LEFT_PAREN):
				expr = self.finishCall(expr)	
			elif self.match(DOT):
				name = self.consume(IDENTIFIER, "Expect property name after '.'.")
				expr = Get(expr, name)
			else:
				break
		return expr 

	def finishCall(self, callee):
		arguments = []
		if not self.check(RIGHT_PAREN):
			arguments.append(self.expression())
			while self.match(COMMA):
				if len(arguments) >= 255:
					self.error(self.peek(), "Can't have more than 255 arguments.")
				arguments.append(self.expression())
		paren = self.consume(RIGHT_PAREN, "Expect ')' after arguments.")
		return Call(callee, paren, arguments)

	def primary(self):
		if (self.match(FALSE)): return Literal(False)
		if (self.match(TRUE)): return Literal(True)
		if (self.match(NIL)): return Literal(None)
		if (self.match(NUMBER, STRING)):
			return Literal(self.previous().literal)
		if self.match(IDENTIFIER):
			return Variable(self.previous())
		if self.match(THIS):
			return This(self.previous())
		if (self.match(LEFT_PAREN)):
			expr = self.expression()
			self.consume(RIGHT_PAREN, "Expect ')' after expression")
			return Grouping(expr)

	def match(self, *token_types):
		for token_type in token_types:
			if self.check(token_type):
				self.advance()
				return True

		return False
	
	def check(self, token_type):
		if self.isAtEnd(): return False
		return self.peek().token_type == token_type

	def advance(self):
		if not self.isAtEnd(): self.current+=1
		return self.previous()

	def isAtEnd(self):
		return self.peek().token_type == EOF
	
	def previous(self):
		return self.tokens[self.current - 1]

	def consume(self, token_type, message):
		if(self.check(token_type)): return self.advance()
		raise self.error(self.peek(), message)
	
	def error(self, token_type, message):
		self.parser_error(token_type, message)
		return ParserError()

	def peek(self):
		return self.tokens[self.current]

	def synchronize(self):
		self.advance()
		while not self.isAtEnd():
			if (self.previous().token_type == SEMICOLON): return

			if self.peek().token_type == CLASS | FUN | VAR | FOR:
				return

			self.advance()