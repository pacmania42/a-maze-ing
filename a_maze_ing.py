import sys

from src.adapter import Adapter, AdapterError
from src.maze_view import MazeView
from src.models import ParseError
from src.parser import Parser
from src.settings import Settings


def main() -> None:
    parser = Parser()
    stg = Settings()
    res = parser.parse_args()

    cfg = None
    output_file = res.file
    if not res.visualize_only:  # generate + visualize
        try:
            cfg = parser.parse_config_file(res.file)
            output_file = cfg.output_file.name
        except ParseError as err:
            print(err)
            sys.exit(1)

    try:
        adapter = Adapter(output_file, cfg, stg)
        adapter.generate()
    except AdapterError as e:
        print(e)
        return

    ui = MazeView(adapter, res.visualize_only, stg)
    ui.show()


if __name__ == "__main__":
    main()
