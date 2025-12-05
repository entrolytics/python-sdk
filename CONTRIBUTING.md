# Contributing to entrolytics

Thank you for your interest in contributing to entrolytics!

This package is part of the [Entrolytics](https://github.com/entrolytics/entrolytics-system) monorepo.

## Getting Started

Please read the main [Contributing Guide](../CONTRIBUTING.md) in the root of this repository for detailed information about:

- Setting up your development environment
- Code style guidelines
- Commit message conventions
- Pull request process

## Package-Specific Information

### Directory Structure

```
entro-python/
├── src/          # Source code
├── dist/         # Built output (generated)
├── package.json  # Package manifest
└── README.md     # Package documentation
```

### Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Type check
mypy src
```

## Questions?

If you have questions, please open an issue in the [main repository](https://github.com/entrolytics/entrolytics-system/issues).
