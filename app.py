# IMPORT FLASK FRAMEWORK FOR WEB APPLICATION
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# IMPORT DATABASE MODELS (Member, Bill, Document)
from models import db, Member, Bill, Document
# IMPORT FILE HANDLING UTILITIES
from werkzeug.utils import secure_filename
# IMPORT RAG SYSTEM FUNCTIONS FOR DOCUMENT INDEXING AND QUERYING
from rag_system import load_and_index_document, query_rules
# IMPORT OS FOR FILE AND FOLDER OPERATIONS
import os

# INITIALIZE FLASK APPLICATION
app = Flask(__name__)
# SET SECRET KEY FOR SESSION ENCRYPTION - KEEPS USER SESSIONS SECURE
app.secret_key = "secretkey"

# CONFIGURE SQLITE DATABASE
# SQLALCHEMY_DATABASE_URI: tells Flask where to store the database file (society.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///society.db'
# SQLALCHEMY_TRACK_MODIFICATIONS: disable to avoid warning messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INITIALIZE DATABASE WITH THE FLASK APP
db.init_app(app)
# CREATE ALL TABLES IF THEY DON'T EXIST
with app.app_context():
    db.create_all()

# SET UP FILE UPLOAD CONFIGURATION
# UPLOAD_FOLDER: where uploaded documents will be saved
UPLOAD_FOLDER = "uploads"
# ALLOWED_EXTENSIONS: only these file types can be uploaded for RAG
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
# CREATE UPLOADS FOLDER IF IT DOESN'T EXIST
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# FUNCTION TO CHECK IF UPLOADED FILE IS ALLOWED
def allowed_file(filename):
    # SPLIT FILENAME BY DOT (.) AND GET THE EXTENSION (part after the dot)
    # THEN CONVERT TO LOWERCASE AND CHECK IF IT'S IN ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============ LOGIN & DASHBOARD ROUTES ============

# LOGIN PAGE - BOTH GET AND POST REQUESTS
@app.route("/", methods=["GET", "POST"])
def login():
    # IF THIS IS A POST REQUEST (USER SUBMITTED LOGIN FORM)
    if request.method == "POST":
        # GET USERNAME AND PASSWORD FROM FORM
        username = request.form["username"]
        password = request.form["password"]

        # CHECK IF ADMIN LOGIN (HARDCODED ADMIN CREDENTIALS)
        if username == "admin" and password == "admin123":
            # SET SESSION VARIABLE TO IDENTIFY USER AS ADMIN
            session["user"] = "admin"
            # REDIRECT ADMIN TO DASHBOARD
            return redirect(url_for("dashboard"))

        # CHECK IF MEMBER LOGIN (SEARCH IN DATABASE)
        # query.filter_by searches database for matching username and password
        member = Member.query.filter_by(username=username, password=password).first()

        # IF MEMBER FOUND IN DATABASE
        if member:
            # SET SESSION VARIABLE TO IDENTIFY USER AS MEMBER
            session["user"] = "member"
            # STORE MEMBER ID IN SESSION (NEEDED FOR BILLS, COMPLAINTS, ETC)
            session["member_id"] = member.id
            # STORE MEMBER NAME IN SESSION (FOR DISPLAYING IN UI)
            session["member_name"] = member.name
            # REDIRECT MEMBER TO DASHBOARD
            return redirect(url_for("dashboard"))

        # IF LOGIN FAILED, SHOW ERROR MESSAGE
        return render_template("login.html", error="Invalid Credentials")

    # IF THIS IS A GET REQUEST, JUST SHOW LOGIN PAGE
    return render_template("login.html")


# DASHBOARD PAGE - SHOWS DIFFERENT CONTENT FOR ADMIN VS MEMBER
@app.route("/dashboard")
def dashboard():
    # CHECK IF USER IS LOGGED IN (SESSION VARIABLE EXISTS)
    if "user" in session:
        # RENDER DASHBOARD WITH USER TYPE (ADMIN OR MEMBER)
        return render_template("dashboard.html", user=session["user"])
    # IF NOT LOGGED IN, REDIRECT TO LOGIN PAGE
    return redirect(url_for("login"))


# ============ MEMBER ROUTES (BILLS, COMPLAINTS, CHATBOT) ============

# BILLS PAGE - SHOWS MONTHLY BILLS FOR MEMBERS
@app.route("/bills")
def bills():
    # GET ALL MEMBERS FROM DATABASE
    members = Member.query.all()
    # RENDER BILLS PAGE WITH ALL MEMBERS
    return render_template("bills.html", members=members)

# COMPLAINTS PAGE - MEMBERS CAN RAISE COMPLAINTS
@app.route("/complaints")
def complaints():
    # RENDER COMPLAINTS PAGE
    return render_template("complaints.html")

