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
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class ParseError(Exception):
    """Exception raised for errors encountered during configuration parsing or
    validation."""

    # Custom exception for parsing/validation errors
    pass


class ConfigData(BaseModel):
    """Configuration data for maze generation and solving."""

    model_config = ConfigDict(
        extra="forbid"
    )  # Forbid extra fields not specified here
    width: int = Field(ge=2)
    height: int = Field(ge=2)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: Path
    perfect: bool = False
    seed: int = 42
    algorithm: Literal["IB", "wilson"] = "wilson"

    @field_validator("output_file")
    @classmethod
    def check_output_file_is_writable_file(cls, v: Path) -> Path:
        """Validates that the output file (if already existing) is writable.

        Args:
            v (Path): Value for `v`.

        Returns:
            Path: Result produced by `check_output_file_is_writable_file`.
        """
        if v.exists() and not os.access(v, os.W_OK):
            raise ParseError(f"ParseError: Output file '{v}' is not writable")
        return v

    @model_validator(mode="after")
    def check_entry_exit_within_bounds(self) -> "ConfigData":
        """Model-level validator to ensure entry and exit are within the maze
        bounds and do not overlap.

        Returns:
            'ConfigData': Result produced by `check_entry_exit_within_bounds`.
        """
        for name, (x, y) in (("entry", self.entry), ("exit", self.exit)):
            # Check x and y are within the boundaries
            if not (0 <= x < self.width):
                raise ParseError(
                        f"ParseError: {name}'s x coordinate has to be between"
                        f" 0 - {self.width-1}"
                        )
            if not (0 <= y < self.height):
                raise ParseError(
                        f"ParseError: {name}'s y coordinate has to be between"
                        f" 0 - {self.height-1}"
                        )
        if self.entry == self.exit:
            raise ParseError("ParseError: entry and exit must differ")
        return self
