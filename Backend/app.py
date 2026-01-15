from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection
from models import create_tables
import requests
import jwt

app = Flask(__name__)
CORS(app)
# -------------------- INIT --------------------

create_tables()

def seed_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, role) VALUES (?,?)", ("Employee One", "employee"))
        cursor.execute("INSERT INTO users (name, role) VALUES (?,?)", ("Manager One", "manager"))

    conn.commit()
    conn.close()

seed_users()

# -------------------- BUSINESS LOGIC --------------------

def calculate_leave_balance(paid_leave, unpaid_leave, requested_days):
    if paid_leave >= requested_days:
        paid_leave -= requested_days
    else:
        unpaid_leave += (requested_days - paid_leave)
        paid_leave = 0
    return paid_leave, unpaid_leave

# -------------------- ROUTES --------------------

@app.route("/")
def home():
    return "Leave Management Backend Running"

# -------- EMPLOYEE: APPLY LEAVE --------

@app.route("/apply-leave", methods=["POST"])
def apply_leave():
    data = request.get_json()
    user_id = data.get("user_id")
    days = data.get("days")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    if user["role"] != "employee":
        conn.close()
        return jsonify({"error": "Only employees can apply for leave"}), 403

    cursor.execute("""
        INSERT INTO leave_requests (user_id, start_date, end_date, days, status)
        VALUES (?, ?, ?, ?, 'PENDING')
    """, (user_id, "2026-01-10", "2026-01-12", days))

    conn.commit()
    conn.close()

    return jsonify({"message": "Leave request submitted"}), 201

# -------- MANAGER: APPROVE LEAVE --------

@app.route("/approve-leave", methods=["POST"])
def approve_leave():
    data = request.get_json()
    manager_id = data.get("manager_id")
    leave_id = data.get("leave_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (manager_id,))
    manager = cursor.fetchone()

    if not manager or manager["role"] != "manager":
        conn.close()
        return jsonify({"error": "Only managers can approve leave"}), 403

    cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id,))
    leave = cursor.fetchone()

    if not leave:
        conn.close()
        return jsonify({"error": "Leave not found"}), 404

    if leave["status"] != "PENDING":
        conn.close()
        return jsonify({"error": "Leave already processed"}), 400

    cursor.execute("SELECT * FROM users WHERE id = ?", (leave["user_id"],))
    employee = cursor.fetchone()

    new_paid, new_unpaid = calculate_leave_balance(
        employee["paid_leave"],
        employee["unpaid_leave"],
        leave["days"]
    )

    cursor.execute("""
        UPDATE users SET paid_leave=?, unpaid_leave=? WHERE id=?
    """, (new_paid, new_unpaid, employee["id"]))

    cursor.execute("""
        UPDATE leave_requests SET status='APPROVED' WHERE id=?
    """, (leave_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Leave approved",
        "paid_leave_remaining": new_paid,
        "unpaid_leave": new_unpaid
    })

# -------- MANAGER: REJECT LEAVE --------

@app.route("/reject-leave", methods=["POST"])
def reject_leave():
    data = request.get_json()
    manager_id = data.get("manager_id")
    leave_id = data.get("leave_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (manager_id,))
    manager = cursor.fetchone()

    if not manager or manager["role"] != "manager":
        conn.close()
        return jsonify({"error": "Only managers can reject leave"}), 403

    cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id,))
    leave = cursor.fetchone()

    if not leave:
        conn.close()
        return jsonify({"error": "Leave not found"}), 404

    if leave["status"] != "PENDING":
        conn.close()
        return jsonify({"error": "Leave already processed"}), 400

    cursor.execute("""
        UPDATE leave_requests SET status='REJECTED' WHERE id=?
    """, (leave_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Leave rejected"})

# -------- VIEW LEAVES (RBAC) --------

@app.route("/view-leaves", methods=["GET"])
def view_leaves():
    user_id = request.args.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    if user["role"] == "manager":
        cursor.execute("""
            SELECT lr.id, u.name, lr.days, lr.status
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
        """)
    else:
        cursor.execute("""
            SELECT id, days, status
            FROM leave_requests
            WHERE user_id = ?
        """, (user_id,))

    leaves = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(leaves)

# ===== COGNITO CONFIG =====
COGNITO_DOMAIN = "https://ap-south-1u6dsufsq3.auth.ap-south-1.amazoncognito.com"
CLIENT_ID = "39j8tm5298re17umi2453f1r2c"
CLIENT_SECRET = "PASTE_CLIENT_SECRET_HERE"
REDIRECT_URI = "https://d1q8n3vr8fjq7n.cloudfront.net/"

# =========================

@app.route("/auth/callback", methods=["POST"])
def auth_callback():
    data = request.json
    code = data.get("code")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    token_url = "https://ap-south-1u6dsufsq3.auth.ap-south-1.amazoncognito.com/oauth2/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": "39j8tm5298re17umi2453f1r2c",
        "client_secret": "1d5or6chnhtj6lv6b2qk0us4e38lfu9pvq5fn5l60mffmimnbcdb",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    tokens = response.json()

    if "id_token" not in tokens:
        return jsonify({"error": "Token exchange failed", "details": tokens}), 400

    id_token = tokens["id_token"]

    # ⚠️ Decode token (no verification for now)
    decoded = jwt.decode(id_token, options={"verify_signature": False})

    email = decoded.get("email", "")
    name = decoded.get("name", "User")

    # ✅ THIS IS THE FIX
    role = decoded.get("custom:Role", "employee")

    return jsonify({
        "email": email,
        "name": name,
        "role": role,
        "id_token": id_token
    })

@app.route("/")
def home():
    return "Backend running", 200

@app.route("/health")
def health():
    return "OK", 200

# -------------------- RUN --------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
