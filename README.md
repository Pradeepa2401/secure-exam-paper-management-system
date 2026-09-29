# Secure Cloud-Based Competitive Examination Question Paper Management System

1. Project Description

This project is a prototype for securely managing government competitive examination question papers. It demonstrates authentication, role-based access control, encryption, integrity verification, audit logging, secure storage, and controlled release of question papers.

2. Technologies / Tools

- Python
- Flask
- HTML
- CSS
- SQLite
- Cryptography (Fernet/AES-based authenticated encryption)
- SHA-256 hashing
- GitHub
- Cloud hosting (can be deployed to a Flask-compatible cloud platform)

3. User Roles

- Admin: Views papers and audit logs.
- Question Setter: Uploads a question paper and sets its release date/time.
- Exam Centre: Accesses the paper only after the scheduled release time.

4. Demo Accounts

These accounts are only for demonstration purposes. Change them before any real deployment.

- Admin: `admin` / `admin123`
- Question Setter: `setter1` / `setter123`
- Exam Centre: `centre1` / `centre123`

5. Security Features
  1. Authentication – verifies username and password.
  2. Password Hashing – passwords are stored as hashes, not plain text.
  3. Role-Based Access Control (RBAC) – users receive permissions according to their role. 
  4. Encryption – uploaded question papers are encrypted before storage.
  5. SHA-256 Integrity Check – detects modification of the original paper.
  6. Audit Logs – records login, upload, access and denied-access events.
  7. Controlled Release – the paper remains locked until its configured release date and time.   
  8. Secure Storage – only encrypted files are kept in the upload storage.
6. Installation
Windows / Linux / macOS
Create a virtual environment:
python -m venv .venv
Activate the environment.
Windows:
.venv\Scripts\activate
Linux/macOS:
source .venv/bin/activate
Install dependencies:
pip install -r requirements.txt
Run the application:
python app.py
Open the application in a browser:
http://127.0.0.1:5000
The database and encryption key are created automatically on first run.
Project Structure
secure-exam-paper-management-system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   └── logs.html
│
├── static/
│   └── style.css
│
└── screenshots/
Sample Input / Output
Upload
Input:
Exam Name: Government Competitive Exam 2026
Exam Date: A future date
Release Time: A future time
Question Paper: sample.pdf
Output:
"Question paper encrypted and securely stored."
Before Release
Input:
Exam Centre tries to access the paper before the release time.
Output:
"Question paper is locked until the configured release time."
After Release
Input:
Exam Centre accesses the paper after the configured release time.
Output:
The decrypted question paper is downloaded after the integrity check succeeds.
Integrity Verification
If the decrypted content does not match the stored SHA-256 hash:
Access is blocked.
An INTEGRITY_VIOLATION event is added to the audit log.
Important Note
This is an educational prototype, not a production government examination system. A real deployment would require stronger key management, HTTPS/TLS, multi-factor authentication (MFA), centralized secrets management, hardened cloud storage, network controls, independent security testing, and formal operational procedures.
