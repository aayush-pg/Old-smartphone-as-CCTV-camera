import sqlite3
import os

def init_db():
    # 1. Create the folder to store actual video files
    if not os.path.exists('recordings'):
        os.makedirs('recordings')
        print("📁 Created 'recordings' folder.")

    # 2. Connect to DB
    conn = sqlite3.connect('webwatch.db')
    cursor = conn.cursor()
    
    print("⚙️ Updating Database Tables...")

    # Users Table (For Login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Recordings Table (Stores info about the video)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            camera_name TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add Admin User (admin / 123)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '123'))
        print("✅ Admin user created.")
    except:
        pass

    conn.commit()
    conn.close()
    print("🎉 Database & Recording System Ready!")

if __name__ == '__main__':
    init_db()