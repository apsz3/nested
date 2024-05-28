from compiler import Compiler

from parser import parse

from rich import print
p = parse().children[0]
p.visit()
print(p)