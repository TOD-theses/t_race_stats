import csv
from pathlib import Path
from typing import Sequence, TypedDict

import pandas as pd

class TimeEntry(TypedDict):
    task: Sequence[str]
    ms: int

def process_timing_stats(input_dir: Path, output_dir: Path):
    timings = load_timings(input_dir)
    fig = create_component_timing_fig(timings)
    fig.savefig(output_dir / "timings_components.png")


def load_timings(input_dir: Path) -> Sequence[TimeEntry]:
    path = input_dir / "timings.csv"

    with open(path) as f:
        reader = csv.DictReader(f)
        return [
            {
                "task": t["task"].split("|"),
                "ms": int(t["elapsed_ms"]),
            }
            for t in reader
        ]


def create_component_timing_fig(timings: Sequence[TimeEntry]):
    df = df_sum_components_ms(timings)
    df["elapsed_s"] = df["elapsed_ms"].div(1000).round(decimals=1)
    ax = df.plot.bar(
        y="elapsed_s",
        rot=0,
        legend=False,
        xlabel="",
        ylabel="seconds",
        title="Running time",
    )
    ax.bar_label(ax.containers[0])  # type: ignore
    fig = ax.get_figure()
    assert fig is not None
    return fig


def df_sum_components_ms(timings: Sequence[TimeEntry]):
    main_tasks = [t for t in timings if len(t['task']) == 2]

    total = next(t['ms'] for t in timings if len(t['task']) == 1)
    mine = next(t['ms'] for t in main_tasks if t['task'][1] == 'mine')
    check = next(t["ms"] for t in main_tasks if t['task'][1] == 'check')
    properties = next(t['ms'] for t in main_tasks if t['task'][1] == 'properties')

    other = total - (mine + check + properties)

    results = [
        ("total", total),
        ("mine", mine),
        ("check", check),
        ("properties", properties),
        ("other", other),
    ]

    return pd.DataFrame.from_records(
        results, index="component", columns=("component", "elapsed_ms")
    )
