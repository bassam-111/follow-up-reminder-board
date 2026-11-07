"""Follow-Up Reminder Board — a tiny Flask app for operations follow-ups.

Keeps a list of people / accounts to follow up with, the next follow-up date,
and the status of each one. Overdue items are highlighted on the board, and
the list can be exported as CSV for a weekly report.

Storage is a plain JSON file (data/followups.json) so the whole app stays
dependency-light and easy to run locally. No database, no accounts.
"""

import csv
import io
import json
import os
from datetime import date

from flask import Flask, abort, redirect, render_template, request, Response, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "followups.json")
SEED_FILE = os.path.join(BASE_DIR, "data", "sample_followups.json")

app = Flask(__name__)

STATUSES = ["waiting", "replied", "done"]


def load_followups():
    """Load follow-ups from the JSON store; fall back to the sample data."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_followups(items):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def classify(item, today=None):
    """Return 'overdue', 'due-today', 'upcoming' or 'closed' for one item."""
    today = today or date.today()
    if item["status"] in ("replied", "done"):
        return "closed"
    due = date.fromisoformat(item["next_followup"])
    if due < today:
        return "overdue"
    if due == today:
        return "due-today"
    return "upcoming"


def summary(items, today=None):
    """Counts per bucket, for the header stats on the board."""
    counts = {"overdue": 0, "due-today": 0, "upcoming": 0, "closed": 0}
    for item in items:
        counts[classify(item, today)] += 1
    return counts


@app.route("/")
def board():
    items = load_followups()
    today = date.today()
    decorated = sorted(
        ((item, classify(item, today)) for item in items),
        key=lambda pair: (pair[1] != "overdue", pair[0]["next_followup"]),
    )
    return render_template(
        "board.html",
        items=decorated,
        counts=summary(items, today),
        today=today.isoformat(),
        statuses=STATUSES,
    )


@app.route("/add", methods=["POST"])
def add():
    contact = request.form.get("contact", "").strip()
    topic = request.form.get("topic", "").strip()
    next_followup = request.form.get("next_followup", "").strip()
    if not contact or not topic or not next_followup:
        abort(400, "Contact, topic and next follow-up date are all required.")
    date.fromisoformat(next_followup)  # raises ValueError on a bad date
    items = load_followups()
    new_id = max((item["id"] for item in items), default=0) + 1
    items.append(
        {
            "id": new_id,
            "contact": contact,
            "company": request.form.get("company", "").strip(),
            "topic": topic,
            "next_followup": next_followup,
            "status": "waiting",
        }
    )
    save_followups(items)
    return redirect(url_for("board"))


@app.route("/status/<int:item_id>/<status>", methods=["POST"])
def set_status(item_id, status):
    if status not in STATUSES:
        abort(400, "Unknown status.")
    items = load_followups()
    for item in items:
        if item["id"] == item_id:
            item["status"] = status
            break
    else:
        abort(404, "Follow-up not found.")
    save_followups(items)
    return redirect(url_for("board"))


@app.route("/export.csv")
def export_csv():
    items = load_followups()
    today = date.today()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "contact", "company", "topic", "next_followup", "status", "bucket"])
    for item in sorted(items, key=lambda i: i["next_followup"]):
        writer.writerow(
            [
                item["id"],
                item["contact"],
                item["company"],
                item["topic"],
                item["next_followup"],
                item["status"],
                classify(item, today),
            ]
        )
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=followups.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
