# Health Assessment Workspace Collaborative (HAWC)

HAWC is a web-based platform for capturing, analyzing, and sharing data related to human-health assessments of chemicals and environmental exposures. It supports hazard identification and quantitative risk assessment workflows for researchers and regulatory agencies.

## Project Structure

- `hawc/`: Django backend (Python 3.13, Django 5.2+, DRF, PostgreSQL 16+, Redis, Celery)
- `hawc/client/`: Python client package for HAWC API
- `frontend/`: React frontend (React 18+, MobX, Vite, Vitest, D3.js, Plotly.js)
- `tests/`: Backend tests (pytest) and integration tests (Playwright)
- `docs/`: Documentation (MkDocs)

## Technology Stack

**Backend:** Python 3.13, Django 5.2+, DRF, PostgreSQL 16+, Redis, Celery, uv, pytest  
**Frontend:** React 18+, MobX, Vite, Yarn, Vitest, D3.js, Plotly.js  
**Architecture:** Hybrid - Django templates for simple pages, React for complex interactions, htmx for enhanced server-side interactions

## Environment Setup

### Prerequisites
Git, Python 3.13, Node.js v24, Yarn < 2, PostgreSQL >= 16, Redis

### Initial Setup

```bash
# Clone and setup environment
git clone https://github.com/shapiromatron/hawc.git
cd hawc
uv venv --python=3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev,docs]"
uv pip install -e client
yarn --cwd ./frontend install

# Setup database
createuser --superuser --no-password hawc
createdb -E UTF-8 -U hawc hawc

# Sync database and load fixtures
poe sync-dev
```

### Running

```bash
poe run-py    # Python backend
poe run-js    # JavaScript frontend (dev mode)
```

## Code Standards

### Python
- **Format/Lint:** `poe format-py` / `poe lint-py` (uses ruff)
- **Style:** PEP 8, type hints where appropriate

### JavaScript  
- **Format/Lint:** `poe format-js` / `poe lint-js` (uses Biome.js)
- **Style:** 4-space indent, double quotes, semicolons, 100 char line width
- **React:** Functional components with hooks, MobX for global state

### HTML (Django Templates)
- **Format/Lint:** `poe format-html` / `poe lint-html` (uses djhtml)
- **Style:** 2-space indentation

### Pre-commit Hooks
Install: `pre-commit install` (runs djhtml and ruff automatically)

## Testing

### Python Tests
```bash
poe test              # Run all tests
poe coverage          # Run with coverage report
poe test-integration  # Run integration tests (installs Playwright)
```

**Note:** Tests use `--record-mode=none` for VCR (external API test isolation).

### JavaScript Tests
```bash
poe test-js           # Run all frontend tests
```

## Common Tasks

```bash
# Code Quality
poe format              # Format all code (Python, JS, HTML)
poe lint                # Lint all code

# Development
poe sync-dev            # Sync database and load fixtures
poe run-py              # Run Python dev server
poe run-js              # Run JavaScript dev server

# Package Management
uv pip install <package>              # Add Python dependency (then add to pyproject.toml)
yarn --cwd ./frontend add <package>   # Add JavaScript dependency

# Database
python manage.py makemigrations       # Create migration
python manage.py migrate              # Apply migrations
```

## Important Rules

### DO
- ✅ Run `poe format` before committing
- ✅ Write tests for new features and bug fixes
- ✅ Use `poe` tasks for common operations (run `poe` to see all tasks)
- ✅ Follow existing code patterns in the same module
- ✅ Add migrations when modifying Django models

### DO NOT
- ❌ Commit generated files (`frontend/dist/`, `*.pyc`, `__pycache__/`)
- ❌ Modify auto-generated parser files in `frontend/shared/parsers/`
- ❌ Hard-code secrets or API keys (use environment variables)
- ❌ Use npm commands (use yarn instead)
- ❌ Remove or modify existing tests unless fixing bugs

## Security
- Secrets managed via environment variables (see `hawc/main/settings/`)
- Use Django's built-in security features (CSRF, XSS protection, SQL injection prevention)
- Use `nh3` for HTML sanitization

## Common Pitfalls
1. **Integration tests fail:** Frontend dev server must be running (`poe run-js`)
2. **Linter failures:** Run `poe format` before committing
3. **Migration conflicts:** Sync with main branch before creating new migrations

## Additional Resources
- **Repository:** https://github.com/shapiromatron/hawc
- **Documentation:** https://hawc.readthedocs.io
- **Development guide:** `docs/docs/development.md`
- **Copilot setup:** `.github/workflows/copilot-setup-steps.yml`

