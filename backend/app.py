from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import hashlib
import uuid
import json
import pytz
from database import db
from models import User, Lender, Borrower, Collateral, Loan, Block

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///defi_loan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Enable CORS
CORS(app, supports_credentials=True)

# Initialize database
db.init_app(app)

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to get IST timezone
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

# Helper function to create a new block in the ledger
def create_block(unique_data_id, actor, event_type, metadata=None):
    # Get the previous block's hash
    prev_block = Block.query.order_by(Block.id.desc()).first()
    prev_hash = prev_block.hash if prev_block else "0" * 64
    
    # Create new block data
    timestamp = get_ist_time().isoformat()
    nonce = 0
    
    # Generate hash
    data_string = prev_hash + unique_data_id + timestamp + str(nonce)
    hash_result = hashlib.sha256(data_string.encode()).hexdigest()
    
    # Create and save block
    block = Block(
        unique_data_id=unique_data_id,
        prev_hash=prev_hash,
        hash=hash_result,
        timestamp=timestamp,
        nonce=nonce,
        actor=actor,
        event_type=event_type,
        block_metadata=json.dumps(metadata) if metadata else None
    )
    
    db.session.add(block)
    db.session.commit()
    
    return block

# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.password == password:
        session['user_id'] = user.id
        session['role'] = user.role
        
        # Update wallet address if provided
        wallet_address = data.get('wallet_address')
        if wallet_address:
            user.wallet_address = wallet_address
            db.session.commit()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'wallet_address': user.wallet_address
            }
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# Admin-only routes
@app.route('/api/register', methods=['POST'])
def register_user():
    # Check if user is admin
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    role = data.get('role')
    
    # Create user (wallet address is now optional)
    user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password'),
        role=role,
        wallet_address=data.get('wallet_address', None)  # Optional wallet address
    )
    
    db.session.add(user)
    db.session.flush()  # Get user ID without committing
    
    # Create role-specific record
    if role == 'lender':
        lender = Lender(
            user_id=user.id,
            min_amount=data.get('min_amount', 0),
            max_amount=data.get('max_amount', 10000),
            interest_rate=data.get('interest_rate', 5.0),
            remarks=data.get('remarks', '')
        )
        db.session.add(lender)
    elif role == 'borrower':
        borrower = Borrower(
            user_id=user.id,
            credit_score=750  # Default credit score
        )
        db.session.add(borrower)
    
    db.session.commit()
    
    # Create block for user creation in blockchain ledger
    unique_data_id = str(uuid.uuid4()) + "_" + get_ist_time().isoformat()
    create_block(unique_data_id, "admin", "User Created", {
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
        "email": user.email
    })
    
    return jsonify({'success': True, 'message': 'User created successfully'})

@app.route('/api/lenders', methods=['GET'])
def get_lenders():
    # Admin, lenders, and borrowers can view lenders
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    lenders = Lender.query.join(User).all()
    result = []
    
    for lender in lenders:
        result.append({
            'id': lender.id,
            'user_id': lender.user_id,
            'name': lender.user.name,
            'email': lender.user.email,
            'wallet_address': lender.user.wallet_address,
            'min_amount': lender.min_amount,
            'max_amount': lender.max_amount,
            'interest_rate': lender.interest_rate,
            'account_balance': lender.account_balance,
            'remarks': lender.remarks,
            'created_at': lender.created_at.isoformat()
        })
    
    return jsonify({'success': True, 'lenders': result})

@app.route('/api/borrowers', methods=['GET'])
def get_borrowers():
    # Only admin can view borrowers
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    borrowers = Borrower.query.join(User).all()
    result = []
    
    for borrower in borrowers:
        result.append({
            'id': borrower.id,
            'user_id': borrower.user_id,
            'name': borrower.user.name,
            'email': borrower.user.email,
            'wallet_address': borrower.user.wallet_address,
            'credit_score': borrower.credit_score,
            'account_balance': borrower.account_balance,
            'created_at': borrower.created_at.isoformat()
        })
    
    return jsonify({'success': True, 'borrowers': result})

