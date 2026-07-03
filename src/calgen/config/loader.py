"""Load calendar configuration from a YAML file."""

import os

import yaml
from pydantic import ValidationError

from calgen.config.calendar import CalendarConfig


def load_config(path: "str | os.PathLike[str]") -> CalendarConfig:
    with open(path, "r", encoding="utf-8") as handle:
        try:
            data = yaml.safe_load(handle)
        except yaml.YAMLError as error:
            raise ValueError(f"Invalid YAML in {path}: {error}") from error

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(
            f"Config in {path} must be a mapping, got {type(data).__name__}"
        )

    try:
        return CalendarConfig(**data)
    except ValidationError as error:
        raise ValueError(f"Invalid configuration in {path}: {error}") from error
