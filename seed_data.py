import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

items = [

    ("Dell Latitude 5420", "Standard company laptop", "Laptop", 25, 25, 0),
    ("HP EliteBook 840", "Lightweight office laptop", "Laptop", 20, 20, 0),
    ("Lenovo ThinkPad X1", "High-performance laptop", "Laptop", 15, 15, 0),

    ("Dell OptiPlex 7090", "Office desktop workstation", "Desktop", 10, 10, 0),
    ("HP ProDesk 600", "Admin desktop computer", "Desktop", 8, 8, 0),

    ("Dell 24in Monitor", "Standard monitor", "Monitor", 40, 40, 0),
    ("HP 27in Monitor", "Large display monitor", "Monitor", 20, 20, 0),

    ("Logitech Mouse", "Wireless mouse", "Mouse", 50, 50, 0),
    ("Logitech Keyboard", "Standard keyboard", "Keyboard", 50, 50, 0),

    ("Dell Dock WD19", "Laptop docking station", "Docking Station", 25, 25, 0),

    ("USB-C Hub", "Multi-port adapter", "Adapter", 30, 30, 0),
    ("Ethernet Adapter", "Wired network adapter", "Adapter", 25, 25, 0),

    ("Epson Projector", "Conference room projector", "Projector", 5, 5, 0),
    ("Conference Camera", "Video meeting camera", "Camera", 6, 6, 0),

    ("Surface Pro Tablet", "Tablet for field use", "Tablet", 10, 10, 0),
    ("iPad", "Presentation tablet", "Tablet", 8, 8, 0),

    ("External HDD 1TB", "Portable hard drive", "Storage", 20, 20, 0),
    ("External SSD 512GB", "Fast storage device", "Storage", 15, 15, 0),

    ("Laptop Charger", "Replacement charger", "Power", 30, 30, 0),
    ("Power Strip", "Multi outlet strip", "Power", 20, 20, 0)
]

cursor.executemany('''
INSERT INTO inventory (name, description, category, total_quantity, available_quantity, checked_out_quantity)
VALUES (?, ?, ?, ?, ?, ?)
''', items)

conn.commit()
conn.close()

print("✅ Clean inventory loaded")