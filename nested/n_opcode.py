
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
    def from_id(i: ASTIdentifier):
        match i.value:
            case "add":
                return Op(OpCode.ADD)
            case "neg":
                return Op(OpCode.NEG)
            case "list":
                return Op(OpCode.LIST)
            case "load":
                return Op(OpCode.LOAD)
            case "load_int":
                return Op(OpCode.LOAD_INT)
            case "load_str":
                return Op(OpCode.LOAD_STR)
            case "argpush":
                return Op(OpCode.ARGPUSH)
            case "argpop":
                return Op(OpCode.ARGPOP)
            case "push":
                return Op(OpCode.PUSH)
            case "pop":
                return Op(OpCode.POP)
            case "print":
                return Op(OpCode.PRINT)
            case "call":
                return Op(OpCode.CALL)
            case "begin_module":
                return Op(OpCode.BEGIN_MODULE)
            case "end_module":
                return Op(OpCode.END_MODULE)
            case _:
                raise ValueError(f"Unknown opcode: {i.value}")