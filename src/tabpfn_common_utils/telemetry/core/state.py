"""State management for telemetry."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from platformdirs import user_config_dir
from typing import Any


# Check if filelock is available
# ruff: noqa: I001
_HAS_FILELOCK = False
try:
    import filelock  # type: ignore[import-untyped] # noqa: F401

    _HAS_FILELOCK = True
except ImportError:
    pass

# Application name and vendor
APP = "tabpfn"
VENDOR = "priorlabs"
FILENAME = "state.json"

# Schema
_DEFAULT_STATE: dict[str, Any] = {
    "created_at": None,  # ISO-8601 | null
    "opted_in": None,  # true | false | null
    "user_id": None,  # string | null
    "email": None,  # string | null
    "email_prompt_count": 0,  # 0..2
    "last_prompted_at": None,  # ISO-8601 | null
    "last_pinged_at": None,  # ISO-8601 | null
}


def _state_path() -> Path:
    """Get the path to the state file.

    Returns:
        Path: The path to the state file.
    """
    # Overrides first
    if p := os.getenv("TABPFN_STATE_PATH"):
        return Path(p).expanduser()
    if d := os.getenv("TABPFN_STATE_DIR"):
        return Path(d).expanduser() / FILENAME

    # Standard per-user config dir
    return Path(user_config_dir(APP, VENDOR)) / FILENAME


def _ensure_dir(path: Path) -> None:
    """Ensure the directory exists.

    Args:
        path: The path to the directory.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.suppress(OSError):
        path.parent.chmod(0o700)


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    """Atomic write to the state file.

    Args:
        path: The path to the state file.
        data: The data to write to the state file.
    """
    # Ensure the directory exists
    _ensure_dir(path)

    # Create a temporary file
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", dir=str(path.parent))

    # Write the data to the temporary file
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            params = {
                "ensure_ascii": False,
                "separators": (",", ":"),
                "default": _json_serialize,
            }
            json.dump(data, f, **params)

            # Flush the file to disk
            f.flush()
            # Sync the file to disk
            os.fsync(f.fileno())

        Path(tmp).replace(path)

        # Set file permissions
        _set_file_permissions(path)
    finally:
        _cleanup_temp_file(tmp)


def _json_serialize(obj: Any) -> Any:
    """Default JSON encoder that handles datetime objects.

    Args:
        obj: The object to potentially encode.

    Returns:
        The object with datetime objects converted to ISO strings.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj


def _set_file_permissions(path: Path) -> None:
    """Set file permissions to 0o600, ignoring any errors.

    Args:
        path: The path to the file.
    """
    with contextlib.suppress(OSError):
        path.chmod(0o600)


def _cleanup_temp_file(tmp_path: str) -> None:
    """Remove temporary file, ignoring any errors.

    Args:
        tmp_path: The path to the temporary file.
    """
    with contextlib.suppress(OSError):
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()


def _read(path: Path) -> dict[str, Any]:
    """Read the state file.

    Args:
        path: The path to the state file.

    Returns:
        The state data (empty dict on errors).
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError):
        # Corrupt -> treat as empty
        return {}


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw state to the current schema.

    Returns:
        A merged state dict conforming to _DEFAULT_STATE.
    """
    if not raw:
        state = dict(_DEFAULT_STATE)
        state["created_at"] = datetime.now(timezone.utc).isoformat()
        return state

    # Backfill defaults without dropping unknown future keys
    return {**_DEFAULT_STATE, **raw}


def load_state() -> dict[str, Any]:
    """Load the telemetry state.

    Returns:
        The telemetry state (schema-normalized).
    """
    path = _state_path()
    raw = _read(path)
    return _normalize(raw)


def save_state(state: dict[str, Any]) -> None:
    """Save the telemetry state.

    Args:
        state: The telemetry state to persist.
    """
    normalized = _normalize(state)
    if not normalized.get("created_at"):
        normalized["created_at"] = datetime.now(timezone.utc).isoformat()

    path = _state_path()
    _atomic_write(path, normalized)


def get_property(key: str, default: Any = None, data_type: type | None = None) -> Any:
    """Get a property from the telemetry state with optional type conversion.

    Args:
        key: The property name.
        default: The default value if the property is not found.
        data_type: The expected data type.

    Returns:
        The property value or default.
    """
    state = load_state()
    value = state.get(key, default)

    if value is None or value == default:
        return value

    if data_type is None:
        return value

    # TODO: handle other type conversions
    try:
        if data_type == datetime:
            # datetime conversion from ISO format string
            if isinstance(value, str):
                value = datetime.fromisoformat(value)
        else:
            # Handle other type conversions
            value = data_type(value)
    except (ValueError, TypeError):
        return default
    else:
        return value


def set_property(key: str, value: Any) -> None:
    """Set a property on the telemetry state.

    Args:
        key: The property name.
        value: The value to set.
    """
    state = load_state()
    state[key] = value
    save_state(state)
