"""
Define paths for data and models.
"""
from pathlib import Path
from typing import Literal

data_dir = Path("data")
data = data_dir / "reduced.csv"
model_dir = Path("models")
cache_dir = Path(".cache")
figure_dir = Path("figures")


def get_filename(
    model: Literal["ipsi", "contra", "bilateral", "midline"],
    kind: Literal["params", "samples", "priors"] | str,
) -> Path:
    """Get the filename of the samples of one of the four trained models."""
    return next((model_dir / model).glob(f"{kind}.*"))
