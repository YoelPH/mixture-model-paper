"""
Define paths for data and models.
"""
from pathlib import Path
from typing import Literal

data_dir = Path("data")
data = data_dir / "reduced.csv"
model_dir = Path("models")


def get_filename(
    model: Literal["ipsi", "contra", "bilateral", "midline"],
    kind: Literal["params", "samples", "priors", "posteriors", "prevalences", "risks"],
) -> Path:
    """Get the filename of the samples of one of the four trained models."""
    return next((model_dir / model).glob(f"{kind}.*"))
