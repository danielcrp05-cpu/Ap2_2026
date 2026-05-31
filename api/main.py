from fastapi import FastAPI
import psycopg2

app = FastAPI()

conn = psycopg2.connect(
    host="postgres",
    database="bookinghub",
    user="admin",
    password="admin",
    port=5432
)

cur = conn.cursor()

@app.get("/")
def home():
    return {"message": "API funcionando"}

@app.get("/customers")
def get_customers():
    cur.execute("SELECT * FROM customers LIMIT 100")
    data = cur.fetchall()
    return data

@app.get("/flights")
def get_flights():
    cur.execute("SELECT * FROM flights LIMIT 100")
    data = cur.fetchall()
    return data

@app.get("/hotels")
def get_hotels():
    cur.execute("SELECT * FROM hotels LIMIT 100")
    data = cur.fetchall()
    return data