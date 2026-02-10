# Multi-Agent Software Development Team - System Design

## 1. Overview

This system implements a **multi-agent software development team** where specialized AI agents collaborate through a message-passing architecture to deliver the full software development lifecycle. Each agent has defined roles, skills, and responsibilities, and they communicate via a central orchestrator.

## 2. Agent Roles & Responsibilities

### 2.1 Product Manager Agent
**Responsibility:** Requirement Analysis & Product Design

| Skill | Description |
|-------|-------------|
| `requirement_analysis` | Parse raw user input/stories into structured requirements (functional, non-functional, constraints) |
| `user_story_writing` | Generate well-formed user stories with acceptance criteria |
| `product_design` | Produce PRDs (Product Requirement Documents) with feature specs, user flows, and priorities |
| `product_review` | Review deliverables against original requirements; flag gaps or scope drift |

### 2.2 Architect Agent
**Responsibility:** System Architecture, API Design & Technical Review

| Skill | Description |
|-------|-------------|
| `system_design` | Produce high-level architecture (component diagrams, data flow, technology choices) |
| `api_design` | Define RESTful / RPC API contracts (endpoints, schemas, error codes) |
| `architecture_review` | Review implementation against architecture; identify violations |
| `tech_stack_selection` | Recommend and justify technology choices based on requirements |

### 2.3 Developer Agent
**Responsibility:** Code Implementation, Unit Testing & Bug Fixing

| Skill | Description |
|-------|-------------|
| `code_generation` | Produce production-quality code from design specs and API contracts |
| `unit_test_writing` | Generate unit tests with edge-case coverage for implemented code |
| `code_review` | Review code for correctness, style, security, and performance |
| `bug_fix` | Diagnose and fix bugs given failing tests or error reports |

### 2.4 QA Engineer Agent
**Responsibility:** Test Planning, Test Design & Automated Test Implementation

| Skill | Description |
|-------|-------------|
| `test_plan_design` | Create system/subsystem test plans with scope, strategy, and risk analysis |
| `test_case_design` | Design detailed test cases (integration, E2E, regression) with expected results |
| `test_automation` | Implement automated test scripts from test case designs |
| `test_review` | Review test coverage and quality; identify gaps |

### 2.5 Team Lead Agent (Orchestrator)
**Responsibility:** Workflow coordination, task assignment, conflict resolution

| Skill | Description |
|-------|-------------|
| `task_decomposition` | Break high-level goals into assignable tasks for agents |
| `task_assignment` | Route tasks to the appropriate agent based on role and current workload |
| `conflict_resolution` | Mediate disagreements between agents (e.g., design vs. implementation feasibility) |
| `progress_tracking` | Track overall project status and report progress |

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      CLI / API Entry                      │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                   Team Lead (Orchestrator)                │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Workflow   │  │    Task      │  │   Progress     │  │
│  │   Engine     │  │    Queue     │  │   Tracker      │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└──────┬────────┬────────┬────────┬────────────────────────┘
       │        │        │        │
       ▼        ▼        ▼        ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│ Product  │ │Architect│ │Developer │ │    QA    │
│ Manager  │ │  Agent  │ │  Agent   │ │ Engineer │
│          │ │         │ │          │ │          │
│ Skills:  │ │ Skills: │ │ Skills:  │ │ Skills:  │
│ -require │ │ -system │ │ -code    │ │ -test    │
│ -stories │ │ -api    │ │ -unit    │ │  plan    │
│ -design  │ │ -review │ │ -review  │ │ -test    │
│ -review  │ │ -tech   │ │ -bugfix  │ │  cases   │
└─────────┘ └─────────┘ └──────────┘ │ -automate│
                                      │ -review  │
                                      └──────────┘
```

## 4. Communication Model

### 4.1 Message Format
All inter-agent communication uses a structured `Message` object:

```python
@dataclass
class Message:
    id: str                    # Unique message ID
    sender: str                # Agent name
    receiver: str              # Target agent name or "broadcast"
    msg_type: MessageType      # REQUEST, RESPONSE, REVIEW, NOTIFICATION
    content: dict              # Payload (task data, artifacts, feedback)
    timestamp: datetime
    correlation_id: str | None # Links request/response pairs
