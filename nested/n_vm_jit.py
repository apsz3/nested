from typing import List
from nested.n_codeobj import CodeObj
from nested.n_frame import Frame, SymTable
from nested.n_opcode import OpCode
from rich import print
from nested.n_backend_py import VMIR

class VMJit:
    """
    Orchestrate execution from Python,
    but call out to the backend for the actual work.
    """
    def __init__(self, backend = VMIR()):
        self.ir = backend

    def run(self, code: CodeObj):
        frame = Frame(code, SymTable(), None)
        self.exec(frame)

    def exec(self, frame: Frame):
        self.stack = []
        self.call_stack: List[Frame] = [frame]
        while self.call_stack:
            frame = self.call_stack.pop()

            while frame.instr:
                op = frame.instr.opcode
                args = frame.instr.args
                # print(self.stack)
                print(f"{frame.ip:2} {op:2} {args}")

                next(frame)

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
                        self.ir.add(self.stack, *args)
                    case OpCode.PRINT:
                        self.ir.print(self.stack, *args)
                    case OpCode.LIST:
                        self.ir.list(self.stack, *args)
                    case OpCode.LOAD_INT:
                        self.ir.load_type(self.stack, OpCode.LOAD_INT, *args)
                    case OpCode.LOAD_STR:
                        self.ir.load_type(self.stack, OpCode.LOAD_STR, *args)
                    case OpCode.LOAD:
                        self.ir.load(self.stack, *args)
                    case OpCode.BEGIN_MODULE:
                        pass
                    case OpCode.END_MODULE:
                        pass
                    case OpCode.CALL:
                        pass
                    case _:
                        raise ValueError(f"Unknown opcode: {op}")
            return self.stack
