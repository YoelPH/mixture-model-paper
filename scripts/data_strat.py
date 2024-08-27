"""Contra involvement by T-category, number of metastatic ipsi LNLs, and midext."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import paths
import shared
from lyscripts import utils
from lyscripts.plot.utils import COLORS
from matplotlib import gridspec
from matplotlib.axes import Axes


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
    nrows, ncols = 2, 2
    plt.rcParams.update(**shared.get_fontsizes())
    plt.rcParams.update(
        **shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            aspect_ratio=1.6,
        )
    )
    plt.rcParams.update({
        "xtick.bottom": False,
        "xtick.major.pad": 1,
        "ytick.left": False,
        "ytick.major.pad": 1,
    })
    fig = plt.figure()
    gs = gridspec.GridSpec(nrows=nrows, ncols=ncols, figure=fig)

    t_cat_ax = fig.add_subplot(gs[0,0])
    ipsi_inv_ax = fig.add_subplot(gs[0,1], sharey=t_cat_ax)
    midext_ax = fig.add_subplot(gs[1,0], sharey=ipsi_inv_ax)
    uncorr_ax = fig.add_subplot(gs[1,1], sharey=midext_ax)
    row = fig.add_subplot(gs[:], frame_on=False)

    ipsi_inv_ax.set_title("Ipsilateral Involvement", fontweight="bold")
    t_cat_ax.set_title("T-category", fontweight="bold")
    midext_ax.set_title("Midline Extension", fontweight="bold")
    uncorr_ax.set_title("Lateralized Tumors", fontweight="bold")

    row.set_xlabel("Lymph Node Level", labelpad=15)
    row.set_ylabel("Contralateral Involvement Prevalence [%]", labelpad=17)
    row.set_xticks([])
    row.set_yticks([])

    raw = utils.load_patient_data(paths.data)
    contra_by_midext = raw[[*shared.get_lnl_cols("contra"), shared.COL.midext]].copy()
    contra_by_midext.columns = contra_by_midext.columns.droplevel([0, 1])

    # stratify by midline extension
    group_and_plot(
        df=contra_by_midext,
        column="extension",
        axes=midext_ax,
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
        axes=ipsi_inv_ax,
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
        axes=t_cat_ax,
        colors=[COLORS["blue"], COLORS["orange"]],
    )

    # plot showing that T-stage and ipsi involvement are still predictive, when
    # considering midline extension
    lateral = raw[raw[shared.COL.midext] == False]

    early = lateral[lateral[shared.COL.t_stage] <= 2]
    early_n0 = early[early["max_llh", "ipsi"].sum(axis=1) == 0]
    early_II = early[early["max_llh", "ipsi", "II"] == True]
    early_II_and_III = early_II[early_II["max_llh", "ipsi", "III"] == True]

    late = lateral[lateral[shared.COL.t_stage] > 2]
    late_II = late[late["max_llh", "ipsi", "II"] == True]

    early_n0 = early_n0[shared.CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)
    early_II = early_II[shared.CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)
    early_II_and_III = early_II_and_III[shared.CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)
    late_II = late_II[shared.CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)

    pos = np.arange(len(early_n0))
    kwargs = {"width": 0.6, "zorder": 2}

    uncorr_ax.bar(
        x=pos+0.2,
        height=100 * early_II_and_III,
        color=COLORS["red"],
        label="early; ipsi II and III",
        **kwargs,
    )
    uncorr_ax.bar(
        x=pos+0.1,
        height=100 * late_II,
        color=COLORS["orange"],
        label="late; ipsi II",
        **kwargs,
    )
    uncorr_ax.bar(
        x=pos,
        height=100 * early_II,
        color=COLORS["blue"],
        label="early; ipsi II",
        **kwargs,
    )
    uncorr_ax.bar(
        x=pos-0.1,
        height=100 * early_n0,
        color=COLORS["green"],
        label="early; ipsi N0",
        **kwargs,
    )

    uncorr_ax.legend()
    uncorr_ax.set_xticks(pos, labels=["I", "II", "III", "IV", "V"])
    uncorr_ax.grid(axis="y", color=COLORS["gray"])

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
