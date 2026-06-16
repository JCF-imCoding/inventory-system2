import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# ✅ Inventory Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    total_quantity INTEGER NOT NULL,
    available_quantity INTEGER NOT NULL,
    checked_out_quantity INTEGER NOT NULL
)
''')

# ✅ Transactions Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    action TEXT,
    quantity INTEGER,
    department TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("✅ Database initialized successfully")