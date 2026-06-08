import csv
import io
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from models import db, Opportunity, Contact, STAGES, STAGE_PROBABILITY
from datetime import datetime, date

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
# Render uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
db.init_app(app)

with app.app_context():
    db.create_all()

SORT_FIELDS = {
    "title":      Opportunity.title,
    "company":    Opportunity.company,
    "value":      Opportunity.value,
    "stage":      Opportunity.stage,
    "probability":Opportunity.probability,
    "close_date": Opportunity.close_date,
}


@app.route("/")
def index():
    stage_filter = request.args.get("stage", "")
    sort_by      = request.args.get("sort", "close_date")
    sort_dir     = request.args.get("dir", "asc")

    query = Opportunity.query
    if stage_filter:
        query = query.filter_by(stage=stage_filter)

    col = SORT_FIELDS.get(sort_by, Opportunity.close_date)
    query = query.order_by(col.desc() if sort_dir == "desc" else col.asc())
    opportunities = query.all()

    total_value = sum(o.value or 0 for o in opportunities if o.stage not in ("Won", "Lost"))
    won_value   = sum(o.value or 0 for o in opportunities if o.stage == "Won")
    open_count  = sum(1 for o in opportunities if o.stage not in ("Won", "Lost"))
    today = date.today()

    return render_template(
        "index.html",
        opportunities=opportunities,
        stages=STAGES,
        stage_filter=stage_filter,
        total_value=total_value,
        won_value=won_value,
        open_count=open_count,
        today=today,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@app.route("/export")
def export():
    stage_filter = request.args.get("stage", "")
    query = Opportunity.query
    if stage_filter:
        query = query.filter_by(stage=stage_filter)
    opportunities = query.order_by(Opportunity.close_date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Company", "Contact", "Value", "Stage", "Probability %", "Close Date", "Notes"])
    for o in opportunities:
        writer.writerow([
            o.title, o.company, o.contact_name or "",
            o.value or "", o.stage, o.probability,
            o.close_date.strftime("%Y-%m-%d") if o.close_date else "",
            o.notes or "",
        ])

    filename = f"crm-export-{date.today()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/new", methods=["GET", "POST"])
def new_opportunity():
    if request.method == "POST":
        opp = Opportunity(
            company=request.form["company"],
            contact_name=request.form.get("contact_name"),
            contact_email=request.form.get("contact_email"),
            title=request.form["title"],
            value=float(request.form["value"]) if request.form.get("value") else None,
            stage=request.form["stage"],
            probability=int(request.form.get("probability") or STAGE_PROBABILITY[request.form["stage"]]),
            close_date=datetime.strptime(request.form["close_date"], "%Y-%m-%d").date() if request.form.get("close_date") else None,
            notes=request.form.get("notes"),
        )
        db.session.add(opp)
        db.session.commit()
        flash("Opportunity created!", "success")
        return redirect(url_for("index"))
    return render_template("form.html", opp=None, stages=STAGES, stage_probabilities=STAGE_PROBABILITY)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    if request.method == "POST":
        opp.company       = request.form["company"]
        opp.contact_name  = request.form.get("contact_name")
        opp.contact_email = request.form.get("contact_email")
        opp.title         = request.form["title"]
        opp.value         = float(request.form["value"]) if request.form.get("value") else None
        opp.stage         = request.form["stage"]
        opp.probability   = int(request.form.get("probability") or STAGE_PROBABILITY[request.form["stage"]])
        opp.close_date    = datetime.strptime(request.form["close_date"], "%Y-%m-%d").date() if request.form.get("close_date") else None
        opp.notes         = request.form.get("notes")
        opp.updated_at    = datetime.utcnow()
        db.session.commit()
        flash("Opportunity updated!", "success")
        return redirect(url_for("index"))
    return render_template("form.html", opp=opp, stages=STAGES, stage_probabilities=STAGE_PROBABILITY)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(opp)
        db.session.commit()
        flash("Opportunity deleted.", "info")
        return redirect(url_for("index"))
    return render_template("confirm_delete.html", opp=opp)


@app.route("/contacts")
def contacts():
    search = request.args.get("q", "")
    query = Contact.query
    if search:
        query = query.filter(
            Contact.name.ilike(f"%{search}%") |
            Contact.company.ilike(f"%{search}%")
        )
    contacts = query.order_by(Contact.company, Contact.name).all()
    return render_template("contacts.html", contacts=contacts, search=search)


if __name__ == "__main__":
    app.run(debug=True)
