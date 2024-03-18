"""
Remove all unnecessary columns from the joined, enhanced and (row-wise) filtered data.
"""
import argparse
from pathlib import Path

import pandas as pd


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Path to the input file.')
    parser.add_argument('output', type=Path, help='Path to the output file.')
    return parser


def main():
    """Main function."""
    parser = create_parser()
    args = parser.parse_args()

    data = pd.read_csv(
        args.input, header=[0,1,2],
    ).drop(columns=[
        "enbloc_dissected",
        "enbloc_positive",
        "positive_dissected",
        "total_dissected",
    ])

    data.to_csv(args.output, index=False)


if __name__ == '__main__':
    main()
