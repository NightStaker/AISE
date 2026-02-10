"""Architecture optimization skill - generates optimization tasks when idle."""

from __future__ import annotations

from typing import Any

from ...core.artifact import Artifact, ArtifactType
from ...core.skill import Skill, SkillContext


class ArchitectureOptimizationSkill(Skill):
    """Generate architecture optimisation tasks when no requirements are waiting.

    In high-availability mode the Team Manager proactively looks for
    improvement opportunities rather than sitting idle.  This skill inspects
    the current architecture design artifact and produces a set of
    optimisation tasks covering scalability, security, performance, and
    maintainability.
    """

    @property
    def name(self) -> str:
        return "architecture_optimization"

    @property
    def description(self) -> str:
        return "Generate architecture optimization tasks when no pending requirements exist"

    @property
    def required_artifact_types(self) -> list[str]:
        return ["architecture_design"]

    def execute(self, input_data: dict[str, Any], context: SkillContext) -> Artifact:
        store = context.artifact_store

        arch_artifact = store.get_latest(ArtifactType.ARCHITECTURE_DESIGN)
        arch_content = arch_artifact.content if arch_artifact else {}

        components = arch_content.get("components", [])
        data_flows = arch_content.get("data_flows", [])

        optimization_tasks: list[dict[str, Any]] = []
        task_id = 1

        # Scalability analysis
        optimization_tasks.append(
            {
                "id": f"OPT-ARCH-{task_id:03d}",
                "category": "scalability",
                "title": "Review horizontal scaling strategy",
                "description": (
                    "Analyse current component topology for horizontal scaling bottlenecks. "
                    f"Current components: {len(components)}. "
                    "Recommend stateless redesign where applicable."
                ),
                "priority": "medium",
                "assigned_agent": "architect",
                "target_skill": "system_design",
            }
        )
        task_id += 1

        # Security hardening
        optimization_tasks.append(
            {
                "id": f"OPT-ARCH-{task_id:03d}",
                "category": "security",
                "title": "Security architecture review",
                "description": (
                    "Evaluate authentication, authorisation, and data-encryption patterns. "
                    "Identify components lacking defence-in-depth measures."
                ),
                "priority": "high",
                "assigned_agent": "architect",
                "target_skill": "architecture_review",
            }
        )
        task_id += 1

        # Performance optimisation
        optimization_tasks.append(
            {
                "id": f"OPT-ARCH-{task_id:03d}",
                "category": "performance",
                "title": "Data flow optimisation",
                "description": (
                    f"Review {len(data_flows)} data flows for unnecessary serialisation hops, "
                    "redundant network calls, and caching opportunities."
                ),
                "priority": "medium",
                "assigned_agent": "architect",
                "target_skill": "system_design",
            }
        )
        task_id += 1

        # Maintainability
        optimization_tasks.append(
            {
                "id": f"OPT-ARCH-{task_id:03d}",
                "category": "maintainability",
                "title": "Component coupling analysis",
                "description": (
                    "Identify tightly-coupled components and propose decoupling strategies "
                    "(event-driven, API gateway, message queues)."
                ),
                "priority": "low",
                "assigned_agent": "architect",
                "target_skill": "system_design",
            }
        )

        return Artifact(
            artifact_type=ArtifactType.PROGRESS_REPORT,
            content={
                "report_type": "architecture_optimization",
                "optimization_tasks": optimization_tasks,
                "task_count": len(optimization_tasks),
                "source_components": len(components),
                "source_data_flows": len(data_flows),
                "project_name": context.project_name,
            },
            producer="team_manager",
            metadata={"type": "architecture_optimization", "project_name": context.project_name},
        )
