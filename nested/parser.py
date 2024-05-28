from lark import Lark, Visitor, v_args # type: ignore
from lark import Tree, Transformer
from lark.visitors import Interpreter

with open('C:/nested/nested/nested.Lark', 'r') as file:
    grammar_contents = file.read()
parser = Lark(grammar_contents)
from rich import print

def parse():
    with open('C:/nested/nested/test.nest', 'r') as file:
        input_contents = file.read()

    # result = parser.parse(input_contents)
    res: Tree= T().transform(parser.parse(input_contents))
    # print(res.children)
    return res



# class ASTNode(Tree):
#     def __init__(self, name, children):
#         self.data = name
#         self.children = children
#         self._meta = []

#     def __repr__(self):
#         return f"ASTNode({self.data}, {self.children})"

#     def visit(self):
#         return tuple(child.visit() for child in self.children)

class ASTNode:

    def __init__(self, type: str, children):
        self.type = type
        self.children = children

@v_args(inline=True)
class T(Transformer):

    def program(self, *children):
        return ('program', *children,)

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

@v_args(inline=True)
class I(Interpreter):
    # To have this work on the transformer parse tree,
    # need to make each rule in the Transformer return a Tree() object
    def program(self, *children):
        return ('program', *children)

    # @v_args(inline=True, meta=True)
    # def s_expr(self, meta, *children):
    #     return ("s-expr", *children,)

    # @v_args(inline=True, meta=True)
    # def list(self, meta, *children):
    #     return ("list", *children,)

    # @v_args(inline=True, meta=True)
    # def number(self, meta, token):
    #     return ("int", token.value)

    # @v_args(inline=True, meta=True)
    # def atom(self, meta, token):
    #     return ("atom", token)

    # @v_args(inline=True, meta=True)
    # def string(self, meta, token):
    #     # Includes `""` in the string
    #     return ("string-lit", token.value)

    # @v_args(inline=True, meta=True)
    # def ident(self, meta, token):
    #     return ("identifier", token.value)




# print(I().interpret(res))

