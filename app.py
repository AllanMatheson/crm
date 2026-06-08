from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Opportunity, STAGES, STAGE_PROBABILITY
from datetime import datetime, date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SECRET_KEY"] = "change-me-in-production"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    stage_filter = request.args.get("stage", "")
    query = Opportunity.query
    if stage_filter:
        query = query.filter_by(stage=stage_filter)
    opportunities = query.order_by(Opportunity.close_date.asc()).all()

    total_value = sum(o.value or 0 for o in opportunities if o.stage not in ("Won", "Lost"))
    won_value = sum(o.value or 0 for o in opportunities if o.stage == "Won")
    open_count = sum(1 for o in opportunities if o.stage not in ("Won", "Lost"))
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
        opp.company = request.form["company"]
        opp.contact_name = request.form.get("contact_name")
        opp.contact_email = request.form.get("contact_email")
        opp.title = request.form["title"]
        opp.value = float(request.form["value"]) if request.form.get("value") else None
        opp.stage = request.form["stage"]
        opp.probability = int(request.form.get("probability") or STAGE_PROBABILITY[request.form["stage"]])
        opp.close_date = datetime.strptime(request.form["close_date"], "%Y-%m-%d").date() if request.form.get("close_date") else None
        opp.notes = request.form.get("notes")
        opp.updated_at = datetime.utcnow()
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


if __name__ == "__main__":
    app.run(debug=True)
