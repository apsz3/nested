from __future__ import annotations

from typing import Optional

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
        yield from self.symbols

    def union(self, other):
        new = SymTable()
        new.symbols.update(self.symbols)
        new.symbols.update(other.symbols)
        return new

# Globals are special, passed by copy into each frame for quick reference...
# Otherwise we wouldnt need a globals table, we'd just have a parent frame,
# and search up the chain; but that is very inefficient

class Frame:
    def __init__(self, globals: SymTable, locals: SymTable, parent: Optional[Frame]):
        self.globals = globals
        self.locals = locals
        self.parent = parent

    def get(self, name):
        if (res := self.locals.get(name)):
            return res
        if (res := self.globals.get(name)):
            return res
        if self.parent:
            return self.parent.lookup(name)
        else:
            raise ValueError(f"Symbol {name} not found in any frame")

    def __rich_repr__(self):
        yield "Frame"
        yield from self.locals
        yield self.parent
