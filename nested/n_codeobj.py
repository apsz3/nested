from typing import List

from nested.n_opcode import OpCode


class CodeObj:
    def __init__(self, code: List[OpCode]):
        self.code = code

    def __rich_repr__(self):
        yield "CodeObj"
        yield from self.code