# Architect Agent

**Role:** `ARCHITECT` | **Module:** `aise.agents.architect` | **Phase:** Design

Owns the design phase. Translates product requirements into system architecture, defines API contracts, selects the technology stack, and validates design completeness.

## Skills

1. `system_design` → `ARCHITECTURE_DESIGN` — derive components and data flows from PRD
2. `api_design` → `API_CONTRACT` — generate endpoint and schema definitions
3. `tech_stack_selection` → `TECH_STACK` — choose and justify technology stack
4. `architecture_review` → `REVIEW_FEEDBACK` — validate design completeness **(review gate)**

Skills 2 and 3 can run in parallel after skill 1. Skill 4 is the review gate.

**Important:** The design phase enforces a minimum of **3 review rounds** between design work and architecture review to ensure design completeness and quality.

## Artifact Flow

**Produces:** ARCHITECTURE_DESIGN, API_CONTRACT, TECH_STACK, REVIEW_FEEDBACK
**Consumes from upstream:** REQUIREMENTS (from PM), PRD (from PM)

**Internal dependencies:**
- api_design reads ARCHITECTURE_DESIGN
- tech_stack_selection reads REQUIREMENTS + ARCHITECTURE_DESIGN
- architecture_review reads ARCHITECTURE_DESIGN + API_CONTRACT + TECH_STACK (+ optionally SOURCE_CODE)

## Upstream / Downstream

- **Upstream:** Product Manager → REQUIREMENTS, PRD
- **Downstream:** Developer consumes ARCHITECTURE_DESIGN, API_CONTRACT, TECH_STACK; QA Engineer consumes ARCHITECTURE_DESIGN, API_CONTRACT

## Quick Reference

```python
from aise.agents.architect import ArchitectAgent

arch = ArchitectAgent(bus, store)

# All skills read from artifact store (PM artifacts must exist)
arch.execute_skill("system_design", {}, project_name="MyProject")
arch.execute_skill("api_design", {}, project_name="MyProject")
arch.execute_skill("tech_stack_selection", {}, project_name="MyProject")
arch.execute_skill("architecture_review", {}, project_name="MyProject")
```
