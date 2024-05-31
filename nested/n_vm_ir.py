from rich import print

def err(msg):
    print(f"[red]Error: {msg}[/red]")

def msg(msg):
    print(f"[green]{msg}[/green]")

class VMIR:
# Keep these functions separate as only in interpreter mode do we want to
# cast things for example

        @staticmethod
        def add(s, n:int):
            if n < 2:
                err("? (Possible nonsense) Add needs 2 or more arguments!")
                return
            s.append(sum([int(s.pop()) for _ in range(n)]))

        @staticmethod
        def print(s, n: int):
            try:
                args = [str(s.pop()) for _ in range(n)]
                msg(f"> {' '.join(args)}")

            except IndexError:
                err("! Need more arguments")

        @staticmethod
        def list(s, n: int):
            s.append([s.pop() for _ in range(n)])
