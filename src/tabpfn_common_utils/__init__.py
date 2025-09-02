from __future__ import annotations

from .telemetry.events import DatasetEvent, FitEvent, PredictEvent
from .telemetry.service import ProductTelemetry

try:
    from importlib.metadata import version as _pkg_version
except ImportError:
    def _pkg_version(distribution_name: str) -> str:
        return "0.1.1"  # Fallback

# Package version
__version__ = _pkg_version("tabpfn-common-utils")

# Public exports
__all__ = [
    "DatasetEvent",
    "FitEvent",
    "PredictEvent",
    "ProductTelemetry",
    "__version__"
]
