"""Team Manager agent - high-availability supervisor for the agent team."""

from __future__ import annotations

from typing import Any

from ..config import ModelConfig
from ..core.agent import Agent, AgentRole
from ..core.artifact import ArtifactStore
from ..core.message import Message, MessageBus, MessageType
from ..skills.manager import (
    AgentHealthMonitorSkill,
    AgentRestartSkill,
    ArchitectureOptimizationSkill,
    CodeOptimizationSkill,
)


class TeamManagerAgent(Agent):
    """High-availability manager that supervises the agent team.

    The Team Manager operates in *high-availability demand mode*:

    1. **Health monitoring** – Continuously monitors agents for stuck or
       unresponsive states by inspecting the message bus and task statuses.
    2. **Agent restart** – When a stuck agent is detected, the manager
       re-initialises its message-bus subscription and re-queues pending
       tasks so the workflow can continue.
    3. **Idle optimisation** – When there are no pending requirements in
       the queue, the manager generates architecture and code optimisation
       tasks to keep the team productive.
    """

    def __init__(
        self,
        message_bus: MessageBus,
        artifact_store: ArtifactStore,
        model_config: ModelConfig | None = None,
    ) -> None:
        super().__init__(
            name="team_manager",
            role=AgentRole.TEAM_MANAGER,
            message_bus=message_bus,
            artifact_store=artifact_store,
            model_config=model_config,
        )
        self.register_skill(AgentHealthMonitorSkill())
        self.register_skill(AgentRestartSkill())
        self.register_skill(ArchitectureOptimizationSkill())
        self.register_skill(CodeOptimizationSkill())

        self._ha_enabled: bool = True

    # ------------------------------------------------------------------
    # High-Availability API
    # ------------------------------------------------------------------

    @property
    def ha_enabled(self) -> bool:
        """Whether high-availability demand mode is active."""
        return self._ha_enabled

    @ha_enabled.setter
    def ha_enabled(self, value: bool) -> None:
        self._ha_enabled = value

    def check_agent_health(
        self,
        agents: dict[str, dict[str, Any]],
        message_history: list[dict[str, Any]],
        task_statuses: list[dict[str, Any]],
        project_name: str = "",
    ) -> dict[str, Any]:
        """Run the health monitor and return the health report.

        Args:
            agents: Map of agent name to info dict (skills list, etc.).
            message_history: Serialised message history from the bus.
            task_statuses: List of task status dicts (agent, skill, status).
            project_name: Current project name.

        Returns:
            Health report content dict.
        """
        artifact = self.execute_skill(
            "agent_health_monitor",
            {
                "agents": agents,
                "message_history": message_history,
                "task_statuses": task_statuses,
            },
            project_name,
        )
        return artifact.content

    def restart_stuck_agents(
        self,
        stuck_agents: list[str],
        agent_registry: dict[str, Any],
        project_name: str = "",
    ) -> dict[str, Any]:
        """Restart a list of stuck agents.

        Args:
            stuck_agents: Names of agents to restart.
            agent_registry: Map of agent name to info for restart.
            project_name: Current project name.

        Returns:
            Restart report content dict.
        """
        artifact = self.execute_skill(
            "agent_restart",
            {
                "stuck_agents": stuck_agents,
                "agent_registry": agent_registry,
            },
            project_name,
        )
        return artifact.content

    def generate_optimization_tasks(self, project_name: str = "") -> list[dict[str, Any]]:
        """Generate optimisation tasks when there are no pending requirements.

        Runs both architecture and code optimisation skills and merges
        the resulting task lists.

        Returns:
            Combined list of optimisation task dicts.
        """
        tasks: list[dict[str, Any]] = []

        try:
            arch_artifact = self.execute_skill("architecture_optimization", {}, project_name)
            tasks.extend(arch_artifact.content.get("optimization_tasks", []))
        except (ValueError, KeyError):
            pass  # Architecture artifacts may not exist yet

        try:
            code_artifact = self.execute_skill("code_optimization", {}, project_name)
            tasks.extend(code_artifact.content.get("optimization_tasks", []))
        except (ValueError, KeyError):
            pass  # Code artifacts may not exist yet

        return tasks

    def run_ha_cycle(
        self,
        agents: dict[str, dict[str, Any]],
        message_history: list[dict[str, Any]],
        task_statuses: list[dict[str, Any]],
        has_pending_requirements: bool,
        project_name: str = "",
    ) -> dict[str, Any]:
        """Execute one high-availability supervision cycle.

        A single HA cycle:
        1. Checks agent health.
        2. Restarts any stuck agents.
        3. If no requirements are waiting, generates optimisation tasks.

        Args:
            agents: Agent info map.
            message_history: Serialised message history.
            task_statuses: Current task statuses.
            has_pending_requirements: Whether requirements are queued.
            project_name: Current project name.

        Returns:
            Cycle result dict with health_report, restart_report, and
            optimization_tasks keys.
        """
        result: dict[str, Any] = {"ha_enabled": self._ha_enabled}

        if not self._ha_enabled:
            return result

        # Step 1: Health check
        health = self.check_agent_health(agents, message_history, task_statuses, project_name)
        result["health_report"] = health

        # Step 2: Restart stuck agents
        stuck = health.get("stuck_agents", [])
        if stuck:
            agent_registry = {name: info for name, info in agents.items() if name in stuck}
            restart = self.restart_stuck_agents(stuck, agent_registry, project_name)
            result["restart_report"] = restart

            # Notify the team about restarts
            self.send_message(
                receiver="broadcast",
                msg_type=MessageType.NOTIFICATION,
                content={
                    "text": (f"Team Manager restarted {len(stuck)} stuck agent(s): {', '.join(stuck)}"),
                    "restarted_agents": stuck,
                },
            )

        # Step 3: Generate optimisation tasks when idle
        if not has_pending_requirements:
            opt_tasks = self.generate_optimization_tasks(project_name)
            result["optimization_tasks"] = opt_tasks

            if opt_tasks:
                self.send_message(
                    receiver="broadcast",
                    msg_type=MessageType.NOTIFICATION,
                    content={
                        "text": (
                            f"Team Manager generated {len(opt_tasks)} optimisation "
                            "task(s) while waiting for new requirements."
                        ),
                        "optimization_task_count": len(opt_tasks),
                    },
                )

        return result

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------

    def handle_message(self, message: Message) -> Message | None:
        """Handle messages; extends base with HA-specific notifications."""
        # Delegate standard skill requests to the base class
        response = super().handle_message(message)
        if response is not None:
            return response

        # React to notification about stuck agents from external monitors
        if (
            message.msg_type == MessageType.NOTIFICATION
            and message.content.get("type") == "agent_stuck"
            and self._ha_enabled
        ):
            stuck_agent = message.content.get("agent_name")
            if stuck_agent:
                return message.reply(
                    {
                        "status": "acknowledged",
                        "action": "will_restart",
                        "agent": stuck_agent,
                    },
                    MessageType.RESPONSE,
                )

        return None
