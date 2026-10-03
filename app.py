from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import os
import io
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
FERNET_KEY = os.environ.get("FERNET_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is missing")

if not SUPABASE_SECRET_KEY:
    raise RuntimeError("SUPABASE_SECRET_KEY environment variable is missing")

if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY environment variable is missing")


# ============================================================
# FLASK + SUPABASE SETUP
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-for-college-project"
)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

BUCKET_NAME = "question-papers"

fernet = Fernet(FERNET_KEY.encode())


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def current_time():
    return datetime.now(ZoneInfo("Asia/Kolkata"))


def login_required(role=None):
    if "username" not in session:
        return False

    if role and session.get("role") not in role:
        return False

    return True


def log_action(action, paper_id=None):
    """
    Store audit log in Supabase.
    """

    if "username" not in session:
        return

    try:
        supabase.table("audit_logs").insert({
            "username": session["username"],
            "action": action,
            "paper_id": paper_id
        }).execute()

    except Exception as e:
        print("Audit log error:", e)


def get_paper(paper_id):
    """
    Get question paper information from Supabase.
    """

    try:
        response = (
            supabase
            .table("papers")
            .select("*")
            .eq("id", paper_id)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception as e:
        print("Get paper error:", e)

    return None


# ============================================================
# CREATE DEMO USERS
# ============================================================

def init_users():
    """
    Creates demo users if they do not already exist.

    Demo accounts:
    admin   / admin123
    setter1 / setter123
    centre1 / centre123
    """

    users = [
        ("admin", "admin123", "admin"),
        ("setter1", "setter123", "setter"),
        ("centre1", "centre123", "centre")
    ]

    for username, password, role in users:

        try:
            existing = (
                supabase
                .table("users")
                .select("id")
                .eq("username", username)
                .limit(1)
                .execute()
            )

            if existing.data:
                continue

            supabase.table("users").insert({
                "username": username,
                "password_hash": generate_password_hash(password),
                "role": role
            }).execute()

            print(f"Created user: {username}")

        except Exception as e:
            print(f"User creation error for {username}:", e)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    if "username" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        try:
            response = (
                supabase
                .table("users")
                .select("*")
                .eq("username", username)
                .limit(1)
                .execute()
            )

            user = response.data[0] if response.data else None

        except Exception as e:

            print("Login error:", e)

            flash(
                "Database connection error.",
                "error"
            )

            return render_template("login.html")

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["username"] = user["username"]
            session["role"] = user["role"]

            log_action("LOGIN")

            return redirect(url_for("dashboard"))

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    if "username" in session:
        log_action("LOGOUT")

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(url_for("login"))

    try:

        papers_response = (
            supabase
            .table("papers")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        logs_response = (
            supabase
            .table("audit_logs")
            .select("*")
            .order("id", desc=True)
            .limit(20)
            .execute()
        )

        papers = papers_response.data or []
        logs = logs_response.data or []

    except Exception as e:

        print("Dashboard error:", e)

        flash(
            "Unable to load dashboard.",
            "error"
        )

        papers = []
        logs = []

    return render_template(
        "dashboard.html",
        papers=papers,
        logs=logs,
        now=current_time()
    )


# ============================================================
# UPLOAD QUESTION PAPER
# ============================================================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if not login_required(["setter", "admin"]):

        flash(
            "Access denied. Setter or Admin access required.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if request.method == "POST":

        exam_name = request.form["exam_name"].strip()
        exam_date = request.form["exam_date"]
        release_time = request.form["release_time"]

        uploaded = request.files.get("paper")

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if (
            not exam_name
            or not exam_date
            or not release_time
            or not uploaded
            or not uploaded.filename
        ):

            flash(
                "Please fill all fields and select a PDF file.",
                "error"
            )

            return redirect(url_for("upload"))

        original_filename = os.path.basename(
            uploaded.filename
        )

        # Only PDF files
        if not original_filename.lower().endswith(".pdf"):

            flash(
                "Only PDF question papers are allowed.",
                "error"
            )

            return redirect(url_for("upload"))

        # ----------------------------------------------------
        # READ ORIGINAL FILE
        # ----------------------------------------------------

        data = uploaded.read()

        if not data:

            flash(
                "Selected file is empty.",
                "error"
            )

            return redirect(url_for("upload"))

        # ----------------------------------------------------
        # ENCRYPT QUESTION PAPER
        # ----------------------------------------------------

        encrypted_data = fernet.encrypt(data)

        # ----------------------------------------------------
        # SHA-256 INTEGRITY HASH
        # ----------------------------------------------------

        file_hash = hashlib.sha256(data).hexdigest()

        # ----------------------------------------------------
        # UNIQUE STORAGE FILE NAME
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        )

        stored_filename = (
            f"{timestamp}_{original_filename}.enc"
        )

        storage_path = stored_filename

        # ----------------------------------------------------
        # UPLOAD ENCRYPTED FILE TO SUPABASE STORAGE
        # ----------------------------------------------------

        try:

            supabase.storage \
                .from_(BUCKET_NAME) \
                .upload(
                    storage_path,
                    encrypted_data,
                    {
                        "content-type": "application/pdf",
                        "upsert": "false"
                    }
                )

        except Exception as e:

            print("Supabase Storage upload error:", e)

            flash(
                "Cloud storage upload failed.",
                "error"
            )

            return redirect(url_for("upload"))

        # ----------------------------------------------------
        # SAVE PAPER DETAILS IN SUPABASE DATABASE
        # ----------------------------------------------------

        try:

            response = (
                supabase
                .table("papers")
                .insert({
                    "exam_name": exam_name,
                    "exam_date": exam_date,
                    "release_time": release_time,
                    "filename": original_filename,
                    "storage_path": storage_path,
                    "file_hash": file_hash,
                    "uploaded_by": session["username"]
                })
                .execute()
            )

            paper_id = (
                response.data[0]["id"]
                if response.data
                else None
            )

        except Exception as e:

            print("Database insert error:", e)

            # If database insertion fails, try to remove
            # the uploaded file from Storage.
            try:
                supabase.storage \
                    .from_(BUCKET_NAME) \
                    .remove([storage_path])
            except Exception:
                pass

            flash(
                "Paper information could not be saved.",
                "error"
            )

            return redirect(url_for("upload"))

        # ----------------------------------------------------
        # AUDIT LOG
        # ----------------------------------------------------

        log_action(
            "UPLOAD_QUESTION_PAPER",
            paper_id
        )

        flash(
            "Question paper encrypted and uploaded securely to Supabase Cloud.",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template("upload.html")


# ============================================================
# ACCESS / DOWNLOAD QUESTION PAPER
# ============================================================

@app.route("/paper/<int:paper_id>")
def access_paper(paper_id):

    if not login_required():

        return redirect(url_for("login"))

    paper = get_paper(paper_id)

    if not paper:

        flash(
            "Question paper not found.",
            "error"
        )

        return redirect(url_for("dashboard"))

    # --------------------------------------------------------
    # ROLE CONTROL
    # --------------------------------------------------------

    allowed_roles = ["admin", "centre"]

    if session.get("role") not in allowed_roles:

        log_action(
            "ACCESS_DENIED_ROLE",
            paper_id
        )

        flash(
            "You are not authorized to access question papers.",
            "error"
        )

        return redirect(url_for("dashboard"))

    # --------------------------------------------------------
    # RELEASE DATE + TIME CHECK
    # --------------------------------------------------------

    try:

       release_datetime = datetime.strptime(
    paper["exam_date"]
    + " "
    + paper["release_time"],
    "%Y-%m-%d %H:%M:%S"
).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    except ValueError:

        flash(
            "Invalid release date/time.",
            "error"
        )

        return redirect(url_for("dashboard"))

    now = current_time()

    # --------------------------------------------------------
    # LOCK BEFORE RELEASE
    # --------------------------------------------------------

    if now < release_datetime:

        log_action(
            "ACCESS_DENIED_BEFORE_RELEASE",
            paper_id
        )

        flash(
            "Question paper is locked until "
            + release_datetime.strftime(
                "%d-%m-%Y %I:%M %p"
            ),
            "error"
        )

        return redirect(url_for("dashboard"))

    # --------------------------------------------------------
    # DOWNLOAD ENCRYPTED FILE FROM SUPABASE
    # --------------------------------------------------------

    try:

        encrypted_data = (
            supabase
            .storage
            .from_(BUCKET_NAME)
            .download(paper["storage_path"])
        )

    except Exception as e:

        print("Cloud download error:", e)

        log_action(
            "CLOUD_DOWNLOAD_FAILURE",
            paper_id
        )

        flash(
            "Unable to retrieve question paper from cloud storage.",
            "error"
        )

        return redirect(url_for("dashboard"))

    # --------------------------------------------------------
    # DECRYPT FILE
    # --------------------------------------------------------

    try:

        original_data = fernet.decrypt(
            encrypted_data
        )

    except Exception as e:

        print("Decryption error:", e)

        log_action(
            "DECRYPTION_FAILURE",
            paper_id
        )

        flash(
            "Security check failed. File could not be decrypted.",
            "error"
        )

        return redirect(url_for("dashboard"))

    # --------------------------------------------------------
    # INTEGRITY CHECK
    # --------------------------------------------------------

    current_hash = hashlib.sha256(
        original_data
    ).hexdigest()

    if current_hash != paper["file_hash"]:

        log_action(
            "INTEGRITY_VIOLATION",
            paper_id
        )

        flash(
            "Integrity violation detected. Access blocked.",
            "error"
        )

        return redirect(url_for("dashboard"))

    # --------------------------------------------------------
    # SUCCESSFUL ACCESS
    # --------------------------------------------------------

    log_action(
        "PAPER_ACCESSED",
        paper_id
    )

    return send_file(
        io.BytesIO(original_data),
        as_attachment=True,
        download_name=paper["filename"],
        mimetype="application/pdf"
    )


# ============================================================
# AUDIT LOGS
# ============================================================

@app.route("/logs")
def logs():

    if not login_required(["admin"]):

        flash(
            "Admin access required.",
            "error"
        )

        return redirect(url_for("dashboard"))

    try:

        logs_response = (
            supabase
            .table("audit_logs")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        logs_data = logs_response.data or []

    except Exception as e:

        print("Logs error:", e)

        logs_data = []

        flash(
            "Unable to load audit logs.",
            "error"
        )

    return render_template(
        "logs.html",
        logs=logs_data
    )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Secure Cloud-Based Competitive Examination")
    print("Question Paper Management System")
    print("=" * 60)

    print("Supabase URL:", SUPABASE_URL)
    print("Storage Bucket:", BUCKET_NAME)

    try:
        init_users()
        print("Demo users checked successfully.")
    except Exception as e:
        print("Demo user initialization error:", e)

    print("Starting Flask server...")
    print("Open: http://127.0.0.1:5000")

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
