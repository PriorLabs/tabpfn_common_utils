import logging
import os
import atexit
import threading
import queue
from queue import Queue
from datetime import datetime
from posthog import Posthog
from .config import download_config
from .events import BaseTelemetryEvent
from .runtime import get_execution_context
from ...utils import singleton
from typing import Any, Dict, Optional


# Set up logging
logger = logging.getLogger(__name__)

# Suppress PostHog and analytics-python logs (unless explicitly enabled)
if os.getenv("TABPFN_ENABLE_TELEMETRY_LOGS", "0").lower() not in ("1", "true"):
    for logger_name in ["posthog", "analytics", "posthog.analytics"]:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)


@singleton
class ProductTelemetry:
    """Service for capturing anonymous and aggregated telemetry data."""

    # Public PostHog project API key
    PROJECT_API_KEY = "phc_wemJSoR4e8rGJomHz0clm6aHdOWp0EvpRP368uVsUvJ"

    # Public PostHog host
    HOST = "https://eu.i.posthog.com"

    def __init__(
        self,
        max_queue_size: int = 10,
        flush_at: int = 5,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the Telemetry service.

        Args:
            max_queue_size: The maximum number of events to queue before flushing.
            flush_at: The number of events to flush after.
            api_key: The API key to use for the PostHog client.
        """
        self._posthog_client: Optional[Posthog] = None
        self._task_queue = Queue(maxsize=1_000)

        # Start worker thread
        self._worker = threading.Thread(
            target=self._worker_loop, daemon=True, name="TelemetryWorker"
        )
        self._worker.start()

        # Register shutdown handler
        # These are useful for shutting down the PostHog client and
        # flushing the queued events - non-blocking.
        atexit.register(self._shutdown)

        # Queue initialization task
        self._enqueue(self.__init, max_queue_size, flush_at, api_key)

    def __init(self, max_queue_size: int, flush_at: int, api_key: Optional[str]):
        """Initialize PostHog client based on whether telemetry is enabled
        or not. Telemetry may be explicitly disabled by the user, but also
        remotely by the server, based on the state of the telemetry config.

        Args:
            max_queue_size: The maximum number of events to queue before flushing.
            flush_at: The number of events to flush after.
            api_key: The API key to use for the PostHog client.
        """
        try:
            # Quick env check first (non-blocking)
            exec_context = get_execution_context()
            default_disable = "1" if exec_context.ci else "0"
            if os.getenv("TABPFN_DISABLE_TELEMETRY", default_disable).lower() in (
                "1",
                "true",
            ):
                logger.debug("Telemetry disabled by environment variable")
                return

            # Check server config (blocking, but in worker thread)
            try:
                config = download_config()
                if not config.get("enabled", True):
                    logger.debug("Telemetry disabled by server config")
                    return
            except Exception as e:
                logger.debug(f"Failed to load config, disabling telemetry: {e}")
                return

            # Initialize PostHog
            self._posthog_client = Posthog(
                project_api_key=api_key or self.PROJECT_API_KEY,
                host=self.HOST,
                disable_geoip=True,
                enable_exception_autocapture=False,
                max_queue_size=max_queue_size,
                flush_at=flush_at,
            )
        except Exception as e:
            logger.debug(f"Failed to initialize telemetry: {e}")

    def capture(
        self,
        event: BaseTelemetryEvent,
        *,
        distinct_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Capture an event. This is a non-blocking operation.

        Args:
            event: The telemetry event to capture.
            distinct_id: The distinct ID to use for the event.
            properties: The properties to use for the event.
            timestamp: The timestamp to use for the event.
        """
        self._enqueue(self._do_capture, event, distinct_id, properties, timestamp)

    def _do_capture(
        self,
        event: BaseTelemetryEvent,
        distinct_id: Optional[str],
        properties: Optional[Dict[str, Any]],
        timestamp: Optional[datetime],
    ):
        if not self._posthog_client:
            return

        try:
            # Enrich the event with additional properties
            # These are properties that are not set at initialization time,
            # because they may be expensive to compute.
            event.enrich()

            # Merge the event properties with the additional properties
            merged_props = {**event.properties, **(properties or {})}

            capture_args = {
                "event": event.name,
                "properties": merged_props,
                "timestamp": timestamp or event.timestamp,
            }

            if distinct_id:
                capture_args["distinct_id"] = distinct_id

            self._posthog_client.capture(**capture_args)
            logger.debug(f"Captured event: {event.name}")
        except Exception as e:
            logger.debug(f"Failed to capture event: {e}")

    def flush(self) -> None:
        """Flush events. This is a non-blocking operation."""
        self._enqueue(self._do_flush)

    def _do_flush(self):
        """Actually flush (runs in worker thread)."""
        if self._posthog_client:
            try:
                self._posthog_client.flush()
                logger.debug("Flushed telemetry queue")
            except Exception as e:
                logger.debug(f"Failed to flush: {e}")

    def _enqueue(self, func, *args, **kwargs):
        """Add a task to the queue.

        Args:
            func: The function to execute.
            args: The arguments to pass to the function.
            kwargs: The keyword arguments to pass to the function.
        """
        try:
            self._task_queue.put((func, args, kwargs), block=False)
        except queue.Full:
            return

    def _worker_loop(self):
        """Process tasks from the queue."""
        while True:
            task = self._task_queue.get(block=True)
            if task is None:  # Shutdown signal
                break
            try:
                func, args, kwargs = task
                func(*args, **kwargs)
            except Exception as e:
                logger.debug(f"Telemetry task error: {e}")

        # Final flush and shutdown in worker
        if self._posthog_client:
            try:
                self._posthog_client.shutdown()
            except Exception as e:
                logger.debug(f"Shutdown error: {e}")

    def _shutdown(self):
        """Shutdown handler.

        We register a shutdown handler to ensure gracefully shutting down
        the PostHog client and flushing the queued events.
        """
        self._task_queue.put(None)

        # Wait for worker to finish
        if self._worker.is_alive():
            self._worker.join(timeout=5.0)


def capture_event(
    event: BaseTelemetryEvent, *, max_queue_size: int = 10, flush_at: int = 10
) -> None:
    """Capture a telemetry event.

    Args:
        event: The telemetry event to capture.
        max_queue_size: The maximum number of events to queue before flushing.
        flush_at: The number of events to flush after.
    """
    client = ProductTelemetry(max_queue_size, flush_at)
    client.capture(event)
