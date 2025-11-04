import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Lender, Borrower, Loan
import pytz
from datetime import datetime

# Helper function to get IST timezone
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def add_demo_data():
    with app.app_context():
        # Check if the demo loan already exists
        borrower_user = User.query.filter_by(name='maddy', role='borrower').first()
        lender_user = User.query.filter_by(name='kv', role='lender').first()
        
        if not borrower_user:
            print("Borrower 'maddy' not found in database")
            return
            
        if not lender_user:
            print("Lender 'kv' not found in database")
            return
            
        # Get borrower and lender records
        borrower = Borrower.query.filter_by(user_id=borrower_user.id).first()
        lender = Lender.query.filter_by(user_id=lender_user.id).first()
        
        if not borrower:
            print("Borrower record for 'maddy' not found")
            return
            
        if not lender:
            print("Lender record for 'kv' not found")
            return
            
        # Check if demo loan already exists
        existing_loan = Loan.query.filter_by(
            borrower_id=borrower.id, 
            lender_id=lender.id, 
            amount=5000.0
        ).first()
        
        if existing_loan:
            print("Demo loan already exists")
            return
            
        # Create a loan from Maddy (borrower) to Kv (lender) for demonstration
        demo_loan = Loan(
            unique_data_id='demo_maddy_loan_' + get_ist_time().isoformat(),
            borrower_id=borrower.id,    # Maddy's borrower id
            lender_id=lender.id,        # Kv's lender id
            amount=5000.0,              # Loan amount of ₹5000
            interest_rate=7.5,          # Interest rate of 7.5%
            status='approved',          # Approved status
            disbursed_at=get_ist_time() # Loan has been disbursed
        )
        db.session.add(demo_loan)
        
        # Update account balances to reflect the loan transaction
        # Kv's balance decreases by loan amount
        lender.account_balance -= 5000.0
        # Maddy's balance increases by loan amount
        borrower.account_balance += 5000.0
        
        # Reduce Maddy's credit score as per our new system when loan is approved
        borrower.credit_score -= 25
        
        # Commit all changes
        db.session.commit()
        
        print("Demo loan data added successfully!")
        print(f"Loan ID: {demo_loan.id}")
        print(f"Amount: ₹5000.00")
        print(f"Borrower: {borrower_user.name}")
        print(f"Lender: {lender_user.name}")
        print(f"New balance for {lender_user.name}: ₹{lender.account_balance:,.2f}")
        print(f"New balance for {borrower_user.name}: ₹{borrower.account_balance:,.2f}")
        print(f"New credit score for {borrower_user.name}: {borrower.credit_score}")

if __name__ == '__main__':
    add_demo_data()