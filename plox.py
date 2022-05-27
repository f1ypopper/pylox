import sys
from ast_printer import AstPrinter
from tokens import Token
from token_type import *
from expr import Expr 

class Plox:
	def __init__(self):
		self.hadError = False

	def report(self, line, where, message):
		self.hadError = True
		print(f"[line {line}] Error: {where} : {message}")

	def error(self, line, message):
		self.report(line, "", message)

	def parser_error(self, token: Token, message: str):
		if (token.token_type == EOF):
			self.report(token.line, " at end", message)
		else:
			self.report(token.line, f" at {token.lexeme}", message)

	def run(self, source):
		from scanner import Scanner
		from parser import Parser
		scanner = Scanner(source, self.erroR)
		tokens = scanner.scanTokens()
		parser = Parser(tokens, self.parser_error)
		expression = parser.parse()
		if self.hadError: return 
		print(AstPrinter().print(expression))

	def run_file(self, path):
		source_text = ""
		with open(path, 'r') as source_file:
			source_text = source_file.read()

		self.run(source_text)
		if self.hadError:
			exit()


	def run_prompt(self):
		while True:
			print("> ", end='')
			line = str(input())
			if (line == ""):
				break
			self.run(line)
			self.hadError = False

	def main(self,args):
		if len(args) > 1:
			print("Usage: plox.py [script]")
			exit()
		elif (len(args) == 1):
			self.run_file(args[0])
		else:
			self.run_prompt()


if __name__ == '__main__':
	Plox().main(sys.argv[1:])
	
def error():
	pass