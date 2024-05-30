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

def parse(text):
    # with open('C:/nested/nested/test.nest', 'r') as file:


    # result = parser.parse(input_contents)
    res: Tree= T().transform(parser.parse(text))
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

    def visit(self):
        print(f"Visiting {self.name}")
        self.children = [child.visit() for child in self.children]

        # if isinstance(self.children[0], ASTOp):
        #     op = self.children[0]
        #     if len(self.children) == 2:
        #         return ASTUnOp(op, self.children[1])
        #     elif len(self.children) == 3:
        #         return ASTBinOp(op, self.children[1], self.children[2])

        return self

class ASTModule(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def num_stmts(self):
        return len(self.children)

    def visit(self):
        self.children = [child.visit() for child in self.children]
        return self

class ASTLeaf(ASTNode):

    def __init__(self, name: str, value: str):
        super().__init__(name, None)
        self.value = value

    def __rich_repr__(self):
        yield self.name
        yield self.value

    def visit(self):
        return self

class ASTConstantValue(ASTLeaf):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ASTUnOp(ASTNode):

    class UnOps(Enum):
        NEG = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.map(self.name.name)

    @staticmethod
    def map(op: str):
        if op == "sub": return ASTUnOp.UnOps.NEG

    @property
    def expr(self):
        return self.children[0]

class ASTOp(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        self.children = [child.visit() for child in self.children]
        if len(self.children) == 1:
            return ASTUnOp(self.name, *self.children)
        elif len(self.children) == 2:
            return ASTBinOp(self.name, *self.children)    #     if self.value in ASTIdentifier.builtins:
        raise ValueError("non-op")

class ASTBinOp(ASTNode):

    class BinOps(Enum):
        ADD = auto()
        SUB = auto()
        MUL = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.map(self.name.value)

    @staticmethod
    def map(op: str):
        if op == "add": return ASTBinOp.BinOps.ADD

    @property
    def LExpr(self):
        return self.children[0]

    @property
    def RExpr(self):
        return self.children[1]

class ASTProc(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proc = self.name # TODO: cheeky, fix

    def visit(self):
        # self.proc = ASTIdentifier(self.name)
        self.children = [child.visit() for child in self.children]
        # RETURN WHETYHER WE DO A PRIMITIVE OP, OR A PROC, FROM HERE
        return self

class ASTList(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        if ASTIdentifier.is_builtin(self.name):
            n = ASTProc(self.name, *self.children) # TODO: when do we visit this???
            n.visit()
            return n
        n = ASTOp(self.name, *self.children)
        n = n.visit()
        return n
        # self.children = [c.visit() for c in self.children]
        # self.name = "foo"
        # return self

class ASTIdentifier(ASTLeaf):
    builtins = {
        "add", "sub"
    }

    @staticmethod
    def is_builtin(node: "ASTIdentifier"):
        return node.name in ASTIdentifier.builtins

    def __init__(self, *args, **kwargs):
        super().__init__("identifier", *args, **kwargs)

    def visit(self):
        if self.value in ASTIdentifier.builtins:
            return ASTOp(self.value)
        return self

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

    @v_args(inline=True)
    def list(self, *children):
        return ASTList (*children)

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
        return ASTIdentifier (token.value)

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

