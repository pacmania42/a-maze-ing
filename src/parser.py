"""
parser.py

Handles the parsing of configuration files for the maze generation and solving
package. Provides the Parser class that reads, validates, and normalizes
configuration data into a validated model.
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.models import ConfigData, ParseError


class Parser:
    """
    Parser for loading and validating maze configuration files.

    Methods
    -------
    parse() -> ConfigData
        Parses CLI args, loads config, validates, and returns config data as a
        model object.
    """

    def parse(self) -> ConfigData:
        """
        Parse the command-line argument to get the config file, read it,
        normalize the data, and return the validated config.

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
        config_file = self._parse_args()
        data = self._parse_lines(config_file)
        normalized_data = self._normalize(data)
        try:
            return ConfigData(**normalized_data)
        except ValidationError as e:
            raise ParseError(f"Parser Error: {e.errors()}") from e

    def _parse_args(self) -> Path:
        """
        Parse the command-line argument to obtain the config file path.

        Returns
        -------
        Path
            Path object pointing to the specified configuration file.
        """
        parser = ArgumentParser(
            prog="python a_maze_ing.py",
            description="A maze generation and solving package & program.",
        )

        # Require config file as positional argument
        parser.add_argument("config_file")

        # Return Path object of the provided config file
        return Path(parser.parse_args().config_file)

    def _parse_lines(self, config_file: Path) -> dict[str, str]:
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
