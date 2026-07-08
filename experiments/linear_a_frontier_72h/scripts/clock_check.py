#!/usr/bin/env python3
"""Mechanical finalization gate — the ONLY authority on campaign completion."""
import json, sys, datetime, os
HERE=os.path.dirname(os.path.abspath(__file__))
c=json.load(open(os.path.join(HERE,"..","CAMPAIGN_CLOCK.json")))
now=datetime.datetime.now(datetime.timezone.utc)
end=datetime.datetime.fromisoformat(c["campaign_end_utc"])
ok_time=now>=end
ok_epochs=c["completed_epochs"]>=c["minimum_epochs"]
auth=ok_time and ok_epochs
print(json.dumps({"now_utc":now.isoformat(),"campaign_end_utc":c["campaign_end_utc"],
 "hours_remaining":round((end-now).total_seconds()/3600,2),
 "completed_epochs":c["completed_epochs"],"minimum_epochs":c["minimum_epochs"],
 "time_gate":ok_time,"epoch_gate":ok_epochs,"finalization_authorized":auth},indent=1))
sys.exit(0 if auth else 1)
