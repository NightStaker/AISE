"""Architect agent."""

from __future__ import annotations

from ..core.agent import Agent, AgentRole
from ..core.artifact import ArtifactStore
from ..core.message import MessageBus
from ..skills.architect import (
    APIDesignSkill,
    ArchitectureReviewSkill,
    SystemDesignSkill,
    TechStackSelectionSkill,
)


class ArchitectAgent(Agent):
    """Agent responsible for system architecture, API design, and technical review."""

    def __init__(self, message_bus: MessageBus, artifact_store: ArtifactStore) -> None:
        super().__init__(
            name="architect",
            role=AgentRole.ARCHITECT,
            message_bus=message_bus,
            artifact_store=artifact_store,
        )
        self.register_skill(SystemDesignSkill())
        self.register_skill(APIDesignSkill())
        self.register_skill(ArchitectureReviewSkill())
        self.register_skill(TechStackSelectionSkill())
