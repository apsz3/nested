from nested.n_opcode import OpCode
from rich import print
class VM:
    def __init__(self, code):
        self.code = code
        self.stack = []
        self.ip = 0

    def exec(self):
        while self.ip < len(self.code):
            instr = self.code[self.ip]
            op = instr.opcode
            args = instr.args
            print(self.stack)
            print(f"{self.ip:2} {op:2} {instr.args}")
            self.ip += 1
            match op:
                case OpCode.CALL:
                    proc = args[0]
                    breakpoint()
                    match proc:
                        case OpCode.ADD:
                            self.stack.append(self.stack.pop() + self.stack.pop())
                        case OpCode.NEG:
                            self.stack.append(-self.stack.pop())
                        case _: raise ValueError(f"Unknown opcode: {proc}")
                case OpCode.LOAD_INT:
                    self.stack.append(*args)
                case OpCode.LOAD_STR:
                    self.stack.append(*args)
                case OpCode.BEGIN_MODULE:
                    pass
                case OpCode.END_MODULE:
                    pass
                case _:
                    raise ValueError(f"Unknown opcode: {op}")
        return self.stack.pop()