from typing import List
from nested.backends.python.n_codeobj import CodeObj
from nested.backends.python.n_frame import Frame, SymTable
from nested.n_opcode import OpCode
from rich import print
from nested.backends.python.n_vm import VMIR

class VM:
    """
    Orchestrate execution from Python,
    but call out to the backend for the actual work.
    """
    def __init__(self, backend):
        self.backend = backend

    def run(self, code: CodeObj):
        self.backend.run(code)

    def debug(self):
        return self.backend.debug()