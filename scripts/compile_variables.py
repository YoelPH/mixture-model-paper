"""Script to compile variables from data and models and stores them in a YAML file."""

from pathlib import Path
from typing import Any

import h5py
import lydata  # noqa: F401
import numpy as np
import pandas as pd
import paths
import shared
import yaml
from lydata.accessor import Q, QueryPortion
from pandas.api.typing import DataFrameGroupBy
from pydantic_settings import BaseSettings

from lyscripts.scenario import Scenario


class CmdSettings(BaseSettings, cli_parse_args=True):
    """Settings for the command-line arguments."""

    risk_hdf5: Path = paths.model_dir / "full" / "risks.hdf5"
    risk_scenarios: Path = paths.scenario_dir / "risks.yaml"
    prevalence_hdf5: Path = paths.model_dir / "full" / "prevalences_overall.hdf5"
    prevalence_scenarios: Path = paths.scenario_dir / "overall.yaml"
    output: Path = Path("_variables.dynamic.yaml")
    precision: int = 2


def group_contra_inv(data: pd.DataFrame) -> DataFrameGroupBy:
    """Group the data by T-stage, num of ipsi involved, and midline extension."""
    lnl_cols = shared.get_lnl_cols("contra", lnls=["I", "II", "III", "IV"])
    num_ipsi_inv = data[shared.get_lnl_cols("ipsi")].sum(axis="columns")
    contra_inv = data[lnl_cols].copy()
    contra_inv.columns = contra_inv.columns.droplevel([0,1])

    contra_inv["t_stage"] = data[shared.COL.t_stage]
    contra_inv["ipsi"] = num_ipsi_inv.map(lambda x: str(x) if x <= 1 else "≥ 2")
    contra_inv["midext"] = data[shared.COL.midext]

    return contra_inv.groupby(by=["t_stage", "ipsi", "midext"])


def cast_numpy_to_native(variables: dict[str, Any]) -> dict[str, Any]:
    """Convert numpy dtypes to native Python types."""
    result = {}

    for key, value in variables.items():
        try:
            result[key] = value.item()
        except AttributeError:
            result[key] = value

    return result


def variables_from_portion(
    key: str,
    portion: QueryPortion,
    precision: int = 2,
) -> dict[str, Any]:
    """Get a dictionary from a QueryPortion object."""
    return {
        f"{key}_match": portion.match,
        f"{key}_total": portion.total,
        f"{key}_percent": round(portion.percent, precision),
    }


def get_diagnosis_label(
    side_diagnosis,
    modality: str = "CT",
    prefix: str = "i",
    joiner: str = "+",
) -> str:
    """Create a short label from a diagnosis."""
    label = ""
    is_n0 = True

    positive = [
        lnl for lnl, status in side_diagnosis.get(modality, {}).items() if status
    ]
    if len(positive) > 0:
        is_n0 = False
        label += prefix + joiner.join(positive)

    if "FNA" in side_diagnosis:
        is_n0 = False
        label += "_FNA"

    return label if not is_n0 else f"{prefix}N0"


def get_variable_name_for_prevalence(scenario: Scenario) -> str:
    """Get the variable name for the scenario."""
    return "_".join([
        str(scenario.t_stages[0]),
        "ext" if scenario.midext else "noext",
        get_diagnosis_label(
            scenario.diagnosis.get("ipsi", {}),
            modality="max_llh",
            prefix="i",
        ),
        get_diagnosis_label(
            scenario.diagnosis.get("contra", {}),
            modality="max_llh",
            prefix="c",
        ),
    ])


def get_variable_name_for_risk(scenario: Scenario) -> str:
    """Get the variable name for the scenario."""
    return "_".join([
        str(scenario.t_stages[0]),
        "ext" if scenario.midext else "noext",
        get_diagnosis_label(scenario.diagnosis.get("ipsi", {}), prefix="i"),
        get_diagnosis_label(scenario.diagnosis.get("contra", {}), prefix="c"),
        list(scenario.involvement["contra"].keys()).pop()
    ])


