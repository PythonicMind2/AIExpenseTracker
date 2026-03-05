"""
Expense Tracker Pro — Flask Web App
Features: Multi-user login, AI chatbot (Gemini), full expense management
"""
from flask import (Flask, render_template, request, jsonify,
                   send_file, session, redirect, url_for, flash)
from werkzeug.security import generate_password_hash, check_password_hash
import json, os, io, calendar, urllib.request, urllib.error, functools
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "expense-tracker-secret-change-me-2025")

# ── Storage paths ──────────────────────────────────────────────────────────────
BASE = os.path.join(os.path.expanduser("~"), ".expense_tracker_web")
os.makedirs(BASE, exist_ok=True)

def _path(*parts): return os.path.join(BASE, *parts)
def _load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f: return json.load(f)
    return default
def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── User store ─────────────────────────────────────────────────────────────────
USERS_FILE = _path("users.json")

def load_users(): return _load(USERS_FILE, {})
def save_users(u): _save(USERS_FILE, u)

def get_user(username): return load_users().get(username)

def user_dir(username):
    d = _path("users", username)
    os.makedirs(d, exist_ok=True)
    return d

# ── Per-user data helpers ──────────────────────────────────────────────────────
def u_load(name, default):
    return _load(os.path.join(user_dir(session["user"]), name), default)
def u_save(name, data):
    _save(os.path.join(user_dir(session["user"]), name), data)

def load_expenses():  return u_load("expenses.json", [])
def load_budgets():   return u_load("budgets.json", {})
def load_recurring(): return u_load("recurring.json", [])
def load_settings():
    d = {"currency": "INR", "theme": "light", "gemini_key": ""}
    d.update(u_load("settings.json", {})); return d
def save_expenses(d):  u_save("expenses.json", d)
def save_budgets(d):   u_save("budgets.json", d)
def save_recurring(d): u_save("recurring.json", d)
def save_settings(d):  u_save("settings.json", d)

# ── Constants ──────────────────────────────────────────────────────────────────
CATEGORIES = [
    "Food & Dining","Transport","Housing","Utilities","Shopping",
    "Entertainment","Healthcare","Education","Travel","Business",
    "Family","Maintenance","Subscriptions","Gifts","Other",
]
CAT_COLORS = {
    "Food & Dining":"#E07A5F","Transport":"#3D9970","Housing":"#2196A6",
    "Utilities":"#F4A261","Shopping":"#9C6B98","Entertainment":"#48A999",
    "Healthcare":"#D47C0F","Education":"#457B9D","Travel":"#6A8D73",
    "Business":"#7D6B4F","Family":"#C97B50","Maintenance":"#5C7A6B",
    "Subscriptions":"#2A7F6F","Gifts":"#C4677A","Other":"#7B6FA0",
}
CAT_ICONS = {
    "Food & Dining":"🍔","Transport":"🚗","Housing":"🏠","Utilities":"💡",
    "Shopping":"🛍️","Entertainment":"🎬","Healthcare":"🏥","Education":"📚",
    "Travel":"✈️","Business":"💼","Family":"👨‍👩‍👧","Maintenance":"🔧",
    "Subscriptions":"📱","Gifts":"🎁","Other":"💰",
}
CURRENCIES = {
    "INR":"₹","USD":"$","EUR":"€","GBP":"£","JPY":"¥","CNY":"¥",
    "AUD":"A$","CAD":"C$","CHF":"CHF","SGD":"S$","AED":"AED","SAR":"SAR",
}

def sym():
    s = load_settings()
    return CURRENCIES.get(s.get("currency","INR"), "₹")

