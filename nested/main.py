from nested.backends.python.n_codeobj import CodeObj
from nested.backends.python.n_frame import Frame, SymTable
from nested.backends.python.n_vm import VMIR
from nested.n_compiler import Compiler
from nested.n_parser import parse as Parse
from nested.n_vm import VM
from rich import print
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory


def repl(debug):
    history = FileHistory(".nst_history.txt")
    v = VM(VMIR())
    session = PromptSession(history=history)
    frame = Frame(CodeObj([]), SymTable(), None)
    while True:
        try:
            program = session.prompt(">>> ")
            p = Parse(program)

            tree = p.children[0]
            tree.visit()

            c = Compiler(tree)
            c.compile_program()

            v = VM(VMIR())
            code = CodeObj(c.buffer)
            stack, frame, call_stack = v.run(code, debug=debug)
            if stack:
                print(stack[-1])

        except Exception as e:
            print(e)


#     # TODO: make the symbol table perist...


#     v = VM(VMIR())
#     # frame = Frame(CodeObj([]), SymTable(), None)
#     while True:
#         try:
#             program = input(">>> ")
#             p = Parse(program)

#             tree = p.children[0]
#             tree.visit()
#             c = Compiler(tree)
#             c.compile_program()
#             code = CodeObj(c.buffer)
#             # TODO: get frame
#             v.run(code)
#             stack, call_stack, _ = v.debug()
#             print(*stack)
#         except Exception as e:
#             print(e)


@click.command()
@click.option("-p", "--parse", is_flag=True, help="Parse the file")
@click.option("-c", "--compile", is_flag=True, help="Compile the file")
@click.option("-d", "--debug", is_flag=True, help="Parse and compile and run")
@click.option("-i", is_flag=True)
@click.argument("file_path", type=click.Path(exists=True))
def main(parse, compile, debug, i, file_path):
    if i:
        repl(debug)
        repl(debug)
        return
    with open(file_path, "r") as fp:
        program = fp.read()
    p = Parse(program)
    if debug:
        print("-- Parse")
        print(p.children)

    tree = p.children[0]
    tree.visit()
    if debug:
        print("-- AST")
        print(tree)

    c = Compiler(tree)
    c.compile_program()
    if debug:
        print("-- IR")
        # Align the operands and arguments for the items in the buffer:
        c.display_buffer()

    v = VM(VMIR())
    code = CodeObj(c.buffer)
    v.run(code, debug=debug)

    if debug:
        stack, call_stack, frame = v.debug()

        print("-- VM")
        print("stack", stack)
        print("call stack", call_stack)
        print(frame)
    # print(f"> {v.run(c.buffer)}")


if __name__ == "__main__":
    main()
