from lark import Tree
from enum import Enum, auto
from rich import print
from nested.backends.python.n_vm import EMPTY, FALSE, RESERVED, TRUE
from nested.n_parser import (
    ASTExpr,
    ASTLeaf,
    ASTList,
    ASTNode,
    ASTModule,
    ASTConstantValue,
    ASTIdentifier,
    ASTOp,
)
from nested.n_opcode import Op, OpCode

RESERVED_WORDS = list(map(lambda k: k.name, RESERVED)) + list(ASTIdentifier.builtins)

# Continuation -- add before / after / during, where during gets
# the parent class fn as an arg.
# opmap = {
#     ASTUnOpExpr.UnOps.NEG: OpCode.NEG,
#     ASTVaryOpExpr.VaryOps.PRINT: OpCode.PRINT,
#     ASTBinOpExpr.BinOps.ADD: OpCode.ADD
# }
class Compiler:

    def __init__(self, tree: Tree, debug = False):
        self.tree = tree
        self.buffer = []
        self.ip = 0
        self.macros = {}
        self.debug = debug

        # TODO: perhaps map to var names as hash map 
        # to not have huge integers as codebase grows...
        self._hygenic_macro_int = 0

    def print_debug(self, x):
        if self.debug:
            print(x)

    def display_buffer(self):
        for i, instr in enumerate(self.buffer):

            print(f"{i:<4}: {instr.opcode:<25} {' '.join(map(str, instr.args)):<15}")


    def emit(self, arg):
        self.buffer.append(arg)
        self.ip += 1

    def patch(self, ip, arg):
        self.buffer[ip] = arg

    def compile_program(self, node: ASTModule = None):
        # TODO: default ASTModule we wrap in should have a value passed...
        # Need distingiusih outer program and inner module this is sloppy
        # TODO: distingusih program and module
        self.emit(Op(OpCode.BEGIN_MODULE, "meta"))
        # Get metadata from self.tree here (not children)
        if node is None:
            self.compile(self.tree.children)
        else: 
            # TODO: PASS THE MODULE NAME WITH THE STATEMENTS
            self.emit(Op(OpCode.BEGIN_MODULE, node.value))
            self.compile(node.children)
            self.emit(Op(OpCode.END_MODULE, "meta"))

        self.emit(Op(OpCode.END_MODULE, "META"))

    def compile(self, nodes):
        for node in nodes:
            self.compile_node(node)

    # def compile_if(self, node: ASTOp):
    #     # TODO: is it possible that this fails in function calls
    #     # because the IPs here are not RELATIVE ?
    #     # As in, they compile against the IP of the whole program,
    #     # but when we execute the function, the IP is relative to the start
    #     # of ITS frame.
    #     # Yes this is the case; use REL JUMP.
    #     rel_ip = self.ip
    #     cond, then, els = node.children
    #     self.compile_node(cond)

    #     backpatch_if_branch_take_jmp = self.ip
    #     self.emit(Op(OpCode.NOP))

    #     self.compile_node(then)
    #     if_branch_finished_ip = self.ip # Capture the IP here because of 0-indexing when accessing the buffer instruction
    #     self.emit(Op(OpCode.NOP))

    #     self.patch(backpatch_if_branch_take_jmp, Op(OpCode.JUMP_IF_FALSE, if_branch_finished_ip + 1 - rel_ip, if_branch_finished_ip + 1)) # Add 1 because the jump target is the instr
    #     # after the isntr we are also patching

    #     self.compile_node(els)
    #     else_branch_finished_ip = self.ip
    #     self.patch(if_branch_finished_ip, Op(OpCode.JUMP, else_branch_finished_ip - rel_ip, else_branch_finished_ip))

    def compile_if(self, node: ASTOp):
        cond, then, els = node.children
        self.compile_node(cond)

        self.emit(Op(OpCode.NOP))
        ip_of_jump_if_false = self.ip

        self.compile_node(then)

        self.emit(Op(OpCode.NOP))
        ip_of_jump_to_end = self.ip

        # Decrement because of 0-indexing instr buffer
        self.patch(
            ip_of_jump_if_false - 1,
            Op(
                OpCode.JUMP_IF_FALSE,
                ip_of_jump_to_end - ip_of_jump_if_false,
                ip_of_jump_to_end,
            ),
        )

        self.compile_node(els)
        self.patch(
            ip_of_jump_to_end - 1, Op(OpCode.JUMP, self.ip - ip_of_jump_to_end, self.ip)
        )

    def compile_const(self, node: ASTConstantValue):
        if node.type == "int":
            self.emit(Op(OpCode.LOAD_INT, node.value))
        elif node.type == "string-lit":
            self.emit(Op(OpCode.LOAD_STR, node.value))
        elif node.type == "symbol":
            match node.value:
                # TODO: LOAD_BOOL with flag for true/false,
                # or just use LOAD_TRUE/LOAD_FALSE?
                case "t":
                    self.emit(Op(OpCode.LOAD_TRUE))
                case "f":
                    self.emit(Op(OpCode.LOAD_FALSE))
                case _:
                    self.emit(Op(OpCode.LOAD_SYM, node.value))
        else:
            raise ValueError(f"Unknown const: {node.type}")

    def compile_list(self, node: ASTList):
        # self.emit(Op(OpCode.PUSH_LIST)
        for child in node.children:
            self.compile_node(child)
        self.emit(Op(OpCode.PUSH_LIST), len(node.children))

    def compile_ref(self, node: ASTIdentifier):
        self.emit(Op(OpCode.PUSH_REF, node.value))

    def compile_expr(self, node: ASTExpr):
        # TODO: Check arity here for builtins etc .. ?

        # Special case: for definition, we must push a Ref,
        # not the value itself, for the symbol to be resolved.
        # We cannot thus compile the children ahead of inspecting that,
        # as for the symbol we are defining, we would issue a Load
        # which would fail on execution
        if isinstance(node.value, ASTOp):  # builtin, just call its opcode
            op = Op.from_id(node.value)
            opcode = op.opcode

            match opcode:
                case OpCode.INCLUDE:
                    assert False # should have been replaced?
                    return 
                case OpCode.STORE:
                    sym = node.children[0]
                    self.compile_ref(sym)
                    for child in node.children[1:]:
                        self.compile_node(child)
                    self.emit(op)
                    return
                    
                case OpCode.PUSH_LAMBDA:
                    self.compile_lambda(node)
                    return
                case OpCode.DEFMACRO:
                    self.compile_defmacro(node)
                    return
                case OpCode.IF:
                    self.compile_if(node)
                    return

                case OpCode.BEGIN:
                    # Only compile the children, not the value
                    # TODO: Should we push the value here too?
                    for child in node.children:
                        self.compile_node(child)
                    return

                case OpCode.QUOTE:
                    # HOW DO QUOTES GET HANDLED IN SCHEME?
                    # TL;DR: They are different; use list when in doubt.
                    # A rule of thumb: use list whenever you want the 
                    # arguments to be evaluated; 
                    # quote “distributes” over its arguments, 
                    # so '(+ 1 2) is like (list '+ '1 '2). 
                    # You’ll end up with a symbol in your list, not a function.

                    def do_quote(n):
                        # TODO: Fix this parser bug that makes children a tuple
                        # breakpoint()
