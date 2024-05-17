"""Compute the prevalence of midline extension (predicted and observed)."""
import h5py

import paths
import shared


def main():
    model = shared.get_model("full")
    samples = shared.get_samples("full")
    predicted = {"early": [], "late": []}

    data = shared.get_data()
    data = data[~data.ly.midext.isna()]
    observed = {
        "early": (
            data[data.ly.t_stage == "early"].ly.is_midext(True).sum(),
            (data.ly.t_stage == "early").sum(),
        ),
        "late": (
            data[data.ly.t_stage == "late"].ly.is_midext(True).sum(),
            (data.ly.t_stage == "late").sum(),
        ),
    }

    for sample in samples[::10]:
        model.set_params(*sample)
        predicted["early"].append(model.marginalize(t_stage="early", midext=True))
        predicted["late"].append(model.marginalize(t_stage="late", midext=True))

    with h5py.File(
        paths.model_dir / "full" / "prevalence_midext.hdf5",
        mode="w",
    ) as h5_file:
        h5_file["early"] = predicted["early"]
        h5_file["early"].attrs["num_match"] = observed["early"][0]
        h5_file["early"].attrs["num_total"] = observed["early"][1]

        h5_file["late"] = predicted["late"]
        h5_file["late"].attrs["num_match"] = observed["late"][0]
        h5_file["late"].attrs["num_total"] = observed["late"][1]


if __name__ == "__main__":
    main()
