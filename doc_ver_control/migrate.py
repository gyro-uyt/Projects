import sqlite3

def migrate():
    conn = sqlite3.connect('vcs.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE revisions ADD COLUMN commit_message TEXT DEFAULT 'No commit message'")
        print("Column added.")
    except sqlite3.OperationalError as e:
        print("Column already exists or error:", e)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
