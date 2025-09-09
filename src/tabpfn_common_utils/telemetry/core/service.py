import os

from datetime import datetime
from posthog import Posthog
from tabpfn_common_utils.telemetry.core.events import BaseTelemetryEvent
from tabpfn_common_utils.utils import singleton
from typing import Any, Dict, Optional


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

    @staticmethod
    def telemetry_enabled() -> bool:
        """
        Check if telemetry is enabled.

        Returns:
            bool: True if telemetry is enabled, False otherwise.
        """
        return os.getenv("TABPFN_DISABLE_TELEMETRY", "0").lower() not in ("1", "true")

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
        if self._posthog_client is None:
            return

        # Anonymous default UUID in case no explicit consent to opt in to telemetry
        user_id = distinct_id or "00000000-0000-0000-0000-000000000000"

        # Merge the event properties with the provided properties
        properties = {**event.properties, **(properties or {})}

        try:
            self._posthog_client.capture(
                distinct_id=user_id,
                event=event.name,
                properties=properties,
                timestamp=timestamp or event.timestamp,
            )
        except Exception:
            # Silently ignore any errors
            pass

    def flush(self) -> None:
        """
        Flush the PostHog client telemetry queue.
        """
        if not self._posthog_client:
            return

        try:
            self._posthog_client.flush()
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
