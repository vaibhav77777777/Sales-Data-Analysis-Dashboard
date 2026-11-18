"""
generate_data.py
================
Generates realistic sales data for an Indian market scenario and stores it
in an SQLite database (sales_data.db).

Tables created:
  - customers  (~500 unique customers)
  - products   (~100 products across 5 categories)
  - orders     (~10,000 orders spanning 2024-01-01 to 2026-11-18)

A SQL view `sales_summary` joins all three tables and adds calculated
revenue and profit columns.

Usage:
    python generate_data.py
"""

import sqlite3
import random
import string
import datetime
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_data.db")

NUM_CUSTOMERS = 500
NUM_ORDERS = 10_000

START_DATE = datetime.date(2024, 1, 1)
END_DATE = datetime.date(2026, 11, 18)

random.seed(SEED)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharva", "Advik", "Pranav",
    "Advaith", "Dhruv", "Kabir", "Ritvik", "Aarush", "Kayaan",
    "Ananya", "Diya", "Myra", "Sara", "Aadhya", "Aaradhya", "Anvi",
    "Prisha", "Riya", "Isha", "Kavya", "Navya", "Anika", "Kiara",
    "Saanvi", "Avni", "Meera", "Pooja", "Neha", "Shreya",
    "Rahul", "Amit", "Suresh", "Rajesh", "Vikram", "Deepak", "Manoj",
    "Sanjay", "Nikhil", "Rohit", "Ankita", "Sunita", "Priya", "Swati",
    "Nisha", "Rekha", "Divya", "Pallavi", "Komal", "Jyoti",
    "Harsh", "Kunal", "Gaurav", "Varun", "Akash", "Mohit", "Sachin",
    "Tushar", "Ajay", "Vijay", "Sneha", "Tanvi", "Simran", "Parul",
    "Megha", "Bhavna", "Richa", "Sonal", "Heena", "Mansi",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Joshi",
    "Reddy", "Nair", "Iyer", "Desai", "Mehta", "Shah", "Rao",
    "Pillai", "Chopra", "Bhatia", "Malhotra", "Kapoor", "Khanna",
    "Tiwari", "Pandey", "Mishra", "Dubey", "Srivastava", "Chauhan",
    "Thakur", "Saxena", "Agarwal", "Bansal", "Jain", "Goyal",
    "Bhatt", "Kulkarni", "Patil", "Deshpande", "Mukherjee", "Ghosh",
    "Das", "Chatterjee", "Bose", "Sen", "Menon", "Warrier",
    "Hegde", "Shetty", "Naidu", "Rajan", "Prasad", "Mohan",
]

# City -> (State, Region)
CITY_DATA = {
    "Mumbai":       ("Maharashtra",    "West"),
    "Delhi":        ("Delhi",          "North"),
    "Bangalore":    ("Karnataka",      "South"),
    "Chennai":      ("Tamil Nadu",     "South"),
    "Hyderabad":    ("Telangana",      "South"),
    "Pune":         ("Maharashtra",    "West"),
    "Kolkata":      ("West Bengal",    "East"),
    "Jaipur":       ("Rajasthan",      "North"),
    "Ahmedabad":    ("Gujarat",        "West"),
    "Lucknow":      ("Uttar Pradesh",  "North"),
    "Chandigarh":   ("Punjab",         "North"),
    "Indore":       ("Madhya Pradesh", "West"),
    "Nagpur":       ("Maharashtra",    "West"),
    "Bhopal":       ("Madhya Pradesh", "West"),
    "Patna":        ("Bihar",          "East"),
    "Kochi":        ("Kerala",         "South"),
    "Coimbatore":   ("Tamil Nadu",     "South"),
    "Visakhapatnam":("Andhra Pradesh", "South"),
    "Surat":        ("Gujarat",        "West"),
    "Vadodara":     ("Gujarat",        "West"),
    "Noida":        ("Uttar Pradesh",  "North"),
    "Gurgaon":      ("Haryana",        "North"),
    "Mysore":       ("Karnataka",      "South"),
    "Thiruvananthapuram": ("Kerala",   "South"),
    "Ranchi":       ("Jharkhand",      "East"),
    "Bhubaneswar":  ("Odisha",         "East"),
    "Guwahati":     ("Assam",          "East"),
    "Dehradun":     ("Uttarakhand",    "North"),
    "Amritsar":     ("Punjab",         "North"),
    "Varanasi":     ("Uttar Pradesh",  "North"),
}

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.5, 0.3, 0.2]  # Consumer-heavy

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Cash on Delivery", "Net Banking"]
PAYMENT_WEIGHTS = [0.25, 0.20, 0.30, 0.15, 0.10]  # UPI is most popular in India

