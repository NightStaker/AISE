"""Tests for the Team Manager agent and skills."""

from aise.agents.team_manager import TeamManagerAgent
from aise.core.agent import AgentRole
from aise.core.artifact import Artifact, ArtifactStore, ArtifactType
from aise.core.message import Message, MessageBus, MessageType


class TestTeamManagerAgent:
    def _make_agent(self):
        bus = MessageBus()
        store = ArtifactStore()
        return TeamManagerAgent(bus, store), bus, store

    def test_has_all_skills(self):
        agent, _, _ = self._make_agent()
        expected = {
            "agent_health_monitor",
            "agent_restart",
            "architecture_optimization",
            "code_optimization",
        }
        assert set(agent.skill_names) == expected

    def test_role_is_team_manager(self):
        agent, _, _ = self._make_agent()
        assert agent.role == AgentRole.TEAM_MANAGER
        assert agent.name == "team_manager"

    def test_ha_enabled_by_default(self):
        agent, _, _ = self._make_agent()
        assert agent.ha_enabled is True

    def test_ha_can_be_disabled(self):
        agent, _, _ = self._make_agent()
        agent.ha_enabled = False
        assert agent.ha_enabled is False

    def test_agent_health_monitor_all_healthy(self):
        agent, _, _ = self._make_agent()
        agents = {
            "developer": {"skills": ["code_generation", "unit_test_writing"]},
            "architect": {"skills": ["system_design", "api_design"]},
        }
        artifact = agent.execute_skill(
            "agent_health_monitor",
            {
                "agents": agents,
                "message_history": [],
                "task_statuses": [],
            },
        )
        assert artifact.content["stuck_count"] == 0
        assert artifact.content["healthy_count"] == 2
        assert artifact.content["stuck_agents"] == []

    def test_agent_health_monitor_detects_stuck(self):
        agent, _, _ = self._make_agent()
        agents = {
            "developer": {"skills": ["code_generation"]},
        }
        message_history = [
            {
                "id": "msg1",
                "sender": "orchestrator",
                "receiver": "developer",
                "msg_type": "request",
            },
        ]
        task_statuses = [
            {"agent": "developer", "skill": "code_generation", "status": "in_progress"},
        ]
        artifact = agent.execute_skill(
            "agent_health_monitor",
            {
                "agents": agents,
                "message_history": message_history,
                "task_statuses": task_statuses,
            },
        )
        assert artifact.content["stuck_count"] == 1
        assert "developer" in artifact.content["stuck_agents"]

    def test_agent_restart(self):
        agent, _, _ = self._make_agent()
        artifact = agent.execute_skill(
            "agent_restart",
            {
                "stuck_agents": ["developer"],
                "agent_registry": {
                    "developer": {
                        "skills": ["code_generation"],
                        "pending_tasks": ["code_generation"],
                    },
                },
            },
        )
        assert artifact.content["restarted_count"] == 1
        assert "developer" in artifact.content["restarted_agents"]

    def test_agent_restart_skips_unknown(self):
        agent, _, _ = self._make_agent()
        artifact = agent.execute_skill(
            "agent_restart",
            {
                "stuck_agents": ["nonexistent_agent"],
                "agent_registry": {},
            },
        )
        assert artifact.content["restarted_count"] == 0
        assert artifact.content["skipped_count"] == 1

    def test_agent_restart_validation(self):
        agent, _, _ = self._make_agent()
        skill = agent.get_skill("agent_restart")
        errors = skill.validate_input({})
        assert len(errors) > 0

    def test_architecture_optimization(self):
        agent, _, store = self._make_agent()
        # Seed an architecture artifact
        store.store(
            Artifact(
                artifact_type=ArtifactType.ARCHITECTURE_DESIGN,
                content={
                    "components": ["api_gateway", "auth_service", "database"],
                    "data_flows": [{"from": "api_gateway", "to": "auth_service"}],
                },
                producer="architect",
            )
        )
        artifact = agent.execute_skill("architecture_optimization", {})
        assert artifact.content["task_count"] == 4
        categories = {t["category"] for t in artifact.content["optimization_tasks"]}
        assert "scalability" in categories
        assert "security" in categories
        assert "performance" in categories
        assert "maintainability" in categories

    def test_code_optimization(self):
        agent, _, store = self._make_agent()
        # Seed code and test artifacts
        store.store(
            Artifact(
                artifact_type=ArtifactType.SOURCE_CODE,
                content={"modules": ["models.py", "routes.py", "services.py"]},
                producer="developer",
            )
        )
        store.store(
            Artifact(
                artifact_type=ArtifactType.UNIT_TESTS,
                content={"test_suites": ["test_models.py", "test_routes.py"]},
                producer="developer",
            )
        )
        artifact = agent.execute_skill("code_optimization", {})
        assert artifact.content["task_count"] == 4
        categories = {t["category"] for t in artifact.content["optimization_tasks"]}
        assert "test_coverage" in categories
        assert "refactoring" in categories
        assert "performance" in categories
        assert "dependencies" in categories

    def test_check_agent_health_method(self):
        agent, _, _ = self._make_agent()
        report = agent.check_agent_health(
            agents={"developer": {"skills": []}},
            message_history=[],
            task_statuses=[],
            project_name="TestProject",
        )
        assert report["stuck_count"] == 0
        assert report["project_name"] == "TestProject"

    def test_restart_stuck_agents_method(self):
        agent, _, _ = self._make_agent()
        report = agent.restart_stuck_agents(
            stuck_agents=["developer"],
            agent_registry={"developer": {"skills": [], "pending_tasks": []}},
            project_name="TestProject",
        )
        assert report["restarted_count"] == 1

    def test_generate_optimization_tasks_empty_store(self):
        agent, _, _ = self._make_agent()
        # No artifacts in store, so both skills will raise/return gracefully
        tasks = agent.generate_optimization_tasks("TestProject")
        # Should not crash; may return empty or partial list
        assert isinstance(tasks, list)

    def test_run_ha_cycle_no_stuck(self):
        agent, _, _ = self._make_agent()
        result = agent.run_ha_cycle(
            agents={"developer": {"skills": []}},
            message_history=[],
            task_statuses=[],
            has_pending_requirements=True,
            project_name="TestProject",
        )
        assert result["ha_enabled"] is True
        assert result["health_report"]["stuck_count"] == 0
        assert "restart_report" not in result
        # Has pending requirements, so no optimization tasks
        assert "optimization_tasks" not in result

    def test_run_ha_cycle_with_stuck_and_idle(self):
        agent, bus, _ = self._make_agent()
        result = agent.run_ha_cycle(
            agents={
                "developer": {
                    "skills": ["code_generation"],
                    "pending_tasks": ["code_generation"],
                },
            },
            message_history=[
                {
                    "id": "msg1",
                    "sender": "orchestrator",
                    "receiver": "developer",
                    "msg_type": "request",
                },
            ],
            task_statuses=[
                {"agent": "developer", "skill": "code_generation", "status": "in_progress"},
            ],
            has_pending_requirements=False,
            project_name="TestProject",
        )
        assert result["health_report"]["stuck_count"] == 1
        assert "restart_report" in result
        assert result["restart_report"]["restarted_count"] == 1
        # No pending requirements, so optimization tasks generated
        assert "optimization_tasks" in result

    def test_run_ha_cycle_disabled(self):
        agent, _, _ = self._make_agent()
        agent.ha_enabled = False
        result = agent.run_ha_cycle(
            agents={},
            message_history=[],
            task_statuses=[],
            has_pending_requirements=False,
        )
        assert result["ha_enabled"] is False
        assert "health_report" not in result

    def test_handle_agent_stuck_notification(self):
        agent, bus, _ = self._make_agent()
        msg = Message(
            sender="external_monitor",
            receiver="team_manager",
            msg_type=MessageType.NOTIFICATION,
            content={"type": "agent_stuck", "agent_name": "developer"},
        )
        response = agent.handle_message(msg)
        assert response is not None
        assert response.content["status"] == "acknowledged"
        assert response.content["action"] == "will_restart"

    def test_handle_standard_skill_request(self):
        agent, bus, _ = self._make_agent()
        msg = Message(
            sender="orchestrator",
            receiver="team_manager",
            msg_type=MessageType.REQUEST,
            content={
                "skill": "agent_health_monitor",
                "input_data": {
                    "agents": {},
                    "message_history": [],
                    "task_statuses": [],
                },
            },
        )
        response = agent.handle_message(msg)
        assert response is not None
        assert response.content["status"] == "success"
