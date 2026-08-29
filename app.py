
import os, sqlite3, json, math
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gram-mitra-change-this-secret")
app.config["DATABASE"] = os.path.join(BASE_DIR, "gram_mitra.db")

def db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

with app.app_context():
    init_db()

def load_json(filename):
    with open(os.path.join(BASE_DIR, "data", filename), "r", encoding="utf-8") as f:
        return json.load(f)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def current_user():
    if "user_id" not in session:
        return None
    conn = db()
    user = conn.execute("SELECT id, name, email FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()
    return dict(user) if user else None

@app.route("/")
def index():
    return render_template("index.html", user=current_user())

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(name) < 2 or "@" not in email or len(password) < 6:
            return render_template("signup.html", error="Enter a valid name, email and a password of at least 6 characters.", user=current_user(), signup=True)
        conn = db()
        try:
            cur = conn.execute(
                "INSERT INTO users(name,email,password,created_at) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), datetime.now().isoformat())
            )
            conn.commit()
            session["user_id"] = cur.lastrowid
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="An account with this email already exists.", user=current_user(), signup=True)
        finally:
            conn.close()
    return render_template("signup.html", user=current_user(), signup=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Incorrect email or password.", user=current_user(), signup=False)
    return render_template("login.html", user=current_user(), signup=False)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())

@app.route("/analysis")
@login_required
def analysis():
    return render_template("business_analysis.html", user=current_user())

@app.route("/copilot")
@login_required
def copilot():
    return render_template("copilot.html", user=current_user())

@app.route("/report")
@login_required
def report():
    return render_template("report.html", user=current_user())

@app.route("/api/locations")
@login_required
def api_locations():
    return jsonify(load_json("locations.json"))

@app.route("/api/categories")
@login_required
def api_categories():
    return jsonify(load_json("business_categories.json"))

@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    data = request.get_json(force=True)
    district = data.get("district", "Karnataka")
    taluk = data.get("taluk", "")
    village = data.get("village", "")
    category = data.get("category", "Retail & Services")
    capital = max(0, float(data.get("capital", 0) or 0))
    address = data.get("address", "")

    categories = load_json("business_categories.json")
    info = categories.get(category, categories["Retail & Services"])
    month = datetime.now().month
    season = "Monsoon" if month in [6,7,8,9] else ("Summer" if month in [3,4,5] else "Festival / Harvest")

    district_bonus = {
        "Bengaluru Urban": 1.2, "Mysuru": 0.9, "Dakshina Kannada": 1.0,
        "Udupi": 0.9, "Belagavi": 0.7, "Dharwad": 0.7,
        "Tumakuru": 0.6, "Shivamogga": 0.7, "Kodagu": 0.8
    }.get(district, 0.45)

    base_cost = float(info["typical_project_cost"])
    viability = min(9.8, max(4.5, 6.2 + district_bonus + (0.5 if capital >= base_cost*0.1 else -0.4)))
    required_margin = round(base_cost * 0.10)
    eligible_loan = round(base_cost * 0.90)
    capital_gap = max(0, required_margin - capital)
    annual_rate = float(info["interest_rate"])
    years = int(info["repayment_years"])
    quarterly_rate = annual_rate / 4 / 100
    quarters = years * 4
    quarterly_payment = round((eligible_loan * quarterly_rate * (1 + quarterly_rate)**quarters) /
                              (((1 + quarterly_rate)**quarters) - 1)) if quarterly_rate else round(eligible_loan/quarters)

    best_businesses = info["best_businesses"]
    swot = info["swot"]
    result = {
        "location": {"district": district, "taluk": taluk, "village": village, "address": address},
        "category": category,
        "season": season,
        "viability_score": round(viability, 1),
        "market_opportunity": info["market_opportunity"],
        "competitor_density": info["competitor_density"],
        "seasonal_analysis": f"{season} conditions can influence demand. For {category}, focus on {info['season_tip']}.",
        "best_businesses": best_businesses,
        "swot": swot,
        "threats": info["threats"],
        "pricing": info["pricing"],
        "market_reach": info["market_reach"],
        "working_capital": round(base_cost * 0.15),
        "project_cost": round(base_cost),
        "required_margin": required_margin,
        "available_capital": round(capital),
        "capital_gap": round(capital_gap),
        "loan_90": eligible_loan,
        "scheme": info["scheme"],
        "interest_rate": annual_rate,
        "repayment_years": years,
        "quarterly_payment": quarterly_payment,
        "summary": f"{category} in {district} shows a {round(viability,1)}/10 indicative viability score based on location, category and available margin capital. This is an advisory estimate and final financing depends on the lender and official scheme eligibility."
    }
    return jsonify(result)