# Borrower routes
@app.route('/api/borrowers/<int:borrower_id>/collateral', methods=['POST'])
def upload_collateral(borrower_id):
    # Check if user is authorized
    if session.get('user_id') != borrower_id and session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    # Sanitize filename
    if file.filename:
        filename = hashlib.md5(file.filename.encode()).hexdigest()[:10] + "_" + file.filename
    else:
        filename = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:10] + "_upload"
    
    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Create collateral record
    unique_data_id = str(uuid.uuid4()) + "_" + get_ist_time().isoformat()
    collateral = Collateral(
        borrower_id=borrower_id,
        filename=file.filename or filename,
        filepath=filepath,
        unique_data_id=unique_data_id
    )
    
    db.session.add(collateral)
    db.session.commit()
    
    # Create block for collateral upload in blockchain ledger
    create_block(unique_data_id, f"borrower_{borrower_id}", "Collateral Uploaded", {
        "collateral_id": collateral.id,
        "filename": file.filename or filename,
        "borrower_id": borrower_id
    })
    
    return jsonify({'success': True, 'message': 'Collateral uploaded successfully'})

# Loan routes
@app.route('/api/loans', methods=['POST'])
def create_loan():
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json()
    # Get borrower_id from session if not provided in request
    borrower_id = data.get('borrower_id') or session.get('user_id')
    amount = data.get('amount')
    
    # Validate borrower_id
    if not borrower_id:
        return jsonify({'success': False, 'message': 'Borrower ID is required'}), 400
    
    # Check if user is authorized (either the borrower themselves or admin)
    if session.get('user_id') != borrower_id and session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Check if borrower has an active loan in the last 24 hours
    twenty_four_hours_ago = get_ist_time() - timedelta(hours=24)
    recent_loan = Loan.query.filter(
        Loan.borrower_id == borrower_id,
        Loan.created_at > twenty_four_hours_ago
    ).first()
    
    if recent_loan:
        return jsonify({'success': False, 'message': 'Cannot request another loan within 24 hours'}), 400
    
    # Create loan without assigning a specific lender
    unique_data_id = str(uuid.uuid4()) + "_" + get_ist_time().isoformat()
    loan = Loan(
        unique_data_id=unique_data_id,
        borrower_id=borrower_id,
        amount=amount,
        # No lender assigned initially
        status='requested'
    )
    
    db.session.add(loan)
    db.session.commit()
    
    # Create block for loan request in blockchain ledger
    create_block(unique_data_id, f"borrower_{borrower_id}", "Loan Requested", {
        "loan_id": loan.id,
        "amount": amount,
        "borrower_id": borrower_id
    })
    
    return jsonify({'success': True, 'message': 'Loan request created successfully', 'loan_id': loan.id})

@app.route('/api/loans/<int:loan_id>/approve', methods=['PUT'])
def approve_loan(loan_id):
    # Check if user is admin or lender
    if session.get('role') not in ['admin', 'lender']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    status = data.get('status')  # approved or rejected
    lender_id = data.get('lender_id')
    interest_rate = data.get('interest_rate')  # Get interest rate from request
    
    # Get loan
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'success': False, 'message': 'Loan not found'}), 404
    
    # Update loan status
    loan.status = status
    if status == 'approved':
        loan.lender_id = lender_id
        loan.interest_rate = interest_rate  # Set the interest rate
        loan.disbursed_at = get_ist_time()
        
        # Transfer funds from lender to borrower when loan is approved
        lender = Lender.query.get(lender_id)
        borrower = Borrower.query.get(loan.borrower_id)
        
        # Get borrower name for better error messages
        borrower_user = User.query.get(borrower.user_id) if borrower else None
        borrower_name = borrower_user.name if borrower_user else 'Unknown Borrower'
        
        if lender and borrower:
            # Check if lender has sufficient balance
            if lender.account_balance >= loan.amount:
                lender.account_balance -= loan.amount
                borrower.account_balance += loan.amount
                
                # Reduce borrower's credit score when loan is approved (as a form of credit check)
                # Reduce by 25 points for taking a loan to reflect the risk
                borrower.credit_score -= 25
            else:
                return jsonify({'success': False, 'message': 'Lender has insufficient balance'}), 400
        else:
            if not lender and not borrower:
                return jsonify({'success': False, 'message': f'Neither lender nor borrower found for loan of {borrower_name}'}), 404
            elif not lender:
                return jsonify({'success': False, 'message': f'Lender not found for loan of {borrower_name}'}), 404
            else:  # not borrower
                return jsonify({'success': False, 'message': f'Borrower {borrower_name} not found'}), 404
    
    db.session.commit()
    
    # Create block for loan approval/rejection in blockchain ledger
    create_block(loan.unique_data_id, session.get('role'), f"Loan {status.capitalize()}", {
        "loan_id": loan.id,
        "status": status,
        "approved_by": session.get('role')
    })
    
    return jsonify({'success': True, 'message': f'Loan {status} successfully'})

