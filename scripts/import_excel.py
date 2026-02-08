import pandas as pd
from app.database import get_connection

EXCEL_PATH = "data/plots_source.xlsx"

df = pd.read_excel(EXCEL_PATH)

conn = get_connection()
cursor = conn.cursor()

# clear existing rows (MVP behavior)
cursor.execute("DELETE FROM plots")

for _, r in df.iterrows():
    cursor.execute("""
        INSERT INTO plots (
            state, city, locality,
            plot_size_sqft, price_per_sqft, total_price,
            status, owner_type, contact, description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        r["state"],
        r["city"],
        r["locality"],
        int(r["plot_size_sqft"]),
        int(r["price_per_sqft"]),
        int(r["total_price"]),
        r["status"],
        r["owner_type"],
        r["contact"],
        r["description"]
    ))

conn.commit()
conn.close()

print("Import done")
