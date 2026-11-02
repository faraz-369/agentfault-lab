from __future__ import annotations

import json
from urllib.request import Request, urlopen

request = Request(
    "http://127.0.0.1:8000/runs",
    data=json.dumps({
        "scenario_id": "notification_timeout",
        "policy": "retry",
        "seed": 7,
    }).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(request, timeout=30) as response:
    print(json.dumps(json.loads(response.read()), indent=2))
