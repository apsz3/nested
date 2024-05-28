from lark import Lark, Visitor, v_args # type: ignore
from lark import Tree, Transformer
from lark.visitors import Interpreter

from pathlib import Path

cwd = Path(__file__).parent
with open(cwd / 'nested.Lark', 'r') as file:
    grammar_contents = file.read()
parser = Lark(grammar_contents)
from rich import print

def parse():
    # with open('C:/nested/nested/test.nest', 'r') as file:
    with open(cwd / 'test.nest', 'r') as file:

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
from rich import pretty
class ASTNode:

    def __init__(self, type: str, *children):
        self.type = type
        self.children = children
    def __rich_repr__(self):
        yield self.type
        yield from self.children

    # def __repr__(self):
    #     return str(pretty.Pretty(self.children))

class ASTLeaf(ASTNode):

    def __init__(self, type: str, value: str):
        super().__init__(type, None)
        self.value = value
    def __rich_repr__(self):
        yield self.type
        yield self.value
    # def __repr__(self):
    #     return str(pretty.Pretty(self))
@v_args(inline=True)
class T(Transformer):

    def program(self, *children):
        return ASTNode ('program', *children,)

    @v_args(inline=True, meta=True)
    def s_expr(self, meta, *children):
        return ASTNode ("s-expr", *children,)

    @v_args(inline=True, meta=True)
    def list(self, meta, *children):
        return ASTNode ("list", *children,)

    @v_args(inline=True, meta=True)
    def number(self, meta, token):
        return ASTLeaf ("int", token.value)

    @v_args(inline=True, meta=True)
    def atom(self, meta, token):
        return ASTNode ("atom", token)

    @v_args(inline=True, meta=True)
    def string(self, meta, token):
        # Includes `""` in the string
        return ASTLeaf ("string-lit", token.value)

    @v_args(inline=True, meta=True)
    def ident(self, meta, token):
        return ASTLeaf ("identifier", token.value)

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

