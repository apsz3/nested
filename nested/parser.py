from lark import Lark, Visitor, v_args # type: ignore
from lark import Tree, Transformer
from lark.visitors import Interpreter
from enum import Enum, auto
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

    def __init__(self, name: str, *children):
        self.name = name
        self.children = children
    def __rich_repr__(self):
        yield self.name
        yield from self.children

class ASTModule(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def num_stmts(self):
        return len(self.children)

class ASTLeaf(ASTNode):

    def __init__(self, name: str, value: str):
        super().__init__(name, None)
        self.value = value

    def __rich_repr__(self):
        yield self.name
        yield self.value

class ASTConstantValue(ASTLeaf):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ASTUnOp(ASTNode):

        class UnOps(Enum):
            NEG = auto()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @staticmethod
        def map(op: str):
            if op == "neg": return ASTUnOp.UnOps.NEG

        @property
        def expr(self):
            return self.children[0]

class ASTOp(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ASTBinOp(ASTNode):

    class BinOps(Enum):
        ADD = auto()
        SUB = auto()
        MUL = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def map(op: str):
        if op == "str": return ASTBinOp.BinOps.ADD

    @property
    def LExpr(self):
        return self.children[0]

    @property
    def RExpr(self):
        return self.children[1]

class ASTIdentifier(ASTLeaf):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@v_args(inline=True)
class T(Transformer):
    # TODO: might be cleaner to have a raw, vanilla Parse transformer,
    # them take that and feed it through a different visitor class that
    # yields the AST nodes.
    def program(self, *children):
        return ASTModule ('program', *children,)

    # @v_args(inline=True, meta=True)
    # def s_expr(self, meta, *children):
    #     return ASTNode ("s-expr", *children,)

    # @v_args(inline=True, meta=True)
    # def op(self, meta, *children):
    #     return ASTIdentifier("op", *children)


        # if len(children) == 1:
        #     return ASTUnOp(children[0])
        # return ASTBinOp ("foo", *children)

    @v_args(inline=True, meta=True)
    def list(self, meta, *children):
        return ASTNode ("list", *children,)

    @v_args(inline=True, meta=True)
    def number(self, meta, token):
        return ASTConstantValue ("int", token.value)

    # @v_args(inline=True, meta=True)
    # def atom(self, meta, token):
    #     return ASTNode ("atom", token)

    @v_args(inline=True, meta=True)
    def string(self, meta, token):
        # Includes `""` in the string
        return ASTConstantValue ("string-lit", token.value)

    @v_args(inline=True, meta=True)
    def ident(self, meta, token):
        return ASTIdentifier ("identifier", token.value)

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

