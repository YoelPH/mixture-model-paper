"""
Run the sampling in this module.
"""
import argparse
from pathlib import Path
import warnings

import numpy as np
from scipy.special import factorial
import pandas as pd
from emcee import EnsembleSampler, backends, moves

from lymph import models, types


warnings.filterwarnings("ignore", category=types.DataWarning)


def binom_pmf(k: np.ndarray, n: int, p: float):
    """Binomial PMF"""
    if p > 1. or p < 0.:
        # This value error is important to enable seamless sampling!
        raise ValueError("Binomial prob must be btw. 0 and 1")
    q = 1. - p
    binom_coeff = factorial(n) / (factorial(k) * factorial(n - k))
    return binom_coeff * p**k * q**(n - k)

def late_binomial(support: np.ndarray, p: float = 0.5) -> np.ndarray:
    """Parametrized binomial distribution."""
    return binom_pmf(k=support, n=support[-1], p=p)


def create_parser() -> argparse.ArgumentParser:
    """Create the parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default="data/filtered.csv",
        help="Path to the data file."
    )
    parser.add_argument(
        "--samples", type=Path, default="models/midline.hdf5",
        help="Path to the generated samples HDF5 file."
    )
    parser.add_argument(
        "--nstep", type=int, default=2000,
        help="Number of steps for the sampling."
    )
    return parser


def create_model(data_path: Path) -> models.Midline:
    """Create the model."""
    graph_dict = {
        ("tumor", "T"): ["II", "III", "IV"],
        ("lnl", "II"): ["III"],
        ("lnl", "III"): ["IV"],
        ("lnl", "IV"): [],
    }
    model = models.Midline(
        graph_dict=graph_dict,
        is_symmetric={"lnl_spread": True},
        use_mixing=True,
        use_central=False,
        use_midext_evo=False,
    )
    model.set_modality("max_llh", spec=1.0, sens=1.0)
    frozen_binom_pmf = binom_pmf(np.arange(model.max_time+1), model.max_time, p=0.3)
    model.set_distribution("early", frozen_binom_pmf)
    model.set_distribution("late", late_binomial)
    df = pd.read_csv(data_path, header=[0,1,2])
    df["tumor", "1", "extension"] = df["tumor", "1", "extension"].astype(bool)
    model.load_patient_data(df)

    return model


def run_sampling(model: models.Midline, samples_path: Path, nstep: int = 5000) -> None:
    """Run the sampling."""
    ndim = model.get_num_dims()
    initial = np.random.uniform(size=(20 * ndim, ndim))

    backend = backends.HDFBackend(filename=samples_path)
    moves_mix = [(moves.DEMove(), 0.8), (moves.DESnookerMove(), 0.2)]

    sampler = EnsembleSampler(
        nwalkers=20 * ndim,
        ndim=ndim,
        log_prob_fn=model.likelihood,
        backend=backend,
        moves=moves_mix,
        parameter_names=list(model.get_params().keys())[:ndim],
    )
    sampler.run_mcmc(initial, nstep, progress=True)


def main() -> None:
    """Run the script."""
    parser = create_parser()
    args = parser.parse_args()

    np.random.seed(42)
    model = create_model(data_path=args.data)
    run_sampling(model, samples_path=args.samples, nstep=args.nstep)


if __name__ == "__main__":
    main()
