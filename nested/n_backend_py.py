from typing import List
from rich import print

from nested.n_codeobj import CodeObj
from nested.n_frame import Frame, SymTable
from nested.n_opcode import OpCode

def err(msg):
    raise ValueError(f"[red]Error: {msg}[/red]")

def msg(msg):
    print(f"[green]{msg}[/green]")

class VMIR:
    # Keep these functions separate as only in interpreter mode do we want to
    # cast things for example
    def run(self, code: CodeObj):
        frame = Frame(code, SymTable(), None)
        self.stack = []
        self.call_stack: List[Frame] = [frame]
        self.exec(frame)

    @property
    def ctx(self):
        return self.call_stack[-1]

    def exec(self, frame: Frame):
        while self.call_stack:
            frame = self.call_stack.pop()

            while frame.instr:
                op = frame.instr.opcode
                args = frame.instr.args
                # print(self.stack)
                print(f"{frame.ip:2} {op:2} {args}")
                next(frame)
                match op:
                    case OpCode.ADD:
                        self.add(*args)
                    case OpCode.PRINT:
                        self.print(*args)
                    case OpCode.LIST:
                        self.list(*args)
                    case OpCode.LOAD_INT:
                        self.load_type(OpCode.LOAD_INT, *args)
                    case OpCode.LOAD_STR:
                        self.load_type(OpCode.LOAD_STR, *args)
                    case OpCode.LOAD:
                        self.load(*args)
                    case OpCode.BEGIN_MODULE:
                        pass
                    case OpCode.END_MODULE:
                        pass
                    case OpCode.CALL:
                        pass
                    case _:
                        raise ValueError(f"Unknown opcode: {op}")
            return self.stack

    def add(self, n:int):
        try:
            self.stack.append(sum([self.stack.pop() for _ in range(n)]))
        except ValueError as e:
            err(str(e))

    def load_type(self, op: OpCode, v: str):
        match op:
            case OpCode.LOAD_INT:
                self.stack.append(int(v))
            case OpCode.LOAD_STR:
                self.stack.append(v)
            case _:
                err(f"Unknown type: {t}")

    def load(self, v: str):
        return self.ctx.getsym(v)

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")
        except IndexError:
            err("! Need more arguments")

    def list(self, n: int):
        self.stack.append([self.stack.pop() for _ in range(n)])

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")

        except IndexError:
            err("! Need more arguments")