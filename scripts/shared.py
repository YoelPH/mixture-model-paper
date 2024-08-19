"""Some shared and reused functions for the scripts."""

from collections import namedtuple
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
from lymph import types

from lyscripts import utils

try:
    from . import paths
except ImportError:
    import paths


pd.options.mode.copy_on_write = False
CM_TO_INCH = 0.393701
GOLDEN_RATIO = 1.61803398875


def get_params() -> dict[str, Any]:
    """Get the parameters."""
    return utils.load_yaml_params(paths.params)


def get_model(
    which: str,
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


def get_samples(which: str) -> np.ndarray:
    """Get the samples of one of the four trained models."""
    samples_path = paths.model_dir / which / "samples.hdf5"
    return utils.load_model_samples(samples_path)


def get_data(map_t_stage: bool = True) -> pd.DataFrame:
    """Get the data."""
    data = utils.load_patient_data(paths.data)

    if map_t_stage:
        data.ly.map_t_stage(lambda x: "early" if x <= 2 else "late")

    return data


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
    individual: bool = False,
) -> dict[str, Any]:
    """Get figure sizes that can be used to update the matplotlib rcParams.

    This is heavily inspired by the tueplots package v0.0.14.
    """
    if unit == "cm":
        width *= CM_TO_INCH
        pad *= CM_TO_INCH

    subplot_width = width / ncols
    height = subplot_width / aspect_ratio

    if not individual:
        height *= nrows

    return {
        "figure.figsize": (width, height),
        "figure.constrained_layout.use": constrained_layout,
        "figure.autolayout": tight_layout,
        "savefig.bbox": "tight",
        "savefig.pad_inches": pad,
    }


def turn_axis_off(axes):
    """Turn off axis."""
    axes.set_xticks([])
    axes.set_yticks([])


def get_figure_path(
    script_path: str,
    prefix: str = "fig_",
    suffix: str = ".svg",
) -> Path:
    """Get the full figure path when providing the script's `__file__`.

    >>> get_figure_path(__file__)
    PosixPath('figures/fig_shared.svg')
    """
    script_path = Path(script_path)
    script_name = script_path.stem
    figure_path = paths.figure_dir / (prefix + script_name)
    return figure_path.with_suffix(suffix)


def get_lnl_cols(
    side: Literal["ipsi", "contra"],
    lnls: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """Get the columns of the LNL involvements."""
    lnls = lnls or ["I", "II", "III", "IV", "V"]
    return [("max_llh", side, lnl) for lnl in lnls]


Columns = namedtuple(
    "Columns", [
        "inst",
        "age",
        "nd",
        "t_stage",
        "n_stage",
        "midext",
        "ipsi_III",
    ])


COL = Columns(
    inst=("patient", "#", "institution"),
    age=("patient", "#", "age"),
    nd=("patient", "#", "neck_dissection"),
    t_stage=("tumor", "1", "t_stage"),
    n_stage=("patient", "#", "n_stage"),
    midext=("tumor", "1", "extension"),
    ipsi_III=("max_llh", "ipsi", "III"),
)
CONTRA_LNLS = [
    ("max_llh", "contra", "I"),
    ("max_llh", "contra", "II"),
    ("max_llh", "contra", "III"),
    ("max_llh", "contra", "IV"),
    ("max_llh", "contra", "V"),
]
