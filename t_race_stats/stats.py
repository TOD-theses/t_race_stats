from pathlib import Path

from t_race_stats.timing.timing_stats import process_timing_stats
from t_race_stats.tod_attack_miner.stats import process_tod_attack_miner_stats


def process_stats(input_dir: Path, output_dir: Path):
    assert (
        input_dir.exists()
    ), f"Could not find results directory: {input_dir.absolute()}"
    output_dir.mkdir(exist_ok=True)

    process_tod_attack_miner_stats(input_dir, output_dir)
    process_timing_stats(input_dir, output_dir)
