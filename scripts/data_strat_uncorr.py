"""Plot how T-stage and ipsi inv. predict contra involv. when controlling for midext."""

import numpy as np
import paths
import shared
from matplotlib import pyplot as plt
from shared import COL, CONTRA_LNLS

from lyscripts import utils
from lyscripts.plot.utils import COLORS


def main():
    """Plot figure."""
    nrows, ncols = 1, 1
    plt.rcParams.update(**shared.get_fontsizes())
    plt.rcParams.update(
        **shared.get_figsizes(
            nrows=nrows,
            ncols=ncols,
            width=17/2,
        )
    )
    _fig, ax = plt.subplots()

    raw = utils.load_patient_data(paths.data)
    lateral = raw[raw[COL.midext] == False]

    early = lateral[lateral[COL.t_stage] <= 2]
    early_n0 = early[early["max_llh", "ipsi"].sum(axis=1) == 0]
    early_II = early[early["max_llh", "ipsi", "II"] == True]
    early_II_and_III = early_II[early_II["max_llh", "ipsi", "III"] == True]

    late = lateral[lateral[COL.t_stage] > 2]
    late_II = late[late["max_llh", "ipsi", "II"] == True]

    early_n0 = early_n0[CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)
    early_II = early_II[CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)
    early_II_and_III = early_II_and_III[CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)
    late_II = late_II[CONTRA_LNLS]["max_llh", "contra"].mean(axis=0)

    pos = np.arange(len(early_n0))
    kwargs = {"width": 0.6, "zorder": 2}

    plt.bar(
        x=pos+0.2,
        height=100 * early_II_and_III,
        color=COLORS["red"],
        label="early; ipsi II and III",
        **kwargs,
    )
    plt.bar(
        x=pos+0.1,
        height=100 * late_II,
        color=COLORS["orange"],
        label="late; ipsi II",
        **kwargs,
    )
    plt.bar(
        x=pos,
        height=100 * early_II,
        color=COLORS["blue"],
        label="early; ipsi II",
        **kwargs,
    )
    plt.bar(
        x=pos-0.1,
        height=100 * early_n0,
        color=COLORS["green"],
        label="early; ipsi N0",
        **kwargs,
    )

    ax.legend()
    ax.set_title("Contra involvement for lateralized tumors")
    ax.set_xticks(pos, labels=["I", "II", "III", "IV", "V"])
    ax.set_ylabel("prevalence [%]")
    ax.grid(axis="y", color=COLORS["gray"])
    plt.savefig(shared.get_figure_path(__file__))


if __name__ == "__main__":
    main()
