"""Script to compile variables from data and models and stores them in a YAML file."""

import argparse
from pathlib import Path

import pandas as pd
import yaml
from pydantic_settings import BaseSettings


class CmdSettings(BaseSettings, cli_parse_args=True):
    """Settings for the command-line arguments."""

    output: Path = Path("_variables.yaml")


def main() -> None:
    """Merge the variables from data and models and store them in `_variables.yaml`."""
    cmd = CmdSettings()

    variables = {}

    with open(cmd.output, mode="w", encoding="utf-8") as file:
        yaml.dump(variables, file)
