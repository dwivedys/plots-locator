import os
from fastapi import FastAPI, Query
from app.database import get_connection
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request


def init_db_if_needed():
    db_exists = os.path.exists("plots.db")

    conn = get_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
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

    # If DB is new, load initial data
    if not db_exists:
        import pandas as pd
        df = pd.read_excel("data/plots_source.xlsx")

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


app = FastAPI(title="Plots Locator")
templates = Jinja2Templates(directory="app/templates")
init_db_if_needed()


@app.get("/")
def home(
    request: Request,
    city: str | None = None,
    min_size: str | None = None,
    max_size: str | None = None,
    locality: str | None = None
):
    results = None
    if city:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT city, locality, plot_size_sqft, price_per_sqft, total_price
            FROM plots
            WHERE LOWER(city) = LOWER(?)
        """ 
        params = [city]

        

        if min_size:
            sql += " AND plot_size_sqft >= ?"
            params.append(int(min_size))

        if max_size:
            sql += " AND plot_size_sqft <= ?"
            params.append(int(max_size))

        # if min_size and max_size:
        #     sql += " AND plot_size_sqft BETWEEN ? AND ?"
        #     params.extend([int(min_size), int(max_size)])
        
        if locality:
            sql += " AND LOWER(locality) = LOWER(?)"
            params.append(locality)

        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
    return templates.TemplateResponse(
        "search.html",
        {"request":request, "results":results}
    )
    # if city and min_size and max_size:
    #     conn = get_connection()
    #     cursor = conn.cursor()

    #     sql = """
    #         SELECT city, locality, plot_size_sqft, price_per_sqft, total_price
    #         FROM plots
    #         WHERE LOWER(city) = LOWER(?)
    #           AND plot_size_sqft BETWEEN ? AND ?
    #     """
    #     params = [city, min_size, max_size]

    #     if locality:
    #         sql += " AND LOWER(locality) = LOWER(?)"
    #         params.append(locality)

    #     cursor.execute(sql, params)
    #     results = cursor.fetchall()
    #     conn.close()

    # return templates.TemplateResponse(
    #     "search.html",
    #     {"request": request, "results": results}
    # )


@app.get("/search")
def search_plots(
    city: str = Query(...),
    min_size: int = Query(...),
    max_size: int = Query(...),
    locality: str = Query(None)
):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            state, city, locality,
            plot_size_sqft, price_per_sqft, total_price,
            status, owner_type, contact, description
        FROM plots
        WHERE city = ?
          AND plot_size_sqft BETWEEN ? AND ?
    """
    params = [city, min_size, max_size]

    if locality:
        sql += " AND locality = ?"
        params.append(locality)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@app.get("/search-ui")
def search_ui(
    request: Request,
    city: str,
    min_size: int,
    max_size: int,
    locality: str = None
):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT city, locality, plot_size_sqft, price_per_sqft, total_price
        FROM plots
        WHERE LOWER(city) = LOWER(?)
          AND plot_size_sqft BETWEEN ? AND ?
    """
    params = [city, min_size, max_size]

    if locality:
        sql += " AND LOWER(locality) = LOWER(?)"
        params.append(locality)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "search.html",
        {"request": request, "results": rows}
    )




