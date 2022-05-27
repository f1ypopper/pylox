from tokens import Token
from token_type import *
from expr import Binary, Unary, Literal, Grouping 
from plox import Plox

class ParserError(Exception):
	pass

class Parser:
	def __init__(self, tokens, parser_error):
		self.tokens = tokens
		self.current = 0
		self.parser_error = parser_error

	def parse(self):
		try: 
			return self.expression()
		except ParserError:
			return None

	def expression(self):
		return self.equality()
	
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
		return self.primary()
	
	def primary(self):
		if (self.match(FALSE)): return Literal(False)
		if (self.match(TRUE)): return Literal(TRUE)
		if (self.match(NIL)): return Literal(NIL)
		if (self.match(NUMBER, STRING)):
			return Literal(self.previous().literal)
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