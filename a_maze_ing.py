from mazegenerator import MazeGenerator

from src.adapter import Adapter, AdapterError
from src.models import ParseError
from src.parser import Parser
from src.ui import UI


def main() -> None:
    try:
        parser = Parser()
        cfg = parser.parse()
    except ParseError as err:
        print(err)

    # generate a maze
    gen = MazeGenerator(
        (cfg.height, cfg.width),
        cfg.perfect,
        cfg.entry,
        cfg.exit,
    )
    gen.generate()

    try:
        adapter = Adapter(gen)
    except AdapterError as e:
        print(e)
        return

    ui = UI(adapter)
    ui.show()


if __name__ == "__main__":
    main()
