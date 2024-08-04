import csv
import json
from pathlib import Path
from typing import Sequence, TypedDict
import matplotlib.ticker
import pandas as pd
import matplotlib.pyplot as plt

class TODCandidate(TypedDict):
    tx_a: str
    tx_b: str
    block_dist: int
    types: Sequence[str]

def process_tod_attack_miner_stats(input_dir: Path, output_dir: Path):
    stats = load_stats(input_dir)
    collisions = load_candidates(input_dir)
    create_charts(stats, collisions, output_dir)


def load_stats(input_dir: Path) -> dict:
    with open(input_dir / "mining_stats.json") as f:
        stats = json.load(f)
        return stats


def load_candidates(input_dir: Path) -> Sequence[TODCandidate]:
    with open(input_dir / "tod_candidates.csv") as f:
        reader = csv.DictReader(f)

        candidates = []

        for row in reader:
            candidates.append(
                {
                    "tx_a": row["tx_a"],
                    "tx_b": row["tx_b"],
                    "block_dist": int(row["block_dist"]),
                    "types": row["types"].split("|"),
                }
            )

        return candidates


def create_charts(stats: dict, candidates: Sequence[TODCandidate], output_dir: Path):
    fig = create_collisions_limited_per_address_fig(
        stats["frequencies"]["collisions_addresses"]
    )
    fig.savefig(output_dir / "collisions_limited_per_address.png")
    fig.clear()

    fig = create_block_dist_fig(candidates)
    fig.savefig(output_dir / "tod_candidates_block_dist.png")
    fig.clear()


def create_block_dist_fig(collisions: Sequence[TODCandidate]):
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


def create_collisions_limited_per_address_fig(
    collision_addresses_frequencies: Sequence[tuple[int, int]],
):
    collisions_with_max_n_per_addr: list[tuple[int, int]] = []
    max_collisions_per_address = collision_addresses_frequencies[0][0]

    for n in range(1, max_collisions_per_address):
        collisions = sum(
            min(colls_per_addr, n) * times
            for colls_per_addr, times in collision_addresses_frequencies
        )
        collisions_with_max_n_per_addr.append((n, collisions))

    df = pd.DataFrame.from_records(
        collisions_with_max_n_per_addr, index="n", columns=["n", "collisions"]
    )

    fig, ax = plt.subplots()
    ax.plot(df.index, df["collisions"])
    ax.set_title("Limit for collisions per address")
    ax.set_xlabel("Collisions limit")
    ax.set_ylabel("Collisions")
    ax.set_ylim(bottom=0)
    ax.set_xlim((0.6, 10000))
    ax.set_xscale("log")
    # ax.set_xticks([1, 5, 10, 50, 100, 500, 1000, 5000])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.grid(axis="both", alpha=0.6, zorder=0)
    return fig
