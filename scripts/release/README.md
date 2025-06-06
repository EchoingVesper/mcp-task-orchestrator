# PyPI Release Process

This directory contains automated scripts for releasing the mcp-task-orchestrator package to PyPI.

## Initial Setup (One-time)

1. **Create PyPI Account**
   - Go to https://pypi.org/account/register/
   - Enable 2FA (required)
   - Create API token: https://pypi.org/manage/account/token/

2. **Configure Environment**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your PyPI token
   # Token should start with "pypi-"
   ```

3. **Install Dependencies**
   ```bash
   pip install python-dotenv twine wheel setuptools
   ```

## Release Commands

### Full Release Process
Handles version bumping, testing, building, and uploading:

```bash
# Bump patch version (1.5.1 -> 1.5.2)
python scripts/release/release.py --patch

# Bump minor version (1.5.2 -> 1.6.0)
python scripts/release/release.py --minor

# Bump major version (1.6.0 -> 2.0.0)
python scripts/release/release.py --major

# Test release (uploads to TestPyPI)
python scripts/release/release.py --patch --test
```

### Upload Only
For uploading already-built packages:

```bash
# Upload to PyPI
python scripts/release/upload.py

# Upload to TestPyPI
python scripts/release/upload.py --test
```

## What the Release Script Does

1. **Version Update**: Updates version in setup.py, __init__.py, README.md
2. **Testing**: Runs test suite (can be disabled in .env)
3. **Building**: Creates source and wheel distributions
4. **Validation**: Checks packages with twine
5. **Upload**: Securely uploads to PyPI using your token
6. **Git Tag**: Creates version tag (can be disabled in .env)
7. **Cleanup**: Removes build artifacts (configurable)

## Environment Variables

Configure behavior in `.env`:

- `PYPI_API_TOKEN`: Your PyPI upload token (required)
- `PYPI_TEST_TOKEN`: TestPyPI token (optional)
- `AUTO_GIT_TAG`: Create git tags automatically (default: true)
- `RUN_TESTS_BEFORE_UPLOAD`: Run tests before release (default: true)
- `CLEAN_BUILD_ARTIFACTS`: Clean dist/ after upload (default: true)

## Security Notes

- Never commit `.env` file (it's in .gitignore)
- Tokens are masked in output
- Use environment variables only, never hardcode tokens
- Consider using GitHub Actions for CI/CD releases

## Troubleshooting

- **"Token not found"**: Ensure .env file exists with PYPI_API_TOKEN
- **"Tests failed"**: Fix failing tests or set RUN_TESTS_BEFORE_UPLOAD=false
- **"Upload failed"**: Check token permissions and network connection
- **"Version conflict"**: Package with this version already exists on PyPI

## Manual Process (if scripts fail)

```bash
# Build packages
python setup.py sdist bdist_wheel

# Check packages
twine check dist/*

# Upload with token
twine upload -u __token__ -p <your-token> dist/*
```