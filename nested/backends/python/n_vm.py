from functools import reduce
from typing import List
from rich import print

from nested.backends.python.n_codeobj import CodeObj, FunObj, ParamObj
from nested.backends.python.n_frame import Frame, SymTable
from nested.n_opcode import Op, OpCode

class Symbol:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, value: object) -> bool:
        # TODO: is this what we want?
        if isinstance(value, Symbol):
            return self.name == value.name
        return False

    @staticmethod
    def from_bool(b: bool):
        # TODO: how much of this is an implementation detail?
        # Should probably handle it specially in compilation
        return Symbol("t") if b else Symbol("f")

class Pair:
    def __init__(self, fst, rst):
        self.fst = fst
        self.rst = rst

    def __str__(self):
        return f"({self.fst} . {self.rst})"

    def __repr__(self):
        return f"({self.fst} . {self.rst})"

    def __rich_repr__(self):
        return f"({self.fst} . {self.rst})"

def err(msg):
    raise ValueError(f"[red]Error: {msg}[/red]")

def msg(msg):
    print(f"[green]{msg}[/green]")

class VMIR:
    # Keep these functions separate as only in interpreter mode do we want to
    # cast things for example
    def run_repl(self, code: CodeObj, debug=False):
        if not hasattr(self, "frame"):
            self.frame = Frame(code, SymTable(), None)

        self.frame.code = code

        self.stack = []
        self.call_stack: List[Frame] = [self.frame]

        self.exec(debug)


    def run(self, code: CodeObj, frame = None, debug=False):
        if frame is None:
            frame = Frame(code, SymTable(), None)
        else:
            frame.code = code

        self.frame = frame
        self.stack = []
        self.call_stack: List[Frame] = [self.frame]

        self.exec(debug)
        return self.stack, self.frame, self.call_stack

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
        # breakpoint()
        self.stack.append(fn) # Append the function object, since this could be inline;
        # a Let / definition will be popping it when needed

    def debug(self):
        return (self.stack, self.call_stack, self.frame)

    def do_op(self, op, args):
        match op:
            case OpCode.ADD:
                self.add(*args)
            case OpCode.SUB:
                self.sub(*args)
            case OpCode.CONS:
                self.cons(*args)
            case OpCode.NEG:
                self.neg()
            case OpCode.PRINT:
                self.print(*args)
            case OpCode.LOAD_INT:
                self.load_type(OpCode.LOAD_INT, *args)
            case OpCode.LOAD_STR:
                self.load_type(OpCode.LOAD_STR, *args)
            case OpCode.LOAD_SYM:
                self.load_type(OpCode.LOAD_SYM, *args)
            case OpCode.EQ:
                self.eq()
            case OpCode.NEQ:
                self.neq()
            case OpCode.HD:
                self.hd()
            case OpCode.TL:
                self.tl()
            case OpCode.FST:
                self.stack.append(self.stack.pop().fst)
            case OpCode.RST:
                self.stack.append(self.stack.pop().rst)
            case OpCode.TL:
                self.tl()
            case OpCode.LOAD:
                self.load(*args)
            case OpCode.QUOTE:
                self.quote(*args)
            case OpCode.EVAL:
                self.eval(*args)
            case OpCode.PUSH_REF:
                self.push_ref(*args)
            case OpCode.STORE:
                self.store(*args)
            case OpCode.LOAD_TRUE:
                self.stack.append(True)
            case OpCode.LOAD_FALSE:
                self.stack.append(False)
            case OpCode.PUSH_LIST:
                self.push_list(*args)
            case OpCode.PUSH_LAMBDA:
                start = self.frame.ip # PUSH_LAMBDA
                while (op := self.frame.instr.opcode) != OpCode.POP_LAMBDA:
                    next(self.frame)
                stop = self.frame.ip # POP_LAMBDA
                self.exec_defn_lambda(start, stop)
                next(self.frame) # Skip the POP_LAMBDA
            case OpCode.JUMP_IF_FALSE:
                cond = self.stack.pop()
                if cond == Symbol("t"):
                    # We've already advanced the IP
                    # before stepping into the match statemenst,
                    # so we don't need to do it again.
                    pass
                else:
                    # Add the relative jump
                    self.frame.ip += args[0]
            case OpCode.JUMP:
                self.frame.ip += args[0]
            case OpCode.BEGIN_MODULE:
                pass
            case OpCode.END_MODULE:
                pass
            case OpCode.CALL:
                self.call(*args)
                # NOTICE THE BREAK -- we must force
                #break

            case _:
                raise ValueError(f"Unknown opcode: {op}")
    def exec(self, debug):
        self.debug = debug
        while self.call_stack:
            self.frame = self.call_stack.pop()
            while self.frame.instr:
                op = self.frame.instr.opcode
                args = self.frame.instr.args

                if debug:
                    print(f"{self.frame.ip:2} {op:2} {args}")
                    print(f"{' ':4}{self.stack}")
                    # print(self.frame)

                next(self.frame)
                self.do_op(op, args)

        return self.stack


    def cons(self, *args):
        # (a b) -> [a, b]
        snd, fst = self.stack.pop(), self.stack.pop()
        # Always a new list, no mutability here ;) TODO
        self.stack.append(Pair(fst, snd))


    def eval(self, *args):
        co : CodeObj = self.stack.pop()
        print(co)
        # We need to execute the code in the current frame

        # self.frame.code = [*self.frame.code[:self.frame.ip], *co.code, *self.frame.code[self.frame.ip:]]

    def quote(self, n):
        # Do nothing -- leave the code unevaluated, will be used later
        # Collect a CodeObj of the last N arguments, and push it.
        # -1 because we have already advanced the instruction pointer
        # to the next instr after fetching the quote op
        ops = self.frame.code[self.frame.ip-n-1:self.frame.ip-1]
        self.stack.append(CodeObj(ops))
        print(ops)
    def sub(self, n:int):
        # (- a b) -> a - b
        try:
            args = [self.stack.pop() for _ in range(n)]
        except IndexError:
            err("! Need more arguments")
        a = args[-1]
        b = sum(args[:-1])
        self.stack.append(a - b)

    def eq(self):
        a, b = self.stack.pop(), self.stack.pop()
        self.stack.append(Symbol.from_bool(a == b))

    # def sub(self, n:int):
    #     try:
    #         self.stack.append(self.stack.pop() - sum([self.stack.pop() for _ in range(n-1)]))
    #     except ValueError as e:
    #         err(str(e))
    def neq(self):
        a, b = self.stack.pop(), self.stack.pop()
        self.stack.append(Symbol.from_bool(a != b))

    def hd(self):
        ls = self.stack.pop()
        self.stack.append(ls[0])

    def tl(self):
        ls = self.stack.pop()
        self.stack.append(ls[1:])


    def push_list(self, n: int):
        # Create Cons pairs where the empty list is the final element.
        # https://old.reddit.com/r/Racket/comments/tnduc9/difference_between_cons_list/
        # if n == 0:
        #     self.stack.append(Symbol('empty'))
        #     return
        if n == 0:
            self.stack.append(Symbol('empty'))
            return

        args = [self.stack.pop() for _ in range(n)]
        p = Pair(args[0], Symbol('empty'))
        for arg in args[1:]:
            p = Pair(arg, p)
        self.stack.append(p)

        # args = [self.stack.pop() for _ in range(n)]
        # res = reduce(lambda elem, ls: Pair(elem, ls), args, Symbol('empty'))
        # print(res)
        # self.stack.append(res)
        # p = Pair(args[0], Symbol('empty'))
        # for a in args[1:]:
        #     print(a)
        #     p = Pair(a, p)
        # self.stack.append(p)
        # breakpoint()
        # ls = reduce(lambda elem, ls: Pair(elem, ls), reversed([self.stack.pop() for _ in range(n)]), [])
        # self.stack.append(ls)

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
            case OpCode.LOAD_SYM:
                self.stack.append(Symbol(v))
            case _:
                err(f"Unknown type: {op}")

    def load(self, v: str):
        #breakpoint()
        self.stack.append(self.frame.getsym(v))

    def store(self):
        # Can't just shove the symbol in with this Instr because
        # the symbol could be evaluated on the stack by compiling
        # and we need to execute to get the proper value... maybe TODO
        # breakpoint()
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
        fn: FunObj = self.stack.pop()
        # Collect args from the stack and assign to locals
        args = [self.stack.pop() for _ in range(n)]
        args.reverse()

        bind = SymTable()
        for param_idx, arg_val in enumerate(args):
            bind.set(fn.params[param_idx].name, arg_val)

        # No need to make a copy of the parent's locals --
        # we will traverse up when needed.
        # Don't push the Function object -- only push its code
        new = Frame(fn.code, bind, self.frame)
        # Save the old frame on the call stack, paradoxically
        self.call_stack.append(self.frame)
        # Set the current frame to the new one
        self.frame = new

    def list(self, n: int):
        args = [self.stack.pop() for _ in range(n)]
        args.reverse()
        res = reduce(lambda elem, ls: Pair(elem, ls), args, Symbol('empty'))
        self.stack.append(res)
        # self.stack.append([self.stack.pop() for _ in range(n)])

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")

        except IndexError:
            err("! Need more arguments")