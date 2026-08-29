*This project has been created as part of the 42 curriculum by lupetill, semebrah.*

# a-maze-ing

*Project version: 2.2*

## Description

`a-maze-ing` is a modular Python project that generates, solves, exports, and
visualizes mazes. Maze generation is delegated to the reusable `mazegen`
module, while this repository handles configuration parsing, adaptation of the
generated data, analysis, and the graphical interface built with MiniLibX.

The project applies graph concepts to maze generation and pathfinding while
keeping the generation logic independent from the visualization layer. It
supports reproducible generation through seeds, perfect and non-perfect mazes,
multiple generation algorithms, a visible `42` pattern, animated maze carving,
an animated shortest-path display, and interactive controls.

A generated maze is also exported to a text file so that it can later be loaded
again in visualize-only mode.

## Instructions

### Requirements

- Python 3.10 or later
- `uv`
- MiniLibX Python binding supplied through the local project wheel
- the `mazegen` maze-generator dependency

### Installation

Synchronize the project dependencies with:

```bash
make install
```

### Run with the default configuration

```bash
make
```

or:

```bash
make run
```

The default target uses `default_config.txt`.

### Run with a custom configuration

```bash
uv run python a_maze_ing.py config_file.txt
```

The application parses the configuration, generates the maze, exports it to the
configured output file, and opens the graphical visualizer.

### Visualize an existing maze file

```bash
uv run python a_maze_ing.py maze.txt -v
```

For the default `maze.txt` file, the Makefile also provides:

```bash
make vis
```

In visualize-only mode, the positional argument is treated as an already
exported maze rather than a configuration file.

### Interactive controls

| Key | Action |
| --- | --- |
| `m` | Regenerate the maze with a new random seed |
| `p` | Show or hide the shortest path |
| `w` | Cycle through the available wall colors |
| `ESC` | Close the application |

When a maze is generated from a configuration file, the visualizer animates the
wall-carving order supplied by the generator. The shortest path is also drawn
progressively.

### Format

```bash
make format
```

### Lint and type-check

```bash
make lint
```

For strict mypy checking:

```bash
make lint-strict
```

The project uses Ruff, Flake8, and mypy.

### Tests

```bash
make test
```

The test suite uses pytest and includes parser validation and checks for the
public `MazeGenerator` API.

### Analyze a generated maze

After generating the default `maze.txt`:

```bash
make analyze
```

The analyzer checks properties such as wall coherence, connectivity, loops, and
dead ends. It can also be executed directly with additional thresholds, for
example:

```bash
uv run python maze_analyzer.py maze.txt --min-loops 2 --max-dead-ends 0
```

Using `--max-dead-ends 0` is useful when checking the no-dead-end bonus.

## Configuration file structure

The configuration is a plain-text file containing one `KEY=VALUE` pair per
line. Empty lines and lines beginning with `#` are ignored.

A complete example is:

```text
WIDTH=15
HEIGHT=15
ENTRY=0,0
EXIT=14,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=IB
```

The current `default_config.txt` uses the same values except that `SEED` is
omitted, so the model default of `42` is used.

### Supported keys

| Key | Format | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `WIDTH` | integer | Yes | — | Number of maze columns |
| `HEIGHT` | integer | Yes | — | Number of maze rows |
| `ENTRY` | `x,y` | Yes | — | Entry-cell coordinates |
| `EXIT` | `x,y` | Yes | — | Exit-cell coordinates |
| `OUTPUT_FILE` | path | Yes | — | File used to export the generated maze |
| `PERFECT` | boolean | No | `False` | Generate a perfect maze when true |
| `SEED` | integer | No | `42` | Seed used for reproducible generation |
| `ALGORITHM` | `IB` or `wilson` | No | `wilson` | Generation algorithm |

Unknown keys are rejected.

### Coordinates

Coordinates use `x,y` order:

```text
ENTRY=0,0
EXIT=14,14
```

Both cells must be inside the configured width and height, and entry and exit
must be different.

### Width and height

`WIDTH` and `HEIGHT` are validated as non-negative integers. In practice, they
must also be large enough for the configured entry and exit coordinates.

### Output file

```text
OUTPUT_FILE=maze.txt
```

If the output file already exists, it must be writable.

### Perfect mode

```text
PERFECT=True
```

requests a perfect maze. If omitted, `PERFECT` defaults to `False`.

### Seed

```text
SEED=42
```

The seed makes random generation reproducible. Reusing the same generation
parameters and seed produces the corresponding deterministic result from the
selected generator algorithm.

### Algorithm

The application currently accepts:

```text
ALGORITHM=IB
```

or:

```text
ALGORITHM=wilson
```

If the key is omitted, the configuration model defaults to `wilson`.

## Maze generation algorithms

The reusable generator supports two algorithms that can be selected from the
configuration file.

### Iterative Backtracking (`IB`)

Iterative Backtracking performs depth-first maze generation using an explicit
stack rather than recursive function calls. It is straightforward, efficient,
and commonly creates long winding corridors. The repository's current
`default_config.txt` selects this algorithm.

### Wilson's algorithm

Wilson's algorithm builds the maze with loop-erased random walks. For perfect
maze generation it produces an unbiased uniform spanning tree, which gives a
different structure from the corridor bias typically associated with
backtracking.

### Why support both

The generator and graphical interface were deliberately separated, so the
application can select different generation strategies without changing the
rendering code. Supporting both algorithms demonstrates that the UI depends on
a stable generator API rather than on one particular implementation. It also
makes it possible to compare the visual characteristics of two substantially
different generation approaches.

## Reusable code: `mazegen`

The maze-generation and solving logic is reusable independently from the MLX
application. It is exposed through the `mazegen` import package and its
`MazeGenerator` class:

