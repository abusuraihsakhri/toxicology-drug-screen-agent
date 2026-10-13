# Toxicology Drug Screen Agent

Python command-line tools, FastAPI endpoints, and a browser-only rule demonstration for synthetic screening examples. Three parallel Python interfaces have different schemas and are retained for compatibility.

**Important limitation:** The built-in numeric thresholds are arbitrary software constants, **not** validated toxicology cutoffs or laboratory reference intervals. This project does not identify drugs, calculate assay-specific cross-reactivity, interpret LC-MS/MS data, or recommend actual confirmatory analytes. Do not use it to diagnose, triage, treat, or otherwise make clinical decisions.

## Available interfaces

- **Root Python CLI / agents package:** Three deterministic checks, an in-memory HMAC-linked audit log, mock chat, JSON FastAPI endpoints.
- **toxicology_drug_screen_agent package:** Separate clinical-labelled dataclass rules, CLI and optional API.
- **tox_screen_agent.py:** Independent CLI/coordinator and optional API.
- **enrichment.py:** Placeholder threshold-checking objects, not validated pharmacokinetics or cross-reactivity algorithms.
- **web/index.html:** Offline, deterministic browser demonstration mirroring the root worker thresholds (primary >25, secondary >12, critical flag or status keywords), with JSON export. No server or Python runtime is necessary.

## Installation and examples

Requires Python 3.9+; CI covers Python 3.10–3.13. Install from a repository checkout:

~~~bash
python -m pip install -e '.[api,test]'
python cli.py audit --task-id DEMO-1 --target SAMPLE-1 --primary 28 --secondary 14 --status DISCORDANT
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
~~~

The root CLI batch command expects columns such as task_id, target_identifier, primary_metric and secondary_metric. The bundled sample.csv instead uses the clinical-labelled schema:

~~~bash
python toxicology_drug_screen_agent_app.py batch -i sample.csv -o results.csv
~~~

Other interfaces:

~~~bash
toxicology-drug-screen-engine audit --case-id DEMO-1 --primary 1 --secondary 1 --status NORMAL
python tox_screen_agent.py audit --case-id DEMO-1 --primary 26 --secondary 13
python tox_screen_agent.py batch -i sample.csv -o results.csv
~~~

Open web/index.html directly in a modern browser for the static demo. It works without an application server. GitHub Pages deployment is defined in .github/workflows/pages.yml; the public URL must be verified after the workflow succeeds.

## Security and data handling

The browser executes local JavaScript without network requests, third-party assets or browser storage. JSON is downloaded only when requested. Use synthetic identifiers only.

Python's identifier guard uses limited regular expressions; **it cannot guarantee PHI removal or HIPAA compliance**. The server APIs have no authentication and must not be exposed for clinical production use. Audits are in-memory, signed with AUDIT_SECRET_KEY (or an ephemeral key if unset) and are not durable records. HMAC checks detect modification of recorded fields, provided the key and process remain trusted.

Supply a unique secret through the environment for Docker Compose:

~~~bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
~~~

The enterprise API provides /health, /api/audit, /api/chat and /api/audit/logs; /metrics currently returns JSON counts, not Prometheus exposition format. Localhost usage does not provide an authorization or privacy boundary for remote access.

## Testing

~~~bash
python -m pytest -q
node web/test_app.cjs
~~~

The GitHub Actions matrix installs the Python package, runs regression tests and checks the JavaScript demo. Docker starts the enterprise FastAPI application; it does not serve web/index.html.

## License

MIT — see [LICENSE](LICENSE).
