"""Script to compile variables from data and models and stores them in a YAML file."""

from pathlib import Path
from typing import Any

import lydata  # noqa: F401
import pandas as pd
import shared
import yaml
from lydata.accessor import Q, QueryPortion
from pandas.api.typing import DataFrameGroupBy
from pydantic_settings import BaseSettings


class CmdSettings(BaseSettings, cli_parse_args=True):
    """Settings for the command-line arguments."""

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


def get_risk_variables(precision: int = 2) -> dict[str, Any]:
    """Get the variables for the risk calculations."""
    variables = {}

    return variables


def main() -> None:
    """Merge the variables from data and models and store them in `_variables.yaml`."""
    cmd = CmdSettings()

    variables = {}
    variables["data"] = get_data_variables(precision=cmd.precision)
    variables["model"] = get_model_variables(precision=cmd.precision)
    variables["risk"] = get_risk_variables(precision=cmd.precision)

    with open(cmd.output, mode="w", encoding="utf-8") as file:
        yaml.dump(variables, file)


if __name__ == "__main__":
    main()
