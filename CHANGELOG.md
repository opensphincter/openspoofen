# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The public repository carries one commit per release; this file is the history.

## 0.3.0 - 2026-11-01

First public release, as `opensphincter/openspoofen`.

### Added

- Community files for an open-source release: `SECURITY.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, issue forms, a pull request template and CODEOWNERS.
- Dependabot (on the private repository, where changes are made).
- A release workflow that builds the sdist and wheel from a version tag.
- `docs/README.md`, an index of the documentation.
- Dashboard: the first status fetch runs immediately, and controls carry ARIA labels.
- Tests: `web.py` coverage from 77 to 98 percent (120 tests).

### Changed

- Documentation is grouped into `docs/guides/`, `docs/design/` and `docs/reference/`.
- CI actions are pinned to commit SHAs; the CI token is least-privilege and the JS dependency audit runs in CI.
- The web unit is sandboxed with systemd hardening options.
- Package metadata: SPDX licence expression, project URLs, classifiers and keywords.

### Removed

- Pytest scratch output (`.tmp-test/`) that had been committed by mistake.
- `references/`, whose only entry (NordVPN's Linux install guide) is now linked from `docs/README.md`.

## 0.2.0 - 2026-10-08

Upgrade pass (no behavior or configuration contract changes; `RP_` variables unchanged):

- Python dependencies: gunicorn 23 to 26, samsungtvws 2.7 to 3.0, pytest 8 to 9 (also resolves the only pip-audit finding, PYSEC-2026-1845 in pytest 8.4.2). pip-audit is clean after the bump.
- Frontend toolchain: Vite 7 to 8 (Rolldown), @vitejs/plugin-react 5 to 6, Tailwind CSS 3 to 4, lucide-react 0.542 to 1.52, framer-motion 12 to 14, cssnano 8 to 9, React 19.2 to 19.3. Built output in `src/openspoofen/static/` regenerated.
- Fixed a latent frontend bug the Tailwind 4 fingerprint exposed: `bg-mint-400/12` used an opacity step Tailwind 3 never generated, so the ConfigPanel success banner tint silently did nothing.
- Security hardening: login `next` parameter can no longer redirect off-site (open redirect); region switch and connect now reject empty or flag-like country values before they can reach provider CLIs; session cookies are explicitly HttpOnly + SameSite=Lax (+ Secure when HTTPS is enabled); pairing-token comparison is constant-time.
- Robustness: corrupt JSON state files (LAN auth, mock, WireGuard, Surfshark, TV remote) now fall back to defaults instead of failing every request; bad numeric `RP_` values fail with an error naming the variable; Surfshark no longer trusts a stale PID file (verifies the PID is an OpenVPN process and rejects non-positive PIDs before any signal); dashboard interface probe tolerates empty command output.
- Tests: suite grows from 42 to 80 (new auth, state-resilience, NordVPN parser, config-validation, and web-hardening coverage).
- Tooling: ruff adopted (dev dependency, clean across `src`, `tests`, `scripts`, `examples`); CI gains a Python 3.13 leg, lint, pip-audit, a frontend build job, and a guard that committed static assets match a fresh build.

## 0.1.0 - 2026-04-08

- Added initial architecture, planning, and first-boot strategy docs.
- Added Raspberry Pi I/O and form-factor feasibility research.
- Added VPN provider comparison focused on appliance fit.
- Added Flask-based mock control surface scaffold.
- Added mock provider and NordVPN wrapper skeleton.
- Added test scaffold and simulation documentation.
- Added standard open-source repo files and versioning metadata.
