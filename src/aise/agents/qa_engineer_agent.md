# QA Engineer Agent

**Role:** `QA_ENGINEER` | **Module:** `aise.agents.qa_engineer` | **Phase:** Testing

Owns the testing phase. Creates test plans, designs test cases, generates automated test scripts, and reviews test quality and coverage.

## Skills

1. `test_plan_design` → `TEST_PLAN` — define testing scope, strategy, and risks
2. `test_case_design` → `TEST_CASES` — design integration, E2E, regression test cases
3. `test_automation` → `AUTOMATED_TESTS` — generate pytest scripts from test cases
4. `test_review` → `REVIEW_FEEDBACK` — validate coverage and quality **(review gate)**

Skills execute in order 1→2→3→4. Skill 4 enforces coverage ≥70% and automation ≥60%.

## Artifact Flow

**Produces:** TEST_PLAN, TEST_CASES, AUTOMATED_TESTS, REVIEW_FEEDBACK
**Consumes from upstream:** ARCHITECTURE_DESIGN, API_CONTRACT (from Architect); TECH_STACK (from Architect); UNIT_TESTS (from Developer)

**Internal dependencies:**
- test_case_design reads ARCHITECTURE_DESIGN + API_CONTRACT
- test_automation reads TEST_CASES + TECH_STACK
- test_review reads TEST_PLAN + TEST_CASES + AUTOMATED_TESTS + API_CONTRACT + UNIT_TESTS

## Upstream / Downstream

- **Upstream:** Architect → ARCHITECTURE_DESIGN, API_CONTRACT; Developer → UNIT_TESTS
- **Downstream:** none (final phase agent)

## Quick Reference

```python
from aise.agents.qa_engineer import QAEngineerAgent

qa = QAEngineerAgent(bus, store)

# Architect + Developer artifacts must exist in store
qa.execute_skill("test_plan_design", {}, project_name="MyProject")
qa.execute_skill("test_case_design", {}, project_name="MyProject")
qa.execute_skill("test_automation", {}, project_name="MyProject")
qa.execute_skill("test_review", {}, project_name="MyProject")
```
