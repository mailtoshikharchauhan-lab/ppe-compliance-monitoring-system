import sqlite3

DB_NAME = "database.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        violation TEXT,
        screenshot TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_alert(timestamp, violation, screenshot):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO alerts (timestamp, violation, screenshot)
    VALUES (?, ?, ?)
    """, (timestamp, violation, screenshot))

    conn.commit()
    conn.close()


def get_all_alerts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    # Convert to list of dictionaries for JSON response
    alerts = []
    for row in rows:
        alerts.append({
            "id": row[0],
            "timestamp": row[1],
            "violation": row[2],
            "screenshot": row[3]
        })

    return alerts