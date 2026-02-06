"""Configuration management for the AISE system."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""

    name: str
    enabled: bool = True


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""

    max_review_iterations: int = 3
    fail_on_review_rejection: bool = False


@dataclass
class ProjectConfig:
    """Top-level project configuration."""

    project_name: str = "Untitled Project"
    agents: dict[str, AgentConfig] = field(default_factory=lambda: {
        "product_manager": AgentConfig(name="product_manager"),
        "architect": AgentConfig(name="architect"),
        "developer": AgentConfig(name="developer"),
        "qa_engineer": AgentConfig(name="qa_engineer"),
        "team_lead": AgentConfig(name="team_lead"),
    })
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
