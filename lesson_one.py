import os
from dotenv import load_dotenv
from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()


app = FastAPI()

conn = psycopg2.connect(
    host = os.getenv("DB_HOST"),
    database = os.getenv("DB_NAME"),
    user = os.getenv("DB_USER"),
    password= os.getenv("DB_PASSWORD")
    )
cur = conn.cursor(cursor_factory = RealDictCursor)



cur.execute("""
    CREATE TABLE IF NOT EXISTS Products(
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    price DECIMAL NOT NULL,
    genre TEXT NOT NULL,
    in_stock BOOLEAN NOT NULL,
    rating DECIMAL(2,1)
    )
    """)
conn.commit()

class Book(BaseModel):
    title : str
    author : str
    price : float
    genre : str
    in_stock : bool
    rating : float | None = None

class Product_Update(BaseModel):
    title : str     | None = None
    price : float   | None = None
    author : str    | None = None
    genre : str     | None = None
    in_stock : bool | None = None
    rating : float  | None = None


@app.post("/products")
def add_product(data:Book):
    cur.execute("""
    INSERT INTO Products(
    title,author,price,genre,in_stock,rating)
    values(%s,%s,%s,%s,%s,%s)""",(
        data.title,data.author,data.price,
        data.genre,data.in_stock,data.rating))

    conn.commit()
    return data
@app.get("/products")
def get_all():
    cur.execute("""
    SELECT * FROM Products""")

    products = cur.fetchall()
    return products

@app.get("/products/{id}")
def get_one(id:int):
    cur.execute("""
    SELECT * FROM Products
    Where id = %s """,(id,))
    
    product = cur.fetchone()

    if product is None:
        raise HTTPException(status_code = 404, detail = "Product not found")
    return product



@app.put("/products/{id}")
def update(data:Book,id:int):
    cur.execute(""" UPDATE Products 
    SET title = %s, author = %s,
    price = %s, genre = %s,
    in_stock = %s, rating = %s
    WHERE id = %s
    RETURNING * """ ,(
    data.title,data.author,
    data.price, data.genre,
    data.in_stock,data.rating,id))

    product = cur.fetchone()
    conn.commit()
    
    if product is None:
            raise HTTPException(status_code = 404, detail = "Product not found")
    return product

    
            
@app.patch("/products/{id}")
def partial_upd(id:int,data: Product_Update):
    cur.execute(""" UPDATE Products 
        SET  title = COALESCE(%s, title), 
        author = COALESCE(%s, author),
        price = COALESCE(%s, price), 
        genre = COALESCE(%s, genre),
        in_stock = COALESCE(%s, in_stock), 
        rating = COALESCE(%s, rating)
        WHERE id = %s
        RETURNING * """,(
        data.title,data.author,data.price,
        data.genre,data.in_stock,data.rating,id))
    product = cur.fetchone()
    conn.commit()

    if product is None:
            raise HTTPException(status_code = 404, detail = "Product not found")
    return product

@app.delete("/products/{id}")
def delete(id:int):
    cur.execute("""
    DELETE FROM Products
    WHERE id = %s 
    RETURNING * """,(id,)) 

    product = cur.fetchone()

    conn.commit()

    if product is None:
         raise HTTPException(status_code=404, detail="product not found")
    return product