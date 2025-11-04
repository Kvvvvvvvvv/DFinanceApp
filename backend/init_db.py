import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Lender, Borrower, Collateral, Loan, Block
import pytz
from datetime import datetime

# Helper function to get IST timezone
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@gmail.com').first()
        
        if not admin_user:
            # Create admin user
            admin = User(
                name='keerthivasan',
                email='admin@gmail.com',
                password='1234',
                role='admin'
            )
            db.session.add(admin)
            db.session.flush()
            
            # Create sample lenders
            lender1 = User(
                name='kv',
                email='kv@lender.com',
                password='1234',
                role='lender',
                wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            )
            db.session.add(lender1)
            db.session.flush()
            
            lender1_details = Lender(
                user_id=lender1.id,
                min_amount=100.0,
                max_amount=10000.0,
                interest_rate=7.5,
                remarks='Preferred lender for small to medium loans',
                account_balance=150000.0
            )
            db.session.add(lender1_details)
            
            lender2 = User(
                name='gaurish',
                email='gaurish@lender.com',
                password='1234',
                role='lender',
                wallet_address='0x842d35Cc6634C0532925a3b844Bc454e4438f44f'
            )
            db.session.add(lender2)
            db.session.flush()
            
            lender2_details = Lender(
                user_id=lender2.id,
                min_amount=5000.0,
                max_amount=50000.0,
                interest_rate=6.0,
                remarks='Specializes in large loans',
                account_balance=200000.0
            )
            db.session.add(lender2_details)
            
            # Create sample borrowers
            borrower1 = User(
                name='ashley',
                email='ashley@borrower.com',
                password='1234',
                role='borrower',
                wallet_address='0x942d35Cc6634C0532925a3b844Bc454e4438f44g'
            )
            db.session.add(borrower1)
            db.session.flush()
            
            borrower1_details = Borrower(
                user_id=borrower1.id,
                credit_score=750,
                account_balance=75000.0
            )
            db.session.add(borrower1_details)
            
            borrower2 = User(
                name='maddy',
                email='maddy@borrower.com',
                password='1234',
                role='borrower',
                wallet_address='0xa42d35Cc6634C0532925a3b844Bc454e4438f44h'
            )
            db.session.add(borrower2)
            db.session.flush()
            
            borrower2_details = Borrower(
                user_id=borrower2.id,
                credit_score=720,
                account_balance=60000.0
            )
            db.session.add(borrower2_details)
            
            # Create a sample loan
            sample_loan = Loan(
                unique_data_id='sample_loan_' + get_ist_time().isoformat(),
                borrower_id=borrower1_details.id,
                lender_id=lender1_details.id,
                amount=1000.0,
                interest_rate=7.5,
                status='approved'
            )
            db.session.add(sample_loan)
            
            # Create a loan from Maddy (borrower) to Kv (lender) for demonstration
            maddy_loan = Loan(
                unique_data_id='maddy_loan_' + get_ist_time().isoformat(),
                borrower_id=borrower2_details.id,  # Maddy's borrower id
                lender_id=lender1_details.id,      # Kv's lender id
                amount=5000.0,                     # Loan amount of ₹5000
                interest_rate=7.5,                 # Interest rate of 7.5%
                status='approved',                 # Approved status
                disbursed_at=get_ist_time()        # Loan has been disbursed
            )
            db.session.add(maddy_loan)
            
            # Update account balances to reflect the loan transaction
            # Kv's balance decreases by loan amount
            lender1_details.account_balance -= 5000.0
            # Maddy's balance increases by loan amount
            borrower2_details.account_balance += 5000.0
            
            # Reduce Maddy's credit score as per our new system when loan is approved
            borrower2_details.credit_score -= 25
            
            # Create genesis block
            genesis_block = Block(
                unique_data_id='genesis_block',
                prev_hash='0' * 64,
                hash='a' * 64,
                timestamp=get_ist_time().isoformat(),
                nonce=0,
                actor='system',
                event_type='Genesis Block'
            )
            db.session.add(genesis_block)
            
            # Commit all changes
            db.session.commit()
            
            print("Database initialized with sample data!")
        else:
            print("Database already initialized!")

if __name__ == '__main__':
    init_db()