@app.route('/api/loans/<int:loan_id>/repay', methods=['POST'])
def repay_loan(loan_id):
    # Check if user is authorized
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'success': False, 'message': 'Loan not found'}), 404
    
    if session.get('user_id') != loan.borrower_id and session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Update loan status
    loan.status = 'paid'
    loan.repaid_at = get_ist_time()
    
    # Update borrower's credit score
    borrower = Borrower.query.get(loan.borrower_id)
    
    # Get borrower name for better error messages
    borrower_user = User.query.get(borrower.user_id) if borrower else None
    borrower_name = borrower_user.name if borrower_user else 'Unknown Borrower'
    
    # Calculate credit score change (increase when repaying loan)
    credit_change = 0
    if loan.repaid_at and loan.due_date and loan.repaid_at <= loan.due_date:
        credit_change += 15  # On time repayment bonus
        if loan.repaid_at < loan.due_date:
            credit_change += 5  # Early repayment bonus
    else:
        credit_change -= 25  # Late repayment penalty
    
    borrower.credit_score += credit_change
    
    # Transfer funds from borrower to lender when loan is repaid
    if loan.lender_id:
        lender = Lender.query.get(loan.lender_id)
        # Calculate total amount to be repaid (principal + interest)
        interest_amount = loan.amount * (loan.interest_rate / 100)
        total_repayment = loan.amount + interest_amount
        
        if borrower and lender:
            # Check if borrower has sufficient balance
            if borrower.account_balance >= total_repayment:
                borrower.account_balance -= total_repayment
                lender.account_balance += total_repayment
            else:
                return jsonify({'success': False, 'message': f'{borrower_name} has insufficient balance for repayment'}), 400
        else:
            if not borrower and not lender:
                return jsonify({'success': False, 'message': f'Neither borrower nor lender found for repayment of loan by {borrower_name}'}), 404
            elif not borrower:
                return jsonify({'success': False, 'message': f'Borrower {borrower_name} not found for loan repayment'}), 404
            else:  # not lender
                lender_user = User.query.get(lender.user_id) if lender else None
                lender_name = lender_user.name if lender_user else 'Unknown Lender'
                return jsonify({'success': False, 'message': f'Lender {lender_name} not found for loan repayment'}), 404
    
    db.session.commit()
    
    # Create block for loan repayment in blockchain ledger
    create_block(loan.unique_data_id, f"borrower_{loan.borrower_id}", "Loan Repaid", {
        "loan_id": loan.id,
        "credit_change": credit_change,
        "repaid_at": loan.repaid_at.isoformat()
    })
    
    return jsonify({'success': True, 'message': 'Loan repaid successfully', 'credit_change': credit_change})

# New endpoint to get all loan requests for lenders
@app.route('/api/loans/requests', methods=['GET'])
def get_loan_requests():
    # Check if user is authorized (lenders and admins can view loan requests)
    if session.get('role') not in ['admin', 'lender']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Get all requested loans
    loans = Loan.query.filter(Loan.status == 'requested').all()
    result = []
    
    for loan in loans:
        borrower = Borrower.query.get(loan.borrower_id)
        user = User.query.get(borrower.user_id) if borrower else None
        
        result.append({
            'id': loan.id,
            'borrower_name': user.name if user else 'Unknown',
            'borrower_id': loan.borrower_id,
            'amount': loan.amount,
            'status': loan.status,
            'created_at': loan.created_at.isoformat() if loan.created_at else None
        })
    
    return jsonify({'success': True, 'loans': result})

@app.route('/api/lenders/<int:lender_id>/loans', methods=['GET'])
def get_lender_loans(lender_id):
    # Check if user is authorized
    if session.get('role') not in ['admin', 'lender'] or (session.get('role') == 'lender' and session.get('user_id') != lender_id):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Get loans for this lender
    loans = Loan.query.filter(Loan.lender_id == lender_id).all()
    result = []
    
    for loan in loans:
        borrower = Borrower.query.get(loan.borrower_id)
        user = User.query.get(borrower.user_id) if borrower else None
        
        result.append({
            'id': loan.id,
            'borrower_name': user.name if user else 'Unknown',
            'amount': loan.amount,
            'interest_rate': loan.interest_rate,
            'status': loan.status,
            'created_at': loan.created_at.isoformat() if loan.created_at else None
        })
    
    return jsonify({'success': True, 'loans': result})

