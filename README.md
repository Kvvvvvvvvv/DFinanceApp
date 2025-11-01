# DeFi Loan Portal

A complete web application with Flask backend and React frontend for managing decentralized finance loans with blockchain-like ledger functionality.

## Features

### Roles & Authentication
- Three roles: Admin, Lender, and Borrower
- Admin credentials: admin@gmail.com / 1234 (pre-seeded)
- Flask-based authentication with session management
- Only admin can create and manage lenders and borrowers

### Lender Module
- Manage lending details (min/max amounts, interest rates)
- View and approve/reject loan requests
- Loan history tracking

### Borrower Module
- Credit score system (starts at 750)
- Collateral upload functionality
- Loan request and repayment capabilities
- 24-hour cooldown period between loans

### Loan Module
- Loan lifecycle management (requested, approved, rejected, disbursed, paid, overdue)
- Automatic credit score updates based on repayment behavior
- Validation of loan amounts within lender limits

### Collateral Module
- Secure file upload to `/uploads/` directory
- Sanitized filenames for security
- Blockchain record creation for each upload

### Blockchain-like Ledger
- Pseudo-blockchain table to store transaction history
- SHA256 hashing for block integrity
- Chain verification functionality
- Records for all key events (user creation, loans, collateral, etc.)

## Technology Stack

### Backend
- Flask (Python web framework)
- Flask-SQLAlchemy (ORM for SQLite)
- SQLite (Database)
- hashlib, uuid (for blockchain functionality)

### Frontend
- React (with hooks and functional components)
- React Router (for navigation)
- ethers.js (for Metamask integration)
- Modern CSS with responsive design

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```bash
   python init_db.py
   ```

6. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend/defi-loan-portal
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## API Endpoints

- `POST /api/login` - User login
- `POST /api/register` - Register new user (admin only)
- `GET /api/lenders` - Get all lenders
- `GET /api/borrowers` - Get all borrowers
- `POST /api/borrowers/<id>/collateral` - Upload collateral
- `POST /api/loans` - Create new loan request
- `PUT /api/loans/<id>/approve` - Approve/reject loan
- `POST /api/loans/<id>/repay` - Mark loan as repaid
- `GET /api/ledger` - Get all blockchain blocks
- `GET /api/ledger/verify` - Verify blockchain integrity

## Seeded Data

The database is preloaded with:
- Admin user: admin@gmail.com / 1234
- 2 sample lenders with different lending criteria
- 2 sample borrowers with initial credit scores
- 1 sample loan for demonstration

## Credit Score Update Scenarios

1. **On-time repayment**: +10 points
2. **Early repayment**: +10 points (on-time) + 5 points (bonus) = +15 points
3. **Late/default repayment**: -25 points

## Blockchain Ledger Demo

Each major action in the system creates a new block in the pseudo-blockchain:
1. User creation
2. Loan requests
3. Collateral uploads
4. Loan approvals/rejections
5. Loan repayments

The blockchain verification feature ensures the integrity of the entire chain by:
- Checking that each block's prev_hash matches the previous block's hash
- Recalculating each block's hash to verify it hasn't been tampered with

## Metamask Integration

The frontend includes Metamask integration:
- "Connect Wallet" button to capture Ethereum wallet address
- Wallet address stored in the database
- Required for major operations
- Optional message signing for identity confirmation

## Bonus Features

- Loan repayment calculator (interest computation)
- Credit score trend visualization
- Admin can export ledger data as CSV
- Borrowers can see "Next eligible loan date" (24-hour cooldown)