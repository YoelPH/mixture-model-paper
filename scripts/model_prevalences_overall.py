"""Compare overall prevalences in the data with the model predictions."""

import matplotlib.pyplot as plt
import numpy as np
import paths
import shared
from matplotlib import gridspec

from lyscripts.plot.utils import COLORS, BetaPosterior, Histogram, draw, split_legends
from lyscripts.scenario import Scenario


def main():
    """Plot the figure."""
    nrows, ncols = 2, 2

    plt.rcParams.update(shared.get_fontsizes())
    plt.rcParams.update(
        shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            aspect_ratio=2.0,
            width=17,
        )
    )

    fig = plt.figure()
    gs = gridspec.GridSpec(nrows=nrows, ncols=ncols, figure=fig)
    axes = np.array(
        [[fig.add_subplot(gs[i, j]) for j in range(ncols)] for i in range(nrows)]
    )
    full = fig.add_subplot(gs[:, :], frame_on=False)
    shared.turn_axis_off(full)

    full.set_title(
        (
            "Observed vs Predicted Prevalence of Contralateral Involvement"
            "\nin the LNLs II, III, and IV"
        ),
        pad=20.0,
        fontsize="large",
    )

    for i, t_stage in enumerate(["early", "late"]):
        axes[i, 0].set_ylabel(f"{t_stage} T-cat.", fontweight="bold")
        for j, midext in enumerate([False, True]):
            axes[0, j].set_title(
                "Mid. ext." if midext else "Lateralized", fontweight="bold"
            )
            axes[0, j].set_xticks([])
            axes[-1, j].set_xlabel("prevalence [%]")
            axes[i, j].set_yticks([])
            content = []
            for lnl, color in zip(
                ["II", "III", "IV"],
                [COLORS["blue"], COLORS["orange"], COLORS["green"]],
            ):
                scenario = Scenario(
                    t_stages=[t_stage],
                    midext=midext,
                    diagnosis={"contra": {"max_llh": {lnl: True}}},
                )
                content.append(
                    Histogram.from_hdf5(
                        filename=paths.model_dir / "full" / "prevalences_overall.hdf5",
                        dataname=scenario.md5_hash("prevalences"),
                        color=color,
                        label="prediction",
                    )
                )
                content.append(
                    BetaPosterior.from_hdf5(
                        filename=paths.model_dir / "full" / "prevalences_overall.hdf5",
                        dataname=scenario.md5_hash("prevalences"),
                        color=color,
                    )
                )
            draw(
                axes=axes[i, j],
                contents=content,
                xlims=(0.0, 15.0 if not midext else 45.0),
            )

    # manually place legends
    split_legends(
        axes=axes[0, 0],
        titles=["LNL II", "LNL III", "LNL IV"],
        locs=[(0.53, 0.6), (0.55, 0.99), (0.12, 0.99)],
    )
    split_legends(
        axes=axes[0, 1],
        titles=["LNL II", "LNL III", "LNL IV"],
        locs=[(0.55, 0.99), (0.27, 0.6), (0.1, 0.99)],
    )
    axes[1, 0].set_ylim(top=1.4)
    split_legends(
        axes=axes[1, 0],
        titles=["LNL II", "LNL III", "LNL IV"],
        locs=[(0.54, 0.99), (0.24, 0.6), (0.11, 0.99)],
    )
    split_legends(
        axes=axes[1, 1],
        titles=["LNL II", "LNL III", "LNL IV"],
        locs=[(0.54, 0.99), (0.4, 0.6), (0.12, 0.99)],
    )

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