```python
from mazegen import MazeGenerator

maze = MazeGenerator()

print(maze.maze)
print(maze.shortest_path)
```

Custom generation parameters can be supplied directly:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    size=(20, 10),
    entry_cell=(0, 0),
    exit_cell=(19, 9),
    perfect=True,
    seed=42,
    algorithm="IB",
)

print(maze.maze)
print(maze.maze_entry)
print(maze.maze_exit)
print(maze.shortest_path)
```

The API consumed by this application provides the generated wall grid, entry
and exit, shortest-path directions, optional pattern data, and the carving
order used by the animation. A maze can be regenerated with:

```python
maze.generate(seed=123)
```

and exported with:

```python
from pathlib import Path

maze.export(Path("maze.txt"))
```

Inside this project, `src/adapter.py` isolates the UI from the generator. It
converts integer wall masks into `Cell` objects and converts the shortest-path
NESW string into the sequence of cells required by the renderer. The same
adapter interface is also implemented for loading an already exported maze in
visualize-only mode.

## Output file format

The exported maze contains:

1. one hexadecimal digit per cell, one maze row per line;
2. a blank line;
3. the entry coordinate as `x,y`;
4. the exit coordinate as `x,y`;
5. the shortest path as a sequence of `N`, `E`, `S`, and `W` directions.

Conceptually:

```text
D539...
93C6...
...

0,0
14,14
EESS...
```

Each bit in a hexadecimal cell value represents one closed wall:

- bit 0: North
- bit 1: East
- bit 2: South
- bit 3: West

## Display and bonus features

The MLX view renders the maze into an image buffer and then displays that image
inside a window. The project currently includes the following advanced display
features:

- animated carving of a newly generated maze;
- animated rendering of the shortest path;
- regeneration with a new random seed using `m`;
- shortest-path visibility toggle using `p`;
- selectable wall colors using `w`;
- rendering of the required `42` pattern;
- display of the selected algorithm in the footer;
- visualize-only mode for previously exported mazes;
- support for multiple maze-generation algorithms.

## Team and project management

### Roles

The project was developed by **lupetill** and **semebrah**. Both members worked
through shared GitHub issues, pull requests, reviews, integration, and testing,
with their main focus areas divided as follows:

- **lupetill** — configuration parsing and validation, project setup, generator
  development/API work, generator integration, testing, and documentation.
- **semebrah** — MLX visualization, adapter/UI integration, interactive display
  features, dependency/environment integration, testing, and documentation.

The separation was not absolute: both members contributed to integration and
reviewed changes affecting the shared application.

### Anticipated planning and how it evolved

The work was planned as small GitHub issues grouped around setup,
configuration, generation, pathfinding/output, visualization, packaging,
testing, and documentation. Feature branches were created from those tasks and
merged through pull requests.

A major design decision was to separate maze generation from the graphical
application. During early UI development, a compatible temporary generator
could be used while the reusable generator package evolved independently. As
the project progressed, the interface grew to include multiple algorithms,
pattern information, and carving-order data used by the animation.

The visualizer also evolved from displaying a static maze into an interactive
application with regeneration, path visibility, wall-color changes, algorithm
information, visualize-only loading, and animation.

### What worked well

- Small issues made the work easier to divide and review.
- Feature branches and pull requests kept changes isolated.
- The adapter provided a clear boundary between generator and renderer.
- The standalone generator allowed generation logic to be developed and tested
  separately from MLX.
- Automated tests, linting, formatting, type checking, and Git hooks caught
  problems before merging.
- Supporting a stable generator API made it possible to add a second algorithm
  without redesigning the UI.

### What could be improved

Integration produced additional work whenever the reusable generator API or
its packaged wheel changed. Development also depended on compatible local MLX
and Python environments. Defining and freezing the application/generator
interface and development-tool versions earlier would reduce this integration
cost.

Animation and graphical refresh behavior also required experimentation with the
MLX event/display model. A future version could further isolate animation state
and timing from the drawing routines so that rendering remains fully event
loop-driven.

### Tools and workflow

The project uses Git and GitHub for version control, issues, branches, pull
requests, and reviews. Development and validation use Python, `uv`, MiniLibX,
Pydantic, pytest, Ruff, Flake8, mypy, Make, and a Git pre-commit hook.

The usual workflow was:

1. choose and assign an open issue;
2. move it to in-progress;
3. create and check out a feature branch;
4. implement the change;
5. add or update tests where applicable;
6. run formatting, linting, and tests;
7. push and open a pull request;
8. review the pull request;
9. squash and merge after approval.

The `.githooks/pre-commit` hook runs project checks before accepting a normal
commit. It can still be deliberately bypassed with Git's `--no-verify` option
when necessary.

## Code documentation

Project classes and functions contain PEP 257-style docstrings describing their
purpose. The main responsibilities are split across:

- `a_maze_ing.py` — application entry point;
- `src/parser.py` — CLI and config-file parsing;
- `src/models.py` — validated configuration model;
- `src/adapter.py` — generator/UI compatibility layer;
- `src/cell.py` — decoded wall representation for one visual cell;
- `src/maze_view.py` — MLX rendering, animation, and key handling;
- `src/settings.py` — graphical constants and `42` pattern;
- `maze_analyzer.py` — structural checks for generated output;
- `tests/` — parser and public generator API tests.

## Resources

References used during development include:

- [Harm Smits' 42 Docs — MiniLibX](https://harm-smits.github.io/42docs/libs/minilibx.html)
- [Keuhdall's MLX image/performance examples](https://github.com/keuhdall/images_example)
- Python documentation
- Pydantic documentation
- pytest documentation
- `uv build` documentation

### AI usage

AI was used responsibily for documenting the project (google-style python docstrings and the README.md).