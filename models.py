from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

STAGES = ["Lead", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
STAGE_PROBABILITY = {
    "Lead": 10,
    "Qualified": 25,
    "Proposal": 50,
    "Negotiation": 75,
    "Won": 100,
    "Lost": 0,
}

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float)
    stage = db.Column(db.String(50), nullable=False, default="Lead")
    probability = db.Column(db.Integer, default=10)
    close_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
