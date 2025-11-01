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
                name='Admin User',
                email='admin@gmail.com',
                password='1234',
                role='admin'
            )
            db.session.add(admin)
            db.session.flush()
            
            # Create sample lenders
            lender1 = User(
                name='John Lender',
                email='john@lender.com',
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
                remarks='Preferred lender for small to medium loans'
            )
            db.session.add(lender1_details)
            
            lender2 = User(
                name='Jane Lender',
                email='jane@lender.com',
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
                remarks='Specializes in large loans'
            )
            db.session.add(lender2_details)
            
            # Create sample borrowers
            borrower1 = User(
                name='Alice Borrower',
                email='alice@borrower.com',
                password='1234',
                role='borrower',
                wallet_address='0x942d35Cc6634C0532925a3b844Bc454e4438f44g'
            )
            db.session.add(borrower1)
            db.session.flush()
            
            borrower1_details = Borrower(
                user_id=borrower1.id,
                credit_score=750
            )
            db.session.add(borrower1_details)
            
            borrower2 = User(
                name='Bob Borrower',
                email='bob@borrower.com',
                password='1234',
                role='borrower',
                wallet_address='0xa42d35Cc6634C0532925a3b844Bc454e4438f44h'
            )
            db.session.add(borrower2)
            db.session.flush()
            
            borrower2_details = Borrower(
                user_id=borrower2.id,
                credit_score=720
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