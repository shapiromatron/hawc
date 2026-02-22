# Health Assessment Workspace Collaborative (HAWC)

HAWC is a web-based platform for capturing, analyzing, and sharing data related to human-health assessments of chemicals and environmental exposures. It supports hazard identification and quantitative risk assessment workflows for researchers and regulatory agencies.

## Folder Structure

- `hawc/`: Python Django backend application
- `hawc/client/`: Python client package
- `frontend/`: JavaScript/React frontend application
- `frontend/tests/`: JavaScript/React tets
- `compose/`: Docker Compose files and deployment configuration
- `tests/`: Python backend tests
- `tests/integration/`: Python integration tests which require the JavaScript code to be compiled. This can be done either in a separate process (via `npm run start`; preferred) or built (via `npm run build`).
- `docs/`: documentation for development and overall structure of application

## Getting Started

To set up your development environment from scratch, follow these steps:

1. **Create and activate a virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. **Sync dependencies and set up the database:**
   ```bash
   poe sync-dev
   ```

This will install all Python and JavaScript dependencies and run the initial database migrations.

## Development Environment

Once your environment is set up, you can start the development servers.

- **Run Python backend:** `poe run-py`
- **Run JavaScript frontend:** `poe run-js`

Before running any other commands, ensure your virtual environment is activated:

```bash
source .venv/bin/activate
```

## Libraries and Frameworks

- **Backend:** Python 3.14, Django, uv (dependency management, packaging)
- **Frontend:** React, MobX, Yarn (dependency management), Vite (build tool)
- **Testing:** Pytest, Coverage.py, Playwright (integration), Jest (JS unit tests)

The HAWC application is a mixture of Django HTML templates for some pages, and then a Django API plus JavaScript application for serving more dynamic pages. We use simpler HTML templates where possible, and only use JavaScript for more complex interactions. We are increasingly using htmx for more complex django HTML template based interactions.

## Code Standards (Linting/Formatting)

- **Python:**
   - Lint with `poe lint-py` (ruff)
   - HTML linting with `poe lint-html`
- **JavaScript:**
   - Lint with `poe lint-js` (uses biome.js)

## Testing (Python)

Run backend tests: `poe test`

## Testing (JavaScript)

Run frontend tests: `poe test-js`

## Testing (Integration)

Integration tests require both backend and frontend to be available.  The integration tests are run using Python and the playwright integration to check browser interactions.

Python integration tests which require the JavaScript code to be compiled. To compile:

- **Preferred:** Start the frontend in a separate process: `poe run-js`
- **Alternative:** Build the frontend before running integration tests: `yarn --cwd ./frontend build`

The preferred approach allows for faster development cycles since it doesn't require a compile step.

To run integration tests: `py.test -sv tests/integration/`

## Agent Development Workflow

When making changes to the codebase, please follow the appropriate workflow below.

### Python (Backend)

1. Make required code changes in the `hawc/` directory.
2. Run `poe lint-py` to ensure code is properly formatted.
3. Run `poe test` to run backend unit tests.

### JavaScript (Frontend)

1. Make required code changes in the `frontend/` directory.
2. Run `poe lint-js` to ensure code is properly formatted.
3. Run `poe test-js` to run frontend unit tests.

### Integration Testing

For changes that may impact both the frontend and backend, run integration tests.

1. Ensure the frontend development server is running with `poe run-js`.
2. In a separate terminal, run `py.test -sv tests/integration/`.

## References:

* See GitHub actions in `.github/workflows`
* See documentation in `docs/`
* For editing [this file](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions?tool=vscode):

