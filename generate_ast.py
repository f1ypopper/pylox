
from email.mime import base


def defineAst(base_class:str, types):
	out_path = f"{base_class.lower()}.py"
	with open(out_path, "w") as file:
		file.write("from abc import ABC\n\n")
		file.write(f"class {base_class}(ABC):\n")
		file.write(f"    pass\n\n")
		
		for key, value in types.items():
			attr = ', '.join(value)
			file.write(f"class {key}({base_class}):\n")
			file.write(f"    def __init__(self, {attr}):\n")
			for attr in value:
				file.write(f"        self.{attr} = {attr}\n")
			file.write('\n')
			file.write(f"    def accept(self, visitor):\n")
			file.write(f"        return visitor.visit{key}{base_class}(self)\n")
			file.write("\n")


def main():
	types = {
		"Assign": ["name", "value"],
		"Binary": ["left", "operator", "right"],
		"Call": ["callee", "paren", "arguments"],
		"Get": ["object", "name"],
		"Set": ["object", "name", "value"],
		"Grouping": ["expression"],
		"Literal": ["value"],
		"Logical": ["left", "operator", "right"],
		"Unary": ["operator", "right"],
		"This": ["keyword"],
		"Variable": ["name"]
	}
	defineAst("Expr", types)
	defineAst(
		"Stmt", {
			"Block": ["statements"],
			"Class": ["name", "methods"],
			"Expression": ["expression"], 
			"Function": ["name", "params", "body"],
			"If": ["condition", "thenBranch", "elseBranch"],
			"Print": ["expression"],
			"Return": ["keyword","value"],
			"Var": ["name", "initializer"],
			"While": ["condition", "body"]
			}
	)

if __name__ == '__main__':
	main()
	