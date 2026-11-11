<div align="center">
  <img src="tobi-logo.svg" alt="Logo de Tobi" width="250"/>
  <h1>T.O.B.I. Framework</h1>
  <p><b>T</b>raffic <b>O</b>rchestration <b>B</b>aseline for <b>I</b>ntelligence</p>

  ![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
  ![Package Manager](https://img.shields.io/badge/uv-managed-purple)
  ![Code Style](https://img.shields.io/badge/Linter-Ruff-black)
  ![License](https://img.shields.io/badge/License-Apache%202.0-green)
</div>

<br>

> *"In the era of hyper-automation, the greatest risk is not obsolescence, but vulnerability through ignorance. T.O.B.I. is the infrastructure that allows you to delegate heavy lifting to machines while maintaining learning, governance, and absolute control in human hands."*

## 📌 What is T.O.B.I.?
T.O.B.I. Framework is an Open Source methodology and object-oriented Python SDK for **Governed Agentic Workflows**, designed for Data Science and Engineering teams. It implements a dynamic routing system ("3 Lanes") that automates repetitive tasks using local and remote AI engines, while protecting critical environments (such as legal, medical, or financial sectors) through deterministic *Policy-as-Code* validations, zero-cost FinOps heuristics, and isolated vector databases (Local RAG).

## 🏗️ Architecture & Methodology (The 7 Pillars)

### 1. Dynamic Traffic System (3 Lanes)
* 🏎️ **Fast Lane (Highway):** 100% automated AI. Repetitive tasks, maximum speed, zero initial human intervention when confidence thresholds and post-validation rules are met.
* 🚗 **Middle Lane (Conventional Road):** Hybrid (80% AI / 20% Human Copilot). AI performs the heavy lifting while a human operator reviews, audits, and approves outputs.
* 🛑 **Slow Lane (Urban Road):** 100% Human. High criticality. Triggered automatically via emergency brakes when unencrypted sensitive data, severe rule violations, or critical business risks are detected.

### 2. Object-Oriented Abstraction (Plug & Play)
* **`Vehicle` (The Agent):** The standardized unit of work encapsulating `payload` (input/task data), `engine` (assigned LLM or heuristic processor), `assigned_lane`, `output`, and a unique `license_plate` (`TOBI-XXXXXX`) for end-to-end auditability.
* **`Road` (The Environment):** Pre-configured execution pipelines that enforce pre-inference rules, execute structured LLM inference with confidence thresholding, and validate outputs through post-inference rules.
* **`TrafficRule` (Policy-as-Code):** Deterministic validators with configurable severity (`WARN_TO_MIDDLE` or `BLOCK_TO_SLOW`) that inspect vehicle payloads before and after AI execution.

### 3. Privacy & Anti-Hallucination (Local RAG)
Uses a local **Qdrant** vector database as the "Policy Library" and ensures *Air-Gapped Privacy* with local Open Source LLMs via **Ollama**. If required context or policy backing is missing from the local vector database, the vehicle is automatically downgraded to the Middle Lane, enforcing zero tolerance for AI hallucinations.

### 4. Governance & Operational Security
Implementation of criticality levels (*Tiering*), safe parallel evaluations (*Shadow Deployments*, *Canary Releases*), and Chaos Engineering decoys to keep the human team sharp and prevent automation bias.

### 5. The Control Tower (Observability)
Live topological tracking, absolute traceability via an immutable **Black Box** per vehicle stored in **DuckDB** and analyzed with **Polars**, and a Stochastic Radar (*Meta-Learning*) to predict bottlenecks and trigger preventive *Early Stopping*.

### 6. Human Factor & Training
* **The Driving School:** Junior engineers learn by auditing AI-generated drafts and code in the Middle Lane under Senior supervision, turning human corrections into training gradients.
* **Error Budgets:** The automated system throttles traffic speed if it detects cognitive overload or fatigue in the human review team.

### 7. FinOps (AI Economics)
Prioritizes zero-cost deterministic heuristics (Regex, **Ruff** static analysis) before invoking GPUs or paid APIs. Combines *Model Routing* (running quantized local models like `qwen2.5-coder:3b` on local VRAM for routine tasks via **Ollama** and **RouteLLM**) with strict JSON schema enforcement (**Instructor** + **Pydantic**) and Semantic Caching.

## 🛠️ Tech Stack & Ecosystem

| Layer | Technology | Role in T.O.B.I. |
|---|---|---|
| Core & Contracts | Python 3.12+, Pydantic, Instructor | Strict typing, JSON schema enforcement, OOP genome |
| FinOps Heuristics | Ruff, Subprocess / Regex | Zero-cost code linting and pre-inference security checks |
| Local AI Engine | Ollama (`qwen2.5-coder:3b`), RouteLLM | Local GPU inference (8-bit quantized) and smart routing |
| Vector Memory | Qdrant (`:6333`), GPTCache | Local Policy RAG and semantic caching |
| Black Box & Data | DuckDB, Polars | High-speed local analytical storage for vehicle audit logs |
| Orchestration | n8n (`:5678`), MCP | Visual Middle-Lane human approval workflows and universal tool exposure |
| Package & QA | `uv`, Pytest, `direnv` | Reproducible dependency locking, unit testing, and environment isolation |

## 📂 Repository Structure

```text
tobi-framework/
├── .envrc                      # Local environment variables loaded via direnv
├── pyproject.toml              # Project metadata, Hatchling build config & dependencies
├── uv.lock                     # Deterministic dependency lockfile
├── README.md                   # Framework documentation
├── src/
│   └── tobi/
│       ├── __init__.py
│       ├── core/               # Pillar 2: Object-Oriented Genome
│       │   ├── vehicle.py      # Vehicle entity & license plate generator
│       │   ├── road.py         # 3-Lane routing logic & confidence checks
│       │   └── rules.py        # TrafficRule, Lane & RuleSeverity definitions
│       ├── engines/            # Pillar 7: AI Engines & FinOps
│       │   ├── heuristics.py   # Zero-cost validators (encryption & Ruff linter)
│       │   ├── local_llm.py    # Structured Ollama client via Instructor
│       │   └── router.py       # Dynamic model routing
│       ├── memory/             # Pillar 3: Privacy & Anti-Hallucination
│       │   ├── policy_rag.py   # Qdrant local policy verification
│       │   └── cache.py        # Semantic caching layer
│       ├── tower/              # Pillars 5 & 6: Control Tower & Human Factor
│       │   ├── blackbox.py     # DuckDB & Polars audit persistence
│       │   └── error_budget.py # Human cognitive load & fatigue tracking
│       └── interfaces/         # External Bridges
│           ├── mcp_server.py   # Model Context Protocol (MCP) exposure
│           └── n8n_bridge.py   # Shared-folder bridge for Middle Lane reviews
└── tests/
    └── test_core_phase2.py     # Unit tests for 3-Lane routing & heuristics

```

## 🚀 Quickstart & Installation

### 1. Prerequisites

* **Python 3.12+** and **[uv](https://github.com/astral-sh/uv)** installed.
* **Ollama** running locally on `http://localhost:11434` with `qwen2.5-coder:3b` pulled.
* **Qdrant** running on `http://localhost:6333` (for Phase 3+ memory modules).

### 2. Setup Environment

```bash
# Clone the repository
git clone [https://github.com/alay-maker/TOBI-Framework.git](https://github.com/alay-maker/TOBI-Framework.git)
cd TOBI-Framework

# Sync virtual environment and install package in editable mode
uv sync

# Configure environment variables (or use direnv)
export OLLAMA_BASE_URL="http://localhost:11434"
export QDRANT_URL="http://localhost:6333"
export TOBI_STORAGE_PATH="$HOME/storage/tobi-data"

```

### 3. SDK Usage Example

```python
from tobi.core.road import Road
from tobi.core.rules import Lane, RuleSeverity, TrafficRule
from tobi.core.vehicle import Vehicle
from tobi.engines.heuristics import (
    check_encryption_compliance,
    validate_python_code_with_ruff,
)

# 1. Configure a governed Road with Pre and Post TrafficRules
dev_road = Road(name="TOBI_Module_Development", confidence_threshold=0.85)

dev_road.add_pre_rule(
    TrafficRule(
        rule_id="SEC-01",
        description="Emergency brake on unencrypted sensitive data",
        severity=RuleSeverity.BLOCK_TO_SLOW,
        validator=check_encryption_compliance,
    )
)

dev_road.add_post_rule(
    TrafficRule(
        rule_id="QUAL-01",
        description="Zero-cost Python syntax and lint check via Ruff",
        severity=RuleSeverity.WARN_TO_MIDDLE,
        validator=validate_python_code_with_ruff,
    )
)

# 2. Dispatch a Vehicle onto the Road
vehicle = Vehicle(
    engine="qwen2.5-coder:3b",
    payload={
        "contains_sensitive_data": True,
        "is_encrypted": True,
        "prompt": "Write a typed Python function that calculates Fibonacci numbers.",
    },
)

result = dev_road.transit(vehicle, run_llm=True)

print(f"License Plate: {result.license_plate}")
print(f"Assigned Lane: {result.assigned_lane.value}")
print(f"Audit Log: {result.audit_log}")
```

### 4. Running Tests & Code Quality

```bash
# Run unit test suite
uv run pytest -v

# Run zero-cost static analysis and formatting checks
uv run ruff check .
uv run ruff format --check .

```

## 🗺️ Development Roadmap (MVP)

* [x] **Phase 1: Environment & Foundations** — Modular `src/tobi` architecture, `uv` reproducible build system, `.envrc` configuration, and storage isolation.
* [x] **Phase 2: Core OOP Genome & Local FinOps** — `Vehicle`, `Road`, and `TrafficRule` entities, zero-cost `Ruff` & encryption heuristics, structured local inference with Ollama + Instructor, and unit test suite.
* [ ] **Phase 3: Anti-Hallucination Policy Library & Black Box** — Automated DuckDB/Polars audit logging (`vehicles_audit`) and Qdrant vector validation (`policy_library`).
* [ ] **Phase 4: Middle-Lane n8n Bridge & Self-Construction via MCP** — Human-in-the-loop review workflows via `/data/shared` in n8n and MCP server exposure.

## ⚠️ Disclaimer

This project is a conceptual template and functional prototype (MVP) developed as part of research on Agile-AI methodologies.

**It is NOT guaranteed for use in critical production environments (Tier 3).**
The author is not responsible for data loss, service interruptions, unforeseen API costs, or algorithmic biases that may arise from implementing this architecture. Any team deciding to implement this methodology must conduct their own audits. It is provided "As-Is" under the Apache 2.0 license.

*Inspired by Tobi. Built for the future.*
