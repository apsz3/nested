from lark import Tree
from enum import Enum, auto
from rich import print
from nested.n_parser import ASTExpr, ASTList, ASTNode, ASTModule, ASTConstantValue, ASTIdentifier, ASTOp
from nested.n_opcode import Op, OpCode

# Continuation -- add before / after / during, where during gets
# the parent class fn as an arg.
# opmap = {
#     ASTUnOpExpr.UnOps.NEG: OpCode.NEG,
#     ASTVaryOpExpr.VaryOps.PRINT: OpCode.PRINT,
#     ASTBinOpExpr.BinOps.ADD: OpCode.ADD
# }
class Compiler:

    def __init__(self, tree: Tree):
        self.tree = tree
        self.buffer = []
        self.ip = 0

    def display_buffer(self):
        for i, instr in enumerate(self.buffer):

            print(f"{i:<4}: {instr.opcode:<25} {' '.join(map(str, instr.args)):<15}")

    def emit(self, arg):
        self.buffer.append(arg)
        self.ip += 1

    def patch(self, ip, arg):
        self.buffer[ip] = arg

    def compile_program(self):
        self.emit(Op(OpCode.BEGIN_MODULE, "META"))
        # Get metadata from self.tree here (not children)
        self.compile(self.tree.children)
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
        self.patch(ip_of_jump_if_false - 1, Op(OpCode.JUMP_IF_FALSE, ip_of_jump_to_end - ip_of_jump_if_false, ip_of_jump_to_end))

        self.compile_node(els)
        self.patch(ip_of_jump_to_end - 1, Op(OpCode.JUMP, self.ip - ip_of_jump_to_end, self.ip))


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
        if isinstance(node.value, ASTOp): # builtin, just call its opcode
            op = Op.from_id(node.value)
            opcode = op.opcode

            match opcode:
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

                case OpCode.IF:
                    self.compile_if(node)
                    return

                case OpCode.BEGIN:
                    # Only compile the children, not the value
                    for child in node.children:
                        self.compile_node(child)
                    return

                case OpCode.QUOTE:
                    # Do not compile things -- we don't want to deal
                    # with implementation ops like jumps, etc.
                    # Rather, just retain the symbolic value of the nodes.
                    start = self.ip
                    # BFS
                    children = [*node.children]
                    while children:
                        child = children.pop(0)
                        if child is None:
                            break
                        if isinstance(child.value, ASTOp):
                            self.emit(Op(OpCode.LOAD_SYM, child.value.value))
                        else:
                            self.emit(Op(OpCode.LOAD_SYM, child.value))
                        # if isinstance(child, ASTOp):
                        #     self.emit(Op.from_id(child.value, 0))
                        for c in child.children:
                            children.append(c)
                    self.emit(Op.from_id(node.value, self.ip - start))
                    return

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
            # Need this for things like ((eval 'add) 1 2)); need to eval procs too
            self.compile_expr(node.value)
        else:
            raise ValueError(f"Unknown expr: {node.value}")

    def compile_lambda(self, node: ASTOp):
        self.emit(Op(OpCode.PUSH_LAMBDA)) # TODO: this is probably not necessary,
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

    def compile_identifier(self, node: ASTIdentifier):
        self.emit(Op(OpCode.LOAD, node.value))

    def compile_node(self, node: ASTNode):
        if isinstance(node, ASTModule):
            self.compile_program(node.children)
        elif isinstance(node, ASTExpr):
            self.compile_expr(node)
        elif isinstance(node, ASTConstantValue):
            self.compile_const(node)
        elif isinstance(node, ASTIdentifier):
            self.compile_identifier(node)
        elif isinstance(node, ASTExpr):
            self.compile_expr(node)
        else:
            msg = " ".join([_ for _ in node.__rich_repr__()])
            raise ValueError(f"Unknown node type '{msg}'")
