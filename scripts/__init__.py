"""
Scripts and other reused code for this paper.
"""
from collections import namedtuple


Columns = namedtuple("Columns", ["t_stage", "midext", "ipsi_III"])
COL = Columns(
    t_stage=("tumor", "1", "t_stage"),
    midext=("tumor", "1", "extension"),
    ipsi_III=("max_llh", "ipsi", "III"),
)
CONTRA_LNLS = [
    ("max_llh", "contra", "I"),
    ("max_llh", "contra", "II"),
    ("max_llh", "contra", "III"),
    ("max_llh", "contra", "IV"),
]
