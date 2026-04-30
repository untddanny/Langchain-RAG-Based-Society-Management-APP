from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secretkey"

# Dummy users
users = {
    "admin": "admin123",
    "member": "member123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("login"))


# ---------- MEMBER ROUTES ----------
@app.route("/pay-bills")
def pay_bills():
    return render_template("pay_bills.html")

@app.route("/complaints")
def complaints():
    return render_template("complaints.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


# ---------- ADMIN ROUTES ----------
@app.route("/admin-complaints")
def admin_complaints():
    return render_template("admin_complaints.html")

@app.route("/admin-docs")
def admin_docs():
    return render_template("admin_docs.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5050)