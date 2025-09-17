#!/usr/bin/env python3
"""Example usage of TabPFN telemetry events."""

import numpy as np

from tabpfn_common_utils.telemetry import (
    PingEvent,
    FitEvent,
    PredictEvent,
    capture_event,
)


def main():
    """Example of sending various telemetry events."""
    print("🔗 Sending TabPFN telemetry events...")

    # 1. Send a ping event (user activity tracking)
    print("\n1. Sending ping event...")
    ping_event = PingEvent()
    capture_event(ping_event)
    print(f"   Sent ping event: {ping_event.name}")

    # 2. Send a fit event (model training)
    print("\n3. Sending fit event...")
    fit_event = FitEvent(
        task="classification",
        num_rows=120,
        num_columns=4,
        duration_ms=1250
    )
    capture_event(fit_event)
    print(f"   Sent fit event: {fit_event.name}")

    # 3. Send a predict event (model prediction)
    print("\n4. Sending predict event...")
    predict_event = PredictEvent(
        task="classification",
        num_rows=30,
        num_columns=4,
        duration_ms=180
    )
    capture_event(predict_event)
    print(f"   Sent predict event: {predict_event.name}")

    # 5. Example with real data shapes
    print("\n5. Sending events with real data...")
    
    # Create sample data
    X_train = np.random.rand(100, 5)
    y_train = np.random.randint(0, 3, 100)
    X_test = np.random.rand(25, 5)
    
    # Fit event with actual training data
    fit_event_real = FitEvent(
        task="classification",
        num_rows=X_train.shape[0],
        num_columns=X_train.shape[1],
        duration_ms=2100
    )
    capture_event(fit_event_real)
    print(f"   Sent fit event with training data: {X_train.shape}")

    # Predict event with test data
    predict_event_real = PredictEvent(
        task="classification",
        num_rows=X_test.shape[0],
        num_columns=X_test.shape[1],
        duration_ms=350
    )
    capture_event(predict_event_real)
    print(f"   Sent predict event with test data: {X_test.shape}")

    print("\n✅ All telemetry events sent successfully!")
    print("\nNote: Events are sent to PostHog anonymously.")
    print("To disable telemetry, set: TABPFN_DISABLE_TELEMETRY=1")


if __name__ == "__main__":
    main()
