# Contributing

## Scope

This project is building a Raspberry Pi VPN-switch appliance, not a general-purpose router platform. Contributions should stay aligned with the documented topology and security goals.

## Ground rules

- Prefer small, focused pull requests.
- Keep networking behavior explicit and documented.
- Do not commit live VPN credentials, tokens, or customer identifiers.
- If a change affects routing, DNS, kill-switch behavior, or onboarding, update docs and tests in the same change.

## Local development

Set up once (Python 3.11 or newer, Node 24):

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
npm ci
```

Run the app with no hardware, using the mock provider:

```bash
RP_PROVIDER=mock python -m openspoofen.serve
npm run dev   # frontend with hot reload, proxied to the running backend
```

- Use the mock provider for UI and workflow development.
- Use real hardware before claiming a networking feature is complete.
- Use the Linux namespace lab described in `docs/guides/testing-and-simulation.md` for pre-hardware routing experiments.

## Testing expectations

```bash
ruff check src tests scripts examples
pytest
npm run build
```

- Run the Python test suite. Lint must stay clean.
- The built frontend in `src/openspoofen/static/` is committed. After changing anything in `frontend/`, run `npm run build` and commit the output; CI fails when it drifts from the sources.
- Don't run `pytest` while a frontend build is running: one test reads `src/openspoofen/static/` while the build rewrites it.
- Document manual validation for Raspberry Pi specific behavior.
- For networking changes, include the exact topology you tested.

## How changes reach this repository

This repository is published from a private working copy: each release arrives as a single commit, and there is no day-to-day branch history here. Pull requests are still welcome. An accepted change is applied upstream, credited in the changelog, and appears here in the next release, so your pull request is closed with a link to that release rather than merged.

## Pull request notes

- Summarize user-visible behavior changes.
- Call out any security or topology assumptions.
- Note anything that was not validated on real Pi hardware.

## Security issues

Report vulnerabilities privately, as described in [SECURITY.md](SECURITY.md), never in a public issue or pull request.

## Code of conduct

Taking part means following the [code of conduct](CODE_OF_CONDUCT.md).
