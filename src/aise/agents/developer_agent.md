# Developer Agent

**Role:** `DEVELOPER` | **Module:** `aise.agents.developer` | **Phase:** Implementation

Owns the implementation phase. Generates source code from architecture designs, writes unit tests, reviews code quality, and fixes bugs.

## Skills

1. `code_generation` → `SOURCE_CODE` — generate module scaffolding (models, routes, services)
2. `unit_test_writing` → `UNIT_TESTS` — generate test suites per module
3. `code_review` → `REVIEW_FEEDBACK` — review quality, security, coverage **(review gate)**
4. `bug_fix` → `BUG_REPORT` — fix bugs with root cause analysis **(on-demand)**

Skills execute 1→2→3 in sequence. Skill 4 is triggered on-demand when bugs are reported.

**Important:** All generated code **must** pass unit tests before proceeding to code review or PR submission. The workflow engine enforces this via the `require_tests_pass` flag on the implementation phase. Additionally, there are a minimum of **3 review rounds** between implementation and review to ensure code quality.

## Artifact Flow

**Produces:** SOURCE_CODE, UNIT_TESTS, REVIEW_FEEDBACK, BUG_REPORT
**Consumes from upstream:** ARCHITECTURE_DESIGN, API_CONTRACT, TECH_STACK (from Architect)

**Internal dependencies:**
- unit_test_writing reads SOURCE_CODE
- code_review reads SOURCE_CODE + UNIT_TESTS
- bug_fix reads SOURCE_CODE

## Upstream / Downstream

- **Upstream:** Architect → ARCHITECTURE_DESIGN, API_CONTRACT, TECH_STACK
- **Downstream:** QA Engineer consumes SOURCE_CODE indirectly via architecture_review alignment

## Supported Outputs

Code generation supports Python/FastAPI and Go/Gin. Per-component structure:
- `app/{module}/models.py` — data models
- `app/{module}/routes.py` — API routes
- `app/{module}/service.py` — business logic
- `app/main.py` — application entry point

## Quick Reference

```python
from aise.agents.developer import DeveloperAgent

dev = DeveloperAgent(bus, store)

# Architect artifacts must exist in store
dev.execute_skill("code_generation", {}, project_name="MyProject")
dev.execute_skill("unit_test_writing", {}, project_name="MyProject")
dev.execute_skill("code_review", {}, project_name="MyProject")

# On-demand bug fixing
dev.execute_skill("bug_fix", {
    "bug_reports": [{"id": "BUG-001", "description": "Login fails on empty password"}]
}, project_name="MyProject")
```
