# Testing Quick Start

Quick reference for running tests in this project.

## Install Test Dependencies

```bash
uv pip install -e ".[dev]"
```

## Run Tests

```bash
# All tests
pytest

# With output
pytest -v

# With coverage
pytest --cov=src --cov-report=term

# Specific file
pytest tests/test_llm_parser.py

# Specific test
pytest tests/test_llm_parser.py::TestLLMParser::test_fallback_parser_basic

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_*.py                # Unit tests
└── integration/
    └── test_*.py            # Integration tests
```

## Writing a New Test

```python
import pytest

class TestMyFeature:
    @pytest.fixture
    def my_fixture(self):
        return SomeObject()
    
    @pytest.mark.unit
    def test_something(self, my_fixture):
        result = my_fixture.do_something()
        assert result == expected
```

## GitHub Actions

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests
- Manual workflow dispatch

View results: Repository → Actions tab

## Full Documentation

See **[docs/TESTING.md](docs/TESTING.md)** for complete testing guide.
