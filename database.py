import sqlite3
import datetime

DB_NAME = "project_data.db"

def init_db():
    """Initializes the SQLite schema required to store processing events."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanned_code TEXT NOT NULL,
            detected_smells TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            user_suggestions TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_scan_session(code, smells, suggestions):
    """Saves structural session parameters to the relational schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO scan_history (scanned_code, detected_smells, timestamp, user_suggestions)
        VALUES (?, ?, ?, ?)
    """, (code, str(smells), timestamp, str(suggestions)))
    
    conn.commit()
    conn.close()

def fetch_history():
    """Returns past optimization sessions for auditing purposes."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, detected_smells FROM scan_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Run structural instantiation if script executed directly
if __name__ == "__main__":
    init_db()
    print(f"[SUCCESS] Initialized Database Architecture within {DB_NAME}")