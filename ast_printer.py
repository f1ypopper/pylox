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

class RPN(Expr):
	def __init__(self):
		pass

	def print(self, expr: Expr):
		return expr.accept(self)
	
	def visitBinaryExpr(self, expr: Binary):
		return self.eval(expr.operator.lexeme , expr.left, expr.right)
	
	def visitUnaryExpr(self, expr: Unary):
		return self.eval(expr.operator.lexeme, expr.right)
	
	def visitLiteralExpr(self, expr: Literal):
		return expr.value

	def visitGroupingExpr(self, expr: Grouping):
		return self.eval(expr.expression)

	def eval(self, name: str, *exprs):
		out = ""
		for expr in exprs:
			out += f" {expr.accept(self)} "
		out += name
		return out


def main():
	expression: Binary = Binary(Unary(Token(token_type.MINUS, "-", None, 1),Literal(123)), Token(token_type.STAR, "*", None, 1), Grouping(Literal(45.29)))
	print(AstPrinter().print(expression))
	expression: Binary = Binary(Binary(Literal(1), Token(token_type.PLUS, "+", None, 1), Literal(2)), Token(token_type.STAR, "*", None, 1), Binary(Literal(4), Token(token_type.MINUS, "-", None, 1), Literal(3)))
	print(RPN().print(expression))
if __name__ == '__main__':
	main()