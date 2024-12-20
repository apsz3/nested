from lark import Lark, Visitor, v_args  # type: ignore
from lark import Tree, Transformer
from lark.visitors import Interpreter
from enum import Enum, auto
from pathlib import Path

cwd = Path(__file__).parent
with open(cwd / "nested.Lark", "r") as file:
    grammar_contents = file.read()
parser = Lark(grammar_contents)
from rich import print


def parse(text, module_name):
    # with open('C:/nested/nested/test.nest', 'r') as file:

    # result = parser.parse(input_contents)
    res: Tree = T(module_name).transform(parser.parse(text))
    # print(res.children)
    return res

def read_and_parse(fname):
    # Parse module
    with open(fname, "r") as fp:
        return parse(fp.read().strip(), fname)

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

    def __repr__(self):
        return f'{self.value} {self.children}'
    
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

    def __hash__(self):
        return hash(self.value)
    
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


class ASTExpr(ASTNode):
    # An Expr denotes application whenever it is in a parenthetical form,
    # with the exception of special forms like `let`, `define`, etc.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def visit(self):
        self.value = (
            self.value.visit()
        )  # Visit the identifier to make it a Proc (builtin) or still just an ID (needs to be looked up in the symbol table)
        self.children = [child.visit() for child in self.children]

        # if isinstance(self.value, ASTIdentifier):
        #     # TODO: may not be necessary, just use ASTExpr still
        #     return ASTProc(self.value, *self.children)
        return self


class ASTList(ASTNode):
    def __init__(self, *args, **kwargs):
        if args == tuple(): # '()
            super().__init__(ASTIdentifier("empty"))
        else:
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
        if n.value == ASTIdentifier("include"):
            path = n.children[0].value
            parsed = read_and_parse(path)
            tree = parsed.children[0]
            return tree.visit()
        return n.visit()


class ASTOp(ASTLeaf):
    # ASTOp is a leaf, but it's a special leaf that represents a builtin
    # operation, which means we don't need to do any sort of symbol lookup
    # on the identifier and load code or values to call -- we just
    # go straight to the VM instructions for it.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __eq__(self, a):
        return isinstance(a, ASTOp) and a.value == self.value

    def __hash__(self):
        return hash(self.value)
    
class ASTIdentifier(ASTLeaf):
    builtins = {
        "+",
        "-",
        "*",
        "/",
        "//",
        "%",
        "=",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "eval",
        "list",
        "fst",
        "rst",
        "cons",
        "assert",
        "quote",
        "hd",
        "tl",
        "if",
        "let",
        "begin",
        "lambda",
        "defmacro",
        "print",
        "include",
        "pos",
        "not",
        "neg",  # unary ops, can be invoked with token shortcut, or as actual op.
        "param" # CLI will read everything from STDIN, PARAM just means we bind the CLI args to that.
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

    def __eq__(self, a):
        return isinstance(a, ASTIdentifier) and a.value == self.value
    
@v_args(inline=True)
class T(Transformer):
    def __init__(self, module_name:str = "UNSPECIFIED_MODULE"):
        self.module_name = module_name
    #    The question-mark prefixing value (”?value”) tells the tree-builder to inline this branch if it has only one member. In this case, value will always have only one member, and will always be inlined.

    # TODO: might be cleaner to have a raw, vanilla Parse transformer,
    # them take that and feed it through a different visitor class that
    # yields the AST nodes.
    def program(self, *children):
        return ASTModule(
            self.module_name,
            *children,
        )

    @v_args(inline=True)
    def list(self, *children):
        return ASTList(*children)

    # @v_args(meta=True, inline=True)
    # def op(self, meta, token, *args):
    #     return ASTExpr(ASTOp(token.value), *[a.value for a in args])

    # @v_args(meta=True, inline=True)
    # def v_op(self, meta, op, *exprs):
    #     return ASTExpr(ASTOp(op.value), *exprs)

    # @v_args(meta=True, inline=True)
    # def un_op(self, meta, op, atom):
    #     match op:
    #         case "+":
    #             return ASTExpr(ASTOp("pos"), self.number(meta, atom))
    #         case "-":
    #             return ASTExpr (ASTOp ("neg"), self.number(meta, atom))
    #         case "!":
    #             return ASTExpr (ASTOp ("not"), self.number(meta, atom))
    #         case _:
    #             raise ValueError(f"Unknown unary op: {op}")
    #     # # return ASTExpr (ASTOp (op), token)

    @v_args(inline=True, meta=True)
    def number(self, meta, token):
        return ASTConstantValue("int", token.value)

    @v_args(inline=True, meta=True)
    def string(self, meta, token):
        # Includes `""` in the string
        return ASTConstantValue("string-lit", token.value)

    @v_args(inline=True, meta=True)
    def ident(self, meta, token):
        return ASTIdentifier(token.value)

    @v_args(inline=True, meta=True)
    def qtd(self, meta, expr):
        if not isinstance(expr, ASTList):
            return ASTExpr(ASTOp("quote"), expr)
        # Treat the list as a single value with space delimiters
        # TODO: handle quoting large lists with operators and embedded quotes...?
        return ASTExpr(ASTOp("quote"), expr.value, *expr.children) # * to UNPACK the list so we don't double-nest parens

    # @v_args(inline=True, meta=True)
    # def symbol(self, meta, token):
    #     return ASTExpr(ASTOp("'"), ASTIdentifier(token.value))
