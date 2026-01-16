# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**claudiminder** - Claude usage tracking & reminder tool with TUI/GUI support for Linux, Windows, and macOS.

### Core Features

- Usage tracking via Anthropic OAuth API (auto-grab from `~/.claude/.credentials.json`)
- 5-hour window reset time display & reminder
- Preset reminder strategies (before reset, on reset, custom intervals)
- System tray icon with usage percentage + hover for reset time
- Auto-open Claude login when token expired
- TUI mode for terminal usage
- GUI mode via Tauri v2

### Tech Stack

- **Backend**: Python 3.12+ (loguru, pydantic-settings, httpx, tenacity)
- **Frontend**: TypeScript + React + Tauri v2
- **Build**: uv (Python), Cargo (Rust), bun (frontend)

## Role & Responsibilities

Your role is to analyze user requirements, delegate tasks to appropriate sub-agents, and ensure cohesive delivery of features that meet specifications and architectural standards.

## Workflows

- Primary workflow: `$HOME/.claude/rules/primary-workflow.md`
- Development rules: `$HOME/.claude/rules/development-rules.md`
- Orchestration protocols: `$HOME/.claude/rules/orchestration-protocol.md`
- Documentation management: `$HOME/.claude/rules/documentation-management.md`
- Project-specific rules: `./docs/02-general/rules/`

**IMPORTANT:** Analyze the skills catalog and activate the skills that are needed for the task during the process.
**IMPORTANT:** You must follow strictly the development rules in `$HOME/.claude/rules/development-rules.md` file.
**IMPORTANT:** Before you plan or proceed any implementation, always read the `./README.md` and `./docs/02-general/rules` files first to get context.

## Project Structure

```
claudiminder/
├── src/
│   ├── backend/           # Python backend (sidecar)
│   │   ├── core/          # Core business logic
│   │   ├── api/           # API client for Anthropic
│   │   ├── models/        # Pydantic models
│   │   └── utils/         # Utilities (credentials, logging)
│   └── frontend/          # Tauri + React frontend
│       ├── src/
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── stores/
│       │   ├── styles/
│       │   ├── types/
│       │   └── utils/
│       └── src-tauri/     # Rust backend for Tauri
├── tests/
│   ├── backend/
│   └── frontend/
├── docs/
│   ├── 01-plans/          # Implementation plans
│   └── 02-general/        # Project docs & rules
└── scripts/               # Build & utility scripts
```

## Key Commands

```bash
# Backend (Python)
uv sync                    # Install dependencies
uv run python -m claudiminder.cli  # Run TUI
uv run pytest              # Run tests

# Frontend (Tauri)
cd src/frontend
bun install                # Install dependencies
bun run tauri dev          # Dev mode
bun run tauri build        # Production build
```

## Hook Response Protocol

### Privacy Block Hook (`@@PRIVACY_PROMPT@@`)

When a tool call is blocked by the privacy-block hook, the output contains a JSON marker between `@@PRIVACY_PROMPT_START@@` and `@@PRIVACY_PROMPT_END@@`. **You MUST use the `AskUserQuestion` tool** to get proper user approval.

## Python Scripts (Skills)

When running Python scripts from `$HOME/.claude/skills/`, use the venv Python interpreter:

- **Linux/macOS:** `$HOME/.claude/skills/.venv/bin/python3 scripts/xxx.py`
- **Windows:** `$HOME\.claude\skills\.venv\Scripts\python.exe scripts\xxx.py`

## [IMPORTANT] Consider Modularization

- If a code file exceeds 200 lines of code, consider modularizing it
- Check existing modules before creating new
- Use kebab-case naming with descriptive names
- After modularization, continue with main task

## Documentation Management

We keep all important docs in `./docs/02-general` folder:

```
./docs/02-general
├── project-overview-pdr.md
├── code-standards.md
├── codebase-summary.md
├── design-guidelines.md
├── system-architecture.md
├── project-roadmap.md
└── rules/
    ├── 00-principles.md
    ├── 01-python.md
    └── 02-tauri.md
```

**IMPORTANT:** _MUST READ_ and _MUST COMPLY_ all _INSTRUCTIONS_ in this file and `./docs/02-general/rules/`.
