import sys

from mazegen import MazeGenerator

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
            gen = MazeGenerator(
                size=(cfg.width, cfg.height),
                entry=cfg.entry,
                exit=cfg.exit,
                output_file=cfg.output_file.name,
                perfect=cfg.perfect,
                seed=cfg.seed,
            )
            gen.export()
            output_file = cfg.output_file.name
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
