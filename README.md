# 💸 DFinanceApp – Decentralized Finance Loan Portal  

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Backend-Flask-red)
![React](https://img.shields.io/badge/Frontend-React-blue)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Blockchain](https://img.shields.io/badge/Feature-PseudoBlockchain-yellow)
![Docker](https://img.shields.io/badge/Container-Docker-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Overview  
**DFinanceApp** is a decentralized finance (DeFi)-style **loan management platform** built using **Flask (backend)** and **React (frontend)**.  
It provides a secure, transparent, and traceable environment for **Admins**, **Lenders**, and **Borrowers** through a **pseudo-blockchain ledger** that ensures transaction integrity and traceability.

---

## 🧩 Features  

### 👨‍💼 Roles & Authentication  
- Three roles: **Admin**, **Lender**, **Borrower**  
- Flask session-based authentication  
- Admin manages all user accounts and loan approvals  
- Pre-seeded Admin credentials:  


Email: admin@gmail.com

Password: 1234


---

### 💰 Lender Module  
- Define loan policies (minimum/maximum amounts, interest rates)  
- Approve or reject loan requests from borrowers  
- View lending and repayment history  

---

### 👤 Borrower Module  
- Default credit score: **750**  
- Request loans based on eligibility and lender's limits  
- Upload **collateral** files securely  
- Repay loans and earn higher credit scores for timely payments  
- 24-hour cooldown enforced between loan requests  

---

### 🔗 Blockchain-like Ledger  
- Each event is recorded as a **block** using SHA-256 hashing  
- Chain verification to ensure **no tampering**  
- Records key activities such as:
  - User creation  
  - Loan requests  
  - Approvals/Rejections  
  - Collateral uploads  
  - Repayments  

---

## ⚙️ Tech Stack  

| Layer | Technology |
|-------|-------------|
| **Frontend** | React.js, React Router, Ethers.js |
| **Backend** | Flask (Python), Flask-SQLAlchemy |
| **Database** | SQLite |
| **Security** | SHA-256 Hashing, Session Authentication |
| **Blockchain Simulation** | Custom Python Ledger |
| **Containerization** | Docker |
| **Version Control** | Git + GitHub Actions |

---

## 🖥️ Project Structure  

```
DFinanceApp/
├── backend/
│   ├── app.py              # Flask application and routes
│   ├── models.py           # Database models
│   ├── database.py         # Database configuration
│   ├── init_db.py          # Database initialization
│   ├── requirements.txt    # Python dependencies
│   └── instance/
│       └── defi_loan.db    # SQLite database
├── frontend/
│   └── defi-loan-portal/   # React application
│       ├── public/
│       └── src/
│           ├── components/ # React components
│           ├── App.js      # Main application component
│           └── index.js    # Entry point
├── uploads/                # Collateral file storage
├── start.sh                # Unix startup script
├── start.bat               # Windows startup script
└── README.md
```

---

## 🧠 Credit Score Logic  

| Event | Score Change |
|--------|---------------|
| On-time repayment | +10 |
| Early repayment | +15 |
| Late or default | −25 |

---

## ⚡ Setup Instructions  

### 🔹 Backend Setup  
```bash
cd backend
python -m venv venv
# Activate virtual environment
# (Windows)
venv\Scripts\activate
# (Linux/Mac)
source venv/bin/activate

pip install -r requirements.txt
python init_db.py
python app.py
```

Backend runs at:
👉 http://127.0.0.1:5000/

### 🔹 Frontend Setup
```bash
cd frontend/defi-loan-portal
npm install
npm start
```

Frontend runs at:
👉 http://localhost:3000/

---

## 🔒 Blockchain Ledger Demo

Each transaction generates a block with:

- Block ID
- Timestamp
- Event Type
- SHA-256 Hash
- Previous Block Hash

### ✅ Verification Process

Each block's `prev_hash` must match the previous block's hash.

If any hash differs, it indicates tampering.

Admin can trigger ledger verification anytime to validate integrity.

---

## 🪙 MetaMask Integration

- Integrated MetaMask wallet via ethers.js
- Users can connect wallets directly from frontend
- Stores wallet address in the backend securely
- (Optional) Signature-based identity verification
- Required for key loan and repayment operations

---

## 🧾 Seeded Database

Default data on first run:

- ✅ Admin: admin@gmail.com / 1234
- ✅ 2 Sample Lenders
- ✅ 2 Sample Borrowers
- ✅ 1 Demo Loan Record

---

## 📊 Bonus Features

- Loan interest rate calculator
- Credit score trend visualization
- CSV export for ledger data
- Cooldown timer for borrowers (24-hour restriction)
- Blockchain verification audit log
- Account balance display and fund management

---

## 🧑‍💻 Contributors
| Name | Role |
|------|------|
| Keerthivasan | Project Lead & Full-Stack Developer |
| (Add your teammates here) | Collaborators / Reviewers |

---

## 🧩 Future Enhancements

- 🔗 Integration with real Ethereum smart contracts
- 🧮 AI-based credit scoring predictions
- ☁️ Cloud deployment on AWS / GCP / Azure
- 🔐 Role-based access control with JWT
- 🪪 Multi-wallet and DeFi protocol integration

---

## ⚙️ CI/CD Pipeline

This repository uses GitHub Actions for continuous integration and deployment:

- ✅ Code linting and formatting
- ✅ Backend test runs (pytest)
- ✅ Frontend build checks
- ✅ Optional auto-deploy to DockerHub or Render

Workflow file path: `.github/workflows/build.yml`

---

## 🪪 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this code with proper attribution.

---

## ⭐ Acknowledgments

Special thanks to the Open Source and DeFi developer communities for inspiration and resources.

💡 This application is for educational and demonstration purposes only. It does not involve real cryptocurrency transactions.
