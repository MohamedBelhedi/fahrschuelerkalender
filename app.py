from flask import Flask, render_template, request, redirect, url_for, session
import datetime as dt

app = Flask(__name__)
app.secret_key = "DiyarSito2021#"

# Login-Daten für Admin
ADMIN_USER = "fahrlehrer"
ADMIN_PASS = "1234"

# ----- Termin-Generierung -----
def generate_week_appointments():
    appointments = {}
    today = dt.date.today()

    # Wenn heute Sonntag (6), dann nächste Woche starten
    if today.weekday() == 6:
        start = today + dt.timedelta(days=1)
    else:
        start = today - dt.timedelta(days=today.weekday())  # Montag dieser Woche

    # 5 Tage (Mo–Fr)
    for i in range(5):
        day = start + dt.timedelta(days=i)
        weekday = day.weekday()  # Montag = 0, Dienstag = 1, ...
        day_str = day.strftime("%A %d.%m.%Y")
        slots = []

        for hour in range(8, 19):
            time_str = f"{hour:02d}:00"

            # 12:30–15:00 Uhr = Pause
            if "12:30" <= time_str < "15:00":
                continue

            # Dienstag Theorie 18–20 Uhr
            if weekday == 1 and "18:00" <= time_str < "20:00":
                continue

            # Freitag 17–20 Uhr keine Termine
            if weekday == 4 and "17:00" <= time_str < "20:00":
                continue

            slots.append({
                "time": time_str,
                "status": "frei",
                "name": ""
            })

        appointments[day_str] = slots

    return appointments


appointments = generate_week_appointments()

# ----- Startseite -----
@app.route("/", methods=["GET", "POST"])
def callCalender():
    lang = request.args.get("lang", "de")

    if request.method == "POST":
        selected_day = request.form.get("day")
        selected_time = request.form.get("time")
        student_name = request.form.get("name", "").strip()

        for slot in appointments[selected_day]:
            if slot["time"] == selected_time and slot["status"] == "frei":
                slot["status"] = "gebucht"
                slot["name"] = student_name

        return redirect(url_for("callCalender", lang=lang))

    return render_template("index.html", appointments=appointments, lang=lang)

# ----- Login -----
@app.route("/login", methods=["GET", "POST"])
def login():
    lang = request.args.get("lang", "de")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("callAdmin", lang=lang))
        else:
            error = "Falsches Passwort" if lang == "de" else "كلمة المرور غير صحيحة"
            return render_template("login.html", lang=lang, error=error)

    return render_template("login.html", lang=lang)

# ----- Logout -----
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("callCalender"))

# ----- Admin -----
@app.route("/admin", methods=["GET", "POST"])
def callAdmin():
    lang = request.args.get("lang", "de")

    if not session.get("logged_in"):
        return redirect(url_for("login", lang=lang))

    if request.method == "POST":
        day = request.form.get("day")
        time = request.form.get("time")
        action = request.form.get("action")

        for slot in appointments[day]:
            if slot["time"] == time:
                if action == "frei":
                    slot["status"] = "frei"
                    slot["name"] = ""
                elif action == "gebucht":
                    slot["status"] = "gebucht"

        return redirect(url_for("callAdmin", lang=lang))

    return render_template("admin.html", appointments=appointments, lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080 ,debug=True)
