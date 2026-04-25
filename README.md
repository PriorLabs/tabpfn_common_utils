# TabPFN Common Utilities

Shared Python utilities used across the [TabPFN](https://github.com/priorlabs/tabpfn) ecosystem (the tabular foundation model).

## Features

### Data Processing Utilities
- **Regression Results**: Handling of prediction outputs with mean, median, mode, and quantiles
- **Data Serialization**: Convert between pandas DataFrames, NumPy arrays, and CSV formats
- **Dataset Management**: Load and preprocess standard ML datasets with proper train/test splits
- **Preprocessing Configuration**: Options for data transformation strategies

### Cost Estimation
- **Resource Planning**: Estimation of computational costs and duration for TabPFN predictions
- **Cloud Pricing**: Useful for resource planning in cloud-based TabPFN services
- **Task-Specific Calculations**: Different cost models for classification vs regression tasks

### Telemetry (optional, opt-out)
- **Anonymous & Aggregated**: No personal information or sensitive data is collected or transmitted
- **Configurable**: Can be disabled via environment variable
- **Usage Patterns**: Aggregate signals used to improve TabPFN

## Installation

```bash
pip install tabpfn-common-utils
```

Or with uv:
```bash
uv add tabpfn-common-utils
```

## Quick Start

### Regression Results

```python
from tabpfn_common_utils.regression_pred_result import RegressionPredictResult

# Handle regression prediction results
result = RegressionPredictResult({
    "mean": [1.2, 2.3, 3.4],
    "median": [1.1, 2.2, 3.3],
    "mode": [1.0, 2.0, 3.0],
    "quantile_0.25": [0.9, 1.9, 2.9],
    "quantile_0.75": [1.5, 2.5, 3.5]
})

# Convert to basic representation for serialization
basic_repr = RegressionPredictResult.to_basic_representation(result)
```

### Data Utilities

```python
from tabpfn_common_utils.utils import get_example_dataset, serialize_to_csv_formatted_bytes
import pandas as pd

# Load example dataset
X_train, X_test, y_train, y_test = get_example_dataset("iris")

# Serialize data to CSV bytes
csv_bytes = serialize_to_csv_formatted_bytes(X_train)
```

### Telemetry

```python
from tabpfn_common_utils.telemetry import ProductTelemetry

# Initialize telemetry service (anonymous; opt-out)
telemetry = ProductTelemetry()

# Track usage events
telemetry.capture(...)

# Disable via environment variable
export TABPFN_DISABLE_TELEMETRY=1
```

## Telemetry notes

- Anonymous and aggregated only — no user identification or tracking
- Disabled by setting `TABPFN_DISABLE_TELEMETRY=1`
- Open source — see `src/tabpfn_common_utils/telemetry/` for what is sent

## Development

### Setup

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run tests
uv run pytest

# Type checking
uv run pyright

# Code formatting
uv run ruff check --fix
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add <package_name>

# Add development dependency
uv add --group dev <package_name>
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure all code passes type checking and formatting requirements.

## Links

- [TabPFN Main Repository](https://github.com/priorlabs/tabpfn)
- [Documentation](https://github.com/priorlabs/tabpfn_common_utils)
- [Issues](https://github.com/priorlabs/tabpfn_common_utils/issues)