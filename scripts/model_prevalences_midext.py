"""Compute the prevalence of midline extension (predicted and observed)."""

import matplotlib.pyplot as plt
import paths
import shared

from lyscripts.plot.utils import COLORS, BetaPosterior, Histogram, draw, split_legends


def main():
    """Plot figure."""
    plt.rcParams.update(shared.get_fontsizes())
    plt.rcParams.update(shared.get_figsizes(width=17.0 / 2.0))

    fig, ax = plt.subplots()
    content = []
    colors = iter([COLORS[c] for c in ["blue", "orange"]])

    for t_stage in ["early", "late"]:
        color = next(colors)
        content.append(
            Histogram.from_hdf5(
                filename=paths.model_dir / "full" / "prevalences_midext.hdf5",
                dataname=t_stage,
                color=color,
                label="prediction",
            )
        )
        content.append(
            BetaPosterior.from_hdf5(
                filename=paths.model_dir / "full" / "prevalences_midext.hdf5",
                dataname=t_stage,
                color=color,
            )
        )

    draw(ax, content, xlims=(0.0, 55.0))
    ax.set_title("Observed vs Predicted Prevalence\nof Midline Extension $\\epsilon$")
    ax.set_yticks([])
    ax.set_ylim(top=0.4)
    ax.set_xlabel("prevalence [%]")

    split_legends(
        axes=ax,
        titles=["early T-cat.", "late T-cat."],
        locs=[(0.05, 0.99), (0.6, 0.99)],
    )

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
