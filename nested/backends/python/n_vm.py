from functools import reduce
from typing import List
from rich import print

from nested.backends.python.n_codeobj import CodeObj, FunObj, ParamObj
from nested.backends.python.n_frame import Frame, SymTable
from nested.n_opcode import Op, OpCode
import operator


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
        return TRUE if b else FALSE


class Pair:
    def __init__(self, fst, rst):
        self.fst = fst
        self.rst = rst

    def __str__(self):
        return f"({self.fst} . {self.rst})"

    def __repr__(self):
        return f"({self.fst} . {self.rst})"

    def __rich_repr__(self):
        yield self.fst
        yield self.rst


def err(msg):
    raise ValueError(f"[red]Error: {msg}[/red]")


def msg(msg):
    print(f"[green]{msg}[/green]")


TRUE = Symbol("t")
FALSE = Symbol("f")
EMPTY = Symbol("empty")


class VMIR:

    @property
    def _builtins(self):
        return {"+": CodeObj([Op(OpCode.ADD, 0)])}

    # Keep these functions separate as only in interpreter mode do we want to
    # cast things for example
    def run_repl(self, code: CodeObj, debug=False):
        if not hasattr(self, "frame"):
            self.frame = Frame(code, SymTable.from_dict(self._builtins), None)

        self.frame.code = code

        self.stack = []
        self.call_stack: List[Frame] = [self.frame]

        self.exec(debug)

    def run(self, code: CodeObj, frame=None, debug=False):
        if frame is None:
            frame = Frame(code, SymTable.from_dict(self._builtins), None)
        else:
            frame.code = code

        self.frame = frame
        self.stack = []
        self.call_stack: List[Frame] = [self.frame]

        self.exec(debug)
        return self.stack, self.frame, self.call_stack

    def exec_defn_lambda(self):
        # Iterate over the code. If we encounter a PUSH_LAMBDA,
        # add another layer to the stack.
        # When encountering PUSH_ARGS and POP_ARGS, collect the arguments
        # and create Param objects,

        envs = [FunObj(CodeObj([]), [])]
        while envs:
            cur = envs.pop()
            # print(cur)
            while True:
                op = self.frame.instr.opcode
                # Nested lambda
                if op == OpCode.PUSH_LAMBDA:
                    envs.append(cur)
                    cur = FunObj(CodeObj([]), [])
                    next(self.frame)
                elif op == OpCode.PUSH_ARGS:
                    next(self.frame)
                    while (op := self.frame.instr.opcode) != OpCode.POP_ARGS:
                        if op == OpCode.PUSH_REF:
                            cur.params.append(ParamObj(self.frame.instr.args[0], "type"))
                        else:
                            err(f"Unknown opcode in args: {op}")
                            return
                        next(self.frame)
                    next(self.frame) # Skip the POP_ARGS
                elif op == OpCode.POP_LAMBDA:
                    # End of the line, add the now defined lambda
                    # with its body fully defined to the stack
                    if len(envs) == 0:
                        self.stack.append(cur)
                        next(self.frame) # Skip the POP_LAMBDA
                        return
                    # We're inside a lambda, add it to the outer layer's
                    # code.
                    # TODO: environments need a place to store tmp objects
                    # and load from them; we would need to store the lambda
                    # somewhere, then retrieve it with a Load, in order to issue the call.
                    co = envs[-1].code
                    # TODO:
                    # 1) store the function object in the symbol table as some
                    # obfuscated id
                    # 2) issue a load + call to it from the outer lambda's code, appending
                    # that code instrs there.

                    # Big TODO: maybe we should have lower-level instructions
                    # like bind-arg that does the variable binding for us, etc,
                    # instead of leaving so much to implementation
                    envs[-1].code.code.append(cur)
                    # envs[-1].code.code.append(Op(OpCode.CALL, 1)) # Add it to the stack frame when encountered. TODO -- need this?
                    next(self.frame) # Skip the POP_LAMBDA of the inner defn
                    break
                else:
                    cur.code.code.append(self.frame.instr)
                    next(self.frame)
                # print(cur)
        self.stack.append(cur)

    # def exec_defn_lambda(self, start, stop):
    #     # Iterate over the list, handling three sections:
    #     # Begin Args, End Args, and End Lambda:
    #     # TODO: optimize
    #     ip = 0

    #     # Skip the PUSH_ARGS instr # TODO: fix this, not necessary probably
    #     instrs = self.frame.code[start + 1 : stop]

    #     # ITerate over the frame, collecting arguments
    #     # until the POP_ARGS opcode is reached, then continue
    #     # collecting the body of the lambda until the POP_LAMBDA:
    #     end_args_ip = list(map(lambda i: i.opcode, instrs)).index(OpCode.POP_ARGS)
    #     start_body_ip = end_args_ip + 1
    #     args = instrs[0:end_args_ip]
    #     body = instrs[start_body_ip:]
    #     params = []
    #     for a in args:
    #         if a.opcode == OpCode.PUSH_REF:
    #             params.append(ParamObj(a.args[0], "type"))
    #         else:
    #             err(f"Unknown opcode in args: {a.opcode}")
    #     # begin_args_ip = start+1
    #     # end_args_ip = _opcodes.index(OpCode.POP_ARGS)
    #     # start_body_ip = end_args_ip+1
    #     # end_body_ip = stop-1

    #     # args = self.frame.instrs[begin_args_ip:end_args_ip]
    #     # body = self.frame.instrs[end_args_ip+1:]
    #     # params = []
    #     # for a in args:
    #     #     if a.opcode == OpCode.PUSH_REF:
    #     #         params.append(ParamObj(a.args[0], 'type'))
    #     #     else:
    #     #         err(f"Unknown opcode in args: {a.opcode}")

    #     # TODO: What if we have nested lambdas?
    #     co = CodeObj(body)
    #     fn = FunObj(co, params)
    #     # breakpoint()
    #     self.stack.append(fn)  # Append the function object, since this could be inline;
    #     # a Let / definition will be popping it when needed

    def debug_output(self):
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
                nargs = self.eval(self.stack.pop(), *args)
                # TODO:
                if isinstance(self.stack[-1], CodeObj):  # Primitive
                    self.do_op(self.stack.pop().code[0].opcode, [nargs - 1])
                if isinstance(self.stack[-1], FunObj):
                    print(nargs, self.stack)
                    self.call(nargs - 1)
                    # TODO: could check args here against
                    # fun obj expected params, just like
                    # we do eleswhere?

                    # fn : FunObj = self.stack[-1]
                    # self.call(len(fn.params))
                # if not isinstance(self.stack[-1], FunObj)
            case OpCode.ASSERT:
                self._assert()
            case OpCode.PUSH_REF:
                self.push_ref(*args)
            case OpCode.STORE:
                self.store(*args)
            case OpCode.LOAD_TRUE:
                self.stack.append(TRUE)
            case OpCode.LOAD_FALSE:
                self.stack.append(FALSE)
            case OpCode.PUSH_LIST:
                self.push_list(*args)
            case OpCode.PUSH_LAMBDA:
                # breakpoin()
                # start = self.frame.ip  # PUSH_LAMBDA
                # TODO: the bug here is that a lambda in the body of a
                # function is not being handled correctly --
                # we need to keep collecting until we hit the _outermost_
                # POP_LAMBDA, which is the end of _this_ definition.
                # Otherwise, we currently prematurely terminate, meaning
                # we don't properly define lambdas in the body of a function.
                # while (op := self.frame.instr.opcode) != OpCode.POP_LAMBDA:
                #     next(self.frame)
                # stop = self.frame.ip  # POP_LAMBDA
                # self.exec_defn_lambda(start, stop)
                # next(self.frame)  # Skip the POP_LAMBDA
                self.exec_defn_lambda()
                # breakpoint()
            case OpCode.POP_LAMBDA:
                # Lambdas used as values, not definitions;
                raise ValueError("VM: POP_LAMBDA encountered outside of definition")
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
                # break

            case _:
                raise ValueError(f"Unknown opcode: {op}")

    def exec(self, debug):
        self.debug = debug
        while self.call_stack:
            self.frame = self.call_stack.pop()
            print(self.frame)
            while self.frame.instr:
                # TODO: we have decided to push FunctionObjects
                # into the body of lambdas that define nested lambdas.
                # In this case, the next "instr" is an anonymous function object.
                # We don't want this, we should alias the lambdas to
                # some name, and call out to those.
                # Or, we can execute them inline here.
                if isinstance(self.frame.instr, FunObj):
                    print(">>", self.frame.instr)
                    self.stack.append(self.frame.instr)
                    self.call(len(self.frame.instr.params) - 1)
                    next(self.frame)
                    continue
                    # self.call_stack.append(Frame(self.frame.instr.code, SymTable(), self.frame))

                print(self.frame.instr)

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

    @staticmethod
    def isint(i: Symbol):
        try:
            int(i.name)
            return True
        except ValueError:
            return False

    @staticmethod
    def isbool(i: Symbol):
        return i.name == "t" or i.name == "f"

    @staticmethod
    def isstr(i: Symbol):
        # A string is a sequence of characters enclosed in double quotes
        return i.name[0] == '"' and i.name[-1] == '"'

    def eval_basic(self, expr: Symbol):
        # Eval the head
        # We have a single expression to evaluate
        # print(expr, type(expr))
        assert not isinstance(expr, Pair)
        if self.isint(expr):
            # breakpoint()
            self.stack.append(int(expr.name))
        elif self.isstr(expr):
            self.stack.append(expr.name)
        elif self.isbool(expr):
            self.stack.append(expr == TRUE)
        else:
            # Look up the symbol
            # TODO: need to handle primitives here
            self.stack.append(self.frame.getsym(expr.name))
            print(self.stack)
        return

    # Define (quote a b c) as (a b c) e.g. A applied to (b, c)
    def eval(self, pair, *args):
        # Eval is going to be an interpreter --
        # look at machine code, and execute it;
        # very similar to our exec loop.
        # We shouldn't though be dealing with ops like
        # Jumps, etc, because those are inserted by the compiler;
        # we just deal with primitives.
        # ops = [self.stack.pop() for _ in range(n)]
        # ops.reverse()
        # print(ops)
        # Literal
        # breakpoint()
        # if not isinstance(pair, Pair):
        #     self.eval_basic(pair)
        #     return 0
        # # Leaf
        # if pair.rst == Symbol('empty'):
        #     return self.eval(pair.fst)

        # # Otherwise, this is APPLICATION;
        # # eval the proc and the args, then DO it.
        # self.eval(pair.fst) # Reverse order, proc goes on last, popped first by call.
        # nargs = len(self.stack)
        # self.eval(pair.rst)
        # # Number of args to push is whatever happened after
        # # evaluating the body of the proc
        # nargs = len(self.stack) - nargs
        # print(self.stack)
        # # breakpoint()
        # return nargs
        # # print(self.stack)
        # # print(self.stack)

        # We expect the arg we operate on to be
        # a constant, or a procedure!
        # We Can assume this, it is intended.
        if isinstance(pair, Pair):
            nargs_fst = self.eval(pair.rst)
            nargs_snd = self.eval(pair.fst)
            return nargs_fst + nargs_snd
        val = pair
        if val == EMPTY:
            return 0
        val = val.name  # It's a symbol
        if str.isnumeric(val):
            self.stack.append(int(val))
        elif val[0] == '"' and val[-1] == '"':
            self.stack.append(val[1:-1])
        else:
            self.stack.append(self.frame.getsym(val))
        return 1
        # # return nargs
        # if isinstance(pair, Pair):
        #     if not pair.rst == Symbol('empty'):
        #         self.eval(pair.rst)
        # else:
        #     self.eval_basic(pair)
        # print(self.stack)

    def quote(self, n):
        # When compiled, we pushed Op(LOAD_SYM, symbol) for each node encountered
        # in the AST.
        # When executing, forget about the LOAD_SYM opcodes, and just push the argument,
        # which is the symbolic value.
        # ops = list(map(lambda op: op.args, self.frame.code[self.frame.ip-n-1:self.frame.ip-1]))
        # print(">>", self.stack, n)
        ops = self.stack.pop()
        # self.stack.pop() # Remove the quote char. TODO: do we need to push it?:
        # print(":", ops)
        self.stack.append(ops)
        # self.stack.append(p)
        if self.debug:
            print(f"Qt: {self.stack}")

    def sub(self, n: int):
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

    def _assert(self):
        # Assert that the top of the stack is True
        if self.stack.pop() != TRUE:
            err("Assertion failed")
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

    def _make_list(self, args):
        if len(args) == 0:
            return Symbol("empty")

        p = Pair(args[0], Symbol("empty"))
        for arg in args[1:]:
            p = Pair(arg, p)
        return p

    def push_list(self, n: int):
        # Create Cons pairs where the empty list is the final element.
        # https://old.reddit.com/r/Racket/comments/tnduc9/difference_between_cons_list/
        # if n == 0:
        #     self.stack.append(Symbol('empty'))
        #     return
        if n == 0:
            self.stack.append(Symbol("empty"))
            return
        # print(self.stack, n)
        args = [self.stack.pop() for _ in range(n)]
        p = Pair(args[0], Symbol("empty"))
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

    def add(self, n: int):
        try:
            self.stack.append(
                reduce(
                    lambda elem, res: operator.add(elem, res),
                    [self.stack.pop() for _ in range(n)],
                )
            )
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
        # breakpoint()
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
        try:
            for param_idx, arg_val in enumerate(args):
                bind.set(fn.params[param_idx].name, arg_val)
        except IndexError:
            raise ValueError("LANG: Invalid number of arguments supplied!")
        except AttributeError:
            raise ValueError(f"LANG: value is not a procedure?")
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
        res = reduce(lambda elem, ls: Pair(elem, ls), args, Symbol("empty"))
        self.stack.append(res)
        # self.stack.append([self.stack.pop() for _ in range(n)])

    def print(self, n: int):
        try:
            args = [str(self.stack.pop()) for _ in range(n)]
            msg(f"> {' '.join(args)}")

        except IndexError:
            err("! Need more arguments")
