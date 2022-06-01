from tokens import Token
from token_type import (
	AND,
	BANG,
	BANG_EQUAL,
	CLASS,
	COMMA,
	DOT,
	ELSE,
	EOF,
	EQUAL,
	LESS,
	EQUAL_EQUAL,
	FALSE,
	GREATER,
	GREATER_EQUAL,
	IDENTIFIER,
	IF,
	LEFT_BRACE,
	LEFT_PAREN,
	LESS_EQUAL,
	MINUS,
	NIL,
	NUMBER,
	PLUS,
	PRINT,
	RETURN,
	RIGHT_BRACE,
	RIGHT_PAREN,
	SEMICOLON,
	SLASH,
	STAR,
	STRING,
	SUPER,
	THIS,
	TRUE,
	VAR,
	FUN,
	IF,
	ELSE,
	FOR,
	OR,
	WHILE,
)

keywords = {}
keywords["and"] = AND
keywords["class"] = CLASS
keywords["else"] = ELSE
keywords["false"] = FALSE
keywords["true"] = TRUE
keywords["for"] = FOR
keywords["fun"] = FUN
keywords["if"] = IF
keywords["nil"] = NIL
keywords["or"] = OR
keywords["print"] = PRINT
keywords["return"] = RETURN
keywords["super"] = SUPER
keywords["this"] = THIS
keywords["var"] = VAR
keywords["while"] = WHILE


class Scanner:
	def __init__(self, source: str, error):
		self.source = source
		self.tokens = []
		self.start = 0
		self.current = 0
		self.line = 1
		self.error = error

	def scanTokens(self):
		while not self.isAtEnd():
			self.start = self.current
			self.scanToken()
		self.tokens.append(Token(EOF, "", None, self.line))
		return self.tokens

	def scanToken(self):
		c = self.advance()
		if c == "(":
			self.addToken(LEFT_PAREN)
		elif c == ")":
			self.addToken(RIGHT_PAREN)
		elif c == "{":
			self.addToken(LEFT_BRACE)
		elif c == "}":
			self.addToken(RIGHT_BRACE)
		elif c == ",":
			self.addToken(COMMA)
		elif c == ".":
			self.addToken(DOT)
		elif c == "-":
			self.addToken(MINUS)
		elif c == "+":
			self.addToken(PLUS)
		elif c == ";":
			self.addToken(SEMICOLON)
		elif c == "*":
			self.addToken(STAR)
		elif c == "!":
			self.addToken(BANG_EQUAL if self.match("=") else BANG)
		elif c == "=":
			self.addToken(EQUAL_EQUAL if self.match("=") else EQUAL)
		elif c == "<":
			self.addToken(LESS_EQUAL if self.match("=") else LESS)
		elif c == ">":
			self.addToken(GREATER_EQUAL if self.match("=") else GREATER)
		elif c == "/":
			if self.match("/"):
				while self.peek() != "\n" and self.isAtEnd():
					self.advance()
			else:
				self.addToken(SLASH)
		elif c == " ":
			pass
		elif c == "\r":
			pass
		elif c == "\t":
			pass
		elif c == "\n":
			self.line += 1
		elif c == '"':
			self.string()
		else:
			if self.isDigit(c):
				self.number()
			elif self.isAlpha(c):
				self.identifier()
			else:
				self.error(self.line, f"({c})Unexpected character.")

	def isDigit(self, c):
		return c >= "0" and c <= "9"

	def isAlpha(self, c):
		return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

	def isAlphaNumeric(self, c):
		return self.isAlpha(c) or self.isDigit(c)

	def identifier(self):
		token_type = IDENTIFIER
		while self.isAlphaNumeric(self.peek()):
			self.advance()
			text = self.source[self.start:self.current]
			token_type = keywords.get(text)
			if (token_type == None):
				token_type = IDENTIFIER
		self.addToken(token_type)

	def number(self):
		while self.isDigit(self.peek()):
			self.advance()

		if self.peek() == "." and self.isDigit(self.peekNext()):
			self.advance()
			while self.isDigit(self.peek()):
				self.advance()

		self.addToken(NUMBER, float(self.source[self.start: self.current]))

	def string(self):
		while self.peek() != '"' and not self.isAtEnd():
			self.advance()
			if self.peek() == "\n":
				line += 1

		if self.isAtEnd():
			self.error(line, "Unterminated string.")

		# Consume '"'
		self.advance()
		value = self.source[self.start + 1: self.current-1]
		self.addToken(STRING, value)

	def peek(self):
		if self.isAtEnd():
			return "\0"
		return self.source[self.current]

	def peekNext(self):
		if self.current + 1 >= len(self.source):
			return "\0"
		return self.source[self.current + 1]

	def match(self, expected):
		if self.isAtEnd():
			return False
		if self.source[self.current] != expected:
			return False
		self.current += 1
		return True

	def advance(self):
		self.current += 1
		return self.source[self.current - 1]

	def addToken(self, t_type, literal=None):
		text = self.source[self.start: self.current]
		self.tokens.append(Token(t_type, text, literal, self.line))

	def isAtEnd(self):
		return self.current >= len(self.source)
