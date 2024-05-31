
from enum import Enum, auto

from nested.n_parser import ASTIdentifier

# TODO: Instr, vs Opcode -- instr has args, opcode doesnt.
class OpCode(Enum):
    ADD = auto()
    NEG = auto()

    LOAD = auto()
    LOAD_INT = auto()
    LOAD_STR = auto()

    LIST = auto()

    ARGPUSH = auto()
    ARGPOP = auto()

    PUSH = auto()
    POP = auto()

    PRINT = auto()

    CALL = auto()

    BEGIN_MODULE = auto()
    END_MODULE = auto()

    def __rich_repr__(self):
        yield self.name

class Op:
    def __init__(self, opcode: OpCode, *args):
        self.opcode = opcode
        self.args = args

    def __rich_repr__(self):
        yield self.opcode.name
        yield from self.args

    @staticmethod
    def from_id(i: ASTIdentifier, *args):
        opcode = None
        match i.value:
            case "add":
                opcode = OpCode.ADD
            case "neg":
                opcode = OpCode.NEG
            case "list":
                opcode = OpCode.LIST
            case "load":
                opcode = OpCode.LOAD
            case "load_int":
                opcode = OpCode.LOAD_INT
            case "load_str":
                opcode = OpCode.LOAD_STR
            case "argpush":
                opcode = OpCode.ARGPUSH
            case "argpop":
                opcode = OpCode.ARGPOP
            case "push":
                opcode = OpCode.PUSH
            case "pop":
                opcode = OpCode.POP
            case "print":
                opcode = OpCode.PRINT
            case "call":
                opcode = OpCode.CALL
            case "begin_module":
                opcode = OpCode.BEGIN_MODULE
            case "end_module":
                opcode = OpCode.END_MODULE
            case _:
                raise ValueError(f"Unknown opcode: {i.value}")
        return Op(opcode, *args)