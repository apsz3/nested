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
        self.value = self.value.visit()
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

# class ASTProc(ASTNode):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     @property
#     def proc(self):
#         return self.value #

#     def visit(self):
#         # self.proc = ASTIdentifier(self.name)
#         self.children = [child.visit() for child in self.children]
#         # RETURN WHETYHER WE DO A PRIMITIVE OP, OR A PROC, FROM HERE
#         return self

class ASTExpr(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        self.value = self.value.visit() # Visit the identifier to make it a Proc (builtin) or still just an ID (needs to be looked up in the symbol table)
        self.children = [child.visit() for child in self.children]
        # if isinstance(self.value, ASTIdentifier):
        #     # TODO: may not be necessary, just use ASTExpr still
        #     return ASTProc(self.value, *self.children)
        return self

class ASTList(ASTNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def visit(self):
    #     if isinstance(self.value, ASTIdentifier):
    #         n = ASTExpr(self.value, *self.children)
    #         return n.visit()
    #     else:
    #         # It's a list / epxr
    #         self.children = [child.visit() for child in self.children]
    #         self.value = self.value.visit()
    #         return self

    def visit(self):
        n = ASTExpr(self.value, *self.children)
        return n.visit()

class ASTOp(ASTLeaf):
    # ASTOp is a leaf, but it's a special leaf that represents a builtin
    # operation, which means we don't need to do any sort of symbol lookup
    # on the identifier and load code or values to call -- we just
    # go straight to the VM instructions for it.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ASTIdentifier(ASTLeaf):
    builtins = {
        "add", "sub", "print", "list",
        "let"
    }

    @property
    def is_builtin(self):
        return self.value in ASTIdentifier.builtins

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        if self.is_builtin:
            return ASTOp(self.value)
        return self

@v_args(inline=True)
class T(Transformer):
    # TODO: might be cleaner to have a raw, vanilla Parse transformer,
    # them take that and feed it through a different visitor class that
    # yields the AST nodes.
    def program(self, *children):
        # breakpoint()
        return ASTModule ("filename.nst", *children,)

    # @v_args(inline=True, meta=True)
    # def s_expr(self, meta, *children):
    #     return ASTNode ("s-expr", *children,)

    # @v_args(inline=True, meta=True)
    # def op(self, meta, *children):
    #     return ASTIdentifier("op", *children)


        # if len(children) == 1:
        #     return ASTUnOpExpr(children[0])
        # return ASTBinOpExpr ("foo", *children)

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