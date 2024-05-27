from lark import Lark, v_args # type: ignore
from lark import Tree, Transformer

with open('C:/nested/nested.Lark', 'r') as file:
    grammar_contents = file.read()

parser = Lark(grammar_contents)
with open('C:/nested/test.nest', 'r') as file:
    input_contents = file.read()

result = parser.parse(input_contents)

from rich import print
print(result)

@v_args(inline=True)
class T(Transformer):

    def program(self, *children):
        return ('program', *children)

    @v_args(inline=True, meta=True)
    def s_expr(self, meta, *children):
        return ("s-expr", *children,)

    @v_args(inline=True, meta=True)
    def list(self, meta, *children):
        return ("list", *children,)

    @v_args(inline=True, meta=True)
    def number(self, meta, token):
        return ("int", token.value)

    @v_args(inline=True, meta=True)
    def atom(self, meta, token):
        return ("atom", token)

    @v_args(inline=True, meta=True)
    def string(self, meta, token):
        # Includes `""` in the string
        return ("string-lit", token.value)

    @v_args(inline=True, meta=True)
    def ident(self, meta, token):
        return ("identifier", token.value)

res: Tree= T().transform(parser.parse(input_contents))
print(res.children)
# for i in range(len(res.children)):
#     # Align the output with python string alignment for numbers in printing:
#     print(f"{i:2}: {res.children[i]}")