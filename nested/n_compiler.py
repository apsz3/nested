from lark import Tree
from enum import Enum, auto
from rich import print
from nested.n_parser import ASTExpr, ASTList, ASTNode, ASTModule, ASTConstantValue, ASTIdentifier, ASTOp
from nested.n_opcode import Op, OpCode

# Continuation -- add before / after / during, where during gets
# the parent class fn as an arg.
# opmap = {
#     ASTUnOpExpr.UnOps.NEG: OpCode.NEG,
#     ASTVaryOpExpr.VaryOps.PRINT: OpCode.PRINT,
#     ASTBinOpExpr.BinOps.ADD: OpCode.ADD
# }
class Compiler:

    def __init__(self, tree: Tree):
        self.tree = tree
        self.buffer = []

    def emit(self, arg):
        self.buffer.append(arg)

    def compile_program(self):
        self.emit(Op(OpCode.BEGIN_MODULE, "META"))
        # Get metadata from self.tree here (not children)
        self.compile(self.tree.children)
        self.emit(Op(OpCode.END_MODULE, "META"))

    def compile(self, nodes):
        for node in nodes:
            self.compile_node(node)

    # def compile_op(self, node: ASTOp):
    #     if node.id == "add":
    #         self.emit(OpCode.ADD)
    #     else:
    #         raise ValueError(f"Unknown op: {node.id}")

    # Note: The main purpose of unop and binop
    # is so that we don't have to use generic Call
    # instructions to execute builtins
    # def compile_binop(self, node: ASTBinOpExpr):
    #     if (op := opmap.get(node.op)):
    #         self.compile_node(node.LExpr)
    #         self.compile_node(node.RExpr)
    #         self.emit(Op(op)) # TODO: make these constant objects?
    #     else:
    #         raise ValueError(f"Unknown binop: {node.op}")

    # def compile_varyop(self, node: ASTVaryOpExpr):
    #     if (op := opmap.get(node.op)) is None:
    #         raise ValueError(f"Unknown varyop: {node.op}")

    #     for child in node.children:
    #         self.compile_node(child)
    #     self.emit(Op(op))

    # def compile_unop(self, node: ASTUnOpExpr):
    #     if node.op == ASTUnOpExpr.UnOps.NEG:
    #         self.compile_node(node.expr)
    #         self.emit(Op(OpCode.NEG))
    #     elif node.op == ASTUnOpExpr.UnOps.PRINT:
    #         self.compile_node(node.expr)
    #         self.emit(Op(OpCode.PRINT))
    #     else:
    #         breakpoint()
    #         raise ValueError(f"Unknown unop: {node.op}")

    def compile_const(self, node: ASTConstantValue):
        if node.type == "int":
            self.emit(Op(OpCode.LOAD_INT, node.value))
        elif node.type == "string-lit":
            self.emit(Op(OpCode.LOAD_STR, node.value))
        else:
            raise ValueError(f"Unknown const: {node.type}")

    # def compile_expr_define(self, node: ASTProcDefn):
    #     ...
    # def compile_list(self, node: ASTList):
    #     for child in node.children:
    #         self.compile_node(child)
    #     self.compile_node(node.value) # TODO: What is this doing?
    #     self.emit(OpCode.LIST, len(node.children)) # Retrieve the last K values
    def compile_ref(self, node: ASTIdentifier):
        self.emit(Op(OpCode.LOAD_REF, node.value))

    def compile_expr(self, node: ASTExpr):
        # TODO: Check arity here for builtins etc .. ?

        # Special case: for definition, we must push a Ref,
        # not the value itself, for the symbol to be resolved.
        # We cannot thus compile the children ahead of inspecting that,
        # as for the symbol we are defining, we would issue a Load
        # which would fail on execution
        if isinstance(node.value, ASTOp): # builtin, just call its opcode
            op = Op.from_id(node.value)
            opcode = op.opcode
            if opcode == OpCode.STORE:
                sym = node.children[0]
                self.compile_ref(sym)
                for child in node.children[1:]:
                    self.compile_node(child)
                self.emit(op)
                return

        for child in node.children:
            self.compile_node(child)
        if isinstance(node.value, ASTOp): # builtin, just call its opcode
            self.emit(Op.from_id(node.value, len(node.children)))
        elif isinstance(node.value, ASTIdentifier):
            #resolved_value = node.value # TODO: adjust
            self.compile_identifier(node.value)
            self.emit(Op(OpCode.CALL, len(node.children)))
        elif isinstance(node.value, ASTExpr):
            # Need this for things like ((eval 'add) 1 2)); need to eval procs too
            self.compile_expr(node.value)
        else:
            raise ValueError(f"Unknown expr: {node.value}")

    def compile_identifier(self, node: ASTIdentifier):
        self.emit(Op(OpCode.LOAD, node.value))

    def compile_node(self, node: ASTNode):
        if isinstance(node, ASTModule):
            self.compile_program(node.children)
        elif isinstance(node, ASTExpr):
            self.compile_expr(node)
        elif isinstance(node, ASTConstantValue):
            self.compile_const(node)
        elif isinstance(node, ASTIdentifier):
            self.compile_identifier(node)
        elif isinstance(node, ASTExpr):
            self.compile_expr(node)
        else:
            raise ValueError(f"Unknown node type: {node}")
