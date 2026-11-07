# Follow-Up Reminder Board

A tiny Flask web app for keeping track of who to follow up with and when —
the kind of board an operations executive checks every morning so no reply,
application, or recruiter thread slips through the cracks.

## What it does

- Lists follow-ups (contact, company, topic, next follow-up date, status).
- Buckets each item automatically: **overdue**, **due today**, **upcoming**, or **closed** (replied / done), with a count for each at the top of the board.
- Overdue rows are highlighted red, due-today rows amber.
- Add a new follow-up from the form on the board; change any item's status
  (waiting / replied / done) with one click.
- **Export CSV** downloads the whole list with its bucket, ready for a weekly
  status report.

Storage is a plain JSON file (`data/followups.json`), created from the sample
data on first run — no database or account setup needed.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open http://127.0.0.1:5000/ in a browser.

## Sample data

`data/sample_followups.json` ships with 6 fictional follow-ups (made-up
contacts and companies), so the board is useful the moment it starts.
Your real follow-up list lives in `data/followups.json`, which is git-ignored
and never uploaded.

## Sample output

Board header counts (for 2026-11-05):

```
Overdue: 1 | Due today: 1 | Upcoming: 3 | Closed: 1
```

CSV export (`/export.csv`):

```
id,contact,company,topic,next_followup,status,bucket
5,David Chen,HealthBridge,"Operations Lead — interview form, page 4 needs video link",2026-11-04,waiting,overdue
3,Sara Iqbal,TalentHub,"Talent & Operations intro message sent, seen",2026-11-05,waiting,due-today
```

## Tests

```bash
.venv/bin/python test_app.py
```

Checks that the board loads, the bucket counts are right, adding and
marking done works, the CSV export is correct, and bad input is rejected
with 400/404. All 5 checks pass, and the live server was verified with
`curl` (HTTP 200 on `/` and `/export.csv`).

## Files

- `app.py` — the Flask app (routes, bucket logic, CSV export)
- `templates/board.html` — the board page
- `static/style.css` — board styling
- `data/sample_followups.json` — sample follow-up data
- `test_app.py` — smoke tests using Flask's test client
- `requirements.txt` — Flask >= 3.0
