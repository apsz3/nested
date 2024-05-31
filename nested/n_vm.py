from nested.n_codeobj import CodeObj
from nested.n_frame import Frame, SymTable
from nested.n_opcode import OpCode
from rich import print
from nested.n_vm_ir import VMIR

class VM:
    def __init__(self, ir = VMIR()):
        self.ir = ir
        self.global_frame = Frame(SymTable(), SymTable(), None) # Would be where you load STDLIBs

    def run(self, code: CodeObj):
        self.exec(code, self.global_frame)

    def exec(self, code: CodeObj, frame: Frame):
        while self.ip < len(self.code):
            instr = self.code[self.ip]
            op = instr.opcode
            args = instr.args
            print(self.stack)
            print(f"{self.ip:2} {op:2} {instr.args}")
            self.ip += 1
            match op:
                # case OpCode.CALL:
                #     proc = args[0]
                #     match proc:
                #         case OpCode.ADD:
                #             self.stack.append(self.stack.pop() + self.stack.pop())
                #         case OpCode.NEG:
                #             self.stack.append(-self.stack.pop())
                #         case _: raise ValueError(f"Unknown opcode: {proc}")
                case OpCode.ADD:
                    self.ir.add(self.stack)
                case OpCode.PRINT:
                    self.ir.print(self.stack)
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
        return self.stack
