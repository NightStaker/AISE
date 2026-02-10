"""Code optimization skill - generates code improvement tasks when idle."""

from __future__ import annotations

from typing import Any

from ...core.artifact import Artifact, ArtifactType
from ...core.skill import Skill, SkillContext


class CodeOptimizationSkill(Skill):
    """Generate code optimisation tasks when no requirements are waiting.

    Complements ``ArchitectureOptimizationSkill`` by focusing on
    implementation-level improvements: refactoring, test-coverage gaps,
    dependency updates, and performance hot-spots.
    """

    @property
    def name(self) -> str:
        return "code_optimization"

    @property
    def description(self) -> str:
        return "Generate code optimization tasks when no pending requirements exist"

    @property
    def required_artifact_types(self) -> list[str]:
        return ["source_code"]

    def execute(self, input_data: dict[str, Any], context: SkillContext) -> Artifact:
        store = context.artifact_store

        code_artifact = store.get_latest(ArtifactType.SOURCE_CODE)
        code_content = code_artifact.content if code_artifact else {}
        test_artifact = store.get_latest(ArtifactType.UNIT_TESTS)
        test_content = test_artifact.content if test_artifact else {}

        modules = code_content.get("modules", [])
        test_suites = test_content.get("test_suites", [])

        optimization_tasks: list[dict[str, Any]] = []
        task_id = 1

        # Test coverage improvement
        optimization_tasks.append(
            {
                "id": f"OPT-CODE-{task_id:03d}",
                "category": "test_coverage",
                "title": "Improve unit test coverage",
                "description": (
                    f"Current modules: {len(modules)}, test suites: {len(test_suites)}. "
                    "Identify modules with insufficient test coverage and generate "
                    "additional unit tests targeting edge cases and error paths."
                ),
                "priority": "high",
                "assigned_agent": "developer",
                "target_skill": "unit_test_writing",
            }
        )
        task_id += 1

        # Code refactoring
        optimization_tasks.append(
            {
                "id": f"OPT-CODE-{task_id:03d}",
                "category": "refactoring",
                "title": "Identify refactoring opportunities",
                "description": (
                    "Scan source code for duplicated logic, overly long functions, "
                    "and violations of the single-responsibility principle. "
                    "Propose targeted refactoring tasks."
                ),
                "priority": "medium",
                "assigned_agent": "developer",
                "target_skill": "code_review",
            }
        )
        task_id += 1

        # Performance hot-spots
        optimization_tasks.append(
            {
                "id": f"OPT-CODE-{task_id:03d}",
                "category": "performance",
                "title": "Performance hot-spot analysis",
                "description": (
                    "Review code for potential performance bottlenecks: "
                    "N+1 queries, unbounded loops, missing caching, "
                    "and inefficient data structures."
                ),
                "priority": "medium",
                "assigned_agent": "developer",
                "target_skill": "code_review",
            }
        )
        task_id += 1

        # Dependency review
        optimization_tasks.append(
            {
                "id": f"OPT-CODE-{task_id:03d}",
                "category": "dependencies",
                "title": "Dependency hygiene review",
                "description": (
                    "Audit third-party dependencies for known vulnerabilities, unused packages, and available updates."
                ),
                "priority": "low",
                "assigned_agent": "developer",
                "target_skill": "code_review",
            }
        )

        return Artifact(
            artifact_type=ArtifactType.PROGRESS_REPORT,
            content={
                "report_type": "code_optimization",
                "optimization_tasks": optimization_tasks,
                "task_count": len(optimization_tasks),
                "source_modules": len(modules),
                "test_suites": len(test_suites),
                "project_name": context.project_name,
            },
            producer="team_manager",
            metadata={"type": "code_optimization", "project_name": context.project_name},
        )
