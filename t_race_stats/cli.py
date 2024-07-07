"""CLI interface for t_race_stats project."""

from argparse import ArgumentParser
from pathlib import Path

from t_race_stats.stats import process_stats


def main():
    parser = ArgumentParser(description="Process T-Race stats")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results"),
        help="Path to the T-Race results dir",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("out"),
        help="Path where charts will be stored",
    )

    args = parser.parse_args()

    process_stats(args.results_dir, args.out_dir)
