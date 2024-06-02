
from enum import Enum, auto

from nested.n_parser import ASTIdentifier

# TODO: Instr, vs Opcode -- instr has args, opcode doesnt.
class OpCode(Enum):
    ADD = auto()
    NEG = auto()

    PRINT = auto()

    IF = auto()

    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()

    TRUE = auto()
    FALSE = auto()

    HD = auto()
    TL = auto()

    LOAD = auto()
    PUSH_REF = auto()

    LOAD_INT = auto()
    LOAD_STR = auto()
    LOAD_SYM = auto()

    STORE = auto()

    PUSH_LIST = auto()

    PUSH_LAMBDA = auto()
    POP_LAMBDA = auto()

    PUSH_ARGS = auto()
    POP_ARGS = auto()

    CALL = auto()

    PUSH = auto()
    POP = auto()

    BEGIN_MODULE = auto()
    END_MODULE = auto()

    def __rich_repr__(self):
        yield self.name

class Op:
    def __init__(self, opcode: OpCode, *args):
        self.opcode = opcode
        self.args = args

    def __rich_repr__(self):
        yield self.opcode
        yield from self.args

    @staticmethod
    def from_id(i: ASTIdentifier, *args):
        opcode = None
        match i.value:
            # Builtin primitives
            case "add":
                opcode = OpCode.ADD
            case "neg":
                opcode = OpCode.NEG
            case "print":
                opcode = OpCode.PRINT

            # List
            case "list":
                opcode = OpCode.PUSH_LIST
            case "hd":
                opcode = OpCode.HD
            case "tl":
                opcode = OpCode.TL
            # Value operations
            case "lambda":
                opcode = OpCode.PUSH_LAMBDA
            case "load_int":
                opcode = OpCode.LOAD_INT
            case "load_str":
                opcode = OpCode.LOAD_STR
            # Symbol operations
            case "let":
                opcode = OpCode.STORE
            case "if":
                opcode = OpCode.IF
            case "push_ref":
                opcode = OpCode.PUSH_REF
            case "load":
                opcode = OpCode.LOAD
            # Function calls
            case "call":
                opcode = OpCode.CALL
            # Stack manipulation
            case "push":
                opcode = OpCode.PUSH
            case "pop":
                opcode = OpCode.POP

            case "begin_module":
                opcode = OpCode.BEGIN_MODULE
            case "end_module":
                opcode = OpCode.END_MODULE
            case _:
                raise ValueError(f"Unknown opcode: {i.value}")
        return Op(opcode, *args)