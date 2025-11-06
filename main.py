from src.tabpfn_common_utils.telemetry.core.events import FitEvent, PredictEvent
from src.tabpfn_common_utils.telemetry.core.service import capture_event

def test_capture_fit_event():
    event = FitEvent(
        task="classification",
        num_rows=100,
        num_columns=10,
        duration_ms=500
    )
    capture_event(event)
    print(f"Captured FitEvent: {event}")

def test_capture_predict_event():
    event = PredictEvent(
        task="regression",
        num_rows=50,
        num_columns=5,
        duration_ms=120
    )
    capture_event(event)
    print(f"Captured PredictEvent: {event}")

if __name__ == "__main__":
    test_capture_fit_event()
    test_capture_predict_event()