# ---------------------------------------------------------------------------
# Product catalog  (name, category, sub_category, unit_price_INR, cost_price_INR)
# ---------------------------------------------------------------------------
PRODUCTS = [
    # ---- Electronics (20 products) ----
    ("Wireless Bluetooth Earbuds",       "Electronics", "Audio",        1499,  850),
    ("Over-Ear Headphones",              "Electronics", "Audio",        2999, 1700),
    ("Portable Bluetooth Speaker",       "Electronics", "Audio",        2499, 1400),
    ("Smartphone 5G 128GB",             "Electronics", "Mobiles",      15999, 10500),
    ("Smartphone 5G 256GB",             "Electronics", "Mobiles",      22999, 15000),
    ("Budget Smartphone 64GB",          "Electronics", "Mobiles",       8999,  6200),
    ("Tablet 10-inch 64GB",             "Electronics", "Tablets",      18999, 13000),
    ("Smartwatch Fitness Tracker",       "Electronics", "Wearables",    3999,  2200),
    ("Smart Band",                       "Electronics", "Wearables",    1999,  1100),
    ("Power Bank 20000mAh",             "Electronics", "Accessories",   1299,   750),
    ("USB-C Fast Charger 65W",          "Electronics", "Accessories",    999,   550),
    ("Wireless Mouse",                   "Electronics", "Peripherals",   699,   350),
    ("Mechanical Keyboard",              "Electronics", "Peripherals",  2999,  1600),
    ("Webcam 1080p",                     "Electronics", "Peripherals",  1999,  1100),
    ("External SSD 500GB",              "Electronics", "Storage",       3999,  2800),
    ("USB Flash Drive 64GB",            "Electronics", "Storage",        499,   250),
    ("LED Monitor 24-inch",             "Electronics", "Displays",     10999,  7500),
    ("Laptop Stand Aluminium",          "Electronics", "Accessories",   1499,   800),
    ("HDMI Cable 2m",                   "Electronics", "Accessories",    399,   180),
    ("Surge Protector 6-Socket",        "Electronics", "Accessories",    899,   480),

    # ---- Clothing (20 products) ----
    ("Men's Cotton T-Shirt",             "Clothing", "Men's Wear",      599,   280),
    ("Men's Formal Shirt",               "Clothing", "Men's Wear",     1299,   650),
    ("Men's Casual Jeans",               "Clothing", "Men's Wear",     1499,   750),
    ("Men's Chinos",                     "Clothing", "Men's Wear",     1199,   600),
    ("Men's Polo T-Shirt",              "Clothing", "Men's Wear",      899,   420),
    ("Women's Kurti",                    "Clothing", "Women's Wear",    799,   380),
    ("Women's Palazzo Pants",            "Clothing", "Women's Wear",    699,   320),
    ("Women's Cotton Saree",             "Clothing", "Women's Wear",   1999,   950),
    ("Women's Denim Jacket",             "Clothing", "Women's Wear",   1799,   900),
    ("Women's Formal Blazer",            "Clothing", "Women's Wear",   2499,  1250),
    ("Unisex Hoodie",                    "Clothing", "Winter Wear",    1599,   800),
    ("Unisex Track Pants",              "Clothing", "Sportswear",      999,   480),
    ("Running Shoes",                    "Clothing", "Footwear",       2999,  1500),
    ("Casual Sneakers",                  "Clothing", "Footwear",       1999,  1000),
    ("Leather Sandals",                  "Clothing", "Footwear",       1299,   650),
    ("Cotton Socks (3 Pack)",           "Clothing", "Accessories",      299,   120),
    ("Leather Belt",                     "Clothing", "Accessories",     699,   320),
    ("Aviator Sunglasses",              "Clothing", "Accessories",      999,   450),
    ("Canvas Backpack",                  "Clothing", "Bags",           1499,   700),
    ("Laptop Messenger Bag",            "Clothing", "Bags",            1999,   950),

    # ---- Food (20 products) ----
    ("Basmati Rice 5kg",                 "Food", "Staples",             599,   420),
    ("Whole Wheat Atta 10kg",           "Food", "Staples",              499,   350),
    ("Cold Pressed Mustard Oil 1L",     "Food", "Cooking Oil",          299,   200),
    ("Extra Virgin Olive Oil 500ml",    "Food", "Cooking Oil",          599,   420),
    ("Organic Honey 500g",              "Food", "Sweeteners",           449,   280),
    ("Assorted Dry Fruits 500g",        "Food", "Dry Fruits",           899,   600),
    ("Premium Cashews 250g",            "Food", "Dry Fruits",           499,   330),
    ("Green Tea (100 Bags)",            "Food", "Beverages",            349,   200),
    ("Instant Coffee 200g",             "Food", "Beverages",            499,   310),
    ("Dark Chocolate Bar 100g",         "Food", "Snacks",               199,   110),
    ("Protein Bars (Box of 6)",         "Food", "Snacks",               599,   380),
    ("Muesli 1kg",                      "Food", "Breakfast",            599,   380),
    ("Oats 1kg",                        "Food", "Breakfast",            299,   180),
    ("Peanut Butter 1kg",              "Food", "Spreads",               399,   240),
    ("Mixed Pickle 500g",              "Food", "Condiments",            199,   110),
    ("Tomato Ketchup 1kg",             "Food", "Condiments",            149,    85),
    ("Masala Spice Box Set",            "Food", "Spices",               699,   400),
    ("Turmeric Powder 500g",           "Food", "Spices",                199,   110),
    ("Ghee 1L",                         "Food", "Dairy",                599,   420),
    ("Paneer 200g",                     "Food", "Dairy",                 99,    60),

    # ---- Furniture (20 products) ----
    ("Ergonomic Office Chair",           "Furniture", "Chairs",         8999,  5500),
    ("Executive Mesh Chair",             "Furniture", "Chairs",        12999,  8000),
    ("Wooden Dining Chair",              "Furniture", "Chairs",         3999,  2400),
    ("Folding Chair",                    "Furniture", "Chairs",         1999,  1200),
    ("Study Desk 120cm",                "Furniture", "Desks",           5999,  3600),
    ("Standing Desk Converter",          "Furniture", "Desks",          7999,  5000),
    ("Computer Table with Drawer",       "Furniture", "Desks",          4499,  2700),
    ("Bookshelf 5-Tier",                "Furniture", "Storage",         3999,  2400),
    ("Wardrobe 3-Door",                 "Furniture", "Storage",        14999,  9500),
    ("Shoe Rack 4-Tier",                "Furniture", "Storage",         1999,  1200),
    ("TV Unit 150cm",                   "Furniture", "Entertainment",   7999,  4800),
    ("Bean Bag XXL",                     "Furniture", "Seating",        2499,  1400),
    ("Floor Cushion Set (3)",           "Furniture", "Seating",         1499,   850),
    ("Coffee Table Wooden",             "Furniture", "Tables",          4999,  3000),
    ("Side Table Round",                "Furniture", "Tables",          1999,  1100),
    ("Dining Table 6-Seater",           "Furniture", "Tables",         15999, 10000),
    ("Mattress Queen Size 6-inch",      "Furniture", "Bedroom",        9999,  6500),
    ("Pillow Memory Foam",             "Furniture", "Bedroom",          999,   550),
    ("Bed Frame Queen Metal",           "Furniture", "Bedroom",        8999,  5500),
    ("Wall Shelf Floating Set (3)",     "Furniture", "Decor",           1299,   700),

    # ---- Office Supplies (20 products) ----
    ("Ballpoint Pen (Pack of 10)",      "Office Supplies", "Writing",    149,    70),
    ("Gel Pen Set (5 Colors)",          "Office Supplies", "Writing",    199,    90),
    ("Mechanical Pencil Set",           "Office Supplies", "Writing",    249,   110),
    ("Highlighter Set (6 Colors)",      "Office Supplies", "Writing",    179,    80),
    ("A4 Copier Paper (500 Sheets)",    "Office Supplies", "Paper",      299,   180),
    ("Spiral Notebook A5 (Pack of 5)",  "Office Supplies", "Paper",      249,   130),
    ("Sticky Notes (Pack of 8)",        "Office Supplies", "Paper",      199,    90),
    ("Legal Pad Yellow A4",             "Office Supplies", "Paper",      129,    60),
    ("Desk Organizer",                  "Office Supplies", "Desk Items",  599,   300),
    ("Stapler Heavy-Duty",             "Office Supplies", "Desk Items",   349,   170),
    ("Paper Clips (Box of 100)",       "Office Supplies", "Desk Items",    49,    20),
    ("Scissors Stainless Steel",       "Office Supplies", "Desk Items",   149,    65),
    ("Transparent Tape (Pack of 6)",   "Office Supplies", "Desk Items",   129,    55),
    ("File Folder Set (10)",           "Office Supplies", "Filing",       299,   140),
    ("Binder Clips Assorted (50)",     "Office Supplies", "Filing",       149,    60),
    ("Document Holder A4",             "Office Supplies", "Filing",       199,    90),
    ("Whiteboard Marker Set (4)",      "Office Supplies", "Presentation", 199,    85),
    ("Whiteboard 60x90cm",             "Office Supplies", "Presentation",1499,   800),
    ("Laminating Pouches A4 (100)",    "Office Supplies", "Presentation", 599,   320),
    ("Calculator Scientific",          "Office Supplies", "Desk Items",   499,   260),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def generate_customers(n: int) -> list[dict]:
    """Generate *n* unique customer records."""
    cities = list(CITY_DATA.keys())
    customers = []
    used_emails: set[str] = set()

    for i in range(1, n + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"

        # Build a unique email
        base_email = f"{first.lower()}.{last.lower()}"
        email = f"{base_email}@example.com"
        counter = 1
        while email in used_emails:
            email = f"{base_email}{counter}@example.com"
            counter += 1
        used_emails.add(email)

        city = random.choice(cities)
        state, region = CITY_DATA[city]
        segment = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS, k=1)[0]

        customers.append({
            "customer_id": i,
            "name": name,
            "email": email,
            "segment": segment,
            "city": city,
            "state": state,
            "region": region,
        })
    return customers


def generate_products() -> list[dict]:
    """Return the product catalog as a list of dicts."""
    products = []
    for idx, (name, cat, sub, price, cost) in enumerate(PRODUCTS, start=1):
        products.append({
            "product_id": idx,
            "name": name,
            "category": cat,
            "sub_category": sub,
            "unit_price": price,
            "cost_price": cost,
        })
    return products


def _seasonal_weight(d: datetime.date) -> float:
    """Return a multiplier for order-generation probability on date *d*.

    Implements:
      - Diwali spike:  Oct 15 – Nov 15  → 2.0×
      - Year-end spike: Dec 1 – Dec 31  → 1.6×
      - Summer dip:     May 1 – Jun 30  → 0.7×
      - Normal:         everything else  → 1.0×
    """
    m, day = d.month, d.day
    if (m == 10 and day >= 15) or (m == 11 and day <= 15):
        return 2.0
    if m == 12:
        return 1.6
    if m in (5, 6):
        return 0.7
    return 1.0


def generate_orders(n: int, num_customers: int, num_products: int) -> list[dict]:
    """Generate *n* order records with seasonal distribution."""

    # Build a weighted list of all dates in the range
    all_dates: list[datetime.date] = []
    weights: list[float] = []
    d = START_DATE
    while d <= END_DATE:
        all_dates.append(d)
        weights.append(_seasonal_weight(d))
        d += datetime.timedelta(days=1)

    # Pre-select order dates using seasonal weights
    order_dates = random.choices(all_dates, weights=weights, k=n)
    order_dates.sort()

    # Discount distribution: heavily skewed toward 0 and low values
    discount_choices = [0.0] * 40 + [0.05] * 20 + [0.10] * 15 + [0.15] * 10 + \
                       [0.20] * 8 + [0.25] * 4 + [0.30] * 3

    # Quantity distribution: weighted toward lower quantities
    qty_weights = [30, 25, 15, 10, 7, 5, 3, 2, 2, 1]  # for quantities 1-10

    orders = []
    for i in range(1, n + 1):
        od = order_dates[i - 1]
        cid = random.randint(1, num_customers)
        pid = random.randint(1, num_products)
        qty = random.choices(range(1, 11), weights=qty_weights, k=1)[0]
        discount = random.choice(discount_choices)

        # Shipping cost: ₹49-₹299, partly correlated with quantity
        shipping = round(random.uniform(49, 99) + qty * random.uniform(10, 20), 2)

        payment = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS, k=1)[0]

        orders.append({
            "order_id": i,
            "order_date": od.isoformat(),
            "customer_id": cid,
            "product_id": pid,
            "quantity": qty,
            "discount": discount,
            "shipping_cost": shipping,
            "payment_method": payment,
        })
    return orders


