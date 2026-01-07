<!--
Sync Impact Report - Constitution v1.0.0
========================================
Version Change: [TEMPLATE] → 1.0.0
Rationale: Initial constitution creation for Stembler project

Modified Principles: N/A (initial creation)
Added Sections:
  - Core Principles (5 principles established)
  - Quality Standards
  - Development Workflow
  - Governance

Removed Sections: N/A

Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligns
  ✅ .specify/templates/spec-template.md - No changes needed
  ✅ .specify/templates/tasks-template.md - No changes needed
  ⚠ Future: Update when new features require specific quality gates

Follow-up TODOs: None
-->

# Stembler Constitution

## Core Principles

### I. Modular Architecture

Every feature must be implemented as a self-contained, independently testable module. Modules
MUST have clear, single responsibilities and well-defined interfaces. Cross-module dependencies
MUST be minimal and explicit. No tightly coupled "god objects" or monolithic classes that mix
concerns.

**Rationale**: Modular design enables independent testing, easier debugging, and allows future
extensions (like swapping AI models) without cascading changes across the codebase.

### II. Test-Driven Development (NON-NEGOTIABLE)

Testing is mandatory with 80%+ coverage requirement. Tests MUST be written before implementation
code. Follow the Red-Green-Refactor cycle:
1. Write failing test
2. Implement minimum code to pass
3. Refactor while keeping tests green

Integration tests MUST cover:
- Input processing for all supported formats (MP3, WAV, FLAC, M4A, Spotify URLs)
- AI model loading and stem separation output
- Output file organization and metadata generation

**Rationale**: TDD ensures code is testable by design, catches regressions early, and provides
living documentation of expected behavior. The 80% threshold balances thoroughness with
pragmatism.

### III. CLI-First Interface

All functionality MUST be accessible via command-line interface before GUI implementation.
CLI commands MUST follow these conventions:
- Arguments via positional params or flags (no interactive prompts for automation)
- Standard I/O: results to stdout, errors to stderr, exit codes for success/failure
- Support both human-readable and JSON output formats for scripting
- Maintain backward compatibility - never break existing CLI behavior

**Rationale**: CLI-first enables automation, scripting, and batch processing. It forces clear
interface design and ensures power users can always access full functionality without GUI
overhead.

### IV. Performance Standards

Processing performance MUST meet these targets:
- **Processing Time**: 1-3 minutes per average song (3-5 minutes) with htdemucs model
- **Memory Usage**: <4GB RAM for typical songs (<10 minutes duration)
- **Startup Time**: CLI <2 seconds, GUI <3 seconds (cold start)
- **GPU Acceleration**: Must support both CUDA-enabled and CPU-only environments

Performance degradation beyond these thresholds requires explicit justification and user approval.
All performance-critical paths MUST be profiled before optimization attempts.

**Rationale**: Stem separation is computationally expensive. Setting clear targets prevents
feature creep that degrades user experience and ensures the tool remains practical for
typical use cases.

### V. Code Quality & Consistency

All code MUST pass automated quality checks before merge:
- **Formatting**: Black (line length 100, Python 3.12+ syntax)
- **Linting**: Ruff with default rules (no warnings tolerated)
- **Type Hints**: All public functions and methods MUST have type annotations
- **Documentation**: Docstrings required for all modules, classes, and public functions

Code reviews MUST verify:
- No security vulnerabilities (command injection, path traversal, unsafe deserialization)
- Error handling exists for all external dependencies (network, filesystem, AI models)
- Logging is present for debugging (use Python logging module, not print statements)

**Rationale**: Consistent code quality reduces cognitive load, makes the codebase welcoming
to contributors, and prevents entire classes of bugs through static analysis.

## Quality Standards

### Testing Requirements

- Unit tests for all core logic (separator, input processor, output manager)
- Integration tests for end-to-end workflows (local file processing, Spotify downloads)
- Fixtures for sample audio files (gitignored, documented how to generate)
- Mock external APIs (Spotify, AI model downloads) in tests to avoid flakiness
- Test execution MUST complete in <60 seconds (excluding slow integration tests marked with @pytest.mark.slow)

### Documentation Standards

- README.md MUST include: quick start, installation, basic usage, common issues
- CLAUDE.md MUST be updated when architecture or key technologies change
- Code comments explain "why" not "what" (the code itself shows what it does)
- Breaking changes MUST be documented in commit messages and CHANGELOG.md

### Dependency Management

- All dependencies MUST be pinned with minimum versions in pyproject.toml
- Security updates applied within 7 days of CVE publication
- Large dependencies (PyTorch, Demucs) MUST justify their inclusion (core functionality only)
- No vendoring of third-party code (use package manager)

## Development Workflow

### Feature Development

1. **Specification**: Write spec in `/specs/{###-feature-name}/spec.md` before coding
2. **Planning**: Generate implementation plan with `/speckit.plan`
3. **Tasks**: Break down work with `/speckit.tasks`
4. **Implementation**: Follow TDD cycle, commit frequently with clear messages
5. **Review**: Self-review against constitution before requesting peer review

### Git Workflow

- Branch naming: `###-feature-name` (matches spec directory)
- Commit messages: Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`)
- No force-push to main branch
- Pre-commit hooks MUST pass (Black, Ruff, pytest for affected modules)

### Release Process

- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog updated before release
- Tagged releases on GitHub
- Packaged executables for GUI (macOS DMG, Windows MSI)

## Governance

This constitution supersedes all other development practices and guidelines. When conflicts arise
between this document and other guidance (README, CLAUDE.md, inline comments), this constitution
takes precedence.

### Amendment Process

1. **Proposal**: Document proposed change with rationale in GitHub issue
2. **Discussion**: Allow 7 days for feedback from maintainers and contributors
3. **Approval**: Requires maintainer approval
4. **Migration**: Update this document, increment version, propagate to templates
5. **Communication**: Announce in README and commit message

### Compliance Verification

- All pull requests MUST include a constitution compliance checklist
- Automated CI checks enforce: test coverage, code quality, type hints
- Manual review verifies: architectural principles, performance standards, documentation

### Version Policy

- **MAJOR**: Backward-incompatible changes to core principles or governance
- **MINOR**: New principles added or existing ones materially expanded
- **PATCH**: Clarifications, wording improvements, typo fixes

Use CLAUDE.md for runtime development guidance and feature-specific instructions.
This constitution addresses project-wide governance and non-negotiable standards.

**Version**: 1.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
