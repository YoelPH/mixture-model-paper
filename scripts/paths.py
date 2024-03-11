"""
Define paths for data and models.
"""
from pathlib import Path

data_dir = Path("data")
filtered = data_dir / "filtered.csv"

model_dir = Path("models")
midline = model_dir / "midline.hdf5"
