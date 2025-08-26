import tkinter as tk
from tkinter import messagebox
import sqlite3

# --- SQLite өгөгдлийн сан үүсгэх ---
conn = sqlite3.connect("store.db")
c = conn.cursor()

# Барааны хүснэгт
c.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    qty INTEGER,
    price REAL
)
""")

# Худалдааны хүснэгт
c.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    qty INTEGER,
    price REAL,
    date TEXT DEFAULT (DATE('now'))
)
""")
conn.commit()

# --- Функцууд ---

def add_product():
    name = entry_name.get()
    qty = entry_qty.get()
    price = entry_price.get()
    if not name or not qty or not price:
        messagebox.showerror("Алдаа", "Бүх талбарыг бөглөнө үү")
        return
    try:
        qty = int(qty)
        price = float(price)
    except ValueError:
        messagebox.showerror("Алдаа", "Тоо болон үнийг зөв оруулна уу")
        return
    c.execute("SELECT qty FROM inventory WHERE name=?", (name,))
    result = c.fetchone()
    if result:
        c.execute("UPDATE inventory SET qty = qty + ?, price=? WHERE name=?", (qty, price, name))
    else:
        c.execute("INSERT INTO inventory (name, qty, price) VALUES (?, ?, ?)", (name, qty, price))
    conn.commit()
    update_inventory_display()
    entry_name.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)

def sell_product():
    name = entry_sell_name.get()
    qty = entry_sell_qty.get()
    price = entry_sell_price.get()
    if not name or not qty or not price:
        messagebox.showerror("Алдаа", "Бүх талбарыг бөглөнө үү")
        return
    try:
        qty = int(qty)
        price = float(price)
    except ValueError:
        messagebox.showerror("Алдаа", "Тоо болон үнийг зөв оруулна уу")
        return
    c.execute("SELECT qty FROM inventory WHERE name=?", (name,))
    result = c.fetchone()
    if not result:
        messagebox.showerror("Алдаа", f"{name} нэртэй бараа олдсонгүй")
        return
    if qty > result[0]:
        messagebox.showerror("Алдаа", "Хангалттай бараа алга")
        return
    c.execute("UPDATE inventory SET qty = qty - ? WHERE name=?", (qty, name))
    c.execute("INSERT INTO sales (name, qty, price) VALUES (?, ?, ?)", (name, qty, price))
    conn.commit()
    update_inventory_display()
    update_sales_display()
    entry_sell_name.delete(0, tk.END)
    entry_sell_qty.delete(0, tk.END)
    entry_sell_price.delete(0, tk.END)

def update_inventory_display():
    inventory_text.config(state="normal")
    inventory_text.delete(1.0, tk.END)
    c.execute("SELECT name, qty, price FROM inventory")
    total_items = 0
    for name, qty, price in c.fetchall():
        inventory_text.insert(tk.END, f"{name}: {qty} ширхэг, {price}₮/ширхэг, Нийт: {qty*price}₮\n")
        total_items += qty
    lbl_total_inventory.config(text=f"Нийт барааны тоо: {total_items}")
    inventory_text.config(state="disabled")

def update_sales_display():
    sales_text.config(state="normal")
    sales_text.delete(1.0, tk.END)
    c.execute("SELECT name, qty, price FROM sales WHERE date = DATE('now')")
    total_qty = 0
    total_amount = 0
    for name, qty, price in c.fetchall():
        sales_text.insert(tk.END, f"{name}: {qty} ширхэг, {price}₮/ширхэг, Нийт: {qty*price}₮\n")
        total_qty += qty
        total_amount += qty*price
    lbl_total_sales_qty.config(text=f"Өдрийн нийт борлуулалт: {total_qty} ширхэг")
    lbl_total_sales_amount.config(text=f"Өдрийн нийт дүн: {total_amount}₮")
    sales_text.config(state="disabled")

# --- GUI ---
root = tk.Tk()
root.title("Дэлгүүрийн Бараа Бүртгэлийн Систем (SQLite)")
root.geometry("900x750")

# Бараа нэмэх хэсэг
frame_add = tk.LabelFrame(root, text="Бараа нэмэх", padx=10, pady=10)
frame_add.pack(fill="both", expand=True, padx=10, pady=5)

tk.Label(frame_add, text="Барааны нэр:").grid(row=0, column=0, sticky="w")
tk.Label(frame_add, text="Тоо ширхэг:").grid(row=1, column=0, sticky="w")
tk.Label(frame_add, text="1 ширхэг үнэ:").grid(row=2, column=0, sticky="w")

entry_name = tk.Entry(frame_add)
entry_qty = tk.Entry(frame_add)
entry_price = tk.Entry(frame_add)

entry_name.grid(row=0, column=1, sticky="ew")
entry_qty.grid(row=1, column=1, sticky="ew")
entry_price.grid(row=2, column=1, sticky="ew")

tk.Button(frame_add, text="Нэмэх", command=add_product).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

inventory_text = tk.Text(frame_add, height=15, width=100, state="disabled")
inventory_text.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=5)

lbl_total_inventory = tk.Label(frame_add, text="Нийт барааны тоо: 0")
lbl_total_inventory.grid(row=5, column=0, columnspan=2, sticky="w")

frame_add.grid_rowconfigure(4, weight=1)
frame_add.grid_columnconfigure(1, weight=1)

# Худалдаа хэсэг
frame_sell = tk.LabelFrame(root, text="Худалдаа", padx=10, pady=10)
frame_sell.pack(fill="both", expand=True, padx=10, pady=5)

tk.Label(frame_sell, text="Барааны нэр:").grid(row=0, column=0, sticky="w")
tk.Label(frame_sell, text="Тоо ширхэг:").grid(row=1, column=0, sticky="w")
tk.Label(frame_sell, text="Худалдсан үнэ:").grid(row=2, column=0, sticky="w")

entry_sell_name = tk.Entry(frame_sell)
entry_sell_qty = tk.Entry(frame_sell)
entry_sell_price = tk.Entry(frame_sell)

entry_sell_name.grid(row=0, column=1, sticky="ew")
entry_sell_qty.grid(row=1, column=1, sticky="ew")
entry_sell_price.grid(row=2, column=1, sticky="ew")

tk.Button(frame_sell, text="Худалдах", command=sell_product).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

sales_text = tk.Text(frame_sell, height=15, width=100, state="disabled")
sales_text.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=5)

lbl_total_sales_qty = tk.Label(frame_sell, text="Өдрийн нийт борлуулалт: 0 ширхэг")
lbl_total_sales_qty.grid(row=5, column=0, columnspan=2, sticky="w")
lbl_total_sales_amount = tk.Label(frame_sell, text="Өдрийн нийт дүн: 0₮")
lbl_total_sales_amount.grid(row=6, column=0, columnspan=2, sticky="w")

frame_sell.grid_rowconfigure(4, weight=1)
frame_sell.grid_columnconfigure(1, weight=1)

update_inventory_display()
update_sales_display()

root.mainloop()
