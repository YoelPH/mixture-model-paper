"""
Marginalize over *observd* midline extension status using sums of beta posteriors.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import beta
from scipy import integrate
from lyscripts.data import accessor  # noqa: F401
from lyscripts.scenario import Scenario
from lyscripts.plot.utils import BetaPosterior

try:
    from . import paths, shared
except ImportError:
    import paths
    import shared


def max_possible_matches(does_match, num_total):
    """Maximum number of additional possible matches."""
    return min(num_total, does_match.sum()) + 1

def min_possible_matches(does_match, num_total):
    """Minimum number of additional possible matches."""
    return min(num_total, max(0, num_total - (~does_match).sum()))


def compute_possible_observed_prevalences(
    data: pd.DataFrame, scenario: Scenario, modality: str = "max_llh"
) -> np.ndarray:
    """Extract possible combinations of prevalences."""
    # when looking at the data, we always consider both sides
    is_uni = scenario.is_uni
    scenario.is_uni = False
    diagnosis_pattern = scenario.get_pattern(get_from="diagnosis", modality=modality)

    # reset `is_uni` to the original value. Otherwise hash computation will fail.
    scenario.is_uni = is_uni

    has_t_stage = data.ly.t_stage.isin(scenario.t_stages)
    has_midext = data.ly.is_midext(scenario.midext)
    eligible_data = data.loc[has_t_stage & has_midext].reset_index()
    does_pattern_match = eligible_data.ly.match(diagnosis_pattern, modality)
    base_num_total = len(eligible_data)

    try:
        matching_data = eligible_data.loc[does_pattern_match]
        base_num_match = len(matching_data)
    except KeyError:
        # return X, X if no actual pattern was selected
        base_num_match = base_num_total

    has_unknown_midext = data.ly.midext.isna()
    unknown_midext_data = data.loc[has_t_stage & has_unknown_midext].reset_index()
    does_pattern_match = unknown_midext_data.ly.match(diagnosis_pattern, modality)
    num_eligible = len(unknown_midext_data)

    results = []
    for pot_num_total in range(num_eligible + 1):
        for pot_num_match in range(
            min_possible_matches(does_pattern_match, pot_num_total),
            max_possible_matches(does_pattern_match, pot_num_total),
        ):
            results.append([
                base_num_match + pot_num_match,
                base_num_total + pot_num_total,
            ])

    return np.array(results)


def summed_beta_pdfs(
    x: np.ndarray,
    nums_match: np.ndarray,
    nums_total: np.ndarray,
) -> np.ndarray:
    """Sum beta PDFs and normalize them."""
    if len(x.shape) == 1:
        x = x[:, None]

    if len(nums_match.shape) == 1:
        nums_match = nums_match[None, :]

    if len(nums_total.shape) == 1:
        nums_total = nums_total[None, :]

    nums_fail = nums_total - nums_match

    beta_pdfs = beta.pdf(x, nums_match + 1, nums_fail + 1)
    summed_pdfs = beta_pdfs.sum(axis=1)

    return summed_pdfs / beta_pdfs.shape[1]


class SummedBetaPosterior(BetaPosterior):
    """Subclass for storing plot config of sum of beta posteriors."""
    num_success: np.ndarray
    num_total: np.ndarray

    @classmethod
    def from_hdf5(*args, **kwargs) -> None:
        raise NotImplementedError

    @property
    def num_fail(self) -> np.ndarray:
        return self.num_total - self.num_success

    def pdf(self, x: np.ndarray) -> np.ndarray:
        return summed_beta_pdfs(x, self.num_success, self.num_total)

    def left_percentile(self, percent: float) -> float:
        raise NotImplementedError

    def right_percentile(self, percent: float) -> float:
        raise NotImplementedError


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
