# GeoStructure-Agent

Energy-preserving numerical methods for complex fluids and Hamiltonian systems. The project
pairs a deterministic contract kernel with an LLM agent layer and uses the GSGE framework
(Gu & Wang) as its intermediate language.

Status: **P0 (engineering foundation)**. No numerical methods are implemented yet.

- Design: `docs/GeoStructure-Agent-Blueprint.html`
- Original brief: `docs/GeoStructure-Agent-CLI-Brief.md`
- Step-by-step code lessons: `docs/lessons/index.html`. All code is published here first and
  then entered into `src/` and `tests/` by hand.
- Rules for coding agents: `AGENTS.md`

## Setup

The project uses [uv](https://docs.astral.sh/uv/), which runs on macOS, Linux and Windows. The
Python version is pinned in `.python-version` (3.12), and exact dependency versions for every
platform are pinned in `uv.lock`.

```bash
# install uv once:  brew install uv   (or see the uv docs for Linux/Windows)
uv sync          # creates .venv, installs Python 3.12 if needed, the package (editable) and dev tools
uv run pytest -q
```

Commit `uv.lock` together with any change to dependencies.
