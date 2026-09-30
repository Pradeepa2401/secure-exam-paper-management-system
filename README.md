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

```text
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
```

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

## Demo Accounts

### Admin

Username: admin  
Password: admin123

### Question Setter

Username: setter1  
Password: setter123

### Exam Centre

Username: centre1  
Password: centre123

## Sample Output

### Before Release Time

Question paper is locked until the configured release time.

### After Release Time

Question paper can be downloaded successfully.

## Security Features

- Authentication
- Password hashing
- Role-Based Access Control
- Question paper encryption
- SHA-256 integrity verification
- Audit logging
- Controlled release time
- Secure storage

## Testing

The following features were tested:

- User login
- Question paper upload
- Release time setting
- Access before release time
- Access after release time
- Integrity verification
- Audit logging

## GitHub Repository

https://github.com/Pradeepa2401/secure-exam-paper-management-system

## Live Demo

The project is deployed on Vercel:

[Open Live Application](https://secure-exam-paper-management-system.vercel.app/)

## Security Note

Do not upload passwords, API keys, .env files, encryption keys or database files to a public GitHub repository.

## Conclusion

This project demonstrates secure and time-controlled management of examination question papers using authentication, encryption, role-based access control, integrity verification and audit logging.