#                        Now, one might ask: what happens if you quote something other than a symbol or a list? Well, the answer is... nothing! You just get it back.


                        if n.children == (None,):
                            # NON-SYMBOL, NON-LIST DO NOT GET QUOTED.
                            if isinstance(n, ASTConstantValue):
                                self.compile_const(n)                            
                            else:
                                self.emit(Op(OpCode.LOAD_SYM, n.value))

                            return

                        do_quote(
                            n.value
                        )  # This must go first, to keep order of args sensible with it
                        for c in n.children:
                            do_quote(c)
                        self.emit(
                            Op(OpCode.PUSH_LIST, len(n.children) + 1)
                        )  # + 1 because we need to include the do_quote(n.value) used above here; note we don't do this in the outer code, because we treat the `'`
                        # operator separately.
                        # NOTE DISTINCTION IS required for (' add 1 2) and (' (add 1 2))
                        return

                    # breakpoint()

                    # TODO: THERE IS A DIFFERENCE BETWEEN
                    # (' + 1 2) and (' (+ 1 2)) !!!!
                    # FIGURE OUT HOW TO INVOKE THAT
                    # Perhaps it is Pair(op, Pair(<args>)) vs (Pair (op, Pair(Pair(arg1, Pair(arg2)  ))))
                    start = self.ip

                    # Differentiate here between an Expr vs Constant-valued child.
                    # One requires a PushList, the other just push the symbol. TODO
                    # TODO: '(1 2 3)
                    # Special case:
                    # If there is only 1 child, we have the situation
                    # 'foo, or (quote foo) -- we do not want to push a list here,
                    # but rather just want to push the symbol.
                    if len(node.children) == 1:
                        assert not isinstance(node.children[0], ASTList)
                        if not isinstance(node.children[0], ASTExpr):
                            self.emit(Op(OpCode.LOAD_SYM, node.children[0].value))
                            self.emit(Op(OpCode.QUOTE, self.ip - start))
                            return

                    for n in node.children:
                        do_quote(n)
                    self.emit(
                        Op(OpCode.PUSH_LIST, len(node.children))
                    )  # Look at children, not total instrs emitted, because those will have been collected with list push/pops in the interim
                    # print("buf", self.buffer)
                    self.emit(Op(OpCode.QUOTE, self.ip - start))
                    # breakpoint()
                    return
                # ASTExpr(ASTOp("'"), ASTExpr(ASTIdentifier('add'), ASTConstantValue('int', '1'), ASTConstantValue('int', '2')))
                # ASTExpr(ASTOp("'"), ASTIdentifier('add'), ASTConstantValue('int', '1'), ASTConstantValue('int', '2'))
                case _:
                    for child in node.children:
                        self.compile_node(child)

                    self.emit(Op.from_id(node.value, len(node.children)))
                    return

        for child in node.children:
            self.compile_node(child)

        if isinstance(node.value, ASTIdentifier):
            self.compile_identifier(node.value)
            self.emit(Op(OpCode.CALL, len(node.children)))

        elif isinstance(node.value, ASTExpr):
            # Need this for things like ((eval 'add) 1 2)); need to eval procs too.
            # If the direct child is an ASTExpr, then we need to issue a call?
            self.compile_expr(node.value)
            # Any ASTExpr(ASTExpr will be calling something; emit a call.
            # TODO: need this? (gut check: yes)
            # Doesn't seem to be right ... fails a use case that should be fine.
            # self.emit(Op(OpCode.CALL, len(node.children)))
        else:
            raise ValueError(f"Unknown expr: {node.value}")

    def compile_lambda(self, node: ASTOp):
        self.emit(Op(OpCode.PUSH_LAMBDA))  # TODO: this is probably not necessary,
        # just check for PUSH_ARGS and take the K values up from there
        args = node.children[0]
        self.emit(Op(OpCode.PUSH_ARGS))

        # TODO When setting up call frame, have to push the args in reverse order
        # to make it easier to pop them off in order when calling the lambda
        # .. or something

        # TODO: Right now the arg identifier list is an ASTExpr because of our parsing;
        # this is not good, because it confuses how we access the values.
        # We should do a second AST pass that transforms
        # Expr(Op(Lambda), Expr(x y z), Expr (body)) into Expr(Op(Lambda), List(x y z), Expr(body))

        for arg in [args.value, *args.children]:
            # TODO: this assumes we only allow actual identifiers
            # in lambda arg definition, and not some fancy expressions or anything.
            # If we DID, we would need to compile_noad / reduce the arg somehow,
            # to an identifier...
            self.emit(Op(OpCode.PUSH_REF, arg.value))
            # self.emit(Op(OpCode.STORE, 1)) # Store will pop the ref and the value off, incrementally, at runtiem

        self.emit(Op(OpCode.POP_ARGS))
        body = node.children[1]
        self.compile_node(body)
        self.emit(Op(OpCode.POP_LAMBDA))

    def compile_defmacro(self, node: ASTOp):
        name = node.children[0]
        if len(node.children) != 3:
            args = None
            body = node.children[1]
        else:
            args = node.children[1]
            body = node.children[2]
        self.macros[name.value] = (args, body)

    def compile_identifier(self, node: ASTIdentifier):
        self.emit(Op(OpCode.LOAD, node.value))

    def compile_macro(self, node: ASTNode):
        # We could do something in the VM bytecode by swapping refs later or
        # whatever but that seems way too complicated.
        macro_id = node.value  # ASTIdentifier
        macro_args, macro_body = self.macros[macro_id.value]  # ARe these hashable?>
        # Bind the args provided to the node
        # to the arg symbols in the `args` list,
        # inject those into the body,
        # and then render the body.


        self.compile_naive_macro(macro_args, macro_body, node)

    def compile_naive_macro(self, macro_args, macro_body, node):
        # TODO: 
        # Get the args from the node, 
        # and bind them to the symbols in the macro_args list,
        # then compile the body of the macro referencing those values.

        # (defmacro add (x y) (+ x y)) ; args are a ASTExpr(ASTIdentifier('x'), ASTIdentifier('y'))
        # and the head of it is the first ID which we want to capture.
        # So total args is len(macro_args.children) + 1 for the head.
        # TODO: this might break
        # TODO: () passed as arg list has length 1 instead of 0 when 
        # comparing to the args being called with.
        # TODO: (<call-macro-name>) as node.children = []
        # whereas in the macro definition (having no args) it's argument value is 'empty;
        # we need to do the  equivalence here.

        # if macro_args.value != ASTIdentifier('empty'):
        #     macro_args =  [macro_args.value, *macro_args.children]
        # else:
        #     macro_args = []
        # TODO: this fails if you define a macro with empty () argslist;
        # you shouldnt be doing that if it takes no args though...
        # We should fix this to standardize it.


        if macro_args is None: 
            assert len(node.children) == 0
            macro_args = []
        else: 
            macro_args =  [macro_args.value, *macro_args.children]
            # if not (node.children == [] and macro_args
            try: 
                assert len(node.children) == len(macro_args)
            except AssertionError:
                # TODO: the issue is that (test (1 2 3)) goes to (1 (2 3)) cons cells.
                # which is length 2 instead of 3
                breakpoint()
                assert False
        # 3) Replace the macro args with the actual values in the macro_body.
        args = node.children
        macro_arg_names = list(map(lambda m: m.value, macro_args))

        # The issue is expression compiling 
        # is recursive; we cannot defer compilation of 
        # the children to compiling the parent node,
        # because we won't be doing any replacements that way.
        # Instead we need to go ahead and just replace things in the AST, and 
        # Substitute in the body.

        this_macro_number = self._hygenic_macro_int
        self._hygenic_macro_int += 1
        macro_local_var_map = {}

        # NOTE: IF YOU STICK A PARAMATER NAME IN THE INNER FUNCTION
        # THAT MATCHES THE NAME OF AN ARGUMENT TO THE MACRO
        # THINGS WILL NOT WORK AS EXPECTED!!!!
        # TODO: FIX THIS IN MACRO CODE SO THAT WE SCOPE PROPERLY
        def substitute(node):
            # TODO: might want to also do this for defmacro 
            # TODO: fix this crap, handle it all below with Expr.
            # HANDLE ASSIGNMENT
            if isinstance(node, ASTExpr) and node.value == ASTOp("let"):
                var_node = node.children[0]
                var_name = var_node.value
                # IF WE ARE DOING AN ASSIGNMENT!!!
                # Sanitize the name of the non-replaced identifier
                # NOTE: we can have a meta-statement like (let (hd x) val)
                # in the macro; we need to therefore let Ops be hashable 
                # so we can look them up in the macro dict.
                # TODO: exclude list of builtin ops from this


                if var_name not in macro_local_var_map and var_name not in RESERVED_WORDS:
                    macro_local_var_map[var_name] = f"{var_name}#{this_macro_number}"

                if isinstance(var_name, ASTOp) and var_name.value in RESERVED:
                    new_name = var_name.value
                else:
                    new_name = macro_local_var_map[var_name]
                # Reassign the identifier to the macro hygenizied name
                new_children = [ASTIdentifier(new_name)] 
                # Process the rest of the children
                for child in node.children[1:]:
                    subbd = substitute(child)
                    new_children.append(subbd)
                return ASTExpr(ASTOp("let"),  *new_children)

            # Could be just an identifier we need to swap out
            elif isinstance(node, ASTIdentifier):
                if node.value in macro_arg_names:
                    idx = macro_arg_names.index(node.value)
                    return args[idx]
                # Replace any previously sanitized macro vars
                # that appear later in the body of the macor with the
                # sanitized name.
                # TODO: this doesnt seem to work if you use a defn / macro 
                # that produces `let` inside a macro body...
                elif node.value in macro_local_var_map:
                    return ASTIdentifier(macro_local_var_map[node.value])
                else:
                    return node
           
            # Excluding identifiers, i.e. constants
            elif isinstance(node, ASTLeaf):
                return node
            # NOT A LEAF (CONSTANT / ID) SO IT MUST BE AN EXPR;
            # THE HEAD COULD BE A MACRO THOUGH!
            me = substitute(node.value)
            new_children = []
            for child in node.children:
                subbd = substitute(child)
                new_children.append(subbd)
            return ASTExpr(me, *new_children)
            
        node_transformed = substitute(macro_body)
        self.print_debug("-- Macro Transform:")
        self.print_debug(macro_body)
        self.print_debug(f"with args {list(zip(macro_arg_names, args))}")
        self.print_debug(node_transformed)
        self.compile_node(node_transformed)
        return


    def compile_node(self, node: ASTNode):
        if isinstance(node, ASTModule):
            self.compile_program(node)
        elif isinstance(node, ASTExpr):
            if (
                isinstance(node.value, ASTIdentifier)
                and node.value.value in self.macros
            ):
                self.compile_macro(node)
            else:
                self.compile_expr(node)
        elif isinstance(node, ASTConstantValue):
            self.compile_const(node)
        elif isinstance(node, ASTIdentifier):
            self.compile_identifier(node)
        else:
            msg = " ".join([_ for _ in node.__rich_repr__()])
            raise ValueError(f"Unknown node type '{msg}'")
