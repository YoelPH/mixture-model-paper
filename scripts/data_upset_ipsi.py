"""Upset plot of ipsilateral lymphatic involvement patterns."""

import matplotlib.pyplot as plt
import pandas as pd
import paths
import shared
import upsetplot
from matplotlib.axes import Axes

from lyscripts import utils
from lyscripts.plot.utils import COLORS


def plot_involvement_upset(
    df: pd.DataFrame,
    lnls: list[str],
) -> Axes:
    """Plot involvement of `side` as upsetplot."""
    indicator_data = upsetplot.from_indicators(
        indicators=lnls,
        data=df,
    )
    upset = upsetplot.UpSet(
        indicator_data,
        sort_by="cardinality",
        sort_categories_by="-input",
        min_subset_size=10,
        facecolor=COLORS["blue"],
    )
    upset.style_subsets(
        absent=lnls,
        facecolor=COLORS["green"],
        label="N0 (all healthy)",
    )
    axes = upset.plot()
    axes["totals"].set_xlabel("Prevalence")
    axes["intersections"].set_ylabel("Scenario size")
    return axes


def main():
    """Plot figure."""
    raw = utils.load_patient_data(paths.data)
    plot_involvement_upset(
        df=raw["max_llh", "ipsi"],
        lnls=[tpl[-1] for tpl in shared.get_lnl_cols("ipsi")],
    )
    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
