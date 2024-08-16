"""Contra involvement by T-category, number of metastatic ipsi LNLs, and midext."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import paths
import shared
from matplotlib import gridspec
from matplotlib.axes import Axes

from lyscripts import utils
from lyscripts.plot.utils import COLORS


def group_and_plot(
    df: pd.DataFrame,
    column: str,
    axes: Axes,
    colors: list[str],
) -> None:
    """Group `df` by `column` and plot the result."""
    grouped = df.groupby(by=column)
    counts = grouped.count().T
    aggregated = 100 * grouped.mean().T
    edges = np.linspace(1.0, 0.0, len(grouped) + 1)
    positions = edges[1:] + ((edges[0] - edges[1]) / 2)

    for i, ((label, series), (_, count)) in enumerate(
        zip(aggregated.items(), counts.items())
    ):
        series.plot(
            ax=axes,
            kind="bar",
            label=f"{label} ({count.iloc[0]})",
            color=colors[i],
            position=positions[i],
            rot=0,
            zorder=2 - i * 0.1,
        )

    axes.legend()
    axes.grid(axis="y", color=COLORS["gray"])
    axes.set_axisbelow(True)


def main():
    """Plot figure."""
    nrows, ncols = 1, 3
    plt.rcParams.update(**shared.get_fontsizes())
    plt.rcParams.update(
        **shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            aspect_ratio=1.1,
        )
    )
    fig = plt.figure()
    gs = gridspec.GridSpec(nrows=nrows, ncols=ncols, figure=fig)

    left = fig.add_subplot(gs[0])
    center = fig.add_subplot(gs[1], sharey=left)
    right = fig.add_subplot(gs[2], sharey=center)
    row = fig.add_subplot(gs[:], frame_on=False)

    right.set_ylabel("contra prevalence [%]")
    right.set_title("Midline Extension")
    center.set_title("Ipsilateral Involvement")
    left.set_title("T-category")
    row.set_xlabel("Lymph Node Level", labelpad=17)
    row.set_xticks([])
    row.set_yticks([])

    raw = utils.load_patient_data(paths.data)
    contra_by_midext = raw[[*shared.get_lnl_cols("contra"), shared.COL.midext]].copy()
    contra_by_midext.columns = contra_by_midext.columns.droplevel([0, 1])

    # stratify by midline extension
    group_and_plot(
        df=contra_by_midext,
        column="extension",
        axes=right,
        colors=[COLORS["green"], COLORS["red"]],
    )

    # stratify by ipsilateral involvement
    num_ipsi_inv = raw[shared.get_lnl_cols("ipsi")].sum(axis="columns")
    contra_by_ipsi = raw[shared.get_lnl_cols("contra")].copy()
    contra_by_ipsi.columns = contra_by_ipsi.columns.droplevel([0, 1])
    contra_by_ipsi["ipsi"] = num_ipsi_inv.map(
        {
            0: "ipsi N0",
            1: "one ipsi LNL",
            2: "≥ two ipsi LNLs",
            3: "≥ two ipsi LNLs",
            4: "≥ two ipsi LNLs",
            5: "≥ two ipsi LNLs",
        }
    )

    group_and_plot(
        df=contra_by_ipsi,
        column="ipsi",
        axes=center,
        colors=[COLORS["green"], COLORS["orange"], COLORS["red"]],
    )

    # stratify by T-category
    contra_by_t = raw[[*shared.get_lnl_cols("contra"), shared.COL.t_stage]].copy()
    contra_by_t.columns = contra_by_t.columns.droplevel([0, 1])
    contra_by_t["t_stage"] = contra_by_t["t_stage"].map(
        {
            0: "T0-2",
            1: "T0-2",
            2: "T0-2",
            3: "T3-4",
            4: "T3-4",
        }
    )

    group_and_plot(
        df=contra_by_t,
        column="t_stage",
        axes=left,
        colors=[COLORS["blue"], COLORS["orange"]],
    )

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
