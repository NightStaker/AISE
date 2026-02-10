"""Agent health monitoring skill - detects stuck or unresponsive agents."""

from __future__ import annotations

from typing import Any

from ...core.artifact import Artifact, ArtifactType
from ...core.skill import Skill, SkillContext


class AgentHealthMonitorSkill(Skill):
    """Monitor agent health and detect stuck or unresponsive agents.

    The Team Manager runs this skill periodically in high-availability mode.
    It inspects the message bus history and workflow task statuses to identify
    agents that are stuck (e.g., a task has been ``in_progress`` for too long
    without producing a response).
    """

    @property
    def name(self) -> str:
        return "agent_health_monitor"

    @property
    def description(self) -> str:
        return "Monitor agent health and detect stuck or unresponsive agents"

    def execute(self, input_data: dict[str, Any], context: SkillContext) -> Artifact:
        agents: dict[str, dict[str, Any]] = input_data.get("agents", {})
        message_history: list[dict[str, Any]] = input_data.get("message_history", [])
        task_statuses: list[dict[str, Any]] = input_data.get("task_statuses", [])

        health_report: dict[str, dict[str, Any]] = {}
        stuck_agents: list[str] = []
        healthy_agents: list[str] = []

        for agent_name, agent_info in agents.items():
            # Count messages sent/received by this agent
            sent = sum(1 for m in message_history if m.get("sender") == agent_name)
            received = sum(1 for m in message_history if m.get("receiver") == agent_name)
            pending_requests = sum(
                1
                for m in message_history
                if m.get("receiver") == agent_name
                and m.get("msg_type") == "request"
                and not any(
                    r.get("sender") == agent_name and r.get("correlation_id") == m.get("id") for r in message_history
                )
            )

            # Check for stuck tasks assigned to this agent
            stuck_tasks = [
                t for t in task_statuses if t.get("agent") == agent_name and t.get("status") == "in_progress"
            ]

            is_stuck = len(stuck_tasks) > 0 and pending_requests > 0
            status = "stuck" if is_stuck else "healthy"

            health_report[agent_name] = {
                "status": status,
                "messages_sent": sent,
                "messages_received": received,
                "pending_requests": pending_requests,
                "stuck_tasks": [t.get("skill", "unknown") for t in stuck_tasks],
                "skills": agent_info.get("skills", []),
            }

            if is_stuck:
                stuck_agents.append(agent_name)
            else:
                healthy_agents.append(agent_name)

        return Artifact(
            artifact_type=ArtifactType.PROGRESS_REPORT,
            content={
                "report_type": "agent_health",
                "agents": health_report,
                "stuck_agents": stuck_agents,
                "healthy_agents": healthy_agents,
                "total_agents": len(agents),
                "stuck_count": len(stuck_agents),
                "healthy_count": len(healthy_agents),
                "project_name": context.project_name,
            },
            producer="team_manager",
            metadata={"type": "agent_health_report", "project_name": context.project_name},
        )
