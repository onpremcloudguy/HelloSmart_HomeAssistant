"""Check which hello_smart entities have None values (will show unavailable)."""
import json
import os
import sys

restore = "/config/.storage/core.restore_state"
d = json.load(open(restore))
data = d.get("data", [])

# Flat list: each item is {state: {entity_id, state, ...}, extra_data, last_seen}
smart = []
for item in data:
    s = item.get("state", {})
    eid = s.get("entity_id", "")
    if "hello_smart" in eid:
        smart.append(s)

unavail = [s for s in smart if s.get("state") in ("unavailable", "unknown")]
none_vals = [s for s in smart if s.get("state") is None or s.get("state") == "None"]

print(f"Total: {len(smart)}, unavailable: {len(unavail)}, unknown/None: {len(none_vals)}")
for s in sorted(unavail + none_vals, key=lambda x: x.get("entity_id", "")):
    eid = s.get("entity_id", "")
    short = eid.split("apac_")[-1] if "apac_" in eid else eid
    print(f"  {short}: {s.get('state')}")
