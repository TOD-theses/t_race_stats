from pathlib import Path

from t_race_stats.timing.timing_stats import load_timings


def get_available_components(input_dir: Path) -> set[str]:
    timings = load_timings(input_dir)

    return set(t["task"][1] for t in timings if len(t["task"]) > 1)
