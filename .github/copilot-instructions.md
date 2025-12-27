# Health Assessment Workspace Collaborative (HAWC)

HAWC is a web-based platform for capturing, analyzing, and sharing data related to human-health assessments of chemicals and environmental exposures. It supports hazard identification and quantitative risk assessment workflows for researchers and regulatory agencies.

## Project Structure

- `hawc/`: Python Django backend application
  - `hawc/apps/`: Django apps organized by feature (animal, assessment, epi, lit, etc.)
  - `hawc/main/`: Core Django configuration and settings
  - `hawc/services/`: Backend services and utilities
  - `hawc/templates/`: Django HTML templates
  - `hawc/static/`: Static files served by Django
- `hawc/client/`: Python client package for HAWC API
- `frontend/`: JavaScript/React frontend application
  - `frontend/tests/`: JavaScript/React tests (using Vitest)
  - `frontend/shared/`: Shared JavaScript utilities and components
- `compose/`: Docker Compose files and deployment configuration
- `tests/`: Python backend tests (pytest)
- `tests/integration/`: Python integration tests using Playwright
- `docs/`: Developer and user documentation (MkDocs)

## Technology Stack

### Backend
- **Python:** 3.13
- **Framework:** Django 5.2+ (web framework), Django REST Framework (API)
- **Database:** PostgreSQL 16+
- **Cache:** Redis
- **Task Queue:** Celery
- **Package Management:** uv (dependency management), flit (packaging)
- **Testing:** pytest, coverage.py, pytest-django
- **Other:** Wagtail (CMS), Pydantic (validation)

### Frontend
- **JavaScript:** ES6+
- **Framework:** React 18+
- **State Management:** MobX
- **Build Tool:** Vite
- **Package Manager:** Yarn (v1)
- **Testing:** Vitest, Testing Library
- **Visualization:** D3.js, Plotly.js
- **Other:** Quill (rich text editor), DataTables

### Architecture Pattern
The application uses a **hybrid architecture**:
- Server-side rendered Django HTML templates for simpler pages
- Client-side React applications for complex interactive features
- Django REST API for data exchange between frontend and backend
- Increasingly using htmx for enhanced server-side interactions without full JavaScript apps

## Environment Setup

### Prerequisites
- Git
- Python 3.13
- Node.js LTS v24
- Yarn < 2
- PostgreSQL >= 16
- Redis (for development)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/shapiromatron/hawc.git
cd hawc

# Create virtual environment
uv venv --python=3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
uv pip install -e ".[dev,docs]"
uv pip install -e client

# Install JavaScript dependencies
yarn --cwd ./frontend install

# Setup database
createuser --superuser --no-password hawc
createdb -E UTF-8 -U hawc hawc

# Sync database and load fixtures
poe sync-dev

# Build frontend (optional, can use dev server instead)
yarn --cwd ./frontend build
```

### Running the Application

**Python backend:**
```bash
poe run-py
# Or: python manage.py runserver
```

**JavaScript frontend (development mode):**
```bash
yarn --cwd ./frontend start
# Or: poe run-js
```

## Code Standards and Style

### Python
- **Formatting:** Use `ruff` for formatting and linting
- **Style:** Follow PEP 8 conventions
- **Imports:** Organize imports automatically with ruff
- **Type Hints:** Use type hints where appropriate (gradually adopting)
- **Docstrings:** Use for public APIs and complex functions
- **Commands:**
  - Format: `poe format-py` or `ruff format . && ruff check . --fix`
  - Lint: `poe lint-py` or `ruff format . --check && ruff check .`

### JavaScript
- **Formatting:** Use Biome.js for formatting and linting
- **Style:** 
  - 4-space indentation
  - Double quotes for strings
  - Semicolons required
  - Line width: 100 characters
- **React:** Use functional components with hooks
- **State Management:** MobX for complex state, React state for local component state
- **Commands:**
  - Format: `yarn --cwd ./frontend run format`
  - Lint: `yarn --cwd ./frontend run lint`

### HTML (Django Templates)
- **Formatting:** Use djhtml for Django template formatting
- **Style:** 2-space indentation
- **Commands:**
  - Format: `poe format-html` or `djhtml --tabwidth 2 hawc/`
  - Lint: `poe lint-html` or `djhtml --tabwidth 2 --check hawc/`

### Pre-commit Hooks
The repository uses pre-commit hooks for automated formatting:
- djhtml for HTML templates
- ruff for Python code
- Install: `pre-commit install`

## Testing

### Python Tests
```bash
# Run all backend tests
pytest --record-mode=none

# Run with coverage
coverage run -m pytest --record-mode=none
coverage report

# Run specific test file or directory
pytest tests/apps/animal/ --record-mode=none

# Run with database isolation
pytest --block-network --allowed-hosts=127.0.0.1,::1
```

**Note:** The `--record-mode=none` flag prevents VCR from recording new cassettes (for testing external API calls).

### JavaScript Tests
```bash
# Run all frontend tests
yarn --cwd ./frontend run test

# Run tests in watch mode (during development)
yarn --cwd ./frontend run test --watch
```

### Integration Tests
Integration tests use Playwright to test browser interactions with both backend and frontend running.

**Setup:**
```bash
# Install Playwright browsers
playwright install --with-deps chromium
```

**Run:**
```bash
# Start frontend dev server in one terminal
yarn --cwd ./frontend start