# CHATBOT PAGE - MEMBERS ASK QUESTIONS ABOUT SOCIETY RULES
@app.route("/chatbot")
def chatbot():
    # CHECK IF USER IS LOGGED IN AND IS A MEMBER
    if "user" not in session or session["user"] != "member":
        # IF NOT, REDIRECT TO LOGIN PAGE
        return redirect(url_for("login"))
    # RENDER CHATBOT PAGE
    return render_template("chatbot.html")


# ============ ADMIN ROUTES (COMPLAINTS, DOCUMENTS) ============

# ADMIN COMPLAINTS PAGE - ADMIN SEES ALL COMPLAINTS FROM MEMBERS
@app.route("/admin-complaints")
def admin_complaints():
    # RENDER ADMIN COMPLAINTS PAGE
    return render_template("admin_complaints.html")

# ADMIN DOCUMENTS PAGE - ADMIN CAN UPLOAD SOCIETY RULES
@app.route("/admin-docs", methods=["GET", "POST"])
def admin_docs():
    # IF THIS IS A POST REQUEST (USER UPLOADING A FILE)
    if request.method == "POST":
        # CHECK IF FILE WAS INCLUDED IN THE FORM
        if 'file' not in request.files:
            # IF NOT, SHOW ERROR MESSAGE
            return render_template("admin_docs.html", error="No file selected")
        
        # GET THE FILE FROM REQUEST
        file = request.files['file']
        
        # CHECK IF FILENAME IS EMPTY
        if file.filename == '':
            # IF EMPTY, SHOW ERROR MESSAGE
            return render_template("admin_docs.html", error="No file selected")
        
        # CHECK IF FILE TYPE IS ALLOWED (PDF, TXT, DOCX)
        if not allowed_file(file.filename):
            # IF NOT ALLOWED, SHOW ERROR MESSAGE
            return render_template("admin_docs.html", error="Only PDF, TXT, DOCX allowed")
        
        # MAKE FILENAME SAFE (REMOVES SPECIAL CHARACTERS)
        filename = secure_filename(file.filename)
        # CREATE FULL PATH WHERE FILE WILL BE SAVED
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        # SAVE FILE TO UPLOADS FOLDER
        file.save(filepath)
        
        # TRY TO INDEX DOCUMENT WITH RAG SYSTEM
        try:
            # LOAD DOCUMENT, SPLIT INTO CHUNKS, ADD TO VECTOR DATABASE
            load_and_index_document(filepath)
            
            # SAVE DOCUMENT INFO TO DATABASE
            # CREATE NEW DOCUMENT OBJECT
            doc = Document(
                # FILENAME (WHAT USER SEE IN LIST)
                filename=filename,
                # FULL PATH TO FILE
                file_path=filepath,
                # WHO UPLOADED IT (ALWAYS "admin")
                uploaded_by="admin"
            )
            # ADD DOCUMENT TO DATABASE
            db.session.add(doc)
            # COMMIT CHANGES TO DATABASE
            db.session.commit()
            
            # SHOW SUCCESS MESSAGE
            return render_template("admin_docs.html", 
                                 success=f"✅ Document '{filename}' uploaded and indexed!")
        # IF ERROR OCCURS DURING INDEXING
        except Exception as e:
            # SHOW ERROR MESSAGE WITH ERROR DETAILS
            return render_template("admin_docs.html", error=f"Error: {str(e)}")
    
    # IF THIS IS A GET REQUEST, JUST SHOW UPLOAD PAGE
    # GET ALL DOCUMENTS FROM DATABASE
    docs = Document.query.all()
    # RENDER ADMIN DOCS PAGE WITH LIST OF UPLOADED DOCUMENTS
    return render_template("admin_docs.html", documents=docs)


# ============ OTHER ROUTES ============

# LOGOUT PAGE - USER CLICKS LOGOUT BUTTON
@app.route("/logout")
def logout():
    # REMOVE USER SESSION (LOG THEM OUT)
    session.pop("user", None)
    # REDIRECT TO LOGIN PAGE
    return redirect(url_for("login"))

