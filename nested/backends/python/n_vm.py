from typing import List
from rich import print

from nested.backends.python.n_codeobj import CodeObj, FunObj, ParamObj
from nested.backends.python.n_frame import Frame, SymTable
from nested.n_opcode import Op, OpCode

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

    def exec_defn_lambda(self, start, stop):
        # Iterate over the list, handling three sections:
        # Begin Args, End Args, and End Lambda:
        # TODO: optimize
        ip = 0

         # Skip the PUSH_ARGS instr # TODO: fix this, not necessary probably
        instrs = self.frame.code[start+1:stop]

        # ITerate over the frame, collecting arguments
        # until the POP_ARGS opcode is reached, then continue
        # collecting the body of the lambda until the POP_LAMBDA:
        end_args_ip = list(map(lambda i: i.opcode, instrs)).index(OpCode.POP_ARGS)
        start_body_ip = end_args_ip + 1
        args = instrs[0:end_args_ip]
        body = instrs[start_body_ip:]
        params = []
        for a in args:
            if a.opcode == OpCode.PUSH_REF:
                params.append(ParamObj(a.args[0], 'type'))
            else:
                err(f"Unknown opcode in args: {a.opcode}")
        # begin_args_ip = start+1
        # end_args_ip = _opcodes.index(OpCode.POP_ARGS)
        # start_body_ip = end_args_ip+1
        # end_body_ip = stop-1

        # args = self.frame.instrs[begin_args_ip:end_args_ip]
        # body = self.frame.instrs[end_args_ip+1:]
        # params = []
        # for a in args:
        #     if a.opcode == OpCode.PUSH_REF:
        #         params.append(ParamObj(a.args[0], 'type'))
        #     else:
        #         err(f"Unknown opcode in args: {a.opcode}")
        co = CodeObj(body)
        fn = FunObj(co, params)
        self.stack.append(fn) # Append the function object, since this could be inline;
        # a Let / definition will be popping it when needed

    def debug(self):
        return (self.stack, self.call_stack, self.frame)

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
                    case OpCode.PUSH_REF:
                        self.push_ref(*args)
                    case OpCode.STORE:
                        self.store(*args)
                    case OpCode.PUSH_LAMBDA:
                        start = self.frame.ip # PUSH_LAMBDA
                        while (op := self.frame.instr.opcode) != OpCode.POP_LAMBDA:
                            next(self.frame)
                        stop = self.frame.ip # POP_LAMBDA
                        self.exec_defn_lambda(start, stop)
                        next(self.frame)
                    case OpCode.BEGIN_MODULE:
                        pass
                    case OpCode.END_MODULE:
                        pass
                    case OpCode.CALL:
                        self.call(*args)
                        pass
                    case _:
                        raise ValueError(f"Unknown opcode: {op}")
            return self.stack

    def add(self, n:int):
        try:
            self.stack.append(sum([self.stack.pop() for _ in range(n)]))
        except ValueError as e:
            err(str(e))

    def push_ref(self, v: str):
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
        # Before we get to issue Call, we will have issued Load.
        # Load will have put the value already on the stack.
        # In our case, the value is a function object.
        # We could handle calls differently, but dont at the moment.
        co: CodeObj = self.stack.pop()
        # Collect args from the stack and assign to locals
        args = [self.stack.pop() for _ in range(n)]
        args.reverse()

        bind = SymTable()
        for param_idx, arg_val in enumerate(args):
            bind.set(co.params[param_idx].name, arg_val)

        # No need to make a copy of the parent's locals --
        # we will traverse up when needed.
        new = Frame(co, bind, self.frame)
        self.call_stack.append(new)

    def list(self, n: int):
        self.stack.append([self.stack.pop() for _ in range(n)])

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")

        except IndexError:
            err("! Need more arguments")