"""
Scripts and other reused code for this paper.
"""
from collections import namedtuple


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
]
