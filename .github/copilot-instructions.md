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

## Libraries and Frameworks

- **Backend:** Python 3.13, Django, uv (dependency management), flit (packaging)
- **Frontend:** React, MobX, Yarn (dependency management), Vite (build tool)
- **Testing:** Pytest, Coverage.py, Playwright (integration), Jest (JS unit tests)

The HAWC application is a mixture of Django HTML templates for some pages, and then a Django API plus JavaScript application for serving more dynamic pages. We use simpler HTML templates where possible, and only use JavaScript for more complex interactions. We are increasingly using htmx for more complex django HTML template based interactions.

## Code Standards (Linting/Formatting)

- **Python:**
   - Lint with `poe lint-py` (ruff)
   - HTML linting with `poe lint-html`
- **JavaScript:**
   - Lint with `yarn --cwd ./frontend run lint` (uses biome.js)

## Testing (Python)

Run backend tests: `pytest --record-mode=none`

## Testing (JavaScript)

Run frontend tests: `yarn --cwd ./frontend run test`

## Testing (Integration)

Integration tests require both backend and frontend to be available.  The integration tests are run using Python and the playwright integration to check browser interactions.

Python integration tests which require the JavaScript code to be compiled. To compile:

- **Preferred:** Start the frontend in a separate process: `yarn --cwd ./frontend run`
- **Alternative:** Build the frontend before running integration tests: `yarn --cwd ./frontend build`

The preferred approach allows for faster development cycles since it doesn't require a compile step.

To run integration tests: `py.test -sv tests/integration/`

## References:

* See GitHub actions in `.github/workflows`
* See documentation in `docs/`
* For editing [this file](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions?tool=vscode):

