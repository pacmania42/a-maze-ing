import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from src.models import ConfigData, ParseError
from src.parser import Parser


# Utility: write a config to a temp file
def write_config(content: str) -> str:
    tf = tempfile.NamedTemporaryFile("w+", delete=False)
    tf.write(content)
    tf.flush()
    return tf.name


# --- TESTS ---


def run_parser_with_file(config_path: str) -> ConfigData:
    """
    Run the parser simulating CLI input by mocking sys.argv.
    """
    parser = Parser()
    with mock.patch.object(sys, "argv", ["prog", config_path]):
        return parser.parse()


def test_valid_config(tmp_path: Path) -> None:
    config_text = f"""
WIDTH=15
HEIGHT=12
ENTRY=0,0
EXIT=7,8
OUTPUT_FILE={tmp_path / "maze_out.txt"}
PERFECT=True
"""
    fname = write_config(config_text)
    try:
        config: ConfigData = run_parser_with_file(fname)
        assert config.width == 15
        assert config.height == 12
        assert config.entry == (0, 0)
        assert config.exit == (7, 8)
        assert config.perfect is True
    finally:
        os.unlink(fname)


def test_missing_key() -> None:
    config_text = """
WIDTH=15
ENTRY=0,0
EXIT=7,8
OUTPUT_FILE=maze.txt
"""
    fname = write_config(config_text)
    try:
        with pytest.raises(ParseError) as exc:
            run_parser_with_file(fname)
        # Robust: Just check missing key (here, "height") mentioned
        assert "height" in str(exc.value).lower()
    finally:
        os.unlink(fname)


def test_unknown_key() -> None:
    config_text = """
WIDTH=15
HEIGHT=12
ENTRY=0,0
EXIT=7,8
OUTPUT_FILE=maze.txt
PERFECT=True
ALIEN=42
"""
    fname = write_config(config_text)
    try:
        with pytest.raises(ParseError) as exc:
            run_parser_with_file(fname)
        err_str = str(exc.value)
        # Just check for the alien field name in the error message
        assert "alien" in err_str.lower()
    finally:
        os.unlink(fname)


def test_non_integer_width() -> None:
    config_text = """
WIDTH=foo
HEIGHT=12
ENTRY=0,0
EXIT=7,8
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    fname = write_config(config_text)
    try:
        with pytest.raises(ParseError) as exc:
            run_parser_with_file(fname)
        # Just check for the field name in the error (width)
        assert "width" in str(exc.value).lower()
    finally:
        os.unlink(fname)


def test_extraneous_value_line() -> None:
    config_text = """
WIDTH=10
HEIGHT=10
ENTRY=0,0,1
EXIT=5,5
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    fname = write_config(config_text)
    try:
        with pytest.raises(ParseError) as exc:
            run_parser_with_file(fname)
        err_str = str(exc.value)
        # Just check for the field (entry) in error string
        assert "entry" in err_str.lower()
    finally:
        os.unlink(fname)
