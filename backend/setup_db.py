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

    # Users Table (For Login) - Enhanced with email and timestamps
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add email column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN email TEXT')
        print("✅ Added email column to users table")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        print("✅ Added created_at column to users table")
    except sqlite3.OperationalError:
        pass

    # Cameras Table - Links cameras to specific users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            status TEXT DEFAULT 'Waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Recordings Table - Links recordings to specific users and cameras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            camera_id INTEGER,
            filename TEXT NOT NULL,
            camera_name TEXT NOT NULL,
            recording_start_time TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE SET NULL
        )
    ''')
    
    # Add user_id column to recordings if it doesn't exist
    try:
        cursor.execute('ALTER TABLE recordings ADD COLUMN user_id INTEGER')
        print("✅ Added user_id column to recordings table")
    except sqlite3.OperationalError:
        pass

    # Add camera_id column to recordings if it doesn't exist
    try:
        cursor.execute('ALTER TABLE recordings ADD COLUMN camera_id INTEGER')
        print("✅ Added camera_id column to recordings table")
    except sqlite3.OperationalError:
        pass

    # Add file_size column to recordings if it doesn't exist
    try:
        cursor.execute('ALTER TABLE recordings ADD COLUMN file_size INTEGER')
        print("✅ Added file_size column to recordings table")
    except sqlite3.OperationalError:
        pass

    # Add recording_start_time column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE recordings ADD COLUMN recording_start_time TIMESTAMP')
        print("✅ Added recording_start_time column to recordings table")
    except sqlite3.OperationalError:
        pass

    # User Settings Table - Store user preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            theme TEXT DEFAULT 'dark',
            notifications_enabled INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Add Admin User (admin / 123)
    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                      ('admin', '123', 'admin@webwatch.com'))
        print("✅ Admin user created.")
    except:
        pass

    conn.commit()
    conn.close()
    print("🎉 Multi-User Database System Ready!")

if __name__ == '__main__':
    init_db()