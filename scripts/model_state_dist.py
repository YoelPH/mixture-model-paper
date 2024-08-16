"""Plot the bilateral state distribution of the model."""

import matplotlib.pyplot as plt
import numpy as np
import paths
import shared
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import AxesGrid

from lyscripts.plot.utils import COLORS


def main():
    """Plot figure."""
    model = shared.get_model(which="simple", load_samples=True)
    state_dist = 100 * model.state_dist(t_stage="late")
    vmax = np.max(state_dist)

    nrows, ncols = 1, 2
    cmap = LinearSegmentedColormap.from_list(
        name="usz",
        colors=[COLORS["green"], COLORS["orange"], COLORS["red"]],
    )
    cmap.set_under(COLORS["gray"])

    plt.rcParams.update(shared.get_fontsizes())
    plt.rcParams.update(
        shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            aspect_ratio=1.0,
            width=17,
        )
    )

    fig = plt.figure()
    grid = AxesGrid(
        fig,
        111,
        nrows_ncols=(nrows, ncols),
        axes_pad=0.2,
        share_all=True,
        cbar_location="right",
        cbar_mode="single",
        cbar_size="8%",
    )
    noext, midext = grid

    im = noext.imshow(state_dist[0], cmap=cmap, vmin=100 * np.exp(-5), vmax=vmax)
    im = midext.imshow(state_dist[1], cmap=cmap, vmin=100 * np.exp(-5), vmax=vmax)
    grid.cbar_axes[0].colorbar(im)
    grid.cbar_axes[0].set_ylabel("Probability [%]")

    noext.set_title(r"tumor lateralized $\epsilon=\text{False}$")
    midext.set_title(r"midline extension $\epsilon=\text{True}$")

    noext.set_ylabel(r"ipsi state $\boldsymbol{\xi}^\text{i}_\ell$")
    noext.set_xlabel(r"contra state $\boldsymbol{\xi}^\text{c}_k$")
    midext.set_xlabel(r"contra state $\boldsymbol{\xi}^\text{c}_k$")

    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
