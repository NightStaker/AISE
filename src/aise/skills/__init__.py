"""All agent skills."""

from .architect import (
    APIDesignSkill,
    ArchitectureReviewSkill,
    SystemDesignSkill,
    TechStackSelectionSkill,
)
from .developer import (
    BugFixSkill,
    CodeGenerationSkill,
    CodeReviewSkill,
    UnitTestWritingSkill,
)
from .github import (
    PRMergeSkill,
    PRReviewSkill,
)
from .lead import (
    ConflictResolutionSkill,
    ProgressTrackingSkill,
    TaskAssignmentSkill,
    TaskDecompositionSkill,
)
from .manager import (
    AgentHealthMonitorSkill,
    AgentRestartSkill,
    ArchitectureOptimizationSkill,
    CodeOptimizationSkill,
)
from .pm import (
    ProductDesignSkill,
    ProductReviewSkill,
    RequirementAnalysisSkill,
    UserStoryWritingSkill,
)
from .qa import (
    TestAutomationSkill,
    TestCaseDesignSkill,
    TestPlanDesignSkill,
    TestReviewSkill,
)

__all__ = [
    # PM
    "RequirementAnalysisSkill",
    "UserStoryWritingSkill",
    "ProductDesignSkill",
    "ProductReviewSkill",
    # Architect
    "SystemDesignSkill",
    "APIDesignSkill",
    "ArchitectureReviewSkill",
    "TechStackSelectionSkill",
    # Developer
    "CodeGenerationSkill",
    "UnitTestWritingSkill",
    "CodeReviewSkill",
    "BugFixSkill",
    # QA
    "TestPlanDesignSkill",
    "TestCaseDesignSkill",
    "TestAutomationSkill",
    "TestReviewSkill",
    # Lead
    "TaskDecompositionSkill",
    "TaskAssignmentSkill",
    "ConflictResolutionSkill",
    "ProgressTrackingSkill",
    # Manager
    "AgentHealthMonitorSkill",
    "AgentRestartSkill",
    "ArchitectureOptimizationSkill",
    "CodeOptimizationSkill",
    # GitHub
    "PRReviewSkill",
    "PRMergeSkill",
]
