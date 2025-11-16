# Testing Guide

This guide covers how to run tests, write new tests, and understand the test suite structure.

## Test Suite Overview

The project uses **pytest** for testing with the following structure:

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_config.py                 # Configuration tests
├── test_llm_parser.py            # LLM parser unit tests
├── test_design_generator.py      # Design generator unit tests
├── test_printful_client.py       # Printful client unit tests
├── test_orchestrator.py          # Orchestrator unit tests
├── test_discord_bot.py           # Discord bot unit tests
└── integration/
    ├── __init__.py
    └── test_full_workflow.py     # End-to-end integration tests
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
uv pip install -r requirements-dev.txt
```

Or install just the runtime dependencies and tests:

```bash
uv pip install -r requirements.txt
uv pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_llm_parser.py
```

### Run Specific Test

```bash
pytest tests/test_llm_parser.py::TestLLMParser::test_fallback_parser_basic
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View HTML report
open htmlcov/index.html
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
uv pip install pytest-xdist

# Run with 4 workers
pytest -n 4
```

## Test Categories

### Unit Tests

Unit tests test individual components in isolation with mocked dependencies.

**Location**: `tests/test_*.py`

**Examples**:
- `test_llm_parser.py` - Tests LLM parser logic
- `test_design_generator.py` - Tests image generation
- `test_printful_client.py` - Tests API client

**Run unit tests**:
```bash
pytest -m unit
```

### Integration Tests

Integration tests verify that components work together correctly.

**Location**: `tests/integration/`

**Examples**:
- `test_full_workflow.py` - Tests complete request workflow

**Run integration tests**:
```bash
pytest -m integration
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from src.services.example import ExampleService

class TestExampleService:
    """Test suite for ExampleService."""
    
    @pytest.fixture
    def service(self):
        """Create a service instance."""
        return ExampleService()
    
    def test_something(self, service):
        """Test a specific functionality."""
        result = service.do_something()
        assert result == expected_value
```

### Async Tests

For async functions, use `pytest.mark.asyncio`:

```python
import pytest

class TestAsyncFunction:
    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test an async function."""
        result = await some_async_function()
        assert result is not None
```

### Mocking External Dependencies

Use `unittest.mock` to mock external services:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    """Test with mocked API call."""
    with patch('src.services.api.make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"status": "success"}
        
        result = await service.process()
        
        assert result["status"] == "success"
        mock_request.assert_called_once()
```

### Using Fixtures

Fixtures provide reusable test data and setup:

```python
import pytest

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "name": "Test",
        "value": 123
    }

def test_with_fixture(sample_data):
    """Test using fixture data."""
    assert sample_data["name"] == "Test"
```

### Parametrized Tests

Test multiple scenarios with one test:

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("test", "TEST"),
])
def test_uppercase(input, expected):
    """Test uppercase conversion with multiple inputs."""
    assert input.upper() == expected
```

## Test Markers

### Available Markers

Defined in `pytest.ini`:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_fast_unit():
    """Fast unit test."""
    assert True

@pytest.mark.integration
@pytest.mark.slow
async def test_slow_integration():
    """Slow integration test."""
    # Complex test that takes time
    pass
```

### Running by Marker

```bash
# Run only unit tests
pytest -m unit

# Run integration but not slow tests
pytest -m "integration and not slow"
```

## Code Coverage

### Measuring Coverage

```bash
# Run tests with coverage
pytest --cov=src

# Generate detailed report
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html
```

### Coverage Goals

- **Minimum**: 70% overall coverage
- **Target**: 80%+ overall coverage
- **Critical paths**: 90%+ coverage (orchestrator, bot)

### Viewing Coverage Reports

HTML reports are generated in `htmlcov/`:

```bash
# Generate and open
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

### Google Cloud Build

The project uses Google Cloud Build for automated building and deployment (see `cloudbuild.yaml` in the project root).

### Running Checks Locally

Run the same checks locally before pushing:

```bash
# Format check
black --check src/ tests/

# Lint
ruff check src/ tests/

# Security scan
bandit -r src/
safety check

# Tests
pytest --cov=src
```

## Troubleshooting Tests

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Install package in development mode:
```bash
uv pip install -e .
```

#### 2. Async Test Failures

**Problem**: `RuntimeError: Event loop is closed`

**Solution**: Ensure `pytest-asyncio` is installed and configured:
```bash
uv pip install pytest-asyncio
```

Add to `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
```

#### 3. Environment Variables

**Problem**: Tests fail due to missing environment variables

**Solution**: Tests use default values set in `conftest.py`. For real API tests, set:
```bash
export DISCORD_BOT_TOKEN="your_token"
export GOOGLE_API_KEY="your_key"
export PRINTFUL_API_KEY="your_key"
```

#### 4. File Permissions

**Problem**: Permission errors when creating test files

**Solution**: Ensure test directories are writable:
```bash
chmod -R u+w tests/
mkdir -p generated_images
chmod u+w generated_images
```

### Debugging Tests

#### Use pytest's debugging features:

```bash
# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Verbose output
pytest -vv
```

#### Use logging in tests:

```python
import logging

def test_with_logging(caplog):
    """Test with log capture."""
    caplog.set_level(logging.INFO)
    
    # Your test code
    
    assert "Expected log message" in caplog.text
```

## Best Practices

### DO's

✅ **Write tests first** (TDD approach)
✅ **Test edge cases** and error conditions
✅ **Use descriptive test names** that explain what is being tested
✅ **Keep tests independent** - each test should run in isolation
✅ **Mock external services** to avoid flaky tests
✅ **Use fixtures** for common setup
✅ **Test both success and failure** paths
✅ **Aim for fast tests** - slow tests discourage running them

### DON'Ts

❌ **Don't test implementation details** - test behavior
❌ **Don't use real API keys** in tests
❌ **Don't make real API calls** in unit tests
❌ **Don't ignore failing tests** - fix them or remove them
❌ **Don't write tests that depend on execution order**
❌ **Don't leave commented-out test code**
❌ **Don't test framework/library code** - trust it works

## Test Coverage by Component

### Current Coverage Goals

| Component | Target | Critical? |
|-----------|--------|-----------|
| `config.py` | 90% | ✅ |
| `llm_parser.py` | 85% | ✅ |
| `design_generator.py` | 80% | ✅ |
| `printful_client.py` | 90% | ✅ |
| `orchestrator.py` | 95% | ✅ |
| `discord_bot.py` | 90% | ✅ |

## Adding New Tests

### Checklist for New Features

When adding a new feature:

1. ✅ Write unit tests for new functions/classes
2. ✅ Add integration tests if multiple components interact
3. ✅ Update `conftest.py` if new fixtures are needed
4. ✅ Add appropriate markers (`@pytest.mark.unit`, etc.)
5. ✅ Ensure coverage doesn't decrease
6. ✅ Update this documentation if needed

### Example: Adding Tests for New Feature

1. **Create test file**:
   ```bash
   touch tests/test_new_feature.py
   ```

2. **Write tests**:
   ```python
   import pytest
   from src.services.new_feature import NewFeature
   
   class TestNewFeature:
       @pytest.fixture
       def feature(self):
           return NewFeature()
       
       @pytest.mark.unit
       def test_basic_functionality(self, feature):
           result = feature.do_something()
           assert result is not None
   ```

3. **Run tests**:
   ```bash
   pytest tests/test_new_feature.py -v
   ```

4. **Check coverage**:
   ```bash
   pytest tests/test_new_feature.py --cov=src.services.new_feature
   ```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

## Questions?

- Check existing tests for examples
- Review this guide
- Ask in GitHub Discussions
- Open an issue with the `testing` label
