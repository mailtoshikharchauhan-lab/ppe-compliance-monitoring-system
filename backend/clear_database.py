"""
Clear Database - Remove all old alerts and reset the system
"""

import os
import sqlite3

DB_NAME = "database.db"

def clear_database():
    """Clear all alerts from the database"""
    
    if not os.path.exists(DB_NAME):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute("SELECT COUNT(*) FROM alerts")
    old_count = cursor.fetchone()[0]
    
    # Delete all alerts
    cursor.execute("DELETE FROM alerts")
    conn.commit()
    
    # Reset auto-increment counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='alerts'")
    conn.commit()
    
    conn.close()
    
    print(f"✅ Database cleared!")
    print(f"   Removed {old_count} old alerts")
    print(f"   Database is now empty and ready for new tests")

def clear_screenshots():
    """Clear all old screenshots"""
    screenshot_dir = "screenshots"
    
    if not os.path.exists(screenshot_dir):
        print("❌ Screenshots directory not found!")
        return
    
    count = 0
    for filename in os.listdir(screenshot_dir):
        if filename.endswith('.jpg'):
            filepath = os.path.join(screenshot_dir, filename)
            os.remove(filepath)
            count += 1
    
    print(f"✅ Screenshots cleared!")
    print(f"   Removed {count} old screenshots")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🗑️  CLEARING OLD DATA")
    print("="*60 + "\n")
    
    clear_database()
    print()
    clear_screenshots()
    
    print("\n" + "="*60)
    print("✨ System is now clean and ready for fresh tests!")
    print("="*60 + "\n")
