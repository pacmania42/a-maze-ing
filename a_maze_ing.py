import sys

from mazegenerator import MazeGenerator

from src.adapter import Adapter, AdapterError
from src.models import ParseError
from src.parser import Parser
from src.ui import UI


def main() -> None:
    parser = Parser()
    res = parser.parse_args()

    if not res.visualize:  # generate + visualize
        try:
            cfg = parser.parse_config_file(res.file)
        except ParseError as err:
            print(err)
            sys.exit(1)
        try:
            # generate a maze
            gen = MazeGenerator(
                (cfg.height, cfg.width),
                cfg.perfect,
                cfg.entry,
                cfg.exit,
            )
            gen.generate()
            # gen.export(Settings.output_file)
        except Exception as e:  # TODO: change to appropriate exception class.
            print(f"Generation error. {e}")
            sys.exit(2)
    else:  # visualize-only
        output_file = res.file

    try:
        adapter = Adapter(output_file)
    except AdapterError as e:
        print(e)
        return

    ui = UI(adapter)
    ui.show()


if __name__ == "__main__":
    main()
