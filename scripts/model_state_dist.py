"""Plot the term P(X_i | t)^T @ P(t) @ P(X_c | t) for the simple model."""

import operator
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np
import shared
from matplotlib.colors import LinearSegmentedColormap

from lyscripts.plot.utils import COLORS


def main():
    """Plot figure."""
    # use the full model's parameters in the smaller, simple model
    smpl_model = shared.get_model(which="simple", load_samples=False)
    full_model = shared.get_model(which="full", load_samples=True)
    smpl_model.set_params(**full_model.get_params())

    ipsi_state_dist_evo = smpl_model.ext.ipsi.state_dist_evo() * 100.0
    _, contra_state_dist_evo = smpl_model.contra_state_dist_evo()
    contra_state_dist_evo *= 100.0
    time_prior = np.diag(smpl_model.get_distribution("late").pmf) * 100.0

    vmin = np.min(
        [
            ipsi_state_dist_evo.min(),
            time_prior.min(),
            contra_state_dist_evo.min(),
        ]
    )
    vmax = np.max(
        [
            ipsi_state_dist_evo.max(),
            time_prior.max(),
            contra_state_dist_evo.max(),
        ]
    )

    nrows, ncols = 1, 3
    plt.rcParams.update(shared.get_fontsizes())
    plt.rcParams.update(
        shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            aspect_ratio=0.7675,
            width=17,
        )
    )

    fig = plt.figure()
    gs = GridSpec(nrows + 1, 2 * ncols, figure=fig, height_ratios=[1, 0.075])

    ipsi = fig.add_subplot(gs[0, 0:2])
    ipsi.set_aspect(operator.truediv(*ipsi_state_dist_evo.shape))

    time = fig.add_subplot(gs[0, 2:4])
    time.set_aspect(operator.truediv(*time_prior.shape))

    contra = fig.add_subplot(gs[0, 4:6], sharey=time)
    contra.set_aspect(operator.truediv(*contra_state_dist_evo.shape))

    cbar_ax = fig.add_subplot(gs[1, 1:5])

    kwargs = {
        "vmin": vmin,
        "vmax": vmax,
        "cmap": "turbo",
    }

    im = ipsi.imshow(ipsi_state_dist_evo.T, **kwargs)
    im = time.imshow(time_prior, **kwargs)
    im = contra.imshow(contra_state_dist_evo, **kwargs)

    cbar = plt.colorbar(im, cax=cbar_ax, orientation="horizontal")

    state_list = smpl_model.ext.ipsi.graph.state_list
    ipsi.set_yticks(range(8), labels=state_list)
    ipsi.set_ylabel("ipsi state $\\mathbf{X}^\\text{i}$")
    ipsi.set_xlabel("time $t$")

    time.set_xlabel("time $t$")

    contra.set_xticks(range(8), labels=state_list, rotation=90)
    contra.set_xlabel("contra state $\\mathbf{X}^\\text{c}$")
    contra.yaxis.tick_right()
    contra.yaxis.set_label_position("right")
    contra.set_ylabel("time $t$")

    cbar.set_label("probability (%)")

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
