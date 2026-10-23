
import json
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

app.config["DATABASE"] = os.environ.get(
    "DATABASE_PATH", "coffee_shop.db"
)

MENU = {
    "Espresso": 60,
    "Americano": 70,
    "Cappuccino": 80,
    "Latte": 90,
    "Mocha": 100,
    "Cold Coffee": 110,
    "Tea": 50,
}


def get_db():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                items TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount REAL NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


@app.route("/")
def home():
    return render_template("index.html", menu=MENU)


@app.route("/order", methods=["POST"])
def place_order():
    customer = request.form.get("customer", "").strip()

    if not customer:
        return "Customer name is required.", 400

    items = []
    subtotal = 0

    for name, price in MENU.items():
        try:
            quantity = int(request.form.get(name, "0"))
        except ValueError:
            return f"Invalid quantity for {name}.", 400

        if quantity < 0 or quantity > 100:
            return f"Quantity for {name} must be between 0 and 100.", 400

        if quantity:
            amount = price * quantity
            items.append({
                "name": name,
                "quantity": quantity,
                "price": price,
                "amount": amount,
            })
            subtotal += amount

    if not items:
        return "Please select at least one item.", 400

    discount = round(subtotal * 0.10, 2) if subtotal >= 500 else 0
    total = round(subtotal - discount, 2)

    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO orders
            (customer, items, subtotal, discount, total, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            customer,
            json.dumps(items),
            subtotal,
            discount,
            total,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        order_id = cursor.lastrowid

    return render_template(
        "index.html",
        menu=MENU,
        bill={
            "id": order_id,
            "customer": customer,
            "items": items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
        },
    )


@app.route("/orders")
def orders():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM orders ORDER BY id DESC"
        ).fetchall()

    return render_template("orders.html", orders=rows)


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

# Coffee Shop Management System - GitHub push demonstration
