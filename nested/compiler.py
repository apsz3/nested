from lark import Tree
from enum import Enum, auto

# Continuation -- add before / after / during, where during gets
# the parent class fn as an arg.


class OpCode(Enum):
    ADD = auto()

    PREPARE_INT = auto()
    PREPARE_STR = auto()

    PUSH = auto()
    POP = auto()

    BEGIN_MODULE = auto()
    END_MODULE = auto()

class Compiler:

    def __init__(self, tree: Tree):
        self.tree = tree
        self.buffer = []

    def emit(self, arg):
        self.buffer.append(arg)

    def compile_program(self, nodes):
        self.emit(self, OpCode.BEGIN_MODULE)
        self.compile(nodes)
        self.emit(self, OpCode.END_MODULE)

    def compile(self, nodes):
        for node in nodes:
            self.compile_node(node)

    def compile_node(self, node):
        if node.data == 'int':
            self.compile_int(node)
        elif node.data == 'string-lit':
            self.compile_string(node)
        elif node.data == 'identifier':
            self.compile_identifier(node)
        elif node.data == 'list':
            self.compile_list(node)
        else:
            raise ValueError(f"Unknown node type: {node.data}")