# Run integration tests in another terminal
INTEGRATION_TESTS=1 py.test -sv tests/integration/

# Or use the poe task (installs browsers automatically)
poe test-integration
```

## Common Tasks

### Package Management
```bash
# Add Python dependency
uv pip install <package>
# Then add to pyproject.toml

# Add JavaScript dependency
yarn --cwd ./frontend add <package>
```

### Database Migrations
```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py reset_db
python manage.py migrate
```

### Code Quality
```bash
# Format all code
poe format  # Runs format-py, format-js, format-html

# Lint all code
poe lint  # Runs lint-py, lint-js, lint-html

# Run all checks (like CI)
poe lint && pytest --record-mode=none && yarn --cwd ./frontend run test
```

## Important Conventions and Rules

### DO
- ✅ Write tests for new features and bug fixes
- ✅ Run linters and formatters before committing
- ✅ Use Django ORM for database queries
- ✅ Use REST API for frontend-backend communication
- ✅ Follow existing code patterns in the same module
- ✅ Use environment variables for configuration (via settings files)
- ✅ Add migrations when modifying Django models
- ✅ Use `poe` tasks for common operations (run `poe` to see available tasks)

### DO NOT
- ❌ Commit without running formatters (`poe format`)
- ❌ Commit generated files (e.g., `frontend/dist/`, `*.pyc`, `__pycache__/`)
- ❌ Modify auto-generated parser files in `frontend/shared/parsers/` (regenerate with `yarn --cwd ./frontend run generate-parsers`)
- ❌ Add console.log statements (use console.warn or console.error only)
- ❌ Hard-code secrets or API keys (use environment variables)
- ❌ Remove or modify existing tests unless fixing bugs
- ❌ Use npm commands (use yarn instead)
- ❌ Break backward compatibility without discussion
- ❌ Commit directly to `main` (use pull requests)

### Security Considerations
- Secrets are managed via environment variables (see `hawc/main/settings/`)
- Never commit real SECRET_KEY values
- Use Django's built-in security features (CSRF, XSS protection, SQL injection prevention)
- Sanitize user input, especially in HTML templates
- Use `nh3` for HTML sanitization when needed
- Review dependencies for known vulnerabilities

## Architecture Patterns

### Backend (Django)
- **Apps:** Feature-based Django apps in `hawc/apps/`
- **Models:** Use Django ORM models with appropriate field types
- **Views:** Mix of function-based and class-based views
- **Serializers:** DRF serializers for API endpoints
- **Permissions:** Django/DRF permission classes for access control
- **Forms:** Django forms with crispy-forms for rendering

### Frontend (React)
- **Components:** Functional components in appropriate app directories
- **State:** MobX stores for global state, React hooks for local state
- **API Calls:** Centralized in service modules
- **Styling:** Mix of Bootstrap 4 and custom CSS
- **Build:** Vite bundles assets; Django serves in production

### Testing Strategy
- **Unit tests:** Test individual functions/components in isolation
- **Integration tests:** Test full user workflows with browser automation
- **API tests:** Test API endpoints using Django test client
- **Fixtures:** Use Django fixtures for test data

## CI/CD

The repository uses GitHub Actions for continuous integration:
- **Workflow file:** `.github/workflows/main.yml`
- **Checks:** Python lint, HTML lint, JavaScript lint, Python tests, JavaScript tests, coverage reporting
- **Requirements:** All checks must pass before merging
- **Copilot Setup:** `.github/workflows/copilot-setup-steps.yml` defines environment setup for GitHub Copilot

## Documentation

- **User docs:** Built with MkDocs, source in `docs/`
- **API docs:** Auto-generated from DRF
- **Code docs:** Docstrings in code
- **Build docs:** `mkdocs serve` (development) or `mkdocs build` (production)

## Common Pitfalls

1. **Integration tests fail:** Ensure frontend dev server is running (`yarn --cwd ./frontend start`)
2. **Database errors:** Check PostgreSQL is running and credentials in environment variables
3. **Import errors:** Ensure virtual environment is activated and dependencies are installed
4. **Frontend not updating:** Clear browser cache or run `yarn --cwd ./frontend build`
5. **Linter failures:** Run `poe format` before committing
6. **Migration conflicts:** Sync with main branch before creating new migrations

## Useful Commands Reference

```bash
# Development
poe run-py              # Run Python dev server
poe run-js              # Run JavaScript dev server
poe sync-dev            # Sync database and load fixtures

# Code Quality
poe format              # Format all code
poe lint                # Lint all code
poe format-py           # Format Python only
poe lint-py             # Lint Python only
poe format-js           # Format JavaScript only
poe lint-js             # Lint JavaScript only
poe format-html         # Format HTML only
poe lint-html           # Lint HTML only

# Testing
poe test                # Run Python tests
poe test-js             # Run JavaScript tests
poe test-integration    # Run integration tests (installs Playwright)

# Database
poe build               # Build package
poe loc                 # Count lines of code
```

## Additional Resources

- **Repository:** https://github.com/shapiromatron/hawc
- **Documentation:** https://hawc.readthedocs.io
- **GitHub Actions:** `.github/workflows/`
- **Development guide:** `docs/docs/development.md`
- **Copilot instructions:** [Editing this file](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- **Copilot setup:** `.github/workflows/copilot-setup-steps.yml`

