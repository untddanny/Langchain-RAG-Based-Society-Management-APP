from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    flat_number = db.Column(db.String(10))
    phone = db.Column(db.String(15))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))  # Default password for simplicity

    bills = db.relationship('Bill', backref='member', lazy=True)


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

    month = db.Column(db.String(20))   # e.g., "September"
    year = db.Column(db.Integer)

    parking = db.Column(db.Float, default=0)
    water = db.Column(db.Float, default=0)
    electricity = db.Column(db.Float, default=0)
    security = db.Column(db.Float, default=0)

    total_amount = db.Column(db.Float)
    balance_amount = db.Column(db.Float)

    status = db.Column(db.String(20), default="unpaid")


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.now())
    uploaded_by = db.Column(db.String(100))  # Admin name    
