# Repository Guidelines

## Project Structure & Module Organization

- `app/main.py` is the async entrypoint wiring the Vertex agent, OAuth flow, and HTTP tooling.
- `app/oauth/` hosts the Starlette `OAuthApp` (login, callback, llm routes); `app/util/` splits shared logic into `config`, `credential`, `envelope`, and `agent` packages.
- `terraform/` contains Google Cloud infrastructure definitions; `cloudrun.yaml` and `Dockerfile` drive service deployment; the `Makefile` aggregates local and ops tasks.

## Build, Test, and Development Commands

- `uv sync` installs dependencies from `pyproject.toml`/`uv.lock`; rerun after editing dev extras.
- `uv run app/main.py` or `make run` starts the local server; pass env vars via `.env`.
- `uv run mypy app` enforces typing; `make build`, `make replace`, and `make stop` wrap container build/publish and Cloud Run lifecycle.

## Coding Style & Naming Conventions

- Follow PEP 8, four-space indentation, and typed signatures; keep module constants upper snake.
- Name packages/modules in `snake_case`, classes `PascalCase`, and async utilities verbs-first (`get_user_profile_tool`).
- Extend shared helpers inside the existing `app/util/<domain>/` subpackages; document non-obvious flows inline.

## Testing Guidelines

- Standardize on `pytest`; install with `uv add --dev pytest pytest-asyncio`, add suites under `tests/` mirroring `app/`.
- Name files `test_<module>.py`, favor async fixtures for Starlette request flows, and mock Google APIs.
- Run coverage locally with `uv run pytest` before pushing; capture OAuth regressions and token encryption paths.

## Commit & Pull Request Guidelines

- Git history is terse (`fix`); switch to `<scope>: <imperative summary>` (e.g., `oauth: guard refresh token`) for clarity.
- Mention Terraform or Cloud Run side effects plus new env/Secret Manager keys in the body.
- PRs should list purpose, test commands (`uv run pytest`, `uv run mypy app`), rollout notes, and screenshots or curl traces for route changes.

## Security & Configuration Tips

- Required env vars (`GCP_KMS_KEY_URI`, `GSM_*`, `GOOGLE_CLOUD_*`, `APP_NAME`, `REDIRECT_URI`) belong in `.env` for local use; production values stay in Secret Manager.
- Run `make replace` only after Terraform applies and KMS aliases exist; otherwise deployments will fail at runtime.
- Avoid logging tokens; rely on `EnvelopeAEAD` helpers and scrub sensitive fields in debug output.