@app.route("/api/copilot", methods=["POST"])
@login_required
def api_copilot():
    data = request.get_json(force=True)
    message = (data.get("message") or "").lower()
    lang = data.get("lang", "en")
    if lang == "kn":
        if any(w in message for w in ["loan", "ಸಾಲ", "em i", "emi"]):
            answer = "ನಿಮ್ಮ ಯೋಜನಾ ವೆಚ್ಚದ 10% ಮಾರ್ಜಿನ್ ಹಣವನ್ನು ಮೊದಲು ಪರಿಶೀಲಿಸಿ. ಉಳಿದ 90% ಹಣಕಾಸು ಆಯ್ಕೆಗಳನ್ನು ಯೋಜನೆಯ ಅರ್ಹತೆ ಮತ್ತು ಸಾಲದಾತರ ನಿಯಮಗಳ ಪ್ರಕಾರ ಪರಿಶೀಲಿಸಬಹುದು. ನಿಮ್ಮ ವ್ಯವಹಾರ ವರ್ಗ ಮತ್ತು ಜಿಲ್ಲೆಯನ್ನು ಕಳುಹಿಸಿದರೆ ನಾನು ಉತ್ತಮವಾಗಿ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತೇನೆ."
        elif any(w in message for w in ["business", "ವ್ಯವಹಾರ", "idea", "ಐಡಿಯಾ"]):
            answer = "ನಿಮ್ಮ ಜಿಲ್ಲೆ, ತಾಲೂಕು, ಲಭ್ಯವಿರುವ ಬಂಡವಾಳ ಮತ್ತು ಆಸಕ್ತಿಯ ವ್ಯವಹಾರ ಕ್ಷೇತ್ರವನ್ನು ತಿಳಿಸಿ. ನಾನು ಮಾರುಕಟ್ಟೆ ಅವಕಾಶ, ಸ್ಪರ್ಧೆ ಮತ್ತು ಆರಂಭಿಕ ವೆಚ್ಚದ ಬಗ್ಗೆ ಸಲಹೆ ನೀಡುತ್ತೇನೆ."
        else:
            answer = "ಖಂಡಿತ! ನಿಮ್ಮ ವ್ಯವಹಾರ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆಯನ್ನು ವಿವರವಾಗಿ ಬರೆಯಿರಿ. ಸ್ಥಳ, ಬಂಡವಾಳ ಮತ್ತು ವ್ಯವಹಾರ ಕ್ಷೇತ್ರ ತಿಳಿಸಿದರೆ ಹೆಚ್ಚು ಉಪಯುಕ್ತ ಸಲಹೆ ನೀಡಬಹುದು."
    else:
        if any(w in message for w in ["loan", "emi", "repay"]):
            answer = "Start by checking whether your available capital covers the expected 10% margin. The remaining financing and repayment terms must be confirmed against the applicable scheme and lender rules. Tell me your district, business category and project budget for a more specific estimate."
        elif any(w in message for w in ["business", "idea", "start"]):
            answer = "Tell me your district, taluk, available capital and business category. I can help compare market opportunity, competition, seasonal demand, working capital and an indicative project cost."
        else:
            answer = "I can help with business feasibility, market opportunity, competition, pricing, working capital and financing estimates. What are you planning to start?"
    return jsonify({"answer": answer})

@app.route("/download-report", methods=["POST"])
@login_required
def download_report():
    data = request.get_json(force=True)
    path = os.path.join(BASE_DIR, "gram_mitra_report.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#1D6B4F"))
    story = [Paragraph("Gram Mitra — Karnataka Business AI", title), Spacer(1, 12)]
    story.append(Paragraph("Business Analysis Report", styles["Heading2"]))
    story.append(Spacer(1, 8))
    location = data.get("location", {})
    rows = [
        ["District", str(location.get("district",""))],
        ["Taluk", str(location.get("taluk",""))],
        ["Village", str(location.get("village","")) or "Not provided"],
        ["Business category", str(data.get("category",""))],
        ["Viability score", f"{data.get('viability_score','')}/10"],
        ["Season", str(data.get("season",""))],
        ["Project cost", f"Rs. {data.get('project_cost',0):,}"],
        ["Required 10% margin", f"Rs. {data.get('required_margin',0):,}"],
        ["Indicative 90% finance", f"Rs. {data.get('loan_90',0):,}"],
        ["Estimated quarterly repayment", f"Rs. {data.get('quarterly_payment',0):,}"],
    ]
    table = Table(rows, colWidths=[180, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E8F3EC")),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#B9C8BD")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("PADDING",(0,0),(-1,-1),8),
    ]))
    story += [table, Spacer(1, 16)]
    for heading, key in [
        ("Market opportunity", "market_opportunity"), ("Seasonal analysis", "seasonal_analysis"),
        ("Pricing suggestions", "pricing"), ("Market reach", "market_reach"),
        ("Threats", "threats"), ("Summary", "summary")
    ]:
        story.append(Paragraph(heading, styles["Heading3"]))
        value = data.get(key, "")
        if isinstance(value, list): value = " • ".join(map(str,value))
        story.append(Paragraph(str(value), styles["BodyText"]))
        story.append(Spacer(1, 8))
    swot = data.get("swot", {})
    story.append(Paragraph("SWOT", styles["Heading3"]))
    swot_rows = [[k.title(), " • ".join(v) if isinstance(v,list) else str(v)] for k,v in swot.items()]
    if swot_rows:
        t = Table(swot_rows, colWidths=[120, 360])
        t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#B9C8BD")),("PADDING",(0,0),(-1,-1),7)]))
        story.append(t)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Important: This report provides indicative advisory estimates. Verify current official scheme eligibility, interest rates and repayment terms with the relevant government department or financial institution.", styles["BodyText"]))
    doc.build(story)
    return send_file(path, as_attachment=True, download_name="Gram_Mitra_Business_Report.pdf")

if __name__ == "__main__":
    app.run(debug=True)
