# Threat model

## Current trust boundary

The current implementation runs a fixed simulator and allowlisted tool functions. It does not execute arbitrary Python code supplied through the API.

## Assets

- Local scenario files.
- Run traces and state snapshots.
- Experiment metadata.
- Any future tool credentials or user-provided data.

## Risks

- Traces may contain secrets if users put them in scenario arguments or state.
- The API has no authentication and should not be exposed to an untrusted network.
- Scenario files are loaded from the local filesystem.
- A future plugin/adapter system could accidentally grant real state-changing capabilities to an experiment.

## Mitigations

- Bind the API to `127.0.0.1` for local use.
- Avoid secrets and personal data in test scenarios.
- Use synthetic state and mock tools.
- Add authentication, rate limiting, and authorization before remote deployment.
- If arbitrary code execution is ever added, use a dedicated sandbox with resource limits, filesystem isolation, network restrictions, and no inherited credentials.
- Use allowlists for real tool integrations and require explicit opt-in for state-changing operations.

## Non-goals

This prototype is not a secure multi-tenant service and has not undergone a formal security audit.
