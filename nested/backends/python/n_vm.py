from functools import reduce
from typing import List
from rich import print

from nested.backends.python.n_codeobj import CodeObj, FunObj, NativeFn, ParamObj
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

    def __eq__(self, a):
        # Two pairs are equal if their fsts are equal and their rsts are equal
        if not isinstance(a, Pair):
            return False
        return self.fst == a.fst and self.rst == a.rst


def err(msg):
    raise ValueError(f"[red]Error: {msg}[/red]")


def msg(msg):
    print(f"[green]{msg}[/green]")


TRUE = Symbol("t")
FALSE = Symbol("f")
EMPTY = Symbol("empty")
RESERVED = [TRUE, FALSE, EMPTY]

class VMIR:

    @property
    def _builtins(self):
        # TODO: This is how we can avoid a bunch of
        # defined builtins and map symbols here... ?
        return {"+": CodeObj([Op(OpCode.ADD, 0)])}


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
                            cur.params.append(
                                ParamObj(self.frame.instr.args[0], "type")
                            )
                        else:
                            err(f"Unknown opcode in args: {op}")
                            return
                        next(self.frame)
                    next(self.frame)  # Skip the POP_ARGS
                elif op == OpCode.POP_LAMBDA:
                    # End of the line, add the now defined lambda
                    # with its body fully defined to the stack
                    if len(envs) == 0:
                        self.stack.append(cur)
                        next(self.frame)  # Skip the POP_LAMBDA
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
                    # TODO: DO NOT APPEND CODE OBJECTS INTO REAL CODE OF ANOTHER CODE OBJECT!!!!
                    # TODO: figure out what to append here!
                    print("!!!!!! FIX N_VM POP_LAMBDA"*20)
                    envs[-1].code.code.append(cur)
                    # envs[-1].code.code.append(Op(OpCode.CALL, 1)) # Add it to the stack frame when encountered. TODO -- need this?
                    next(self.frame)  # Skip the POP_LAMBDA of the inner defn
                    break
                else:
                    cur.code.code.append(self.frame.instr)
                    next(self.frame)
                # print(cur)
        self.stack.append(cur)

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
            case OpCode.NOT:
                self._not()
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
                elif isinstance(self.stack[-1], FunObj):
                    # self.print_debug("!", nargs, self.stack)
                    # breakpoint()
                    self.call(nargs - 1)
                    # TODO: could check args here against
                    # fun obj expected params, just like
                    # we do eleswhere?

                    # fn : FunObj = self.stack[-1]
                    # self.call(len(fn.params))
                else:
                    raise ValueError("VM: EVAL encountered non-code object in Eval")
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
            case OpCode.GT:
                self.gt()
            case OpCode.LT:
                self.lt()
            case OpCode.GTE:
                self.gte()
            case OpCode.LTE:
                self.lte()

            case _:
                raise ValueError(f"Unknown opcode: {op}")

    def print_debug(self, *args):
        if self.debug:
            print(*args)

    def exec(self, debug):
        self.debug = debug
        while self.call_stack:
            self.frame = self.call_stack.pop()
             # TODO: we have decided to push FunctionObjects
             # into the body of lambdas that define nested lambdas.
             # In this case, the next "instr" is an anonymous function object.
             # We don't want this, we should alias the lambdas to
             # some name, and call out to those.
             # Or, we can execute them inline here.

             # Check if we've set up a DEFINITION VIA A PUSH_REF;
             # THEN THIS IS A NESTED FUNCTION.
             # OTHERWISE, IT"S TRULY ANONYMOUS, AND WE EXECUTE IT HERE AND NOW
            self.print_debug("> pop frame")
            # We've set the frame to the FNObj at call time, its a new frame
            # and it should contain the code we want to execute.
            while self.frame.instr:
                self.print_debug(">", self.frame.instr)
                # TODO: this is where we would figure out how to handle objects
                # on the stack that arne't just code.
                # However we should REALLY not be injecting code
                # in the form of function objects

                # ###########
                # IT DEPENDS ON WHETHER WE ARE CALLING A FUNCTION OBJECT
                # OR JUST PUTTING ONE ON THE STACK
                # ###########
                # WE DONT SEEM TO HAVE ENOUGH INFO TO KNOW WHICH IS WHICH
                # AT THIS POINT?
                if isinstance(self.frame.instr, FunObj):
                    # I think we get here when we do a self.do_op of a CALL
                    # and the function object is on the stack.
                    fn  = self.frame.instr
                    self.print_debug(f"{' ':4}{self.stack}")
                    self.print_debug(f"<FnObj>ip:{self.frame.ip:2} #nargs{fn.nargs:2} params({fn.params})")
                    # We need to know if we have CALLED a function object vs just
                    # put one on the stack...
                    # Also, we aren't actually calling or putting anything on the stack....
                    ###### DO SOMETHING WITH FUNCTION OBJ CODE HERE
                    breakpoint()
                    for co in fn.code.code:
                        self.do_op(co.opcode, co.args)
                    ##### END DOING SOMETHING
                    next(self.frame)

                    # self.do_op(OpCode.CALL, [fn.nargs])
                else:
                    op = self.frame.instr.opcode
                    args = self.frame.instr.args

                    self.print_debug(f"{' ':4}{self.stack}")
                    self.print_debug(f"{self.frame.ip:2} {op:2} {args}")
                    # print(self.frame)

                    next(self.frame)
                    # If this op is a CALL, then
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

    # def eval_basic(self, expr: Symbol):
    #     # Eval the head
    #     # We have a single expression to evaluate
    #     # print(expr, type(expr))
    #     assert not isinstance(expr, Pair)
    #     if self.isint(expr):
    #         # breakpoint()
    #         self.stack.append(int(expr.name))
    #     elif self.isstr(expr):
    #         self.stack.append(expr.name)
    #     elif self.isbool(expr):
    #         self.stack.append(expr == TRUE)
    #     else:
    #         # Look up the symbol
    #         # TODO: need to handle primitives here
    #         self.stack.append(self.frame.getsym(expr.name))
    #         self.print_debug(self.stack)
    #     return

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
        # By the time things show up here they have been stripped
        # of their outer AST class wrapping and are just values,
        # either Pair, Symbol, or int/str etc.
        if type(val) in [int, str]:
            self.stack.append(val)
        else:
            self.stack.append(self.frame.getsym(val.name))
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
        self.print_debug(f"Qt: {self.stack}")

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
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(Symbol.from_bool(a == b))

    def lt(self):
        b, a = self.stack.pop(), self.stack.pop()
        # breakpoint()
        self.stack.append(Symbol.from_bool(a < b))

    def gt(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(Symbol.from_bool(a > b))

    def gte(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(Symbol.from_bool(a >= b))

    def lte(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(Symbol.from_bool(a <= b))

    def _not(self):

        val = self.stack.pop()
        if val != FALSE and val != TRUE:
            err("Cannot negate non-boolean")
        if val == FALSE:
            self.stack.append(TRUE)
        else:
            self.stack.append(FALSE)

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
        self.stack.append(ls.fst)

    def tl(self):
        ls = self.stack.pop()
        self.stack.append(ls.rst)

    def _make_list(self, args):
        if len(args) == 0:
            return EMPTY

        p = Pair(args[0], EMPTY)
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
            self.stack.append(EMPTY)
            return
        # print(self.stack, n)
        args = [self.stack.pop() for _ in range(n)]
        p = Pair(args[0], EMPTY)
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
        # TODO: if we rely on sending in `n` for nargs,
        # how do we handle ((eval '+) 1 2)?
        # We don't know the arg count at compile time
        # We need to rely on expression groupings instead!
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
        # Create a new entry on the call stack
        # and set the new frame so that next loop in exec
        # pulls down the new frame

        # Before we get to issue Call, we will have issued Load.
        # Load will have put the value already on the stack.
        # In our case, the value is a function object.
        # We could handle calls differently, but dont at the moment.
        # breakpoint()
        fn = self.stack.pop()
        if not isinstance(fn, FunObj):
            breakpoint()
            assert isinstance(fn, NativeFn)
        # Collect args from the stack and assign to locals
        args = [self.stack.pop() for _ in range(n)]
        args.reverse()
        bind = SymTable()
        try:
            for param_idx, arg_val in enumerate(args):
                bind.set(fn.params[param_idx].name, arg_val)
        except IndexError:
            breakpoint()
            raise ValueError("LANG: Invalid number of arguments supplied!")
        except AttributeError:
            breakpoint()
            raise ValueError(f"LANG: value is not a procedure?")
        # No need to make a copy of the parent's locals --
        # we will traverse up when needed.
        # Don't push the Function object -- only push its code
        # breakpoint()
        # WHY IS INSTR GOING TO A FUNOBJ?
        # FRAME.INSTR = FRAME.CODE[FRAME.IP]

        # EXPLANATION
        # Our calling model is push function object -> OpCode.CALL
        #** This means that when we do a CALL of a CALL (like `((expr))` )**
        # the way we construct the frame matters.
        # Normally `fn.code` we push as the code of the Frame
        # is an OPCODE because *nothing* is an object EXCEPT FUNCTIONOBJS
        # (CodeObj always resides inside FunObj.)
        # This means that when we go to put the frame on the stack,
        # ONLY when calling, and then pull it off and execute it,
        # we get a FunObj instead of an OPCODE.
        # We should change this / wrap it so that FunObjs are properly
        # stored in some intermediate storage and then loaded like everything else.

        # new_code = CodeObj([OpCode.LOAD()
        # We need some way of getting an opcode object handler here properly.
        # for when dealinhg with FunctionObjects

        #  ALSO, IF WE HAVE A FUNCTION OBJECT CALLING A FUNCTION OBJECT
        # WHEN WE APPEND THE CODE OBJECT TO THE OUTER FUNCTION OBJECT
        # ITS JUST GOING TO BE A FUNCTION OBJECT ITSELF AND SO
        # WE ARE IN THE SAME AMBIGUOOUS SITUATION WHICH IS WHY
        # WE SEE THIS SITUATION POPPPING UP WHEN WE DO ((FOO))
        # CALLS OR WHEN WE DO ((DOUBLE INC) 1)
        # breakpoint()
        # THe issue is what if we have FunObj(CoObj(FhunObk))?
        # The first instr will be a FunObj, how do we set that up?
        new = Frame(fn.code, bind, self.frame)
        # Save the old frame on the call stack, paradoxically
        self.call_stack.append(self.frame)
        # Set the current frame to the new one
        self.frame = new

    def list(self, n: int):
        args = [self.stack.pop() for _ in range(n)]
        args.reverse()
        res = reduce(lambda elem, ls: Pair(elem, ls), args, EMPTY)
        self.stack.append(res)
        # self.stack.append([self.stack.pop() for _ in range(n)])