# ── Auth decorator ─────────────────────────────────────────────────────────────
def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            if request.is_json:
                return jsonify({"error": "Not authenticated"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper

# ── Recurring helper ───────────────────────────────────────────────────────────
def next_due(rec):
    freq = rec["frequency"]
    last = rec.get("last_applied") or rec["start"]
    try: d = datetime.strptime(last, "%Y-%m-%d").date()
    except: return None
    if freq == "Daily":       d += timedelta(days=1)
    elif freq == "Weekly":    d += timedelta(weeks=1)
    elif freq == "Bi-weekly": d += timedelta(weeks=2)
    elif freq == "Monthly":
        m = d.month+1; y = d.year+m//13; m = m%12 or 12
        d = d.replace(year=y, month=m)
    elif freq == "Yearly":    d = d.replace(year=d.year+1)
    return d

def apply_recurring():
    today = date.today(); exp = load_expenses(); rec = load_recurring(); changed = False
    for r in rec:
        if not r.get("active", True): continue
        last = r.get("last_applied")
        nd = datetime.strptime(r["start"], "%Y-%m-%d").date() if last is None else next_due(r)
        if nd and nd <= today:
            exp.append({
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "amount": r["amount"], "description": "[Auto] "+r["name"],
                "category": r["category"], "date": nd.strftime("%Y-%m-%d"),
                "notes": (r.get("notes","")+" (recurring)").strip(),
                "added_on": datetime.now().isoformat(),
            })
            r["last_applied"] = nd.strftime("%Y-%m-%d"); changed = True
    if changed: save_expenses(exp); save_recurring(rec)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET"])
def login_page():
    if "user" in session: return redirect(url_for("index"))
    has_users = bool(load_users())
    return render_template("login.html", has_users=has_users)

@app.route("/login", methods=["POST"])
def do_login():
    data = request.json
    username = data.get("username","").strip().lower()
    password = data.get("password","")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    users = load_users()
    user = users.get(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401
    session["user"] = username
    session["display"] = user.get("display", username)
    return jsonify({"ok": True, "redirect": "/"})

@app.route("/register", methods=["POST"])
def do_register():
    data = request.json
    username = data.get("username","").strip().lower()
    password = data.get("password","")
    display  = data.get("display", username).strip()
    if not username or not password:
        return jsonify({"error": "All fields required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    users = load_users()
    if username in users:
        return jsonify({"error": "Username already taken"}), 409
    users[username] = {
        "password": generate_password_hash(password),
        "display": display or username,
        "created": datetime.now().isoformat(),
    }
    save_users(users)
    session["user"] = username
    session["display"] = display or username
    return jsonify({"ok": True, "redirect": "/"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
@login_required
def index():
    apply_recurring()
    settings = load_settings()
    return render_template("index.html",
        categories=CATEGORIES, cat_icons=CAT_ICONS,
        currencies=list(CURRENCIES.keys()),
        settings=settings, cat_colors=json.dumps(CAT_COLORS),
        username=session.get("display", session["user"]),
    )

# ── Expenses API ───────────────────────────────────────────────────────────────
@app.route("/api/expenses", methods=["GET"])
@login_required
def get_expenses():
    exp = load_expenses()
    cat    = request.args.get("category","All")
    search = request.args.get("search","").lower()
    month  = request.args.get("month","")
    year   = request.args.get("year","")
    if cat != "All": exp = [e for e in exp if e["category"]==cat]
    if search: exp = [e for e in exp if search in e["description"].lower() or search in e.get("notes","").lower()]
    if month: exp = [e for e in exp if e["date"].startswith(month)]
    elif year: exp = [e for e in exp if e["date"].startswith(year)]
    return jsonify(sorted(exp, key=lambda x: x["date"], reverse=True))

@app.route("/api/expenses", methods=["POST"])
@login_required
def add_expense():
    d = request.json
    try:
        amt = float(d["amount"])
        if amt <= 0: raise ValueError
        datetime.strptime(d["date"], "%Y-%m-%d")
        if not d.get("description","").strip(): raise ValueError
    except:
        return jsonify({"error": "Invalid data"}), 400
    e = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "amount": amt, "description": d["description"].strip(),
        "category": d["category"], "date": d["date"],
        "notes": d.get("notes",""), "added_on": datetime.now().isoformat(),
    }
    exp = load_expenses(); exp.append(e); save_expenses(exp)
    return jsonify(e), 201

@app.route("/api/expenses/<eid>", methods=["DELETE"])
@login_required
def delete_expense(eid):
    save_expenses([e for e in load_expenses() if e["id"] != eid])
    return jsonify({"ok": True})

@app.route("/api/expenses/bulk-delete", methods=["POST"])
@login_required
def bulk_delete():
    ids = set(request.json.get("ids", []))
    save_expenses([e for e in load_expenses() if e["id"] not in ids])
    return jsonify({"ok": True})

# ── Dashboard API ──────────────────────────────────────────────────────────────
@app.route("/api/dashboard")
@login_required
def dashboard():
    exp = load_expenses(); today = date.today()
    today_s = today.strftime("%Y-%m-%d"); month_s = today.strftime("%Y-%m"); year_s = str(today.year)
    t_today = sum(e["amount"] for e in exp if e["date"]==today_s)
    t_month = sum(e["amount"] for e in exp if e["date"].startswith(month_s))
    t_year  = sum(e["amount"] for e in exp if e["date"].startswith(year_s))
    avg_day = t_month/today.day if today.day else 0
    rec = load_recurring()
    rec_monthly = sum(r["amount"] for r in rec if r.get("active",True) and r["frequency"]=="Monthly")
    cat_totals = {}
    for e in exp:
        if e["date"].startswith(month_s):
            cat_totals[e["category"]] = cat_totals.get(e["category"],0)+e["amount"]
    trend = []
    for i in range(5,-1,-1):
        y,m = today.year, today.month-i
        while m<=0: m+=12; y-=1
        p = f"{y}-{m:02d}"
        trend.append({"label":calendar.month_abbr[m],"month":p,
                      "amount":sum(e["amount"] for e in exp if e["date"].startswith(p)),
                      "is_current":m==today.month and y==today.year})
    return jsonify({"kpis":{"today":t_today,"month":t_month,"year":t_year,
                             "avg_day":avg_day,"recurring":rec_monthly},
                    "cat_breakdown":sorted(cat_totals.items(),key=lambda x:x[1],reverse=True),
                    "trend":trend,"currency":sym()})

# ── Charts API ─────────────────────────────────────────────────────────────────
@app.route("/api/charts")
@login_required
def charts():
    year = request.args.get("year", str(date.today().year))
    month = request.args.get("month","")
    prefix = f"{year}-{month.zfill(2)}" if month else year
    exp = [e for e in load_expenses() if e["date"].startswith(prefix)]
    cat_totals = {}
    for e in exp: cat_totals[e["category"]] = cat_totals.get(e["category"],0)+e["amount"]
    today = date.today()
    monthly = []
    for i in range(11,-1,-1):
        y,m = today.year, today.month-i
        while m<=0: m+=12; y-=1
        p = f"{y}-{m:02d}"
        monthly.append({"label":calendar.month_abbr[m],
                         "amount":sum(e["amount"] for e in load_expenses() if e["date"].startswith(p)),
                         "is_current":m==today.month and y==today.year})
    daily = {}
    for e in exp: daily[e["date"]] = daily.get(e["date"],0)+e["amount"]
    return jsonify({
        "cat_totals":[{"cat":k,"amount":v,"color":CAT_COLORS.get(k,"#888")}
                      for k,v in sorted(cat_totals.items(),key=lambda x:x[1],reverse=True)],
        "monthly":monthly,
        "daily":[{"date":k,"amount":v} for k,v in sorted(daily.items())],
        "currency":sym(),"prefix":prefix,
    })

# ── Budget API ─────────────────────────────────────────────────────────────────
@app.route("/api/budgets", methods=["GET"])
@login_required
def get_budgets():
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    exp = load_expenses(); bgt = load_budgets(); monthly = {}
    for e in exp:
        if e["date"].startswith(month):
            monthly[e["category"]] = monthly.get(e["category"],0)+e["amount"]
    all_cats = sorted(set(list(bgt)+list(monthly)))
    result = []
    for cat in all_cats:
        budget=bgt.get(cat,0); spent=monthly.get(cat,0)
        pct=(spent/budget*100) if budget>0 else (100 if spent>0 else 0)
        result.append({"category":cat,"budget":budget,"spent":spent,
                        "remaining":budget-spent,"pct":min(pct,200),"color":CAT_COLORS.get(cat,"#888")})
    return jsonify({"budgets":result,"currency":sym()})

@app.route("/api/budgets", methods=["POST"])
@login_required
def save_budget():
    d = request.json; bgt = load_budgets()
    bgt[d["category"]] = float(d["amount"]); save_budgets(bgt)
    return jsonify({"ok":True})

@app.route("/api/budgets/<path:cat>", methods=["DELETE"])
@login_required
def delete_budget(cat):
    bgt = load_budgets(); bgt.pop(cat, None); save_budgets(bgt)
    return jsonify({"ok":True})

# ── Recurring API ──────────────────────────────────────────────────────────────
@app.route("/api/recurring", methods=["GET"])
@login_required
def get_recurring():
    rec = load_recurring()
    for r in rec:
        nd = next_due(r)
        r["next_due"] = nd.strftime("%Y-%m-%d") if nd else "—"
    return jsonify(rec)

@app.route("/api/recurring", methods=["POST"])
@login_required
def add_recurring_route():
    d = request.json
    try: float(d["amount"]); datetime.strptime(d["start"], "%Y-%m-%d")
    except: return jsonify({"error":"Invalid data"}),400
    r = {"id":datetime.now().strftime("%Y%m%d%H%M%S%f"),"name":d["name"],
         "amount":float(d["amount"]),"category":d["category"],"frequency":d["frequency"],
         "start":d["start"],"notes":d.get("notes",""),"last_applied":None,"active":True}
    rec = load_recurring(); rec.append(r); save_recurring(rec)
    return jsonify(r),201

@app.route("/api/recurring/<rid>", methods=["DELETE"])
@login_required
def delete_recurring_route(rid):
    save_recurring([r for r in load_recurring() if r["id"]!=rid])
    return jsonify({"ok":True})

@app.route("/api/recurring/apply", methods=["POST"])
@login_required
def apply_now():
    apply_recurring(); return jsonify({"ok":True})

# ── Settings API ───────────────────────────────────────────────────────────────
@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings(): return jsonify(load_settings())

@app.route("/api/settings", methods=["POST"])
@login_required
def update_settings():
    s = load_settings(); s.update(request.json); save_settings(s)
    return jsonify(s)

# ── Export API ─────────────────────────────────────────────────────────────────
@app.route("/api/export/csv")
@login_required
def export_csv():
    exp = load_expenses()
    df = pd.DataFrame(exp)[["date","description","category","amount","notes"]] if exp else pd.DataFrame(columns=["date","description","category","amount","notes"])
    df.columns = ["Date","Description","Category",f"Amount ({sym()})","Notes"]
    buf = io.StringIO(); df.to_csv(buf, index=False); buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue().encode()),mimetype="text/csv",
                     as_attachment=True,download_name=f"expenses_{date.today()}.csv")

@app.route("/api/export/xlsx")
@login_required
def export_xlsx():
    exp = load_expenses()
    df = pd.DataFrame(exp)[["date","description","category","amount","notes"]] if exp else pd.DataFrame(columns=["date","description","category","amount","notes"])
    df.columns = ["Date","Description","Category",f"Amount ({sym()})","Notes"]
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Expenses")
        if len(df):
            summ = df.groupby("Category")[f"Amount ({sym()})"].agg(["sum","count"])
            summ.columns=["Total","Count"]; summ.to_excel(w,sheet_name="Summary")
    buf.seek(0)
    return send_file(buf,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True,download_name=f"expenses_{date.today()}.xlsx")

@app.route("/api/export/pdf")
@login_required
def export_pdf_route():
    period = request.args.get("period","All Time")
    exp = load_expenses(); bgt = load_budgets(); currency = sym()
    buf = io.BytesIO(); _build_pdf(buf, exp, bgt, currency, period); buf.seek(0)
    return send_file(buf,mimetype="application/pdf",
                     as_attachment=True,download_name=f"report_{date.today()}.pdf")

# ══════════════════════════════════════════════════════════════════════════════
# AI CHATBOT  —  Google Gemini (gemini-2.0-flash via REST, no SDK needed)
# ══════════════════════════════════════════════════════════════════════════════

# Gemini REST endpoint — swap the model name here if you want 1.5-pro etc.
GEMINI_MODEL   = "gemini-2.0-flash"
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def _build_expense_context() -> str:
    """Build a rich financial context string from the current user's data."""
    exp      = load_expenses()
    bgt      = load_budgets()
    rec      = load_recurring()
    settings = load_settings()
    currency = CURRENCIES.get(settings.get("currency", "INR"), "₹")
    today    = date.today()
    month_s  = today.strftime("%Y-%m")
    year_s   = str(today.year)

    total_all   = sum(e["amount"] for e in exp)
    total_month = sum(e["amount"] for e in exp if e["date"].startswith(month_s))
    total_year  = sum(e["amount"] for e in exp if e["date"].startswith(year_s))
    total_today = sum(e["amount"] for e in exp if e["date"] == today.strftime("%Y-%m-%d"))

    cat_month: dict = {}
    for e in exp:
        if e["date"].startswith(month_s):
            cat_month[e["category"]] = cat_month.get(e["category"], 0) + e["amount"]

    cat_year: dict = {}
    for e in exp:
        if e["date"].startswith(year_s):
            cat_year[e["category"]] = cat_year.get(e["category"], 0) + e["amount"]

    recent = sorted(exp, key=lambda x: x["date"], reverse=True)[:10]

    lines = [
        f"USER FINANCIAL DATA  (currency: {currency})",
        f"Today: {today.strftime('%d %B %Y')}",
        "",
        "=== SUMMARY ===",
        f"- Spent today:       {currency}{total_today:,.2f}",
        f"- Spent this month ({today.strftime('%B %Y')}): {currency}{total_month:,.2f}",
        f"- Spent this year ({year_s}): {currency}{total_year:,.2f}",
        f"- All-time total:    {currency}{total_all:,.2f}",
        f"- Total transactions: {len(exp)}",
        "",
        "=== THIS MONTH BY CATEGORY ===",
    ]
    for cat, amt in sorted(cat_month.items(), key=lambda x: x[1], reverse=True):
        bgt_amt = bgt.get(cat, 0)
        if bgt_amt:
            pct    = amt / bgt_amt * 100
            b_info = f"  [budget {currency}{bgt_amt:,.0f}, {pct:.0f}% used]"
        else:
            b_info = "  [no budget set]"
        lines.append(f"  {cat}: {currency}{amt:,.2f}{b_info}")

    lines += ["", "=== THIS YEAR BY CATEGORY ==="]
    for cat, amt in sorted(cat_year.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {cat}: {currency}{amt:,.2f}")

    if bgt:
        lines += ["", "=== MONTHLY BUDGETS ==="]
        for cat, budget in sorted(bgt.items()):
            spent  = cat_month.get(cat, 0)
            rem    = budget - spent
            status = "OVER BUDGET" if rem < 0 else f"{currency}{rem:,.0f} remaining"
            lines.append(
                f"  {cat}: budget={currency}{budget:,.0f}  "
                f"spent={currency}{spent:,.0f}  ({status})"
            )

    if rec:
        lines += ["", "=== RECURRING EXPENSES ==="]
        for r in rec:
            lines.append(f"  {r['name']}: {currency}{r['amount']:,.0f}  [{r['frequency']}]")

    if recent:
        lines += ["", "=== 10 MOST RECENT TRANSACTIONS ==="]
        for e in recent:
            lines.append(
                f"  {e['date']} | {e['description']} "
                f"| {e['category']} | {currency}{e['amount']:,.2f}"
            )

    return "\n".join(lines)


def _call_gemini(api_key: str, system_prompt: str,
                 history: list, user_message: str) -> str:
    """
    Call the Gemini REST API.

    Gemini does not have a separate 'system' role in the contents array —
    we prepend the system instruction to the first user turn as recommended
    by Google, and use systemInstruction when supported.

    Returns the text reply or raises on error.
    """
    # Build contents array: alternating user / model turns
    contents = []

    # Inject history (last 8 turns, keeping user/model alternation)
    for msg in history[-8:]:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Current user turn
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = json.dumps({
        # systemInstruction is supported from Gemini 1.5 onwards
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }).encode("utf-8")

    url = f"{GEMINI_API_URL}?key={api_key}"
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # Extract text from response
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        # Fallback: check for blockReason
        reason = (result.get("candidates", [{}])[0]
                       .get("finishReason", "UNKNOWN"))
        raise ValueError(f"Gemini returned no text (finishReason: {reason})")


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data         = request.json
    user_message = data.get("message", "").strip()
    history      = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    settings = load_settings()
    api_key  = settings.get("gemini_key", "").strip()
    if not api_key:
        return jsonify({
            "error": "No Gemini API key set. Go to ⚙️ Settings to add it."
        }), 400

    expense_context = _build_expense_context()
    system_prompt   = (
        "You are a smart, friendly personal finance assistant built into "
        "Expense Tracker Pro. You have full access to the user's expense data "
        "shown below. Use it to give specific, accurate, helpful answers.\n\n"
        "Guidelines:\n"
        "- Be conversational and warm.\n"
        "- Always use the user's own currency when quoting amounts.\n"
        "- Format numbers with commas for readability.\n"
        "- Keep responses concise. Use short paragraphs or bullet points.\n"
        "- If asked for tips, make them specific to the user's actual data.\n"
        "- Never make up numbers that are not in the data.\n\n"
        f"--- USER'S EXPENSE DATA ---\n{expense_context}\n--- END OF DATA ---"
    )

    try:
        reply = _call_gemini(api_key, system_prompt, history, user_message)
        return jsonify({"reply": reply})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err = json.loads(body)["error"]["message"]
        except Exception:
            err = body[:300]
        return jsonify({"error": f"Gemini API error: {err}"}), 502
    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 502


@app.route("/api/chat/key", methods=["POST"])
@login_required
def save_api_key():
    key = request.json.get("key", "").strip()
    s   = load_settings()
    s["gemini_key"] = key
    save_settings(s)
    return jsonify({"ok": True})

# ── PDF builder ────────────────────────────────────────────────────────────────
def _build_pdf(buf, expenses, budgets, currency, period_label):
    doc = SimpleDocTemplate(buf,pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    def rl(h):
        c=h.lstrip("#"); return rl_colors.Color(int(c[0:2],16)/255,int(c[2:4],16)/255,int(c[4:6],16)/255)
    ACC=rl("#2D6A4F");ACC_L=rl("#EAF3EE");TXT=rl("#1C2B20");TXT2=rl("#6B7A6E")
    RED=rl("#C0392B");GRN=rl("#2D9E6B");YLW=rl("#D4870A");LG=rl("#F5F0E8");MG=rl("#DDD5C5")
    st=getSampleStyleSheet()
    H1=ParagraphStyle("H1",parent=st["Normal"],fontSize=22,textColor=ACC,fontName="Helvetica-Bold",spaceAfter=4)
    H2=ParagraphStyle("H2",parent=st["Normal"],fontSize=13,textColor=ACC,fontName="Helvetica-Bold",spaceBefore=14,spaceAfter=6)
    sub=ParagraphStyle("sub",parent=st["Normal"],fontSize=9,textColor=TXT2,spaceAfter=2)
    norm=ParagraphStyle("n",parent=st["Normal"],fontSize=9,textColor=TXT)
    rgt=ParagraphStyle("r",parent=st["Normal"],fontSize=9,textColor=TXT,alignment=TA_RIGHT)
    story=[]
    story.append(Paragraph("Expense Report",H1))
    story.append(Paragraph(f"Period: {period_label}  •  Generated: {date.today().strftime('%d %B %Y')}",sub))
    story.append(HRFlowable(width="100%",thickness=1,color=ACC,spaceAfter=12))
    total=sum(e["amount"] for e in expenses);n=len(expenses);avg=total/n if n else 0
    mx=max(expenses,key=lambda e:e["amount"]) if expenses else None
    kd=[["Total Spent","Transactions","Average","Largest"],
        [f"{currency}{total:,.2f}",str(n),f"{currency}{avg:,.2f}",f"{currency}{mx['amount']:,.2f}" if mx else "-"]]
    kt=Table(kd,colWidths=[4.2*cm]*4)
    kt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ACC),("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),
        ("BACKGROUND",(0,1),(-1,1),ACC_L),("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),
        ("FONTSIZE",(0,1),(-1,1),13),("TEXTCOLOR",(0,1),(-1,1),ACC),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("BOX",(0,0),(-1,-1),0.5,MG),("INNERGRID",(0,0),(-1,-1),0.5,MG),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(kt);story.append(Spacer(1,18))
    cat_totals={}
    for e in expenses: cat_totals[e["category"]]=cat_totals.get(e["category"],0)+e["amount"]
    if cat_totals:
        story.append(Paragraph("Spending by Category",H2))
        rows=[["Category","Amount","% of Total","Transactions"]]
        for cat,amt in sorted(cat_totals.items(),key=lambda x:x[1],reverse=True):
            pct=amt/total*100 if total else 0
            cnt=sum(1 for e in expenses if e["category"]==cat)
            rows.append([Paragraph(cat,norm),Paragraph(f"{currency}{amt:,.2f}",rgt),
                         Paragraph(f"{pct:.1f}%",rgt),Paragraph(str(cnt),rgt)])
        ct=Table(rows,colWidths=[7.5*cm,3.5*cm,3*cm,3*cm])
        ct.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),ACC),("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[LG,rl_colors.white]),
            ("BOX",(0,0),(-1,-1),0.5,MG),("INNERGRID",(0,0),(-1,-1),0.3,MG),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(ct);story.append(Spacer(1,18))
    story.append(Paragraph("Expense Log",H2))
    lr=[["Date","Description","Category","Amount","Notes"]]
    for e in sorted(expenses,key=lambda x:x["date"],reverse=True):
        lr.append([Paragraph(e["date"],norm),Paragraph(e["description"][:38],norm),
                   Paragraph(e["category"],norm),Paragraph(f"{currency}{e['amount']:,.2f}",rgt),
                   Paragraph(e.get("notes","")[:28],norm)])
    lt=Table(lr,colWidths=[2.5*cm,5.5*cm,4*cm,2.5*cm,3.5*cm])
    lt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ACC),("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[LG,rl_colors.white]),
        ("BOX",(0,0),(-1,-1),0.5,MG),("INNERGRID",(0,0),(-1,-1),0.3,MG),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),
    ]))
    story.append(lt);story.append(Spacer(1,20))
    story.append(HRFlowable(width="100%",thickness=0.5,color=MG))
    story.append(Paragraph("Generated by Expense Tracker Pro Web",sub))
    doc.build(story)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
