"""Quick smoke tests for the Follow-Up Reminder Board (uses Flask test client)."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as board  # noqa: E402

client = board.app.test_client()

# 1. Board page loads.
resp = client.get("/")
assert resp.status_code == 200, resp.status_code
html = resp.get_data(as_text=True)
assert "Follow-Up Reminder Board" in html
print("1. board loads: OK")

# 2. Bucket counts: 2026-11-05 is 'today' in the sample data.
#    overdue: HealthBridge (11-04); due-today: Sara Iqbal (11-05); closed: Kenji Tanaka (replied).
counts = board.summary(board.load_followups(), today=date(2026, 11, 5))
assert counts == {"overdue": 1, "due-today": 1, "upcoming": 3, "closed": 1}, counts
print("2. bucket summary for 2026-11-05:", counts, "OK")

# 3. Add a follow-up, then change its status to done.
resp = client.post("/add", data={"contact": "Test Person", "company": "Test Co",
                                 "topic": "Test topic", "next_followup": "2026-11-12"})
assert resp.status_code == 302, resp.status_code
items = board.load_followups()
new = [i for i in items if i["contact"] == "Test Person"]
assert len(new) == 1
resp = client.post(f"/status/{new[0]['id']}/done")
assert resp.status_code == 302
assert [i for i in board.load_followups() if i["id"] == new[0]["id"]][0]["status"] == "done"
print("3. add + mark done: OK")

# 4. CSV export contains the header and the new row.
resp = client.get("/export.csv")
assert resp.status_code == 200 and "text/csv" in resp.content_type
csv_text = resp.get_data(as_text=True)
assert "id,contact,company,topic,next_followup,status,bucket" in csv_text
assert "Test Person" in csv_text
print("4. CSV export: OK")

# 5. Bad input is rejected (missing fields, bad date, unknown status).
assert client.post("/add", data={"contact": "", "topic": "x", "next_followup": "2026-11-12"}).status_code == 400
assert client.post("/status/1/nope").status_code == 400
assert client.post("/status/999/done").status_code == 404
print("5. validation errors (400/404): OK")

# Clean up the test row so the store matches the sample data again.
items = [i for i in board.load_followups() if i["contact"] != "Test Person"]
board.save_followups(items)
print("Cleanup: test row removed. All tests passed.")
