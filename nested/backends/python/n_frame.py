from __future__ import annotations

from typing import Optional

from nested.backends.python.n_codeobj import CodeObj

class SymTable:
    def __init__(self):
        self.symbols = {}

    def set(self, name, value):
        self.symbols[name] = value

    def get(self, name):
        return self.symbols.get(name, None)

    def __getitem__(self, name):
        return self.symbols[name]

    def __rich_repr__(self):
        yield "SymTable"
        for sym in self.symbols:
            yield sym, self.symbols.get(sym, "...")

    def union(self, other):
        new = SymTable()
        new.symbols.update(self.symbols)
        new.symbols.update(other.symbols)
        return new

    def dump(self):
        return self.symbols

    def copy(self):
        new = SymTable()
        new.symbols.update(self.symbols)
        return new

# We allow lexical scoping so overriding globals, hence the need to always
# traverse up the chain of frames for lookups
class Frame:
    def __init__(self, code: CodeObj, locals: SymTable, parent: Optional[Frame]):
        self.code = code
        self.locals = locals
        self.parent = parent
        self.ip = 0

    @property
    def instr(self):
        if self.ip >= len(self.code):
            return None
        return self.code[self.ip]

    def __next__(self):
        self.ip += 1

    def setsym(self, name: str, value: str):
        self.locals.set(name, value)

    def getsym(self, name):
        if (res := self.locals.get(name)):
            return res
        if self.parent:
            return self.parent.getsym(name)
        else:
            raise ValueError(f"Symbol {name} not found in any scope")

    def __rich_repr__(self):
        yield self.locals
        yield self.parent
