"""Plot the burn-in history of the sampling."""

from collections import namedtuple

import matplotlib.pyplot as plt
import pandas as pd
import paths
import shared
from matplotlib import ticker


def custom(x, pos):
    """Return custom format."""
    return f"{x / 1000:.1f}"


PlotConfig = namedtuple("PlotConfig", ["title", "ylabel", "label"])


def main():
    """Plot figure."""
    nrows, ncols = 1, 2
    config_map = {
        "acor_times": PlotConfig(
            title="Estimated Autocorrelation Time",
            ylabel="steps",
            label="Autocorrelation Time",
        ),
        "accept_fracs": PlotConfig(
            title="Average Acceptance Fraction of Walkers",
            ylabel=None,
            label=None,
        ),
    }

    plt.rcParams.update(shared.get_fontsizes())
    plt.rcParams.update(
        shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            width=17,
        )
    )

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        sharex=True,
    )

    for model in ["full"]:
        history = pd.read_csv(f"models/{model}/history.csv").set_index("steps")
        for i, (column, config) in enumerate(config_map.items()):
            axes[i].set_title(config.title, fontweight="bold")
            axes[i].plot(history.index, history[column], label=config.label)
            axes[i].autoscale(enable=True, tight=True, axis="x")
            axes[i].set_ylabel(config.ylabel)
            axes[i].xaxis.set_major_formatter(ticker.FuncFormatter(custom))
            axes[i].set_xlabel(r"steps [$\times 10^3$]")

    params = shared.get_params()

    axes[0].plot(
        history.index,
        history.index / params["sampling"]["trust_fac"],
        "--",
        color="black",
        label="Trust Threshold",
    )
    axes[0].legend()
    axes[1].yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0%}"))

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
