# Security policy

AgentFault Lab is a local research prototype, not a hardened multi-tenant service.
The API has no authentication or authorization and should only be bound to localhost
unless it is placed behind appropriate access controls.

The current runner uses an allowlist of simulated tools and does not execute arbitrary
scenario-provided Python. Scenario inputs and traces may still contain sensitive values;
use synthetic data and review outputs before sharing them.

Please report suspected security issues privately to the repository maintainer rather
than publishing exploit details before a fix is available. No dedicated security email
is configured in this prototype, so use the repository host's private vulnerability
reporting feature when available.
