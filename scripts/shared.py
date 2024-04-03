"""
Some shared and reduced functions for the scripts.
"""
from typing import Any, Literal

from lymph import types
from lyscripts import utils
import numpy as np

from . import paths


CM_TO_INCH = 0.393701
GOLDEN_RATIO = 1.61803398875


def get_model(
    which: Literal["ipsi", "contra", "bilateral", "midline"],
    load_samples: bool = True,
) -> types.Model:
    """Get one of the four trained models."""
    params_path = paths.model_dir / which / "params.yaml"
    params = utils.load_yaml_params(params_path)
    model = utils.create_model(params)

    if not load_samples:
        return model

    samples_path = paths.model_dir / which / "samples.hdf5"
    samples = utils.load_model_samples(samples_path)
    model.set_params(*samples.mean(axis=0))
    return model


def get_samples(
    which: Literal["ipsi", "contra", "bilateral", "midline"]
) -> np.ndarray:
    """Get the samples of one of the four trained models."""
    samples_path = paths.model_dir / which / "samples.hdf5"
    return utils.load_model_samples(samples_path)


def get_fontsizes(base: int = 8, offset: int = 2) -> dict[str, int]:
    """Get fontsizes that can be used to update the matplotlib rcParams.

    This is essentially taken from the tueplots package v0.0.14.
    """
    return {
        "font.size": base,
        "axes.labelsize": base,
        "legend.fontsize": base - offset,
        "xtick.labelsize": base - offset,
        "ytick.labelsize": base - offset,
        "axes.titlesize": base,
    }


def get_figsizes(
    nrows: int = 1,
    ncols: int = 1,
    aspect_ratio: float = GOLDEN_RATIO,
    width: float = 17.0,
    pad: float = 0.005,
    unit: Literal["cm", "in"] = "cm",
    constrained_layout: bool = True,
    tight_layout: bool = True,
) -> dict[str, Any]:
    """Get figure sizes that can be used to update the matplotlib rcParams.

    This is heavily inspired by the tueplots package v0.0.14.
    """
    if unit == "cm":
        width *= CM_TO_INCH
        pad *= CM_TO_INCH

    subplot_width = width / ncols
    subplot_height = subplot_width / aspect_ratio
    height = subplot_height * nrows

    return {
        "figure.figsize": (width, height),
        "figure.constrained_layout.use": constrained_layout,
        "figure.autolayout": tight_layout,
        "savefig.bbox": "tight",
        "savefig.pad_inches": pad,
    }
