"""Client code for anonymously tracking model usage."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import requests
from ...telemetry import PingEvent, ProductTelemetry, capture_event

from .prompt import (
    get_default_prompt,
    prompt_email_ipython,
    prompt_email_tty,
)
from .runtime import get_runtime
from ..core.state import get_property, set_property

# Logger
logger = logging.getLogger(__name__)

# Silence third-party logs
logging.getLogger("posthog").setLevel(logging.CRITICAL + 1)

# Initialize the telemetry client for optional usage analytics
_telemetry = ProductTelemetry()

# Constants
_API_URL = os.environ.get(
    "TABPFN_API_URL", "https://tabpfn-server-wjedmz7r5a-ez.a.run.app"
)


def ping(enabled: bool = True) -> None:
    """Ping the usage service to track usage and analytics."""
    # Skip if disabled
    if not enabled:
        return

    utc_now = datetime.now(timezone.utc)

    # Determine whether we should ping
    last_pinged_at = get_property("last_pinged_at", data_type=datetime)
    if last_pinged_at and utc_now - last_pinged_at < timedelta(days=1):
        return

    # Ping the usage service
    event = PingEvent()
    capture_event(event)

    # Acknowledge the ping
    set_property("last_pinged_at", utc_now)


def subscribe(enabled: bool = True, delta_days: int = 30, max_prompts: int = 2) -> None:
    """Prompt the user to subscribe to newsletter about releases, critical bux
    fixes and major research insights from the Prior Labs team.
    """
    # Skip if disabled
    if not enabled:
        return

    # tabpfn not run in interactive mode
    runtime = get_runtime()
    if not runtime.interactive:
        return

    # Check if user already subscribed
    email = get_property("email", default=None)
    if email:
        return

    # Determine whether to prompt the user or not
    utc_now = datetime.now(timezone.utc)

    last_prompted_at = get_property("last_prompted_at", data_type=datetime)
    if last_prompted_at:
        # Ignore if last prompted less than 30 days ago
        if utc_now - last_prompted_at < timedelta(days=delta_days):
            return

        # Ignore if prompted for more than 2 times
        prompt_count = get_property("email_prompt_count", 0, data_type=int)
        if prompt_count >= max_prompts:
            return

    # Prompt the user
    title, body, hint = get_default_prompt()

    if runtime.kernel in {"ipython", "jupyter"}:
        result = prompt_email_ipython(title, body, hint)
    else:
        result = prompt_email_tty(title, body, hint)

    # Acknowledge the prompt
    set_property("last_prompted_at", utc_now)

    # Subscribe the user to newsletter
    if result.outcome != "accepted":
        return

    # Subscribe via API
    if result.email:
        _subscribe_user(result.email)

    # Generate a user ID when opted in
    user_id = str(uuid.uuid4())

    # Update the on-disk properties
    set_property("user_id", user_id)
    set_property("email", result.email)

    return


def _subscribe_user(email: str) -> None:
    """Subscribe the user to newsletter using the API.

    Args:
        email: The email of the user to subscribe.
    """
    endpoint = _API_URL + "/newsletter/subscribe"
    r = requests.post(endpoint, json={"email": email}, timeout=5)
    if r.status_code != 200:
        logger.debug(f"Failed to subscribe user {email}: {r.text}")
        return
