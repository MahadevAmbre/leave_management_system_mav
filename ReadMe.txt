Perfect timing. A strong **README** will actually *save* this project in reviews and interviews.

Below is a **clean, professional, beginner-friendly README** that matches **exactly what you built**, without overclaiming.
You can **copy–paste this as `README.md`**.

---

# Leave Management System (Cloud-Based)

## 📌 Overview

The **Leave Management System** is a cloud-based web application designed to manage employee leave requests efficiently. It allows employees to apply for leave and managers to review, approve, or reject requests. The system is built with a modern cloud architecture using AWS services and a Python-based backend.

This project demonstrates practical understanding of:

* Cloud deployment
* Backend APIs
* Authentication concepts
* Real-world business logic
* Full-stack integration

---

## 🚀 Features

### 👤 Employee

* Secure login
* Apply for leave (number of days, reason)
* View leave history and status (Pending / Approved / Rejected)

### 👔 Manager

* Secure login
* View all employee leave requests
* Approve or reject leave requests
* Track pending, approved, and rejected leaves

---

## 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* JavaScript
* Hosted on **AWS S3** (Static Website Hosting)

### Backend

* Python
* Flask
* Gunicorn (production WSGI server)
* Hosted on **AWS EC2 (Ubuntu)**

### Authentication

* **AWS Cognito**

  * User Pool for authentication
  * Role-based access (Employee / Manager)

### Database

* **SQLite**

  * Used for demo and development
  * Stores users, leave requests, and leave balances
  * Architecture is RDS-ready for future scalability

---

## ☁️ Cloud Architecture

```
Frontend (S3 Static Website)
        |
        | HTTPS
        |
Authentication (AWS Cognito)
        |
        | JWT / User Role
        |
Backend (EC2 + Flask + Gunicorn)
        |
        |
     SQLite Database
```

---

## 📂 Project Structure

```
Leave_Management_System_AWS/
│
├── Backend/
│   ├── app.py              # Flask application
│   ├── database.py         # Database connection (SQLite)
│   ├── models.py           # DB schema & queries
│   ├── requirements.txt    # Python dependencies
│   └── leave_management.db # SQLite database
│
├── Frontend/
│   ├── employee.html
│   ├── manager.html
│   ├── loading.html
│   ├── script.js
│   └── style.css
│
└── README.md
```

---

## ⚙️ Backend Setup (EC2 – Ubuntu)

### 1. SSH into EC2

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run backend using Gunicorn

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

Backend will be available at:

```
http://<EC2_PUBLIC_IP>:5000
```

---

## 🌐 Frontend Setup (S3)

1. Upload frontend files (`.html`, `.css`, `.js`) to an S3 bucket
2. Enable **Static Website Hosting**
3. Access via the S3 website endpoint

---

## 🔐 Authentication Flow (AWS Cognito)

1. User logs in via Cognito Hosted UI
2. Cognito authenticates the user
3. JWT token contains user role (`employee` or `manager`)
4. Frontend redirects user based on role
5. Backend APIs are accessed using authenticated requests

---

## 📈 Future Improvements

* Replace SQLite with **AWS RDS (MySQL/PostgreSQL)**
* Add **Nginx reverse proxy**
* Enable HTTPS on backend
* Add pagination and filtering
* Add admin dashboard
* Improve frontend UI/UX

---

## 🧠 Key Learnings

* Deploying a backend on EC2 using Flask & Gunicorn
* Handling authentication using AWS Cognito
* Building role-based access control
* Integrating frontend and backend over public APIs
* Understanding trade-offs between SQLite and RDS

---

## 👨‍💻 Author

**Mahadev Ambre**
B.Tech (CSE / Data Science)
Cloud & Backend Enthusiast

---

## ✅ Notes for Reviewers

* SQLite is intentionally used for demo simplicity
* Architecture supports easy migration to RDS
* Focus is on **cloud understanding and backend logic**

---