def get_data_variables(precision: int = 2) -> dict[str, Any]:
    """Get the variables from the data."""
    variables = {}
    data = shared.get_data()

    variables["num_patients"] = len(data)

    is_early = Q("t_stage", "==", "early")
    is_late = Q("t_stage", "==", "late")
    has_midext = Q("midext", "==", True)
    not_has_midext = Q("midext", "==", False)
    is_cII_involved = Q(("max_llh", "contra", "II"), "==", True)
    is_ipsi_healthy = (
        Q(("max_llh", "ipsi", "I"), "==", False)
        & Q(("max_llh", "ipsi", "II"), "==", False)
        & Q(("max_llh", "ipsi", "III"), "==", False)
        & Q(("max_llh", "ipsi", "IV"), "==", False)
        & Q(("max_llh", "ipsi", "V"), "==", False)
    )
    is_iII_involved = (
        Q(("max_llh", "ipsi", "I"), "==", False)
        & Q(("max_llh", "ipsi", "II"), "==", True)
        & Q(("max_llh", "ipsi", "III"), "==", False)
        & Q(("max_llh", "ipsi", "IV"), "==", False)
        & Q(("max_llh", "ipsi", "V"), "==", False)
    )
    is_iIIandIII_involved = (
        Q(("max_llh", "ipsi", "I"), "==", False)
        & Q(("max_llh", "ipsi", "II"), "==", True)
        & Q(("max_llh", "ipsi", "III"), "==", True)
        & Q(("max_llh", "ipsi", "IV"), "==", False)
        & Q(("max_llh", "ipsi", "V"), "==", False)
    )

    variables.update(variables_from_portion(
        key="early_with_midext",
        portion=data.ly.portion(query=has_midext, given=is_early),
        precision=precision,
    ))
    variables.update(variables_from_portion(
        key="late_with_midext",
        portion=data.ly.portion(query=has_midext, given=is_late),
        precision=precision,
    ))

    variables.update(variables_from_portion(
        key="early_ipsin0_cII",
        portion=data.ly.portion(
            query=is_cII_involved,
            given=is_early & is_ipsi_healthy,
        ),
        precision=precision,
    ))
    variables.update(variables_from_portion(
        key="early_ipsiII_cII",
        portion=data.ly.portion(
            query=is_cII_involved,
            given=is_early & is_iII_involved,
        ),
        precision=precision,
    ))
    variables.update(variables_from_portion(
        key="early_ipsiIIandIII_cII",
        portion=data.ly.portion(
            query=is_cII_involved,
            given=is_early & is_iIIandIII_involved,
        ),
        precision=precision,
    ))
    variables.update(variables_from_portion(
        key="late_ipsiIIandIII_cII",
        portion=data.ly.portion(
            query=is_cII_involved,
            given=is_late & is_iIIandIII_involved,
        ),
        precision=precision,
    ))
    variables.update(variables_from_portion(
        key="early_nomidext_cII",
        portion=data.ly.portion(
            query=is_cII_involved,
            given=is_early & not_has_midext,
        ),
        precision=precision,
    ))

    return cast_numpy_to_native(variables)


def get_model_variables(precision: int = 2) -> dict[str, Any]:
    """Get the variables from the models."""
    variables = {}
    model = shared.get_model(which="full", load_samples=True)

    variables["params"] = cast_numpy_to_native({
        k: round(v, precision)
        for k, v in model.get_params().items()
    })
    variables["params_percent"] = cast_numpy_to_native({
        k: round(100 * v, precision)
        for k, v in model.get_params().items()
    })
    early_dist = model.get_distribution("early")
    variables["early_expected_time"] = round(
        number=early_dist.support @ early_dist.pmf,
        ndigits=precision,
    ).item()
    late_dist = model.get_distribution("late")
    variables["late_expected_time"] = round(
        number=late_dist.support @ late_dist.pmf,
        ndigits=precision,
    ).item()

    return variables


def get_prevalence_variables(
    prevalences_file: Path,
    scenarios_file: Path,
    precision: int = 2,
) -> dict[str, Any]:
    """Get the variables of the prevalence calculations."""
    with h5py.File(prevalences_file, mode="r") as file:
        prevalences = {key: dset[:] for key, dset in file.items()}
        portions = {
            key: QueryPortion(
                match=dset.attrs["num_match"],
                total=dset.attrs["num_total"],
            )
            for key, dset in file.items()
        }

    with open(scenarios_file, mode="r", encoding="utf-8") as file:
        scenario_params = yaml.safe_load(file)
        scenarios = Scenario.list_from_params(scenario_params)

    variables = {}

    for scenario in scenarios:
        hash_ = scenario.md5_hash(for_comp="prevalences")
        key = get_variable_name_for_prevalence(scenario)
        mean_prevalence = round(100 * prevalences[hash_].mean().item(), precision)
        variables[key] = {
            "predicted": mean_prevalence,
            "observed": round(portions[hash_].percent.item(), precision),
        }

    return variables


def get_risk_variables(
    risks_file: Path,
    scenarios_file: Path,
    precision: int = 2,
) -> dict[str, Any]:
    """Get the variables for the risk calculations."""
    with h5py.File(risks_file, mode="r") as file:
        risks = {key: dset[:] for key, dset in file.items()}

    with open(scenarios_file, mode="r", encoding="utf-8") as file:
        scenario_params = yaml.safe_load(file)
        scenarios = Scenario.list_from_params(scenario_params)

    variables = {}

    for scenario in scenarios:
        hash_ = scenario.md5_hash(for_comp="risks")
        key = get_variable_name_for_risk(scenario)
        mean_risk = round(100 * risks[hash_].mean().item(), precision)
        variables[key] = mean_risk

    return variables


def main() -> None:
    """Merge the variables from data and models and store them in `_variables.yaml`."""
    cmd = CmdSettings()

    variables = {}
    variables["data"] = get_data_variables(precision=cmd.precision)
    variables["model"] = get_model_variables(precision=cmd.precision)
    variables["prevalence"] = get_prevalence_variables(
        prevalences_file=cmd.prevalence_hdf5,
        scenarios_file=cmd.prevalence_scenarios,
        precision=cmd.precision,
    )
    variables["risk"] = get_risk_variables(
        risks_file=cmd.risk_hdf5,
        scenarios_file=cmd.risk_scenarios,
        precision=cmd.precision,
    )

    with open(cmd.output, mode="w", encoding="utf-8") as file:
        yaml.dump(variables, file)


if __name__ == "__main__":
    main()