# ---------------------------------------------------------------------------
# Database creation
# ---------------------------------------------------------------------------

def create_database(customers, products, orders):
    """Create the SQLite database, insert all data, and add the summary view."""

    # Remove old DB if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -- customers table --
    cur.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            segment     TEXT NOT NULL CHECK(segment IN ('Consumer','Corporate','Home Office')),
            city        TEXT NOT NULL,
            state       TEXT NOT NULL,
            region      TEXT NOT NULL CHECK(region IN ('North','South','East','West'))
        );
    """)

    cur.executemany(
        "INSERT INTO customers VALUES (:customer_id,:name,:email,:segment,:city,:state,:region)",
        customers,
    )

    # -- products table --
    cur.execute("""
        CREATE TABLE products (
            product_id  INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            sub_category TEXT NOT NULL,
            unit_price  REAL NOT NULL,
            cost_price  REAL NOT NULL
        );
    """)

    cur.executemany(
        "INSERT INTO products VALUES (:product_id,:name,:category,:sub_category,:unit_price,:cost_price)",
        products,
    )

    # -- orders table --
    cur.execute("""
        CREATE TABLE orders (
            order_id       INTEGER PRIMARY KEY,
            order_date     TEXT NOT NULL,
            customer_id    INTEGER NOT NULL REFERENCES customers(customer_id),
            product_id     INTEGER NOT NULL REFERENCES products(product_id),
            quantity       INTEGER NOT NULL,
            discount       REAL NOT NULL,
            shipping_cost  REAL NOT NULL,
            payment_method TEXT NOT NULL CHECK(payment_method IN
                ('Credit Card','Debit Card','UPI','Cash on Delivery','Net Banking'))
        );
    """)

    cur.executemany(
        """INSERT INTO orders VALUES
           (:order_id,:order_date,:customer_id,:product_id,:quantity,:discount,:shipping_cost,:payment_method)""",
        orders,
    )

    # -- Indexes for common queries --
    cur.execute("CREATE INDEX idx_orders_date ON orders(order_date);")
    cur.execute("CREATE INDEX idx_orders_customer ON orders(customer_id);")
    cur.execute("CREATE INDEX idx_orders_product ON orders(product_id);")

    # -- sales_summary view --
    cur.execute("""
        CREATE VIEW sales_summary AS
        SELECT
            o.order_id,
            o.order_date,
            c.customer_id,
            c.name           AS customer_name,
            c.segment,
            c.city,
            c.state,
            c.region,
            p.product_id,
            p.name           AS product_name,
            p.category,
            p.sub_category,
            p.unit_price,
            p.cost_price,
            o.quantity,
            o.discount,
            o.shipping_cost,
            o.payment_method,
            ROUND(o.quantity * p.unit_price * (1 - o.discount), 2)  AS revenue,
            ROUND(o.quantity * p.unit_price * (1 - o.discount)
                  - (o.quantity * p.cost_price)
                  - o.shipping_cost, 2)                             AS profit
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products  p ON o.product_id  = p.product_id;
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def print_summary():
    """Print high-level stats from the generated database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 60)
    print("  SALES DATA GENERATION — SUMMARY")
    print("=" * 60)

    # Row counts
    for table in ("customers", "products", "orders"):
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:>12s}: {count:>6,} rows")

    print("-" * 60)

    # Date range
    min_d, max_d = cur.execute(
        "SELECT MIN(order_date), MAX(order_date) FROM orders"
    ).fetchone()
    print(f"  Order date range : {min_d}  to  {max_d}")

    # Revenue & profit
    row = cur.execute(
        "SELECT ROUND(SUM(revenue),2), ROUND(SUM(profit),2) FROM sales_summary"
    ).fetchone()
    print(f"  Total revenue    : Rs.{row[0]:>14,.2f}")
    print(f"  Total profit     : Rs.{row[1]:>14,.2f}")

    # By category
    print("\n  Revenue by category:")
    for cat, rev in cur.execute(
        "SELECT category, ROUND(SUM(revenue),2) FROM sales_summary GROUP BY category ORDER BY SUM(revenue) DESC"
    ):
        print(f"    {cat:<20s}  Rs.{rev:>14,.2f}")

    # By region
    print("\n  Revenue by region:")
    for reg, rev in cur.execute(
        "SELECT region, ROUND(SUM(revenue),2) FROM sales_summary GROUP BY region ORDER BY SUM(revenue) DESC"
    ):
        print(f"    {reg:<10s}  Rs.{rev:>14,.2f}")

    # By year
    print("\n  Revenue by year:")
    for yr, rev in cur.execute(
        "SELECT SUBSTR(order_date,1,4) AS yr, ROUND(SUM(revenue),2) FROM sales_summary GROUP BY yr ORDER BY yr"
    ):
        print(f"    {yr}  Rs.{rev:>14,.2f}")

    # Payment methods
    print("\n  Orders by payment method:")
    for pm, cnt in cur.execute(
        "SELECT payment_method, COUNT(*) FROM orders GROUP BY payment_method ORDER BY COUNT(*) DESC"
    ):
        print(f"    {pm:<22s}  {cnt:>5,}")

    # Segments
    print("\n  Customers by segment:")
    for seg, cnt in cur.execute(
        "SELECT segment, COUNT(*) FROM customers GROUP BY segment ORDER BY COUNT(*) DESC"
    ):
        print(f"    {seg:<15s}  {cnt:>4,}")

    print("=" * 60)
    print(f"  Database saved to: {DB_PATH}")
    print("=" * 60)

    conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating customers...")
    customers = generate_customers(NUM_CUSTOMERS)

    print("Generating products...")
    products = generate_products()

    print(f"Generating {NUM_ORDERS:,} orders with seasonal patterns...")
    orders = generate_orders(NUM_ORDERS, len(customers), len(products))

    print("Writing SQLite database...")
    create_database(customers, products, orders)

    print_summary()


if __name__ == "__main__":
    main()
