import csv
import json
from pathlib import Path
from typing import Sequence
import pandas as pd
import matplotlib.pyplot as plt


def process_tod_attack_miner_stats(input_dir: Path, output_dir: Path):
    stats = load_stats(input_dir)
    collisions = load_candidates(input_dir)
    create_charts(stats, collisions, output_dir)


def load_stats(input_dir: Path) -> dict:
    with open(input_dir / "mining_stats.json") as f:
        stats = json.load(f)
        return stats


def load_candidates(input_dir: Path) -> Sequence[dict]:
    with open(input_dir / "tod_candidates.csv") as f:
        reader = csv.DictReader(f)

        candidates = []

        for row in reader:
            candidates.append(
                {
                    "tx_write_hash": row["tx_write_hash"],
                    "tx_access_hash": row["tx_access_hash"],
                    "block_dist": int(row["block_dist"]),
                    "types": row["types"].split("|"),
                }
            )

        return candidates


def create_charts(stats: dict, candidates: Sequence[dict], output_dir: Path):
    fig = create_block_dist_fig(candidates)
    fig.savefig(output_dir / "tod_candidates_block_dist.png")


def create_block_dist_fig(collisions: Sequence[dict]):
    df = pd.DataFrame.from_records(collisions, columns=["block_dist"])

    cdf = (
        df.groupby("block_dist")["block_dist"]
        .aggregate("count")
        .pipe(pd.DataFrame)
        .rename(columns={"block_dist": "frequency"})
    )
    cdf["pdf"] = cdf["frequency"] / sum(cdf["frequency"])
    cdf["cdf"] = cdf["pdf"].cumsum()
    cdf = cdf[["cdf", "frequency"]]

    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    ax.grid(axis="x", alpha=0.6, zorder=0)
    ax2.grid(alpha=0.6, zorder=0)

    ax.bar(x=cdf.index, height=cdf["frequency"], label="TOD candidates", zorder=2)
    ax.set_xlabel("Block distance")
    ax.set_ylabel("TOD candidates")

    # shift eCDF one to the right, s.t. the lines match the bars
    cdf.loc[-1] = [0, 0]
    cdf.index = cdf.index + 1
    cdf = cdf.sort_index()

    ax2.step(
        x=cdf.index,
        y=cdf["cdf"],
        color="tab:orange",
        label="eCDF of TOD candidates",
        zorder=1,
    )
    ax2.set_ylim((0, 1))
    ax2.set_ylabel("Cumulative percentage of TOD candidates")
    fig.legend(loc="upper left")

    return fig
