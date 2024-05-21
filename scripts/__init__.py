"""
Scripts and other reused code for this paper.
"""
from collections import namedtuple
from typing import Literal


Columns = namedtuple(
    "Columns", [
        "inst",
        "age",
        "nd",
        "t_stage",
        "n_stage",
        "midext",
        "ipsi_III",
    ])
COL = Columns(
    inst=("patient", "#", "institution"),
    age=("patient", "#", "age"),
    nd=("patient", "#", "neck_dissection"),
    t_stage=("tumor", "1", "t_stage"),
    n_stage=("patient", "#", "n_stage"),
    midext=("tumor", "1", "extension"),
    ipsi_III=("max_llh", "ipsi", "III"),
)
CONTRA_LNLS = [
    ("max_llh", "contra", "I"),
    ("max_llh", "contra", "II"),
    ("max_llh", "contra", "III"),
    ("max_llh", "contra", "IV"),
    ("max_llh", "contra", "V"),
]

def get_lnl_cols(
    side: Literal["ipsi", "contra"],
    lnls: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """Get the columns of the LNL involvements."""
    lnls = lnls or ["I", "II", "III", "IV", "V"]
    return [("max_llh", side, lnl) for lnl in lnls]