# ADD MEMBER PAGE - ADMIN CAN ADD NEW MEMBERS
@app.route("/add-member", methods=["GET", "POST"])
def add_member():
    # IF THIS IS A POST REQUEST (FORM SUBMITTED)
    if request.method == "POST":
        # GET MEMBER DETAILS FROM FORM
        name = request.form.get("name")
        # GET FLAT NUMBER
        flat = request.form.get("flat")
        # GET PHONE NUMBER
        phone = request.form.get("phone")

        # PRINT FOR DEBUGGING (CAN BE REMOVED)
        print("Received:", name, flat, phone)

        # CHECK IF FLAT ALREADY EXISTS (DUPLICATE CHECK)
        # query.filter_by searches for member with same flat_number
        existing = Member.query.filter_by(flat_number=flat).first()
        # IF FLAT ALREADY EXISTS
        if existing:
            # SHOW ERROR MESSAGE
            return "Flat already exists"

        # CREATE NEW MEMBER OBJECT WITH DETAILS
        member = Member(
            name=name,
            flat_number=flat,
            phone=phone,
            # USERNAME = FLAT NUMBER (FOR LOGIN)
            username=flat,
            # DEFAULT PASSWORD = "1234"
            password="1234"
        )

        # ADD NEW MEMBER TO DATABASE
        db.session.add(member)
        # SAVE CHANGES TO DATABASE
        db.session.commit()

        # PRINT SUCCESS MESSAGE FOR DEBUGGING
        print("Member added successfully!")

        # REDIRECT TO DASHBOARD
        return redirect(url_for("dashboard"))

    # IF THIS IS A GET REQUEST, SHOW ADD MEMBER FORM
    return render_template("add_member.html")

# GENERATE BILL PAGE - ADMIN CREATES MONTHLY BILLS
@app.route("/generate-bill", methods=["GET", "POST"])
def generate_bill():
    # IF THIS IS A POST REQUEST (FORM SUBMITTED)
    if request.method == "POST":
        # GET MEMBER ID FROM FORM
        member_id = request.form["member_id"]
        # GET MONTH (E.G. "January")
        month = request.form["month"]
        # GET YEAR (E.G. 2024) AND CONVERT TO INTEGER
        year = int(request.form["year"])

        # GET INDIVIDUAL CHARGES
        # PARKING CHARGE FOR THE MONTH
        parking = float(request.form["parking"])
        # WATER CHARGE FOR THE MONTH
        water = float(request.form["water"])
        # ELECTRICITY CHARGE FOR THE MONTH
        electricity = float(request.form["electricity"])
        # SECURITY CHARGE FOR THE MONTH
        security = float(request.form["security"])

        # CALCULATE TOTAL BILL (SUM OF ALL CHARGES)
        total = parking + water + electricity + security

        # CREATE NEW BILL OBJECT
        bill = Bill(
            member_id=member_id,
            month=month,
            year=year,
            parking=parking,
            water=water,
            electricity=electricity,
            security=security,
            # TOTAL AMOUNT DUE
            total_amount=total,
            # AMOUNT STILL PENDING (SAME AS TOTAL INITIALLY)
            balance_amount=total,
            # BILL STATUS = NOT PAID YET
            status="unpaid"
        )

        # ADD NEW BILL TO DATABASE
        db.session.add(bill)
        # SAVE CHANGES TO DATABASE
        db.session.commit()

        # REDIRECT TO DASHBOARD
        return redirect(url_for("dashboard"))

    # IF THIS IS A GET REQUEST, SHOW GENERATE BILL FORM
    # GET ALL MEMBERS FROM DATABASE (TO SHOW IN DROPDOWN)
    members = Member.query.all()
    # RENDER GENERATE BILL PAGE WITH MEMBERS LIST
    return render_template("generate_bill.html", members=members)


# ============ API ROUTES FOR CHATBOT (JSON) ============

# CHATBOT API - RECEIVES QUESTION, RETURNS ANSWER
@app.route("/api/chat", methods=["POST"])
def api_chat():
    # CHECK IF USER IS LOGGED IN AND IS A MEMBER
    if "user" not in session or session["user"] != "member":
        # IF NOT, RETURN 401 (UNAUTHORIZED) ERROR
        return jsonify({"error": "Unauthorized"}), 401
    
    # GET JSON DATA FROM REQUEST
    data = request.json
    
    # CHECK IF 'question' KEY EXISTS IN JSON
    if not data or "question" not in data:
        # IF NOT, RETURN 400 (BAD REQUEST) ERROR
        return jsonify({"error": "Missing question"}), 400
    
    # GET THE QUESTION FROM JSON
    question = data["question"]
    
    # TRY TO QUERY RAG SYSTEM FOR ANSWER
    try:
        # CALL query_rules FUNCTION TO GET ANSWER FROM DOCUMENTS
        # This searches vector database and uses LLM to generate answer
        answer = query_rules(question)
        
        # RETURN ANSWER AS JSON WITH 200 (OK) STATUS
        return jsonify({"answer": answer}), 200
    # IF ERROR OCCURS DURING QUERY
    except Exception as e:
        # RETURN 500 (SERVER ERROR) WITH ERROR MESSAGE
        return jsonify({"error": f"Error: {str(e)}"}), 500


# START THE FLASK APPLICATION
if __name__ == "__main__":
    # RUN ON LOCALHOST:5050
    # debug=True: reloads app when code changes (for development)
    app.run(debug=True, port=5050)
