from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Member, Bill

app = Flask(__name__)
app.secret_key = "secretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///society.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()
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

        # Admin login
        if username == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect(url_for("dashboard"))

        # Member login (DB)
        member = Member.query.filter_by(username=username, password=password).first()

        if member:
            session["user"] = "member"
            session["member_id"] = member.id
            session["member_name"] = member.name
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("login"))


# ---------- MEMBER ROUTES ----------
@app.route("/bills")
def bills():
    members = Member.query.all()
    return render_template("bills.html", members=members)

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

@app.route("/add-member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        name = request.form.get("name")
        flat = request.form.get("flat")
        phone = request.form.get("phone")

        print("Received:", name, flat, phone)

        # Check duplicate
        existing = Member.query.filter_by(flat_number=flat).first()
        if existing:
            return "Flat already exists"

        member = Member(
            name=name,
            flat_number=flat,
            phone=phone,
            username=flat,
            password="1234"
        )

        db.session.add(member)
        db.session.commit()

        print("Member added successfully!")

        return redirect(url_for("dashboard"))

    return render_template("add_member.html")

@app.route("/generate-bill", methods=["GET", "POST"])
def generate_bill():
    if request.method == "POST":
        member_id = request.form["member_id"]
        month = request.form["month"]
        year = int(request.form["year"])

        parking = float(request.form["parking"])
        water = float(request.form["water"])
        electricity = float(request.form["electricity"])
        security = float(request.form["security"])

        total = parking + water + electricity + security

        bill = Bill(
            member_id=member_id,
            month=month,
            year=year,
            parking=parking,
            water=water,
            electricity=electricity,
            security=security,
            total_amount=total,
            balance_amount=total,
            status="unpaid"
        )

        db.session.add(bill)
        db.session.commit()

        return redirect(url_for("dashboard"))

    members = Member.query.all()
    return render_template("generate_bill.html", members=members)

from werkzeug.utils import secure_filename
from rag_system import load_and_index_document, query_rules
from models import Document
import os

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/admin-docs", methods=["GET", "POST"])
def admin_docs():
    if request.method == "POST":
        # Check if file in request
        if 'file' not in request.files:
            return render_template("admin_docs.html", error="No file selected")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template("admin_docs.html", error="No file selected")
        
        if not allowed_file(file.filename):
            return render_template("admin_docs.html", error="Only PDF, TXT, DOCX allowed")
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Index with RAG
        try:
            load_and_index_document(filepath)
            
            # Save to database
            doc = Document(
                filename=filename,
                file_path=filepath,
                uploaded_by="admin"
            )
            db.session.add(doc)
            db.session.commit()
            
            return render_template("admin_docs.html", 
                                 success=f"✅ Document '{filename}' uploaded and indexed!")
        except Exception as e:
            return render_template("admin_docs.html", error=f"Error: {str(e)}")
    
    # GET request - show upload page
    docs = Document.query.all()
    return render_template("admin_docs.html", documents=docs)

if __name__ == "__main__":
    app.run(debug=True, port=5050)