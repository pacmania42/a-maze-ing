*This project has been created as part of the 42 curriculum by lupetill and semebrah.*

*Project version* **2.2**

## Description

a-maze-ing is a modular python project to generate and solve mazes of different
complexity. It builds mazes based on the user's preference in the form of a
configuration and saves the maze solution to a file for later use. It also
displays this in a beautiful GUI.

The main objective of this project is to familarize with and do a deep research
graph theory from computer science.


## Instructions

a-maze-ing comes with a Makefile to automate some of the common tasks with the
project such as to install, run, format, lint and test.

### Installation
````
  make install
````

### Running the application
````
  make # or
  make run # or
  uv run python a_maze_ing.py config_file.txt
````

### Running the application on visualize-only mode
The application can also be used to visaulize an already-generated maze by setting the `-v` switch in which case, the mandatory file will be treated as a generated maze data.
````
  uv run python a_maze_ing.py output_maze.txt -v
````


### Formating the source files
````
  make format
````
This recipie uses ruff to format files quickly.

### Linting the source files
````
  make lint
````
or to lint with stricter rules,

````
  make lint
````
This recipie uses ruff, flake8 and mypy for linting and static type-checking.

### Testing the project
````
  make test
````
This uses pytest to run the test suite in tests/ which include a thorough
test suite for the parser.

## Configuring the maze definition

To define a maze to generate in a configurable way, the program accepts the
following keys.

| key name | format   | defining | constraints |
|----------|----------|----------|-------------|
| HEIGHT   | int      | vertical cell count       | 0 - 800 |
| WIDTH    | int      | horizontal cell count     | 0 - 800 |
| ENTRY    | int,int  | entry coordinates         | None    |
| EXIT     | int,int  | exit coordinates          | None    |
| OUTPUT_FILE | string| file to save the solution | Writable file |
| PERFECT | boolean   | whether to create a *perfect maze*   | None |

## mazegenerator package
To facilitate the development, the project has been devided into 2 big parts:
- maze generation/solving
- ui

This approach allows ui to be developed and tested independently of the maze generation part.
During the early stages of the development, we have used a temporary mazegenerator from pacman
while own mazegenerator package was being developed. Hence, the mazegenerator package is API-compatible
with 42's mazegenerator (from Pac-Man).

mazegenerator exposes a `MazeGenerator` class with the following structure:
```
MazeGenerator(
    size: tuple[int, int] = (15, 15),
    perfect: bool = False,
    entry_cell: tuple[int, int] = (0, 0),
    exit_cell: tuple[int, int] = (-1, -1),
    seed: int = 0
) None

  # fields
  maze: list[list[int]]
  shortest_path: str
  
  # methods
  generate(self, seed: int = 0) -> None
 
```

## Collaboration workflow
Working in a team, we followed the following workflow:
- Take a task from any open issues (assign to oneself)
- Move the task to 'In progress'.
- Create a branch (preferably from the issue page).
- Fetch and checkout to that branch on your local.
- Commit (several) and push.
- Create test cases.
- Update the readme.
- Test (make test) & check linting (make lint-strict).
- Create a PR.
- Set the task done after the PR is merged

#### Reviewer's role
- Review
- Merge (using `squash and merge`)

### Git hooks
To make sure we push clean code, we tapped into the commit hook (pre-commit) and we made it run the following things:
- Format the code
- Check lint
- Check tests

the hooks sit at .githooks/

Failure at any point prevents the commit.
This can be bypassed by doing `git commit --no-verify` when necessary.

## Resources
[Harm Smits's 42 Docs](https://harm-smits.github.io/42docs/libs/minilibx.html) \
[Keuhdall's mlx performance optimization guide/repo](https://github.com/keuhdall/images_example)
