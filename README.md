# Secure Cloud-Based Competitive Examination Question Paper Management System

## Project Description

A web-based system used to securely manage examination question papers. It prevents unauthorized access before the scheduled examination time.

The system provides different access for Admin, Question Setter and Exam Centre users.

## Technologies / Tools Used

- Python
- Flask
- HTML
- CSS
- SQLite
- Fernet Encryption
- SHA-256 Hashing
- GitHub
- Vercel

## Main Features

- User login
- Role-based access
- Secure question paper upload
- Question paper encryption
- Password hashing
- Examination time restriction
- Download blocked before release time
- Download allowed after release time
- Audit logs
- Integrity verification

## User Roles

### Admin

- View question papers
- View audit logs

### Question Setter

- Upload question papers
- Set release date and time

### Exam Centre

- Access question paper after release time

## Project Structure

secure-exam-paper-management-system/

├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   └── style.css
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   └── logs.html
└── screenshots/

## Installation

Create a virtual environment:
