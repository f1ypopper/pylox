import sys

hadError = False 

def report(line, where, message):
	print(f"[line {line}] Error: {where} : {message}")
	hadError = True

def error(line, message):
	report(line, "", message)

def run(source):
	scanner = Scanner(source)
	tokens = scanner.scanTokens()
	for token in tokens:
		print(token)

def run_file(path):
	source_text = ""
	with open(path, 'r') as source_file:
		source_text = soruce_file.read()

	run(source_text)
	if hadError:
		exit()


def run_promt():
	while True:
		print("> ", end='')
		line = str(input())
		if (line.empty()):
			break
		run(line)
		hadError = False

def main(args):
	if len(args) > 1:
		print("Usage: plox.py [script]")
		exit()
	elif (len(args) == 1):
		run_file(args[0])
	else:
		run_prompt()


if __name__ == '__main__':
	main(sys.argv[1:])
	