from enum import Enum
from typing import Callable, Optional, Tuple

from .analytics_func import (
    get_calling_class,
    get_python_version,
    get_unique_call_id,
)


class ANALYTICS_KEYS(str, Enum):
    UniqueCallID = "PL-Unique-Call-Id"
    PythonVersion = "PL-Python-Version"
    CallingClass = "PL-Calling-Class"
    ModuleName = "PL-Module-Name"


ANALYTICS_HEADER_CONFIG: Tuple[Tuple[str, Optional[Callable]], ...] = (
    (ANALYTICS_KEYS.UniqueCallID, get_unique_call_id),
    (ANALYTICS_KEYS.PythonVersion, get_python_version),
    (ANALYTICS_KEYS.CallingClass, get_calling_class),
    (ANALYTICS_KEYS.ModuleName, None),  # Value provided by AnalyticsHttpClient
)
