# Contributing Guide

Thank you for your interest in contributing to the Discord T-Shirt Bot! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- UV package manager
- Git
- A Discord account for testing
- API keys for development (Discord, Google Gemini, Printful)

### Setting Up Development Environment

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/discord-tshirt-bot.git
   cd discord-tshirt-bot
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your test API keys
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-image-generation` - For new features
- `fix/parser-error` - For bug fixes
- `docs/update-readme` - For documentation
- `refactor/improve-design` - For refactoring

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Add docstrings to new functions/classes
- Include type hints
- Update tests for your changes

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_llm_parser.py

# Run with coverage
pytest --cov=src
```

### 4. Format Code

```bash
# Format with black
black src/ tests/

# Check with ruff
ruff check src/ tests/
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add AI image generation feature

- Integrate DALL-E API for image generation
- Add configuration for image styles
- Update design generator to include images
- Add tests for image generation"
```

Commit message format:
- First line: Short summary (50 chars or less)
- Blank line
- Detailed description with bullet points

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title describing the change
- Detailed description of what and why
- Reference any related issues
- Screenshots/examples if applicable

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes

Example:

```python
async def process_request(
    message: str,
    user_id: str,
) -> TShirtResult:
    """
    Process a t-shirt request from a user.

    Args:
        message: The user's message
        user_id: Discord user ID

    Returns:
        TShirtResult with success status and product URL

    Raises:
        ValueError: If message is invalid
    """
    # Implementation
```

### Logging

- Use the `logging` module
- Log at appropriate levels:
  - `DEBUG`: Detailed debugging information
  - `INFO`: General information
  - `WARNING`: Warning messages
  - `ERROR`: Error messages

Example:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Processing request for user {user_id}")
logger.error(f"Failed to create product: {error}", exc_info=True)
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors with context
- Don't expose sensitive information in error messages

Example:

```python
try:
    result = await api_call()
except aiohttp.ClientError as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise ProcessingError("Failed to communicate with service") from e
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Test both success and failure cases
- Use descriptive test names
- Use fixtures for common setup

Example:

```python
import pytest
from src.services.llm_parser import LLMParser

@pytest.fixture
def parser():
    return LLMParser()

@pytest.mark.asyncio
async def test_parse_basic_message(parser):
    """Test parsing a basic t-shirt request."""
    request = await parser.parse_message("I want a shirt that says 'Test'")
    
    assert request is not None
    assert "Test" in request.phrase
    assert request.style in ["modern", "bold", "script"]
```

### Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test interactions between components
- **End-to-end tests**: Test the full workflow (mark as `slow`)

### Running Tests

```bash
# All tests
pytest

# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# With coverage
pytest --cov=src --cov-report=html
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def create_design(text: str, style: str) -> Image:
    """
    Create a t-shirt design image.

    Args:
        text: The text to display on the shirt
        style: The style to apply (modern, retro, etc.)

    Returns:
        PIL Image object with the design

    Raises:
        ValueError: If text is empty or style is invalid
    """
```

### README and Docs

- Update relevant documentation when making changes
- Add examples for new features
- Keep documentation clear and concise
- Include code examples where helpful

## Areas for Contribution

### High Priority

- [ ] Add AI image generation (DALL-E, Stable Diffusion)
- [ ] Implement caching for repeated requests
- [ ] Add support for multiple product types
- [ ] Improve error handling and recovery

### Medium Priority

- [ ] Add more text styles and fonts
- [ ] Implement user preference storage
- [ ] Add order tracking via webhooks
- [ ] Create web dashboard for monitoring

### Low Priority / Nice to Have

- [ ] Multi-language support
- [ ] A/B testing framework
- [ ] Design preview before ordering
- [ ] Custom font upload

## Getting Help

- **Discord**: Join our Discord server (link in README)
- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers (see README)

## Code Review Process

1. All PRs require at least one approval
2. All tests must pass
3. Code must follow style guidelines
4. Documentation must be updated
5. No merge conflicts

Reviewers will check for:
- Code quality and style
- Test coverage
- Documentation
- Security concerns
- Performance implications

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release tag
4. Build and publish Docker image
5. Deploy to production

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

## Questions?

Feel free to ask questions by:
- Creating an issue with the `question` label
- Posting in GitHub Discussions
- Reaching out to maintainers

Thank you for contributing! 🎉
