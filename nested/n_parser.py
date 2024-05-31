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

    def __init__(self, value, *children):
        self.value = value
        self.children = children

    @property
    # ALWAYS JUST FOR DEBUG / PRINT, NEVER SWITCH ON IT
    def _id(self) -> str:
        return self.__class__.__name__

    def __rich_repr__(self):
        yield self.value
        yield from self.children

    def visit(self):
        self.children = [child.visit() for child in self.children]
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

    def __init__(self, value):
        super().__init__(value, None)

    def visit(self):
        return self

    def __rich_repr__(self):
        yield self.value

class ASTConstantValue(ASTLeaf):
    def __init__(self, type: str, value: str):
        super().__init__(value)
        self.type = type

    def __rich_repr__(self):
        yield self.type
        yield self.value
class ASTUnOp(ASTNode):

    class UnOps(Enum):
        NEG = auto()
        PRINT = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.op = self.map(self.value)

    @staticmethod
    def map(op: str):
        if op == "sub": return ASTUnOp.UnOps.NEG
        elif op == "print": return ASTUnOp.UnOps.PRINT

    @property
    def expr(self):
        return self.children[0]

class ASTOp(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        self.children = [child.visit() for child in self.children]
        if len(self.children) == 1:
            return ASTUnOp(self.value, *self.children)
        elif len(self.children) == 2:
            return ASTBinOp(self.value, *self.children)    #     if self.value in ASTIdentifier.builtins:
        raise ValueError("non-op")

class ASTBinOp(ASTNode):

    class BinOps(Enum):
        ADD = auto()
        SUB = auto()
        MUL = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def op(self):
        return self.value

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

    @property
    def proc(self):
        return self.value #

    def visit(self):
        # self.proc = ASTIdentifier(self.name)
        self.children = [child.visit() for child in self.children]
        # RETURN WHETYHER WE DO A PRIMITIVE OP, OR A PROC, FROM HERE
        return self

class ASTList(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        if isinstance(self.value, ASTIdentifier):
            # Not a list
            if ASTIdentifier.is_builtin(self.value): # ID = "identifier"", VALUE = THE THING WE WANT e.g. "add"
                n = ASTOp(self.value, *self.children) # TODO: when do we visit this???
            else:
                n = ASTProc(self.value, *self.children)
            return n.visit()
        else:
            # It's a list / epxr
            self.children = [child.visit() for child in self.children]
            self.value = self.value.visit()
            return self

class ASTIdentifier(ASTLeaf):
    builtins = {
        "add", "sub", "print"
    }

    @staticmethod
    def is_builtin(node: "ASTIdentifier"):
        return node.value in ASTIdentifier.builtins

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        return ASTModule ("filename.nst", *children,)

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