import sqlite3
from pathlib import Path
from datetime import date

DB = Path(__file__).parent / "shopmind.db"

def connect():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    c=connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        purchase_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        min_stock INTEGER NOT NULL DEFAULT 5,
        supplier TEXT
    );
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total REAL NOT NULL,
        sale_date TEXT NOT NULL,
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        expense_date TEXT NOT NULL
    );
    """)
    c.commit()
    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
        seed(c)
    c.close()

def seed(c):
    products=[
        ("Maggi","Grocery",12,18,42,10,"ABC Distributor"),
        ("Pepsi 500ml","Cold Drink",28,35,24,8,"XYZ Beverages"),
        ("Parle-G","Biscuit",8,10,60,15,"Local Supplier"),
        ("Dairy Milk","Chocolate",32,45,7,10,"Chocolate Distributor"),
        ("Amul Milk","Dairy",25,30,18,8,"Amul Supplier")
    ]
    for p in products:
        c.execute("""INSERT INTO products
        (name,category,purchase_price,selling_price,stock,min_stock,supplier)
        VALUES(?,?,?,?,?,?,?)""",p)
    ids={r["name"]:r["id"] for r in c.execute("SELECT id,name FROM products")}
    demo=[
        ("Maggi",8,18,"2026-09-22"),("Maggi",10,18,"2026-09-23"),
        ("Maggi",12,18,"2026-09-24"),("Maggi",14,18,"2026-09-25"),
        ("Pepsi 500ml",8,35,"2026-09-22"),("Pepsi 500ml",12,35,"2026-09-23"),
        ("Pepsi 500ml",14,35,"2026-09-24"),("Pepsi 500ml",15,35,"2026-09-25"),
        ("Parle-G",20,10,"2026-09-22"),("Parle-G",18,10,"2026-09-23"),
        ("Parle-G",22,10,"2026-09-24")
    ]
    for n,q,price,d in demo:
        c.execute("INSERT INTO sales(product_id,quantity,price,total,sale_date) VALUES(?,?,?,?,?)",
                  (ids[n],q,price,q*price,d))
    c.execute("INSERT INTO expenses(title,amount,category,expense_date) VALUES(?,?,?,?)",
              ("Electricity",450,"Utilities",str(date.today())))
    c.commit()

def products_df():
    import pandas as pd
    return pd.read_sql_query("SELECT * FROM products ORDER BY name",connect())

def sales_df():
    import pandas as pd
    return pd.read_sql_query("""SELECT s.*,p.name product,p.purchase_price
                                FROM sales s JOIN products p ON p.id=s.product_id
                                ORDER BY sale_date""",connect())

def expenses_df():
    import pandas as pd
    return pd.read_sql_query("SELECT * FROM expenses ORDER BY expense_date DESC",connect())

def add_product(name,category,buy,sell,stock,min_stock,supplier):
    c=connect()
    c.execute("""INSERT INTO products(name,category,purchase_price,selling_price,stock,min_stock,supplier)
                 VALUES(?,?,?,?,?,?,?)""",(name,category,buy,sell,stock,min_stock,supplier))
    c.commit(); c.close()

def add_sale(product_id,qty,price=None,sale_date=None):
    c=connect()
    p=c.execute("SELECT * FROM products WHERE id=?",(product_id,)).fetchone()
    if not p: raise ValueError("Product not found")
    if qty>p["stock"]: raise ValueError("Stock insufficient")
    price=p["selling_price"] if price is None else price
    d=sale_date or str(date.today())
    c.execute("INSERT INTO sales(product_id,quantity,price,total,sale_date) VALUES(?,?,?,?,?)",
              (product_id,qty,price,qty*price,d))
    c.execute("UPDATE products SET stock=stock-? WHERE id=?",(qty,product_id))
    c.commit(); c.close()

def add_expense(title,amount,category):
    c=connect()
    c.execute("INSERT INTO expenses(title,amount,category,expense_date) VALUES(?,?,?,?)",
              (title,amount,category,str(date.today())))
    c.commit(); c.close()
