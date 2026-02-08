from fastapi import FastAPI, Query
from app.database import get_connection
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request


app = FastAPI(title="Plots Locator")
templates = Jinja2Templates(directory="app/templates")


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




