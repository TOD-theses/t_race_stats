import csv
from pathlib import Path
from typing import Sequence

import pandas as pd


def process_timing_stats(input_dir: Path, output_dir: Path):
    timings = load_timings(input_dir)
    fig = create_component_timing_fig(timings)
    fig.savefig(output_dir / "timings_components.png")


def load_timings(input_dir: Path) -> Sequence[dict]:
    path = input_dir / "timings.csv"

    with open(path) as f:
        reader = csv.DictReader(f)
        return [
            {
                "type": t["type"],
                "component": t["component"],
                "step": t["step"] or None,
                "elapsed_ms": int(t["elapsed_ms"]),
            }
            for t in reader
        ]


def create_component_timing_fig(timings: Sequence[dict]):
    df = df_sum_components_ms(timings)
    df["elapsed_s"] = df["elapsed_ms"].div(1000).round()
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


def df_sum_components_ms(timings: Sequence[dict]):
    df = pd.DataFrame.from_records(timings)
    df_steps = df[(df["type"] == "step") & df["component"].isin(("trace", "analyze"))]
    df_trace_analyze_percentage = (
        df_steps.groupby("component")["elapsed_ms"].agg("sum")
        / df_steps["elapsed_ms"].sum()
    )
    df_components = df[(df["type"] == "component")]

    trace_analyze_ms = df_components[df_components["component"] == "trace_analyze"][
        "elapsed_ms"
    ].values[0] # type: ignore
    df_trace_analyze = df_trace_analyze_percentage * trace_analyze_ms

    results = [
        (
            "total",
            int(
                df_components[df_components["component"] == "t_race"][
                    "elapsed_ms"
                ].values[0] # type: ignore
            ),
        ),
        (
            "mine",
            int(
                df_components[df_components["component"] == "mine"][
                    "elapsed_ms"
                ].values[0] # type: ignore
            ),
        ),
        ("trace", int(df_trace_analyze["trace"])),
        ("analyze", int(df_trace_analyze["analyze"])),
    ]
    return pd.DataFrame.from_records(
        results, index="component", columns=("component", "elapsed_ms")
    )
