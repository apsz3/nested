from rich import print
class VMIR:

# Keep these functions separate as only in interpreter mode do we want to
# cast things for example

    @staticmethod
    def add(s):
        s.append(int(s.pop()) + int(s.pop()))

    @staticmethod
    def print(s):
        print(f"> {s.pop()}")