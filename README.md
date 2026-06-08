# CRM – Sales Opportunity Tracker

A simple, local web app for tracking sales deals and pipeline.

## Features

- Track opportunities through stages: Lead → Qualified → Proposal → Negotiation → Won / Lost
- Dashboard showing open deal count and pipeline value
- Filter by stage
- Add, edit, and delete opportunities
- Overdue deal highlighting

## Setup

```bash
# 1. Create a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

The SQLite database is created automatically at `instance/crm.db` on first run.

## Roadmap

- [ ] Sort table by column
- [ ] Weighted pipeline value (value × probability)
- [ ] Export to CSV
- [ ] Activity log per opportunity
