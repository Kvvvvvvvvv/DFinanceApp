from datetime import datetime
import pytz
from database import db

# Helper function to get IST timezone
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

# User model (base model for all roles)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, lender, borrower
    wallet_address = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)
    
    # Relationships
    lender = db.relationship('Lender', backref='user', uselist=False)
    borrower = db.relationship('Borrower', backref='user', uselist=False)

# Lender model
class Lender(db.Model):
    __tablename__ = 'lenders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    min_amount = db.Column(db.Float, default=0.0)
    max_amount = db.Column(db.Float, default=10000.0)
    interest_rate = db.Column(db.Float, default=5.0)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)

# Borrower model
class Borrower(db.Model):
    __tablename__ = 'borrowers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    credit_score = db.Column(db.Integer, default=750)
    uploaded_collateral = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)
    
    # Relationships
    collaterals = db.relationship('Collateral', backref='borrower')
    loans = db.relationship('Loan', backref='borrower')

# Collateral model
class Collateral(db.Model):
    __tablename__ = 'collaterals'
    
    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrowers.id'), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=get_ist_time)
    file_metadata = db.Column(db.Text, nullable=True)
    unique_data_id = db.Column(db.String(100), unique=True, nullable=False)

# Loan model
class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_data_id = db.Column(db.String(100), unique=True, nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrowers.id'), nullable=False)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=True)  # Made nullable
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=True)  # Made nullable
    status = db.Column(db.String(20), default='requested')  # requested, approved, rejected, disbursed, paid, overdue
    due_date = db.Column(db.DateTime, nullable=True)
    disbursed_at = db.Column(db.DateTime, nullable=True)
    repaid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)
    
    # Relationships
    lender = db.relationship('Lender', backref='loan')

# Blockchain-like ledger model
class Block(db.Model):
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_data_id = db.Column(db.String(100), nullable=False)
    prev_hash = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    nonce = db.Column(db.Integer, nullable=False)
    actor = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    block_metadata = db.Column(db.Text, nullable=True)