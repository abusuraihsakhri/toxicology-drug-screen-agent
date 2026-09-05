# Toxicology Drug Screen Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** CAP / CLSI / ISO Standards, AACT / EAPCCT Poisoning Consensus

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Toxicology Drug Screen Agent** is an advanced analytical and computational platform implementing Immunoassay Cross-Reactivity & Confirmatory LC-MS/MS Planner. It cross-references urine drug immunoassay presumptive positives with prescribed medications, identifying false-positive cross-reactivities and LC-MS targets.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`ImmunoassayCrossReactivityAgent`**: Specialized Sub-Agent 1 for toxicology-drug-screen-agent
- **`PrescriptionReconcilerAgent`**: Specialized Sub-Agent 2 for toxicology-drug-screen-agent
- **`LCMSConfirmatoryPlannerAgent`**: Specialized Sub-Agent 3 for toxicology-drug-screen-agent

### 🏗️ Architecture

The project contains two parallel implementations:

| Module | Description |
|--------|-------------|
| `agents/` | Enterprise-grade implementation with Pydantic models, HMAC audit trail, PHI guard |
| `toxicology_drug_screen_agent/` | Clinical-focused implementation with dataclass models, AACT/EAPCCT standards |
| `tox_screen_agent.py` | Standalone CLI agent with FastAPI server |
| `enrichment.py` | LC-MS/MS confirmatory target generation and drug concentration modeling |

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/toxicology-drug-screen-agent.git
cd toxicology-drug-screen-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Optional: Set audit secret key for persistent audit trail
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Case Audit
```bash
# Using the enterprise agent
python cli.py audit --task-id CASE-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT

# Using the standalone agent
python tox_screen_agent.py audit --case-id CASE-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task / case identifier
- `--target`: Entity, patient key, or target identifier
- `--primary`: Primary domain measurement or score (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--critical`: Emergency escalation flag
- `--status`: Status code or phenotype descriptor

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Unique case identifier | Required |
| `patient_synthetic_id` | Anonymized patient identifier | Required |
| `metric_primary` | Primary measurement value | Required |
| `metric_secondary` | Secondary measurement value | Required |
| `is_stat` | STAT priority flag | Required |
| `status_flag` | Status descriptor | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Path Traversal Protection:** Batch file operations validate paths remain within the working directory.
* **Input Validation:** Numeric parameters validated as finite numbers; CSV rows with invalid data are skipped with warnings.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable to ensure audit trail persistence across restarts:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Windows PowerShell
$env:AUDIT_SECRET_KEY = -join ((1..32) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Run specific test files:

```bash
pytest tests/ -v
pytest test_tox_screen_agent.py -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t toxicology-drug-screen-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secret-key" toxicology-drug-screen-agent
```

---

## 📁 Project Structure

```
toxicology-drug-screen-agent/
├── agents/                          # Enterprise agent implementation
│   ├── __init__.py
│   ├── api.py                       # FastAPI REST server
│   ├── base.py                      # PHI guard, HMAC audit trail
│   ├── learning.py                  # Bayesian calibration engine
│   ├── llm_factory.py               # LLM provider factory
│   ├── metrics.py                   # Prometheus metrics
│   ├── models.py                    # Pydantic data models
│   ├── streamer.py                  # WebSocket telemetry
│   ├── supervisor.py                # Master coordinator
│   └── workers.py                   # Specialized worker agents
├── toxicology_drug_screen_agent/    # Clinical agent implementation
│   ├── __init__.py
│   ├── agents.py                    # Sub-agents coordinator
│   ├── cli.py                       # CLI interface
│   ├── engine.py                    # Clinical domain engine
│   ├── models.py                    # Dataclass models
│   └── server.py                    # FastAPI server
├── tests/                           # Test suite
│   ├── test_enrichment.py
│   └── test_toxicology_drug_screen_agent.py
├── test_tox_screen_agent.py        # Standalone agent tests
├── cli.py                           # Main CLI entry point
├── tox_screen_agent.py              # Standalone agent
├── enrichment.py                    # LC-MS/MS enrichment features
├── simulator.py                     # High-throughput simulator
├── sample.csv                       # Sample input data
├── sample_payload.json              # Sample API payload
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Docker Compose config
└── pyproject.toml                   # Project metadata
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
