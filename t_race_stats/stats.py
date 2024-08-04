from pathlib import Path

from t_race_stats.timing.timing_stats import process_timing_stats
from t_race_stats.tod_attack_miner.stats import process_tod_attack_miner_stats
from t_race_stats.utils.available_components import get_available_components


def process_stats(input_dir: Path, output_dir: Path):
    assert (
        input_dir.exists()
    ), f"Could not find results directory: {input_dir.absolute()}"
    output_dir.mkdir(exist_ok=True)

    available_components = get_available_components(input_dir)
    print(f"Creating stats for components: {available_components}")

    if "mine" in available_components:
        process_tod_attack_miner_stats(input_dir, output_dir)

    if (
        "mine" in available_components
        and "trace" in available_components
        and "analyze" in available_components
    ):
        process_timing_stats(input_dir, output_dir)
