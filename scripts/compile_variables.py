"""Script to compile variables from data and models and stores them in a YAML file."""

import argparse
from pathlib import Path

import pandas as pd
import yaml


def create_parser() -> argparse.ArgumentParser:
    """Create an argument parser for the script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("_variables.yaml"),
        help="Path to the output YAML.",
    )
    return parser


def main() -> None:
    """Merge the variables from data and models and store them in `_variables.yaml`."""
    args = create_parser().parse_args()

    variables = {}

    with open(args.output, mode="w", encoding="utf-8") as file:
        yaml.dump(variables, file)