```

### 4.2 Artifact Model
Agents produce and consume typed artifacts that flow through the pipeline:

| Artifact Type | Producer | Consumer(s) |
|---------------|----------|-------------|
| `Requirements` | Product Manager | Architect, QA |
| `PRD` | Product Manager | Architect, Team Lead |
| `ArchitectureDesign` | Architect | Developer, QA |
| `APIContract` | Architect | Developer, QA |
| `SourceCode` | Developer | QA, Architect (review) |
| `UnitTests` | Developer | QA |
| `TestPlan` | QA | Team Lead, Developer |
| `TestCases` | QA | Developer |
| `AutomatedTests` | QA | Developer, Team Lead |
| `ReviewFeedback` | Any reviewer | Original producer |

## 5. Workflow Pipeline

The default development pipeline follows these phases:

```
Phase 1: Requirements      Phase 2: Design          Phase 3: Implementation
┌─────────────────────┐   ┌────────────────────┐   ┌──────────────────────┐
│ PM: analyze reqs    │──▶│ Arch: system design│──▶│ Dev: code generation │
│ PM: write stories   │   │ Arch: API design   │   │ Dev: unit tests      │
│ PM: product design  │   │ PM: design review  │   │ Arch: code review    │
│ PM: product review  │   │ Arch: arch review  │   │ Dev: bug fix (loop)  │
└─────────────────────┘   └────────────────────┘   └──────────────────────┘
                                                              │
                          Phase 5: Release         Phase 4: Testing
                          ┌──────────────────┐    ┌──────────────────────┐
                          │ TL: final report │◀───│ QA: test plan        │
                          └──────────────────┘    │ QA: test cases       │
                                                  │ QA: test automation  │
                                                  │ QA: test review      │
                                                  └──────────────────────┘
```

Each phase includes **review gates** - an agent's output must be approved before proceeding. If review fails, the artifact goes back for revision (max 3 iterations).

**Design and Implementation phases** enforce a minimum of **3 review rounds** between the work and review steps to ensure thorough quality validation. The **Implementation phase** additionally requires that all unit tests pass before the code review gate is reached (i.e., before any PR can be submitted).

## 6. Project Structure

```
AISE/
├── design.md
├── pyproject.toml
├── README.md
├── src/
│   └── aise/
│       ├── __init__.py
│       ├── main.py                 # CLI entry point
│       ├── config.py               # Configuration management
│       ├── core/
│       │   ├── __init__.py
│       │   ├── agent.py            # Base Agent class
│       │   ├── skill.py            # Base Skill class
│       │   ├── message.py          # Message & MessageBus
│       │   ├── artifact.py         # Artifact model
│       │   ├── orchestrator.py     # Team Lead orchestrator
│       │   └── workflow.py         # Pipeline / workflow engine
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── product_manager.py
│       │   ├── architect.py
│       │   ├── developer.py
│       │   ├── qa_engineer.py
│       │   └── team_lead.py
│       └── skills/
│           ├── __init__.py
│           ├── pm/                 # Product Manager skills
│           │   ├── __init__.py
│           │   ├── requirement_analysis.py
│           │   ├── user_story_writing.py
│           │   ├── product_design.py
│           │   └── product_review.py
│           ├── architect/          # Architect skills
│           │   ├── __init__.py
│           │   ├── system_design.py
│           │   ├── api_design.py
│           │   ├── architecture_review.py
│           │   └── tech_stack_selection.py
│           ├── developer/          # Developer skills
│           │   ├── __init__.py
│           │   ├── code_generation.py
│           │   ├── unit_test_writing.py
│           │   ├── code_review.py
│           │   └── bug_fix.py
│           ├── qa/                 # QA Engineer skills
│           │   ├── __init__.py
│           │   ├── test_plan_design.py
│           │   ├── test_case_design.py
│           │   ├── test_automation.py
│           │   └── test_review.py
│           └── lead/               # Team Lead skills
│               ├── __init__.py
│               ├── task_decomposition.py
│               ├── task_assignment.py
│               ├── conflict_resolution.py
│               └── progress_tracking.py
└── tests/
    ├── __init__.py
    ├── test_core/
    │   ├── __init__.py
    │   ├── test_agent.py
    │   ├── test_message.py
    │   ├── test_artifact.py
    │   ├── test_orchestrator.py
    │   └── test_workflow.py
    └── test_agents/
        ├── __init__.py
        ├── test_product_manager.py
        ├── test_architect.py
        ├── test_developer.py
        ├── test_qa_engineer.py
        └── test_team_lead.py
```

## 7. Key Design Decisions

1. **Plugin-based skills**: Each skill is a standalone class implementing a common `Skill` interface, making it easy to add/replace skills.
2. **Message bus**: Decoupled communication via a central message bus prevents tight agent coupling.
3. **Artifact registry**: A shared artifact store lets agents reference each other's outputs by type and version.
4. **Review loops**: Built-in review gates with configurable max iterations prevent infinite loops while ensuring quality.
5. **Stateless skills**: Skills are pure functions of (input artifacts + context) -> output artifacts, making them testable and composable.
6. **Configurable workflows**: The pipeline is defined declaratively, allowing different project types to use different phase sequences.
