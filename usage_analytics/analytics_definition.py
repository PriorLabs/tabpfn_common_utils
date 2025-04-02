from tabpfn_common_utils.usage_analytics.analytics_func import (
    get_calling_class,
    get_python_version,
    get_unique_call_id,
)


ANALYTICS_TO_TRACK = [
    ("X-Unique-Call-Id", get_unique_call_id),
    ("X-Calling-Class", get_calling_class),
    ("X-Python-Version", get_python_version),
]
