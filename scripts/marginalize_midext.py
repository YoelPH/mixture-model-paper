"""
Marginalize over *observd* midline extension status using sums of beta posteriors.
"""

from dataclasses import dataclass
from typing import Any, TypeVar
import matplotlib.pyplot as plt
from matplotlib.axes import Axes as MPLAxes
import pandas as pd
import numpy as np
from scipy.stats import beta
from lyscripts.data import accessor  # noqa: F401
from lyscripts.scenario import Scenario
from lyscripts.plot.utils import BetaPosterior
from lyscripts.compute.prevalences import compute_observed_prevalence, get_modality_subset

try:
    from . import paths, shared
except ImportError:
    import paths
    import shared


def max_possible_matches(num_match: int, num_total: int) -> int:
    """Maximum number of additional possible matches."""
    return min(num_total, num_match) + 1

def min_possible_matches(num_not_match: int, num_total: int) -> int:
    """Minimum number of additional possible matches."""
    return min(num_total, max(0, num_total - num_not_match))


def compute_possible_observed_prevalences(
    data: pd.DataFrame, scenario: Scenario, modality: str = "max_llh"
) -> np.ndarray:
    """Extract possible combinations of prevalences."""
    # when looking at the data, we always consider both sides
    base_num_match, base_num_total = compute_observed_prevalence(data, scenario)

    has_t_stage = data.ly.t_stage.isin(scenario.t_stages)
    modality = get_modality_subset(scenario.diagnosis).pop()
    diagnosis_pattern = scenario.get_pattern(get_from="diagnosis", modality=modality)

    has_unknown_midext = data.ly.midext.isna()
    unknown_midext_data = data.loc[has_t_stage & has_unknown_midext].reset_index()
    does_pattern_match = unknown_midext_data.ly.match(diagnosis_pattern, modality)
    unknown_match = does_pattern_match.sum()
    unknown_total = len(unknown_midext_data)

    return compute_match_total_combinations(
        base_match=base_num_match,
        base_total=base_num_total,
        unknown_match=unknown_match,
        unknown_total=unknown_total,
    )


def compute_match_total_combinations(
    base_total: int,
    base_match: int,
    unknown_match: int,
    unknown_total: int,
) -> np.ndarray:
    """Compute all possible combinations of match/total pairs."""
    results = []
    for pot_num_total in range(unknown_total + 1):
        for pot_num_match in range(
            min_possible_matches(unknown_total - unknown_match, pot_num_total),
            max_possible_matches(unknown_match, pot_num_total),
        ):
            results.append([
                base_match + pot_num_match,
                base_total + pot_num_total,
            ])

    return np.array(results)


def prepare_betas(
    nums_match: np.ndarray,
    nums_total: np.ndarray,
):
    """Prepare beta posteriors for each possible observed prevalence."""
    if len(nums_match.shape) == 1:
        nums_match = nums_match[None, :]

    if len(nums_total.shape) == 1:
        nums_total = nums_total[None, :]

    nums_fail = nums_total - nums_match
    return beta(nums_match + 1, nums_fail + 1)


def summed_beta_pdf(
    x: np.ndarray,
    nums_match: np.ndarray,
    nums_total: np.ndarray,
) -> np.ndarray:
    """Sum beta PDFs and normalize them."""
    if len(x.shape) == 1:
        x = x[:, None]

    beta_pdfs = prepare_betas(nums_match, nums_total).pdf(x)
    summed_pdfs = beta_pdfs.sum(axis=1)
    return summed_pdfs / beta_pdfs.shape[1]


def summed_beta_cdf(
    x: np.ndarray,
    nums_match: np.ndarray,
    nums_total: np.ndarray,
) -> np.ndarray:
    """Sum beta CDFs."""
    if len(x.shape) == 1:
        x = x[:, None]

    beta_cdfs = prepare_betas(nums_match, nums_total).cdf(x)
    summed_cdfs = beta_cdfs.sum(axis=1)
    return summed_cdfs / beta_cdfs.shape[1]


FloatOrArrayT = TypeVar("FloatOrArrayT", float, np.ndarray)

def summed_beta_ppf(
    q: FloatOrArrayT,
    nums_match: np.ndarray,
    nums_total: np.ndarray,
) -> FloatOrArrayT:
    """PPF of summed CDFs."""
    x = np.linspace(0, 1, 1000)
    y = summed_beta_cdf(x, nums_match, nums_total)

    return np.interp(q, y, x)


@dataclass
class SummedBetaPosterior(BetaPosterior):
    """Subclass for storing plot config of sum of beta posteriors."""

    num_success: np.ndarray
    num_total: np.ndarray

    @classmethod
    def from_hdf5(*args, **kwargs) -> None:
        raise NotImplementedError

    def _get_label(self) -> str:
        min_success = self.num_success.min()
        max_success = self.num_success.max()
        min_total = self.num_total.min()
        max_total = self.num_total.max()
        return (
            f"data: {min_success} to {max_success} "
            f"of {min_total} to {max_total}"
        )

    @property
    def num_fail(self) -> np.ndarray:
        return self.num_total - self.num_success

    def pdf(self, x: np.ndarray) -> np.ndarray:
        return summed_beta_pdf(
            (x - self.offset) / self.scale,
            self.num_success,
            self.num_total,
        ) / self.scale

    def left_percentile(self, percent: float) -> float:
        return summed_beta_ppf(
            percent / 100.,
            self.num_success,
            self.num_total,
        ) * self.scale + self.offset

    def right_percentile(self, percent: float) -> float:
        return summed_beta_ppf(
            1 - (percent / 100.),
            self.num_success,
            self.num_total,
        ) * self.scale + self.offset

    def draw(self, axes: MPLAxes, resolution: int = 300, **defaults) -> Any:
        """Draw the PDF of the summed beta distributions into ``axes``."""
        left, right = axes.get_xlim()
        x = np.linspace(left, right, resolution)
        y = self.pdf(x)

        plot_kwargs = defaults["plot"].copy()
        plot_kwargs.update(self.kwargs)

        if self.label is not None:
            plot_kwargs["label"] = self.label

        return axes.plot(x, y, **plot_kwargs)


def main():
    data = shared.get_data()
    scenario = Scenario(
        t_stages=["early"],
        midext=True,
        diagnosis={
            "ipsi": {"max_llh": {"III": True}},
            "contra": {"max_llh": {"II": True}},
        },
    )
    nums_match, nums_total = compute_possible_observed_prevalences(data, scenario).T
    summed_beta = SummedBetaPosterior(nums_match, nums_total)

    p = np.linspace(0, 0.3, 2**10 + 1)
    plt.plot(p, summed_beta.pdf(p))
    plt.plot(p, beta.pdf(p, 3, 29))
    plt.savefig(paths.figure_dir / "marginalized_midext.png")


if __name__ == "__main__":
    main()
