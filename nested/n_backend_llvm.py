# Stack gets passed as an object in bc the internal IR for interpreting needs it,
# but this driver doesnt need it.
def add(_stk, nargs):
    ...