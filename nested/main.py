from nested.n_compiler import Compiler
from nested.n_parser import parse as Parse
from nested.n_vm import VM
from rich import print
import click


@click.command()
@click.option('-p', '--parse', is_flag=True, help='Parse the file')
@click.option('-c', '--compile', is_flag=True, help='Compile the file')
@click.option('-d', '--debug', is_flag=True, help='Parse and compile and run')
@click.argument('file_path', type=click.Path(exists=True))
def main(parse, compile, debug, file_path):
    with open(file_path, "r") as fp:
        program = fp.read()
    p = Parse(program)
    print("-- Parse")
    print(p.children)

    tree = p.children[0]
    tree.visit()
    print("-- AST")
    print(tree)
    c = Compiler(tree)
    c.compile_program()
    print("-- IR")
    print(c.buffer)

    v = VM(c.buffer)
    print(v.exec())

if __name__ == '__main__':
    main()

