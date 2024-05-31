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
        self.frame = frame

        self.stack = []
        self.call_stack: List[Frame] = [self.frame]

        self.exec()

    def exec(self):
        while self.call_stack:
            self.frame = self.call_stack.pop()

            while self.frame.instr:
                op = self.frame.instr.opcode
                args = self.frame.instr.args
                # print(self.stack)
                print(f"{self.frame.ip:2} {op:2} {args}")
                next(self.frame)
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
                    case OpCode.LOAD_REF:
                        self.load_ref(*args)
                    case OpCode.STORE:
                        self.store(*args)
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

    def load_ref(self, v: str):
        self.stack.append(v)

    def load_type(self, op: OpCode, v: str):
        match op:
            case OpCode.LOAD_INT:
                self.stack.append(int(v))
            case OpCode.LOAD_STR:
                self.stack.append(v)
            case _:
                err(f"Unknown type: {op}")

    def load(self, v: str):
        self.stack.append(self.frame.getsym(v))

    def store(self):
        # Can't just shove the symbol in with this Instr because
        # the symbol could be evaluated on the stack by compiling
        # and we need to execute to get the proper value... maybe TODO
        val, sym = self.stack.pop(), self.stack.pop()
        self.frame.setsym(sym, val)

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")
        except IndexError:
            err("! Need more arguments")

    def call(self, n: int):
        sym: str = self.stack.pop() # First load the code object
        co: CodeObj = self.frame.getsym(sym)
        new = Frame(co, SymTable(), self.frame)
        self.call_stack.append(new)

    def list(self, n: int):
        self.stack.append([self.stack.pop() for _ in range(n)])

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")

        except IndexError:
            err("! Need more arguments")