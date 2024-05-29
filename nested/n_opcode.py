
from enum import Enum, auto
import rich

class OpCode(Enum):
    ADD = auto()
    NEG = auto()

    LOAD = auto()
    LOAD_INT = auto()
    LOAD_STR = auto()

    ARGPUSH = auto()
    ARGPOP = auto()

    PUSH = auto()
    POP = auto()

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