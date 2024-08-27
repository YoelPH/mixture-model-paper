"""Time-prior and evolution over midline extension probability."""

import matplotlib.pyplot as plt
import numpy as np
import shared
from lyscripts.plot.utils import COLORS
from matplotlib import ticker


def main():
    """Plot figure."""
    model = shared.get_model("simple", load_samples=True)

    t = np.linspace(0, 10, 11)
    p_midline = {
        "lateralized": (1 - model.midext_prob) ** t,
        "extension": 1 - (1 - model.midext_prob) ** t,
    }
    dist = {
        "early": model.get_distribution("early").pmf,
        "late": model.get_distribution("late").pmf,
    }
    p_colors = {"lateralized": COLORS["green"], "extension": COLORS["red"]}
    t_colors = {"early": COLORS["blue"], "late": COLORS["orange"]}

    nrows, ncols = 2, 1
    plt.rcParams.update(shared.get_fontsizes())
    plt.rcParams.update(
        shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            width=17 / 2,
        )
    )
    plt.rcParams.update(shared.get_axes_params())

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex=True)
    w = 0.3

    for label, p in p_midline.items():
        axes[0].plot(
            t,
            p_midline[label],
            "o-",
            label=rf"cond. prob. $P(\epsilon={label=='extension'} \mid t)$",
            color=p_colors[label],
        )
        for i, t_stage in enumerate(["early", "late"]):
            if label == "lateralized":
                axes[0].bar(
                    t + i * w - w / 2,
                    dist[t_stage],
                    color=t_colors[t_stage],
                    width=w,
                    label=f"{t_stage} T-cat. prior $P(t)$",
                )
            axes[1].plot(
                t,
                p * dist[t_stage],
                "o-",
                c=p_colors[label],
                mfc=t_colors[t_stage],
                mec=t_colors[t_stage],
                label=rf"{label} ($\epsilon={label=='extension'}$) for {t_stage} T-cat."
            )

    axes[0].set_ylim(0.0, 1.0)
    axes[0].tick_params(bottom=False, labelbottom=False)
    axes[0].yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0%}"))
    axes[0].set_ylabel("probability")
    axes[0].grid(axis="y", color=COLORS["gray"], alpha=0.5)

    axes[0].legend(labelspacing=0.2)

    axes[1].set_xlim(min(t), max(t))
    axes[1].set_xticks(t)
    axes[1].set_xlabel("time-step $t$")

    axes[1].set_ylim(0.0, 0.25)
    axes[1].yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0%}"))
    axes[1].set_ylabel(r"joint probability $P(\epsilon, t)$")
    axes[1].grid(axis="y", color=COLORS["gray"], alpha=0.5)

    axes[1].legend(labelspacing=0.2)

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
