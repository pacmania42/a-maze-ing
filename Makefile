PYTHON := uv run python
MAIN := a_maze_ing.py
CONFIG := default_config.txt

SRC = $(MAIN) \
	./src/parser.py \
	./src/models.py \
	./tests/test_parser.py

SYNC := .synced

run: install
	$(PYTHON) $(MAIN) $(CONFIG)

install: $(SYNC)

$(SYNC): pyproject.toml
	uv sync || pip install uv && uv sync
	@touch $(SYNC)
	
debug: $(SYNC)
	$(PYTHON) -n pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -f maze.txt

lint: $(SYNC)
	ruff check $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC) \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict: $(SYNC)
	ruff check $(SRC)
	uv run flake8 $(SRC)
	uv run mypy $(SRC) --strict

format:
	ruff format $(SRC)

analyze:
	$(PYTHON) ./maze_analyzer.py maze.txt

test: $(SYNC)
	uv run pytest
	

.PHONY: install run debug clean lint lint-strict format analyze
