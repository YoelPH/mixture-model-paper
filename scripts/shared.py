"""
Some shared and reduced functions for the scripts.
"""
from typing import Literal

from lymph import types
from lyscripts import utils
import numpy as np

from . import paths


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