# Add this new endpoint for borrowers to get their own data
@app.route('/api/borrowers/me', methods=['GET'])
def get_current_borrower():
    # Check if user is logged in and is a borrower or admin
    user_id = session.get('user_id')
    user_role = session.get('role')
    
    if not user_id or user_role not in ['borrower', 'admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Get the borrower record for this user
    borrower = Borrower.query.filter_by(user_id=user_id).first()
    
    if not borrower:
        # If no borrower record exists, return user data with default borrower info
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
        return jsonify({
            'success': True,
            'borrower': {
                'id': user_id,
                'user_id': user_id,
                'name': user.name,
                'email': user.email,
                'wallet_address': user.wallet_address,
                'credit_score': 750,
                'account_balance': 50000.0,
                'created_at': get_ist_time().isoformat()
            }
        })
    
    # Return borrower data
    return jsonify({
        'success': True,
        'borrower': {
            'id': borrower.id,
            'user_id': borrower.user_id,
            'name': borrower.user.name,
            'email': borrower.user.email,
            'wallet_address': borrower.user.wallet_address,
            'credit_score': borrower.credit_score,
            'account_balance': borrower.account_balance,
            'created_at': borrower.created_at.isoformat() if borrower.created_at else get_ist_time().isoformat()
        }
    })

# Add this new endpoint for borrowers to get their loans
@app.route('/api/borrowers/<int:borrower_id>/loans', methods=['GET'])
def get_borrower_loans(borrower_id):
    # Check if user is authorized
    if session.get('role') not in ['admin', 'borrower'] or (session.get('role') == 'borrower' and session.get('user_id') != borrower_id):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Get loans for this borrower
    loans = Loan.query.filter(Loan.borrower_id == borrower_id).all()
    result = []
    
    for loan in loans:
        lender = Lender.query.get(loan.lender_id) if loan.lender_id else None
        user = User.query.get(lender.user_id) if lender else None
        
        result.append({
            'id': loan.id,
            'lender_name': user.name if user else 'Unknown',
            'amount': loan.amount,
            'interest_rate': loan.interest_rate,
            'status': loan.status,
            'created_at': loan.created_at.isoformat() if loan.created_at else None,
            'due_date': loan.due_date.isoformat() if loan.due_date else None,
            'disbursed_at': loan.disbursed_at.isoformat() if loan.disbursed_at else None,
            'repaid_at': loan.repaid_at.isoformat() if loan.repaid_at else None
        })
    
    return jsonify({'success': True, 'loans': result})

# Ledger routes
@app.route('/api/ledger', methods=['GET'])
def get_ledger():
    blocks = Block.query.order_by(Block.id.asc()).all()
    result = []
    
    for block in blocks:
        result.append({
            'id': block.id,
            'unique_data_id': block.unique_data_id,
            'prev_hash': block.prev_hash,
            'hash': block.hash,
            'timestamp': block.timestamp,
            'actor': block.actor,
            'event_type': block.event_type,
            'metadata': json.loads(block.block_metadata) if block.block_metadata else None
        })
    
    return jsonify({'success': True, 'blocks': result})

# Utility route to verify blockchain integrity
@app.route('/api/ledger/verify', methods=['GET'])
def verify_ledger():
    blocks = Block.query.order_by(Block.id.asc()).all()
    is_valid = True
    error_message = ""
    
    for i, block in enumerate(blocks):
        if i == 0:
            # Genesis block validation
            if block.prev_hash != "0" * 64:
                is_valid = False
                error_message = f"Invalid genesis block prev_hash at index {i}"
                break
        else:
            # Validate hash chain
            prev_block = blocks[i-1]
            if block.prev_hash != prev_block.hash:
                is_valid = False
                error_message = f"Hash mismatch at block {i}"
                break
            
            # Recalculate hash to verify integrity
            data_string = block.prev_hash + block.unique_data_id + block.timestamp + str(block.nonce)
            recalculated_hash = hashlib.sha256(data_string.encode()).hexdigest()
            
            if block.hash != recalculated_hash:
                is_valid = False
                error_message = f"Hash calculation mismatch at block {i}"
                break
    
    return jsonify({
        'success': True,
        'is_valid': is_valid,
        'error_message': error_message if not is_valid else None
    })

# New endpoint to get user details by name for demonstration
@app.route('/api/users/name/<user_name>', methods=['GET'])
def get_user_by_name(user_name):
    try:
        # Get user by name
        user = User.query.filter_by(name=user_name).first()
        if not user:
            return jsonify({'success': False, 'message': f'User {user_name} not found'}), 404
        
        result = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'wallet_address': user.wallet_address,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        
        # Add role-specific details
        if user.role == 'lender':
            lender = Lender.query.filter_by(user_id=user.id).first()
            if lender:
                result['account_balance'] = lender.account_balance
                result['min_amount'] = lender.min_amount
                result['max_amount'] = lender.max_amount
                result['interest_rate'] = lender.interest_rate
                result['remarks'] = lender.remarks
        elif user.role == 'borrower':
            borrower = Borrower.query.filter_by(user_id=user.id).first()
            if borrower:
                result['account_balance'] = borrower.account_balance
                result['credit_score'] = borrower.credit_score
        
        return jsonify({'success': True, 'user': result})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error retrieving user: {str(e)}'}), 500

# New endpoint to get loan details between two users for demonstration
@app.route('/api/loans/between/<lender_name>/<borrower_name>', methods=['GET'])
def get_loan_between_users(lender_name, borrower_name):
    try:
        # Get lender and borrower users
        lender_user = User.query.filter_by(name=lender_name, role='lender').first()
        borrower_user = User.query.filter_by(name=borrower_name, role='borrower').first()
        
        if not lender_user:
            return jsonify({'success': False, 'message': f'Lender {lender_name} not found'}), 404
        
        if not borrower_user:
            return jsonify({'success': False, 'message': f'Borrower {borrower_name} not found'}), 404
        
        # Get lender and borrower records
        lender = Lender.query.filter_by(user_id=lender_user.id).first()
        borrower = Borrower.query.filter_by(user_id=borrower_user.id).first()
        
        if not lender:
            return jsonify({'success': False, 'message': f'Lender record for {lender_name} not found'}), 404
        
        if not borrower:
            return jsonify({'success': False, 'message': f'Borrower record for {borrower_name} not found'}), 404
        
        # Get loans between these users
        loans = Loan.query.filter_by(lender_id=lender.id, borrower_id=borrower.id).all()
        
        result = []
        for loan in loans:
            result.append({
                'id': loan.id,
                'amount': loan.amount,
                'interest_rate': loan.interest_rate,
                'status': loan.status,
                'created_at': loan.created_at.isoformat() if loan.created_at else None,
                'disbursed_at': loan.disbursed_at.isoformat() if loan.disbursed_at else None,
                'repaid_at': loan.repaid_at.isoformat() if loan.repaid_at else None
            })
        
        # Also return current account balances
        response_data = {
            'loans': result,
            'lender': {
                'name': lender_user.name,
                'account_balance': lender.account_balance
            },
            'borrower': {
                'name': borrower_user.name,
                'account_balance': borrower.account_balance,
                'credit_score': borrower.credit_score
            }
        }
        
        return jsonify({'success': True, 'data': response_data})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error retrieving loan details: {str(e)}'}), 500

# New endpoint to add money to user account
@app.route('/api/users/add-money', methods=['POST'])
def add_money():
    # Check if user is logged in
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    amount = data.get('amount')
    
    # Validate amount
    if not amount or amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    
    user_id = session.get('user_id')
    user_role = session.get('role')
    
    try:
        if user_role == 'lender':
            # Get lender record
            lender = Lender.query.filter_by(user_id=user_id).first()
            # Get user name for better error messages
            user = User.query.get(user_id)
            user_name = user.name if user else 'Unknown User'
            
            if lender:
                lender.account_balance += amount
                db.session.commit()
                return jsonify({
                    'success': True, 
                    'message': f'₹{amount} added successfully',
                    'new_balance': lender.account_balance
                })
            else:
                return jsonify({'success': False, 'message': f'Lender record for {user_name} not found'}), 404
                
        elif user_role == 'borrower':
            # Get borrower record
            borrower = Borrower.query.filter_by(user_id=user_id).first()
            # Get user name for better error messages
            user = User.query.get(user_id)
            user_name = user.name if user else 'Unknown User'
            
            if borrower:
                borrower.account_balance += amount
                db.session.commit()
                return jsonify({
                    'success': True, 
                    'message': f'₹{amount} added successfully',
                    'new_balance': borrower.account_balance
                })
            else:
                return jsonify({'success': False, 'message': f'Borrower record for {user_name} not found'}), 404
                
        elif user_role == 'admin':
            # Admins don't have account balances in the current model
            return jsonify({'success': False, 'message': 'Admins cannot add money'}), 400
            
        else:
            return jsonify({'success': False, 'message': 'Invalid user role'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to add money: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)