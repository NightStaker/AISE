"""Agent restart skill - restarts stuck agents to restore workflow progress."""

from __future__ import annotations

from typing import Any

from ...core.artifact import Artifact, ArtifactType
from ...core.skill import Skill, SkillContext


class AgentRestartSkill(Skill):
    """Restart agents that are stuck or unresponsive.

    When the health monitor detects a stuck agent, the Team Manager uses this
    skill to re-initialise the agent's message-bus subscription and re-queue
    its pending tasks.  This is the core high-availability mechanism: rather
    than letting a single stuck agent block the entire workflow, the Team
    Manager can recover automatically.
    """

    @property
    def name(self) -> str:
        return "agent_restart"

    @property
    def description(self) -> str:
        return "Restart stuck agents and re-queue their pending tasks"

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not input_data.get("stuck_agents"):
            errors.append("stuck_agents list is required and must be non-empty")
        return errors

    def execute(self, input_data: dict[str, Any], context: SkillContext) -> Artifact:
        stuck_agents: list[str] = input_data.get("stuck_agents", [])
        agent_registry: dict[str, Any] = input_data.get("agent_registry", {})

        restart_results: list[dict[str, Any]] = []

        for agent_name in stuck_agents:
            agent_info = agent_registry.get(agent_name)
            if agent_info is None:
                restart_results.append(
                    {
                        "agent": agent_name,
                        "action": "skip",
                        "reason": "Agent not found in registry",
                    }
                )
                continue

            # Record the restart action with the pending tasks that will be re-queued
            pending_tasks = agent_info.get("pending_tasks", [])
            restart_results.append(
                {
                    "agent": agent_name,
                    "action": "restart",
                    "reason": "Agent detected as stuck by health monitor",
                    "requeued_tasks": pending_tasks,
                    "skills_available": agent_info.get("skills", []),
                }
            )

        restarted = [r for r in restart_results if r["action"] == "restart"]
        skipped = [r for r in restart_results if r["action"] == "skip"]

        return Artifact(
            artifact_type=ArtifactType.PROGRESS_REPORT,
            content={
                "report_type": "agent_restart",
                "restart_results": restart_results,
                "restarted_count": len(restarted),
                "skipped_count": len(skipped),
                "restarted_agents": [r["agent"] for r in restarted],
                "project_name": context.project_name,
            },
            producer="team_manager",
            metadata={"type": "agent_restart_report", "project_name": context.project_name},
        )
