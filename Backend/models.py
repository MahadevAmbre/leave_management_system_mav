from database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT CHECK(role IN ('employee', 'manager')) NOT NULL,
            paid_leave INTEGER DEFAULT 30,
            unpaid_leave INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            status TEXT CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED')) DEFAULT 'PENDING',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
