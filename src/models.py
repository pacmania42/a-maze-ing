"""
models.py

Defines data models and validation logic for maze configuration, entry/exit
validation, and related exceptions.

Contains:
- ParseError: Error raised during parsing or validation.
- ConfigData: Pydantic model for configuration, with custom field and model
  validators.
"""

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class ParseError(Exception):
    """
    Exception raised for errors encountered during configuration parsing or
    validation.
    """

    # Custom exception for parsing/validation errors
    pass


class ConfigData(BaseModel):
    """
    Configuration data for maze generation and solving.

    Attributes
    ----------
    width : int
        Maze width (must be non-negative).
    height : int
        Maze height (must be non-negative).
    entry : tuple[int, int]
        Entry cell coordinates (x, y).
    exit : tuple[int, int]
        Exit cell coordinates (x, y).
    output_file : Path
        Output path where the maze will be saved.
    perfect : bool, optional
        If True, generates a "perfect" maze. Defaults to False.
    seed : Optional[int], optional
        Randomization seed, if any.
    algorithm : Optional[Literal['prim', 'wilson']]
        Maze generation algorithm. Can be 'prim' or 'wilson'.
    """

    model_config = ConfigDict(
        extra="forbid"
    )  # Forbid extra fields not specified here
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: Path
    perfect: bool = Field(default=False)
    seed: Optional[int] = None
    algorithm: Optional[Literal["prim", "wilson"]] = None

    @field_validator("output_file")
    @classmethod
    def check_output_file_is_writable_file(cls, v: Path) -> Path:
        """
        Validates that the output file (if already existing) is writable.

        Parameters
        ----------
        v : Path
            The output file path.

        Returns
        -------
        Path
            The same Path, if writable.

        Raises
        ------
        ParseError
            If the file exists and is not writable.
        """
        if v.exists() and not os.access(v, os.W_OK):
            raise ParseError(f"Output file '{v}' is not writable")
        return v

    @model_validator(mode="after")
    def check_entry_exit_within_bounds(self) -> "ConfigData":
        """
        Model-level validator to ensure entry and exit are within the maze
        bounds and do not overlap.

        Returns
        -------
        ConfigData
            Self (for model chaining).

        Raises
        ------
        ParseError
            If entry/exit are out of range or duplicate.
        """
        for name, (x, y) in (("entry", self.entry), ("exit", self.exit)):
            # Check x and y are within the boundaries
            if not (0 <= x < self.width):
                raise ParseError(f"{name} x-coordinate out of bounds")
            if not (0 <= y < self.height):
                raise ParseError(f"{name} y-coordinate out of bounds")
        if self.entry == self.exit:
            raise ParseError("entry and exit must differ")
        return self
