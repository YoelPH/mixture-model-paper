"""Predicted/observed prevalences of contra III involvement, dep. on upstream level."""

import matplotlib.pyplot as plt
import numpy as np
import paths
import shared
from matplotlib import gridspec

from lyscripts.plot.utils import COLORS, BetaPosterior, Histogram, draw, split_legends
from lyscripts.scenario import Scenario


def main():
    """Plot figure."""
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
            "Observed vs Predicted Prevalence of Contralateral LNL III Involvement"
            "\nDependent on Upstream LNL III Involvement"
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
            for upstream, color in zip([False, True], [COLORS["green"], COLORS["red"]]):
                scenario = Scenario(
                    t_stages=[t_stage],
                    midext=midext,
                    diagnosis={
                        "contra": {"max_llh": {"II": upstream, "III": True}},
                    },
                )
                content.append(
                    Histogram.from_hdf5(
                        filename=paths.model_dir
                        / "full"
                        / "prevalences_with_upstream.hdf5",
                        dataname=scenario.md5_hash("prevalences"),
                        color=color,
                        label="prediction",
                    )
                )
                content.append(
                    BetaPosterior.from_hdf5(
                        filename=paths.model_dir
                        / "full"
                        / "prevalences_with_upstream.hdf5",
                        dataname=scenario.md5_hash("prevalences"),
                        color=color,
                    )
                )
            draw(
                axes=axes[i, j],
                contents=content,
                xlims=(0.0, 15.0 if midext else 4.0),
            )

    split_legends(
        axes=axes[0, 0],
        titles=["upstream healthy", "upstream involved"],
        locs=[(0.4, 0.99), (0.5, 0.55)],
    )
    split_legends(
        axes=axes[0, 1],
        titles=["upstream healthy", "upstream involved"],
        locs=[(0.3, 0.99), (0.6, 0.55)],
    )
    split_legends(
        axes=axes[1, 0],
        titles=["upstream healthy", "upstream involved"],
        locs=[(0.2, 0.99), (0.65, 0.99)],
    )
    split_legends(
        axes=axes[1, 1],
        titles=["upstream healthy", "upstream involved"],
        locs=[(0.3, 0.99), (0.65, 0.99)],
    )

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
