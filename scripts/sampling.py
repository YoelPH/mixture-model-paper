"""
Implement the sampling in this module.
"""
import numpy as np
import pandas as pd
from emcee import EnsembleSampler, backends, moves

from lymph import models


from scipy.special import factorial

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


def create_model() -> models.Midline:
    """Create the model."""
    graph_dict = {
        ("tumor", "T"): ["II", "III"],
        ("lnl", "II"): ["III"],
        ("lnl", "III"): [],
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
    model.load_patient_data(pd.read_csv("data/enhanced.csv", header=[0,1,2]))

    return model


def run_sampling(model: models.Midline, nstep: int = 5000) -> None:
    """Run the sampling."""
    ndim = model.get_num_dims()
    initial = np.random.uniform(size=(20 * ndim, ndim))

    suffix = "evo" if model.use_midext_evo else "fix"
    backend = backends.HDFBackend(filename=f"models/midline_{suffix}.hdf5")
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
    np.random.seed(42)
    model = create_model()
    run_sampling(model, nstep=5000)


if __name__ == "__main__":
    main()
