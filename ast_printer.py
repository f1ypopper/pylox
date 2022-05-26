from lib2to3.pgen2 import token
from expr import Expr, Binary, Grouping, Literal, Unary
from tokens import Token
import token_type
class AstPrinter(Expr):
	def __init__(self):
		pass
	
	def print(self, expr: Expr):
		return expr.accept(self)			
	
	def visitBinaryExpr(self, expr: Binary):
		return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
	
	def visitGroupingExpr(self, expr: Grouping):
		return self.parenthesize("group",expr.expression)
	
	def visitLiteralExpr(self, expr: Literal):
		return expr.value
	
	def visitUnaryExpr(self, expr: Unary):
		return self.parenthesize(expr.operator.lexeme, expr.right)
	
	def parenthesize(self, name:str , *exprs: Expr):
		out = ""
		out+=f"({name}"
		for expr in exprs:
			out+=f" {expr.accept(self)}"
		out+=")"
		return out


def main():
	expression: Binary = Binary(Unary(Token(token_type.MINUS, "-", None, 1),Literal(123)), Token(token_type.STAR, "*", None, 1), Grouping(Literal(45.29)))
	print(AstPrinter().print(expression))

if __name__ == '__main__':
	main()