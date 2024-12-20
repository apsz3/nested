from enum import Enum, auto

from nested.n_parser import ASTIdentifier


# TODO: Instr, vs Opcode -- instr has args, opcode doesnt.
class OpCode(Enum):
    ADD = auto()
    SUB = auto()

    NEG = auto()

    HD = auto()
    TL = auto()

    IF = auto()
    JUMP_IF_FALSE = auto()
    JUMP = auto()

    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    NOT = auto()

    QUOTE = auto()
    EVAL = auto()

    LOAD = auto()
    PUSH_REF = auto()

    LOAD_INT = auto()
    LOAD_STR = auto()
    LOAD_TRUE = auto()
    LOAD_FALSE = auto()
    LOAD_SYM = auto()

    CONS = auto()
    FST = auto()
    RST = auto()

    STORE = auto()

    ASSERT = auto()

    BEGIN = auto()
    PUSH_LIST = auto()

    PUSH_LAMBDA = auto()
    POP_LAMBDA = auto()

    PUSH_ARGS = auto()
    POP_ARGS = auto()

    CALL = auto()

    PRINT = auto()

    # Internal
    BEGIN_MODULE = auto()
    END_MODULE = auto()
    PUSH = auto()
    POP = auto()
    NOP = auto()

    # TODO should builtins IDs be like a ID(<name>)
    # so that instead of defining ne opcodes for every
    # reserved word we have something more modular?
    DEFMACRO = auto()
    INCLUDE = auto()
    PARAM = auto()
    
    def __rich_repr__(self):
        yield self.name

    def __repr__(self):
        return self.name


class Op:
    def __init__(self, opcode: OpCode, *args):
        self.opcode = opcode
        self.args = args

    def __rich_repr__(self):
        yield self.opcode
        yield from self.args

    def __repr__(self):
        return f"{self.opcode} {self.args}"
    
    @staticmethod
    def from_id(i: ASTIdentifier, *args):
        opcode = None
        match i.value:
            # Builtin primitives
            case "+":
                opcode = OpCode.ADD
            case "-":
                opcode = OpCode.SUB
            case ">":
                opcode = OpCode.GT
            case ">=":
                opcode = OpCode.GTE
            case "<":
                opcode = OpCode.LT
            case "<=":
                opcode = OpCode.LTE
            case "=":
                opcode = OpCode.EQ
            case "!=":
                opcode = OpCode.NEQ
            case "pos":
                opcode = OpCode.POS
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
            case "fst":
                opcode = OpCode.FST
            case "rst":
                opcode = OpCode.RST
            # case "'":
            #     opcode = OpCode.QUOTE
            case "eval":
                opcode = OpCode.EVAL
            case "cons":
                opcode = OpCode.CONS
            case "not":
                opcode = OpCode.NOT
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
            case "defmacro":
                opcode = OpCode.DEFMACRO
            case "include":
                opcode = OpCode.INCLUDE
            case "param":
                opcode = OpCode.PARAM
            # Conditionals and control flow
            case "if":
                opcode = OpCode.IF
            case "push_ref":
                opcode = OpCode.PUSH_REF
            case "load":
                opcode = OpCode.LOAD
            # Function calls
            case "call":
                opcode = OpCode.CALL
            case "quote":
                opcode = OpCode.QUOTE
            # Stack manipulation
            case "push":
                opcode = OpCode.PUSH
            case "pop":
                opcode = OpCode.POP
            case "begin_module":
                opcode = OpCode.BEGIN_MODULE
            case "end_module":
                opcode = OpCode.END_MODULE
            case "begin":
                opcode = OpCode.BEGIN
            case "assert":
                opcode = OpCode.ASSERT
            case _:
                raise ValueError(f"Unknown opcode: {i.value}")
        return Op(opcode, *args)
