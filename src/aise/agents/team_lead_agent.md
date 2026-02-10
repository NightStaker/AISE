# Team Lead Agent

**Role:** `TEAM_LEAD` | **Module:** `aise.agents.team_lead` | **Phase:** Cross-cutting (all phases)

Orchestrates the development workflow. Decomposes goals into tasks, assigns work to agents, resolves inter-agent conflicts, and tracks progress.

## Skills

1. `task_decomposition` → `PROGRESS_REPORT` — break goals into ordered, agent-assignable tasks
2. `task_assignment` → `PROGRESS_REPORT` — assign tasks to agents by required skills
3. `conflict_resolution` → `REVIEW_FEEDBACK` — resolve conflicts using NFR-aligned heuristics
4. `progress_tracking` → `PROGRESS_REPORT` — report per-phase completion and overall status

No fixed execution order. Patterns:
- **Project start:** 1→2 (plan and distribute)
- **During execution:** 3 (on-demand conflict resolution)
- **Monitoring:** 4 (status reporting at any time)

## Artifact Flow

**Produces:** PROGRESS_REPORT, REVIEW_FEEDBACK
**Consumes:** REQUIREMENTS (for conflict_resolution heuristics); all artifact types (for progress_tracking)

## Integration

Coordinates all agents:
- Assigns requirements-phase tasks to **Product Manager**
- Assigns design-phase tasks to **Architect**
- Assigns implementation-phase tasks to **Developer**
- Assigns testing-phase tasks to **QA Engineer**

Conflict resolution uses NFR keywords (performance, security) to align decisions. Falls back to first proposed option when no NFR match is found.

## Quick Reference

```python
from aise.agents.team_lead import TeamLeadAgent

lead = TeamLeadAgent(bus, store)

# Decompose and assign
lead.execute_skill("task_decomposition", {
    "goals": ["User auth", "Product catalog", "Shopping cart"]
}, project_name="MyProject")

lead.execute_skill("task_assignment", {
    "tasks": [...]  # task objects from decomposition
}, project_name="MyProject")

# On-demand
lead.execute_skill("conflict_resolution", {
    "conflicts": [{"parties": ["architect", "developer"],
                   "issue": "DB choice",
                   "options": ["PostgreSQL", "MongoDB"]}]
}, project_name="MyProject")

lead.execute_skill("progress_tracking", {}, project_name="MyProject")
```
