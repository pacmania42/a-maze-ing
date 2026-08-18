"""
parser.py

Handles the parsing of configuration files for the maze generation and solving
package. Provides the Parser class that reads, validates, and normalizes
configuration data into a validated model.
"""

from argparse import ArgumentParser, Namespace
from typing import Any

from pydantic import ValidationError

from src.models import ConfigData, ParseError


class Parser:
    default_output: str = "output_maze.txt"
    """
    Parser for loading and validating maze configuration files.

    Methods
    -------
    parse() -> ConfigData
        Parses CLI args, loads config, validates, and returns config data as a
        model object.
    """

    def parse_args(self) -> Namespace:
        """
        Parse the command-line argument to obtain the target file path.

        Returns
        -------
        Path
          : dictionary-like object containing values for `file` and `visualize`
        """
        parser = ArgumentParser(
            prog="uv run python a_maze_ing.py",
            description="A maze generation and solving package & program.",
        )

        # Require config file as positional argument
        parser.add_argument("file")

        # visualize-only mode
        parser.add_argument(
            "-v",
            "--visualize",
            action="store_true",
            help="Visulize only, config_file will be treated as output file",
        )

        return parser.parse_args()

    def parse_config_file(self, config_file: str) -> ConfigData:
        """
        Parses the config file.

        Parameters:
          config_file: configuration file location.

        Returns
        -------
        ConfigData
            A validated configuration data object for the maze.

        Raises
        ------
        ParseError
            If the file is not accessible or values are not valid per the
            ConfigData model.
        """
        data = self._parse_lines(config_file)
        normalized_data = self._normalize(data)
        try:
            return ConfigData(**normalized_data)
        except ValidationError as e:
            raise ParseError(f"Parser Error: {e.errors()}") from e

    def _parse_lines(self, config_file: str) -> dict[str, str]:
        """
        Parse config file lines into a dictionary.

        Parameters
        ----------
        config_file : Path
            Path to the configuration file.

        Returns
        -------
        dict[str, str]
            Keys/values from all valid (non-empty, non-comment) lines in the
            file.

        Raises
        ------
        ParseError
            If a line is in the wrong format or the file is inaccessible.
        """
        data: dict[str, str] = {}
        try:
            with open(config_file) as file:
                for line in file:
                    line = line.strip()

                    # Ignore blanks and comments
                    if not line or line.startswith("#"):
                        continue

                    try:
                        # Expect format "key=value" on each line
                        key, value = line.split("=")
                        data[key.strip()] = value.strip()
                    except ValueError as err:
                        raise ParseError(f"Extraneous value: {line}") from err

                return data
        except OSError as err:
            raise ParseError(f"{config_file} not accessible: {err}") from err

    def _normalize(self, data: dict[str, str]) -> dict[str, Any]:
        """
        Normalize parsed dictionary's keys and values for model validation.

        Parameters
        ----------
        data : dict[str, str]
            Dictionary from the config file.

        Returns
        -------
        dict[str, Any]
            Dictionary ready for use by ConfigData. Entry/exit values split to
            lists; keys lowercased.

        Raises
        ------
        ParseError
            If ENTRY or EXIT are not in 'x,y' form.
        """
        new_dict: dict[str, Any] = {}

        for k, v in data.items():
            val: Any = v

            # Split ENTRY and EXIT fields into lists
            if k in ["ENTRY", "EXIT"]:
                try:
                    val = v.split(",")
                except ValueError as e:
                    raise ParseError(
                        f"{k} should be in the format of 'x,y': {v}"
                    ) from e
            new_dict[k.lower()] = val

        return new_dict
