# 📊 Sales Data Analysis Dashboard

An end-to-end **Sales Data Analysis** project built with **Python**, **SQL (SQLite)**, **Streamlit**, and **Plotly**. Features realistic Indian market data, SQL-powered analytics, and an interactive dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![SQLite](https://img.shields.io/badge/SQLite-Database-green)
![Plotly](https://img.shields.io/badge/Plotly-Visualizations-purple)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sample data (creates sales_data.db)
python generate_data.py

# 3. Launch the dashboard
streamlit run dashboard.py
```

---

## 📁 Project Structure

```
Sales Data Analysis/
├── generate_data.py      # Generates realistic sales data → SQLite
├── sql_analysis.py       # 14 SQL analysis functions (pandas + sqlite3)
├── dashboard.py          # Interactive Streamlit dashboard
├── sales_data.db         # SQLite database (auto-generated)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🗄️ Database Schema

### Tables

| Table | Columns | Rows |
|-------|---------|------|
| `customers` | customer_id, name, email, segment, city, state, region | 500 |
| `products` | product_id, name, category, sub_category, unit_price, cost_price | 100 |
| `orders` | order_id, order_date, customer_id, product_id, quantity, discount, shipping_cost, payment_method | 10,000 |

### View: `sales_summary`
Joins all three tables with computed columns:
- **Revenue** = quantity × unit_price × (1 − discount)
- **Profit** = revenue − (quantity × cost_price) − shipping_cost

---

## 📊 Dashboard Pages

### 🏠 Overview
- KPI cards: Total Revenue, Profit, Orders, Avg Order Value, Profit Margin
- Monthly revenue trend, category pie chart, regional bars, top products

### 📈 Revenue Trends
- Monthly revenue & profit with dual-axis chart
- Month-over-month growth (%) with positive/negative coloring
- Quarterly revenue by year (grouped bars)
- Seasonal pattern analysis (Diwali, year-end spikes)

### 🛍️ Product Analysis
- Category performance: revenue, profit, margin comparison
- Top N products slider (5–25) with horizontal bar chart

### 🗺️ Regional Analysis
- Regional revenue pie chart & bar comparison
- Profit margin by region (color-coded)
- City-wise breakdown with treemap visualization

### 👥 Customer Insights
- Customer segment analysis (Consumer/Corporate/Home Office)
- **RFM Analysis**: Recency–Frequency–Monetary segmentation
  - Pie chart of segment distribution
  - Scatter plot (Recency vs Frequency, size = Monetary)
  - Full customer table with scores

### 💳 Payment & Discounts
- Payment method distribution (pie + bar)
- Discount impact analysis on revenue & profit margins

### 🔮 Forecasting
- Linear trend forecast (6 months ahead)
- 3-month and 6-month moving averages
- R² fit quality score
- Forecast summary table

---

## 🔧 SQL Analysis Functions

The `sql_analysis.py` module exposes 14 functions:

| # | Function | Description |
|---|----------|-------------|
| 1 | `get_kpi_summary()` | Total revenue, profit, orders, AOV, margin |
| 2 | `get_monthly_revenue_trend()` | Monthly revenue & profit |
| 3 | `get_category_performance()` | Revenue by product category |
| 4 | `get_top_products(n)` | Top N products by revenue |
| 5 | `get_regional_analysis()` | Revenue by region |
| 6 | `get_city_wise_sales(n)` | Top N cities by revenue |
| 7 | `get_customer_segmentation()` | Revenue by customer segment |
| 8 | `get_rfm_analysis()` | RFM customer scoring & segmentation |
| 9 | `get_payment_method_analysis()` | Revenue by payment method |
| 10 | `get_monthly_growth()` | Month-over-month growth % |
| 11 | `get_quarterly_revenue()` | Quarterly breakdown |
| 12 | `get_discount_impact()` | Discount range vs profit margin |
| 13 | `get_seasonal_pattern()` | Avg revenue by calendar month |
| 14 | `get_forecast_data()` | Monthly data for forecasting |

Each function uses SQL (with CTEs, window functions) and returns a pandas DataFrame.

---

## 📋 Data Highlights

- **Geography**: 10+ Indian cities across 4 regions (North/South/East/West)
- **Products**: 100 products in 5 categories (Electronics, Clothing, Food, Furniture, Office Supplies)
- **Payments**: Credit Card, Debit Card, UPI, Cash on Delivery, Net Banking
- **Seasonality**: Diwali spike (Oct–Nov), year-end spike (Dec), summer dip (May–Jun)
- **Date Range**: January 2024 – November 2026

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Database | SQLite 3 |
| SQL | CTEs, Window Functions, JOINs, Views |
| Dashboard | Streamlit |
| Visualization | Plotly Express & Graph Objects |
| Data Processing | pandas, NumPy |

---

## 📄 License

This project is for educational and portfolio purposes. Feel free to use and modify.
