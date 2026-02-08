from app.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS plots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT,
    city TEXT,
    locality TEXT,
    plot_size_sqft INTEGER,
    price_per_sqft INTEGER,
    total_price INTEGER,
    status TEXT,
    owner_type TEXT,
    contact TEXT,
    description TEXT
)
""")

conn.commit()
conn.close()

print("Database initialized")

