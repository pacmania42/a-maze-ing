PYTHON := uv run python
MAIN := ./a_maze_ing.py
CONFIG := ./default_config.txt
OUTPUT := ./output_maze.txt

SRC = $(MAIN) \
	./src/adapter.py \
	./src/cell.py \
	./src/__init__.py \
	./src/models.py \
	./src/parser.py \
	./src/settings.py \
	./src/ui.py \
	./tests/test_parser.py \
	./tests/test_mazegenerator.py

MYPY_OPTIONS := --warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

SYNC := .synced

run: install
	$(PYTHON) $(MAIN) $(CONFIG)

vis: install
	$(PYTHON) $(MAIN) $(OUTPUT) -v

install: $(SYNC)

$(SYNC): pyproject.toml
	git config core.hooksPath .githooks
	uv sync || pip install uv && uv sync
	@touch $(SYNC)
	
debug: $(SYNC)
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -f maze.txt

lint: $(SYNC)
	ruff check $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC) $(MYPY_OPTIONS)

lint-strict: $(SYNC)
	ruff check $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC) --strict

format:
	ruff check --fix $(SRC)

analyze:
	$(PYTHON) ./maze_analyzer.py maze.txt

test: $(SYNC)
	uv run pytest
	

.PHONY: install run debug clean lint lint-strict format analyze test
