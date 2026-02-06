"""Tests for the base Agent class."""

from typing import Any

import pytest

from aise.core.agent import Agent, AgentRole
from aise.core.artifact import Artifact, ArtifactStore, ArtifactType
from aise.core.message import MessageBus, MessageType
from aise.core.skill import Skill, SkillContext


class DummySkill(Skill):
    @property
    def name(self) -> str:
        return "dummy"

    @property
    def description(self) -> str:
        return "A test skill"

    def execute(self, input_data: dict[str, Any], context: SkillContext) -> Artifact:
        return Artifact(
            artifact_type=ArtifactType.REQUIREMENTS,
            content={"echo": input_data},
            producer="test",
        )


class FailingSkill(Skill):
    @property
    def name(self) -> str:
        return "failing"

    @property
    def description(self) -> str:
        return "Always fails validation"

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        return ["always fails"]

    def execute(self, input_data: dict[str, Any], context: SkillContext) -> Artifact:
        raise RuntimeError("Should not be called")


class TestAgent:
    def _make_agent(self):
        bus = MessageBus()
        store = ArtifactStore()
        return Agent("test_agent", AgentRole.DEVELOPER, bus, store), bus, store

    def test_register_and_get_skill(self):
        agent, _, _ = self._make_agent()
        skill = DummySkill()
        agent.register_skill(skill)
        assert agent.get_skill("dummy") is skill
        assert "dummy" in agent.skill_names

    def test_execute_skill(self):
        agent, _, store = self._make_agent()
        agent.register_skill(DummySkill())
        artifact = agent.execute_skill("dummy", {"hello": "world"})
        assert artifact.content == {"echo": {"hello": "world"}}
        assert store.get(artifact.id) is artifact

    def test_execute_unknown_skill(self):
        agent, _, _ = self._make_agent()
        with pytest.raises(ValueError, match="no skill"):
            agent.execute_skill("nonexistent", {})

    def test_execute_skill_validation_failure(self):
        agent, _, _ = self._make_agent()
        agent.register_skill(FailingSkill())
        with pytest.raises(ValueError, match="Invalid input"):
            agent.execute_skill("failing", {})

    def test_handle_message_request(self):
        agent, bus, _ = self._make_agent()
        agent.register_skill(DummySkill())

        from aise.core.message import Message

        msg = Message(
            sender="other",
            receiver="test_agent",
            msg_type=MessageType.REQUEST,
            content={"skill": "dummy", "input_data": {"x": 1}},
        )
        reply = agent.handle_message(msg)
        assert reply is not None
        assert reply.content["status"] == "success"

    def test_request_skill_via_bus(self):
        bus = MessageBus()
        store = ArtifactStore()
        agent_a = Agent("a", AgentRole.DEVELOPER, bus, store)
        agent_b = Agent("b", AgentRole.DEVELOPER, bus, store)
        agent_b.register_skill(DummySkill())

        results = agent_a.request_skill("b", "dummy", {"test": True})
        assert len(results) == 1
        assert results[0].content["status"] == "success"

    def test_repr(self):
        agent, _, _ = self._make_agent()
        agent.register_skill(DummySkill())
        r = repr(agent)
        assert "test_agent" in r
        assert "dummy" in r
