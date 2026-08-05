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
  make run
````
or simply,

````
  make run
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
