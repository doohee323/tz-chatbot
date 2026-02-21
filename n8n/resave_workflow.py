#!/usr/bin/env python3
"""GET workflow, PUT to re-save, print webhookId from response."""
import json
import os
import urllib.request

url = os.environ["N8N_URL"].rstrip("/")
key = os.environ["N8N_API_KEY"]
wid = os.environ.get("WORKFLOW_ID", "8t4YdniKM2RSGevA")

req = urllib.request.Request(
    f"{url}/api/v1/workflows/{wid}",
    headers={"X-N8N-API-KEY": key},
)
with urllib.request.urlopen(req) as r:
    wf = json.loads(r.read().decode())

payload = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
req2 = urllib.request.Request(
    f"{url}/api/v1/workflows/{wid}",
    data=json.dumps(payload).encode(),
    method="PUT",
    headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"},
)
with urllib.request.urlopen(req2) as r:
    res = json.loads(r.read().decode())

for n in res.get("nodes", []):
    t = n.get("type", "")
    if "chatTrigger" in t or "webhook" in t:
        print("name:", n.get("name"), "| type:", t, "| webhookId:", n.get("webhookId"))
