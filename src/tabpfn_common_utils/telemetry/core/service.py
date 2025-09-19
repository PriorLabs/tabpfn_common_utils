import logging
import os
import requests

from datetime import datetime
from posthog import Posthog
from .events import BaseTelemetryEvent
from .runtime import get_runtime
from ...utils import singleton, ttl_cache
from typing import Any, Dict, Optional


# Set up logging
logger = logging.getLogger(__name__)


@singleton
class ProductTelemetry:
    """
    Service for capturing anonymous and aggregated telemetry data.
    """

    # Public PostHog project API key
    PROJECT_API_KEY = "phc_wemJSoR4e8rGJomHz0clm6aHdOWp0EvpRP368uVsUvJ"

    # Public PostHog host (EU)
    HOST = "https://eu.i.posthog.com"

    # PostHog client instance
    _posthog_client: Optional[Posthog] = None

    def __init__(self, max_queue_size: int = 10, flush_at: int = 10) -> None:
        """
        Initialize the Telemetry service.
        """
        # If telemetry is disabled, don't initialize the PostHog client
        if not self.telemetry_enabled():
            self._posthog_client = None
            return

        # Initialize the PostHog client
        self._posthog_client = Posthog(
            project_api_key=self.PROJECT_API_KEY,
            host=self.HOST,
            disable_geoip=True,
            enable_exception_autocapture=False,
            max_queue_size=max_queue_size,
            flush_at=flush_at,
        )

    @classmethod
    def telemetry_enabled(cls) -> bool:
        """
        Check if telemetry is enabled.

        Returns:
            bool: True if telemetry is enabled, False otherwise.
        """
        # Disable telemetry by default in CI environments, but allow override
        runtime = get_runtime()
        default_disable = "1" if runtime.ci else "0"

        # Overwrite any settings based on server-side configuration
        config = cls._download_config()
        if config["enabled"] is False:
            return False

        value = os.getenv("TABPFN_DISABLE_TELEMETRY", default_disable).lower()
        return value not in ("1", "true")

    @classmethod
    @ttl_cache(ttl_seconds=60 * 5)
    def _download_config(cls) -> Dict[str, Any]:
        """Download the configuration from server.

        Returns:
            Dict[str, Any]: The configuration.
        """
        # The default configuration
        default = {"enabled": False}

        # This is a public URL anyone can and should read from
        url = os.environ.get(
            "TABPFN_TELEMETRY_CONFIG_URL",
            "https://storage.googleapis.com/prior-labs-tabpfn-public/config/telemetry.json",
        )
        try:
            resp = requests.get(url)
        except Exception:
            logger.debug(f"Failed to download telemetry config: {url}")
            return default

        # Disable telemetry by default
        if resp.status_code != 200:
            logger.debug(f"Failed to download telemetry config: {resp.status_code}")
            return {"enabled": False}

        return resp.json()

    def capture(
        self,
        event: BaseTelemetryEvent,
        *,
        distinct_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Send an event. Optionally override distinct_id (useful in API).

        Args:
            event (BaseTelemetryEvent): The event to send.
            distinct_id (str): The distinct ID to send the event to.
            properties (dict): The additional properties attached to an event.
            timestamp (datetime): The timestamp of the event.
        """
        if self.telemetry_enabled() is False:
            return

        # Add the check just for type safety
        if self._posthog_client is None:
            return

        # Merge the event properties with the provided properties
        properties = {**event.properties, **(properties or {})}

        # Set up dynamic `capture` arguments
        capture_args = {
            "event": event.name,
            "properties": properties,
            "timestamp": timestamp or event.timestamp,
        }

        # Do not capture any user ID if it is not provided
        if distinct_id:
            capture_args["distinct_id"] = distinct_id

        try:
            self._posthog_client.capture(**capture_args)
        except Exception:
            # Silently ignore any errors
            pass

    def flush(self) -> None:
        """
        Flush the PostHog client telemetry queue.
        """
        if self.telemetry_enabled() is False:
            return

        try:
            self._posthog_client.flush()  # type: ignore
        except Exception:
            # Silently ignore any errors
            pass


def capture_event(
    event: BaseTelemetryEvent, max_queue_size: int = 10, flush_at: int = 10
) -> None:
    """Capture a telemetry event.

    Args:
        event: The event to capture.
        max_queue_size: The maximum size of the queue.
        flush_at: The number of events to flush.
    """
    client = ProductTelemetry(max_queue_size, flush_at)
    client.capture(event)
