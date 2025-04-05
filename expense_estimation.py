from typing import Literal

from utils import estimate_memory_usage, VERTEX_GPU_FACTOR


def estimate_duration(
    num_rows: int,
    num_features: int,
    task: Literal["classification", "regression"],
    tabpfn_config: dict = {},
    duration_factor: float = VERTEX_GPU_FACTOR,
    latency_offset: float = 0.0,
) -> float:
    """
    Estimates the duration of a prediction task.
    """
    base_memory_usage = estimate_memory_usage(num_rows, num_features, task, tabpfn_config)
    
    return round(base_memory_usage * duration_factor + latency_offset, 3)