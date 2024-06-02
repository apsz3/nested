from typing import List

from nested.n_opcode import OpCode


class CodeObj:
    def __init__(self, code: List[OpCode]):
        self.code = code

    def __len__(self):
        return len(self.code)

    def __rich_repr__(self):
        yield from self.code

class ParamObj:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    def __rich_repr__(self):
        yield self.name
        yield self.type

class FunObj:
    def __init__(self, code: List[OpCode], params: List[ParamObj]):
        self.code = code
        self.params = params

    def __len__(self):
        return len(self.code)

    @property
    def nargs(self):
        return len(self.params)

    def __rich_repr__(self):
        yield self.params
        yield from self.code