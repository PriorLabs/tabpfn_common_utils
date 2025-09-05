# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2024-12-19

### Changed
- **NumPy Compatibility**: Updated `scikit-learn` dependency to match `tabpfn` requirements
- **Development Dependencies**: Added pytest as an explicit dev dependency for consistent testing across environments

## [0.1.1] - 2024-12-19

### Added
- **Privacy-First Telemetry System**: New GDPR-compliant telemetry system using PostHog for anonymous, aggregated usage data collection
- **Telemetry Events**: Implemented specific events (`fit_called`, `dataset`, `predict_called`, `PingEvent`) for TabPFN usage tracking
- **ProductTelemetry Class**: Singleton service for capturing and pushing events with opt-out via `TABPFN_DISABLE_TELEMETRY` environment variable
- **Python 3.13 Support**: Added Python 3.13 classifier and CI testing
- **Comprehensive Documentation**: Complete README overhaul with installation guides, quick start examples, and privacy compliance details

### Changed
- **Package Metadata**: Updated `pyproject.toml` with authors, maintainers, keywords, and extended Python version support
- **Dependencies**: Added `posthog~=6.7` as runtime dependency
- **Type Hints**: Enhanced type safety across utility modules with explicit typing imports
- **Version Management**: Dynamic package version retrieval using `importlib.metadata`

### Fixed
- **Type Annotations**: Corrected return type annotations in `get_example_dataset()` function
- **DataFrame Compatibility**: Improved pandas DataFrame column initialization for better type safety
- **Code Quality**: Enhanced type hinting and removed outdated modules

### Removed
- **load_test.py**: Removed outdated module (moved to API repository)
- **Outdated Configuration**: Cleaned up redundant pyright and ruff configuration sections

---

## [0.1.0] - Initial Release

### Added
- Core utility functions for TabPFN
- Regression prediction result handling
- Data processing and serialization utilities
- Basic project structure and testing framework