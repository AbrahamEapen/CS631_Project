🏦 Banking Web Application

A full-stack web-based banking system built with Flask, PostgreSQL, JWT authentication, and a modular service-oriented architecture. The system supports user account management, transactions, and admin-level oversight through a secure REST API and interactive frontend.

📌 Table of Contents
Overview
Frontend Architecture
Backend Architecture
System Design Model
Database Schema
Features
Technologies Used
Setup Instructions
API Overview

📖 Overview

This application simulates a simplified banking system where users can:

Register and log in securely
Manage bank accounts
Perform deposits and withdrawals
View transaction history

Admins can:

View all users
View all transactions in the system

The system is designed using a layered architecture separating:

Presentation Layer (Frontend)
API Layer (Routes)
Business Logic Layer (Services)
Data Layer (Database Models)

🎨 Frontend Architecture

The frontend is built using:

Jinja2 Templates (Flask rendering)
**Bootstrap 5 (UI styling)`
Vanilla JavaScript (AJAX-based API calls)
📁 Structure
static/
├── css/styles.css
├── js/
│   ├── api.js
│   ├── auth.js
│   ├── dashboard.js
│   └── transactions.js
templates/
├── login.html
├── dashboard.html
⚙️ Key Features
🔐 Authentication UI
Login and registration forms
JWT token stored in localStorage
Redirect-based session handling
📊 Dashboard
Displays user accounts
Shows balances
Allows account creation/deletion
💳 Transactions UI
Deposit funds
Withdraw funds
View transaction history dynamically

🧠 Backend Architecture

The backend follows a modular Flask application factory pattern.

📁 Structure
app/
├── routes/
├── services/
├── models/
├── extensions.py
├── __init__.py

🔷 Layers
1. Routes Layer (API Controllers)

Handles HTTP requests only:

Input validation
JWT verification
Response formatting

2. Service Layer (Business Logic)

Contains all core logic:

Account validation
Transaction processing
Ownership enforcement

3. Data Layer (Models)

SQLAlchemy ORM models represent:

Users
Customers
Accounts
Transactions
Branches
Employees

4. Extensions Layer

Manages shared components:

SQLAlchemy (db)
JWT Manager (jwt)

🧱 System Architecture Model

The system follows a 3-tier architecture:

Frontend (Jinja + JS)
        ↓
Flask REST API (Routes + Services)
        ↓
PostgreSQL Database
🔐 Authentication Flow
User Login → JWT Token Generated → Stored in Browser →
API Requests include Bearer Token → Backend Validates Token

🔄 Transaction Flow
Frontend Action (Deposit/Withdraw)
        ↓
API Request (JWT secured)
        ↓
Service Layer validates ownership
        ↓
Balance updated in DB
        ↓
Transaction recorded
        ↓
Response returned to UI

🗄️ Database Schema (Normalized Design)

The database is fully normalized (3NF) and based on relational banking ERD.

📌 Core Tables
👤 Users
id (PK)
username
password_hash
role (user/admin)
🧑 Customers
customer_ssn (PK)
name
🏦 Accounts
account_number (PK)
balance
🔗 Account Holders (M:N)
customer_ssn (FK)
account_number (FK)
💳 Transactions
transaction_id (PK)
account_number (FK)
amount
transaction_type (deposit/withdraw)
transaction_date
🏢 Branches
branch_id (PK)
name
city
address
assets
👨‍💼 Employees
emp_ssn (PK)
name
branch_id (FK)
manager_ssn (self-reference)
📞 Employee Phones / Dependents
Normalized child tables for multi-valued attributes
📊 Relationships Summary
Customer ↔ Account = Many-to-Many
Account → Transactions = One-to-Many
Branch → Employees = One-to-Many
Employee → Employee = Hierarchical (Manager)

🚀 Features
👤 User Features
Register / Login
View profile
Manage accounts
Deposit / Withdraw money
View transaction history
🛠️ Admin Features
View all users
View all transactions
System monitoring

🧰 Technologies Used
🖥️ Backend
Python 3.12
Flask
Flask-JWT-Extended
Flask-SQLAlchemy
PostgreSQL
Werkzeug (security)
🎨 Frontend
HTML5
CSS3
Bootstrap 5
Vanilla JavaScript
Jinja2
🗄️ Database
PostgreSQL
Fully normalized relational schema
Foreign key constraints
⚙️ DevOps / CI
Docker
Docker Compose
GitHub Actions (CI pipeline)
Pytest (testing)
🧪 Testing
pytest
Flask test client
In-memory SQLite test DB
JWT-authenticated test fixtures

⚙️ Setup Instructions
1. Clone Repository
git clone <repo-url>
cd project
2. Start with Docker
docker-compose up --build
3. Run Locally (Optional)
pip install -r requirements.txt
python run.py
4. Run Tests
pytest -v

🔌 API Overview
🔐 Auth
POST /auth/register
POST /auth/login
👤 User
GET /user/profile
GET /user/accounts
POST /user/accounts
DELETE /user/accounts/<id>
💳 Transactions
GET /transactions/<account_id>
POST /transactions/deposit
POST /transactions/withdraw
🛠 Admin
GET /admin/dashboard
GET /admin/transactions