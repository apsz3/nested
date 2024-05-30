from lark import Tree
from enum import Enum, auto
from rich import print
from nested.n_parser import ASTUnOp, ASTNode, ASTModule, ASTBinOp, ASTConstantValue, ASTIdentifier, ASTProc
from nested.n_opcode import Op, OpCode

# Continuation -- add before / after / during, where during gets
# the parent class fn as an arg.


class Compiler:

    def __init__(self, tree: Tree):
        self.tree = tree
        self.buffer = []

    def emit(self, arg):
        self.buffer.append(arg)

    def compile_program(self):
        self.emit(Op(OpCode.BEGIN_MODULE, self))
        # Get metadata from self.tree here (not children)
        self.compile(self.tree.children)
        self.emit(Op(OpCode.END_MODULE, self))

    def compile(self, nodes):
        for node in nodes:
            self.compile_node(node)

    # def compile_op(self, node: ASTOp):
    #     if node.name == "add":
    #         self.emit(OpCode.ADD)
    #     else:
    #         raise ValueError(f"Unknown op: {node.name}")

    def compile_binop(self, node: ASTBinOp):
        if node.name == ASTBinOp.BinOps.ADD:
            self.compile_node(node.LExpr)
            self.compile_node(node.RExpr)
            self.emit(Op(OpCode.ADD))
        else:
            raise ValueError(f"Unknown binop: {node.name}")

    def compile_unop(self, node: ASTUnOp):
        if node.name == ASTUnOp.UnOps.NEG:
            self.compile_node(node.expr)
            self.emit(Op(OpCode.NEG))
        elif node.name == ASTUnOp.UnOps.PRINT:
            self.compile_node(node.expr)
            self.emit(Op(OpCode.PRINT))
        else:
            raise ValueError(f"Unknown unop: {node.name}")

    def compile_const(self, node: ASTConstantValue):
        if node.name == "int":
            self.emit(Op(OpCode.LOAD_INT, node.value))
        elif node.name == "string-lit":
            self.emit(Op(OpCode.LOAD_STR, node.value))
        else:
            raise ValueError(f"Unknown const: {node.name}")

    # def compile_proc_define(self, node: ASTProcDefn):
    #     ...

    def compile_proc(self, node: ASTProc):
        for child in node.children:
            self.compile_node(child)
            # self.emit(OpCode.ARGPUSH)
        self.emit(Op(OpCode.CALL, node.proc)) # ARGPUSH puts things on the arg stack, so we dont have to manage it.

    def compile_identifier(self, node: ASTIdentifier):
        self.emit(Op(OpCode.LOAD, node.value))

    def compile_node(self, node: ASTNode):
        if isinstance(node, ASTModule):
            self.compile_program(node.children)
        elif isinstance(node, ASTBinOp):
            self.compile_binop(node)
        elif isinstance(node, ASTConstantValue):
            self.compile_const(node)
        elif isinstance(node, ASTIdentifier):
            self.compile_identifier(node)
        elif isinstance(node, ASTUnOp):
            self.compile_unop(node)
        elif isinstance(node, ASTProc):
            self.compile_proc(node)
        # elif isinstance(node, ASTOp):
        #     breakpoint()
        else:
            raise ValueError(f"Unknown node type: {node}")
