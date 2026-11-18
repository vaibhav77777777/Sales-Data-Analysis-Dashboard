"""
SQL-Based Sales Data Analysis Module
=====================================

Provides functions that run SQL queries against a SQLite sales database
and return results as pandas DataFrames. Covers KPIs, trends, segmentation,
RFM analysis, discount impact, seasonality, and more.

Dependencies: pandas, sqlite3 (stdlib)
"""

import sqlite3
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH = r"c:\Users\VAIBHAV\Downloads\Sales Data Analysis\sales_data.db"

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Execute *sql* against the sales database and return a DataFrame.

    Parameters
    ----------
    sql : str
        A valid SQLite SQL statement.
    params : tuple, optional
        Bind parameters for the query.

    Returns
    -------
    pd.DataFrame
        Query result set.
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


# ---------------------------------------------------------------------------
# 1. KPI Summary
# ---------------------------------------------------------------------------


def get_kpi_summary() -> pd.DataFrame:
    """High-level business KPIs.

    Returns
    -------
    pd.DataFrame
        Single-row frame with total_revenue, total_profit, total_orders,
        avg_order_value, and profit_margin_pct.
    """
    sql = """
    SELECT
        ROUND(SUM(revenue), 2)                          AS total_revenue,
        ROUND(SUM(profit), 2)                           AS total_profit,
        COUNT(DISTINCT order_id)                        AS total_orders,
        ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
        ROUND(SUM(profit) * 100.0 / SUM(revenue), 2)   AS profit_margin_pct
    FROM sales_summary;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 2. Monthly Revenue Trend
# ---------------------------------------------------------------------------


def get_monthly_revenue_trend() -> pd.DataFrame:
    """Monthly revenue and profit over the entire date range.

    Returns
    -------
    pd.DataFrame
        Columns: month, revenue, profit (sorted chronologically).
    """
    sql = """
    SELECT
        strftime('%Y-%m', order_date)       AS month,
        ROUND(SUM(revenue), 2)              AS revenue,
        ROUND(SUM(profit), 2)               AS profit
    FROM sales_summary
    GROUP BY month
    ORDER BY month;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 3. Category Performance
# ---------------------------------------------------------------------------


def get_category_performance() -> pd.DataFrame:
    """Revenue, profit, and order count broken down by product category.

    Returns
    -------
    pd.DataFrame
        Columns: category, revenue, profit, order_count, profit_margin_pct.
    """
    sql = """
    SELECT
        category,
        ROUND(SUM(revenue), 2)                        AS revenue,
        ROUND(SUM(profit), 2)                         AS profit,
        COUNT(*)                                      AS order_count,
        ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS profit_margin_pct
    FROM sales_summary
    GROUP BY category
    ORDER BY revenue DESC;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 4. Top Products
# ---------------------------------------------------------------------------


def get_top_products(n: int = 10) -> pd.DataFrame:
    """Top *n* products ranked by total revenue.

    Parameters
    ----------
    n : int, optional
        Number of products to return (default 10).

    Returns
    -------
    pd.DataFrame
        Columns: product_name, category, revenue, profit, quantity_sold.
    """
    sql = """
    SELECT
        product_name,
        category,
        ROUND(SUM(revenue), 2)  AS revenue,
        ROUND(SUM(profit), 2)   AS profit,
        SUM(quantity)            AS quantity_sold
    FROM sales_summary
    GROUP BY product_id, product_name, category
    ORDER BY revenue DESC
    LIMIT ?;
    """
    return run_query(sql, (n,))


# ---------------------------------------------------------------------------
# 5. Regional Analysis
# ---------------------------------------------------------------------------


def get_regional_analysis() -> pd.DataFrame:
    """Revenue, profit, and order count by geographic region.

    Returns
    -------
    pd.DataFrame
        Columns: region, revenue, profit, order_count, profit_margin_pct.
    """
    sql = """
    SELECT
        region,
        ROUND(SUM(revenue), 2)                        AS revenue,
        ROUND(SUM(profit), 2)                         AS profit,
        COUNT(*)                                      AS order_count,
        ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS profit_margin_pct
    FROM sales_summary
    GROUP BY region
    ORDER BY revenue DESC;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 6. City-Wise Sales
# ---------------------------------------------------------------------------


def get_city_wise_sales(n: int = 15) -> pd.DataFrame:
    """Top *n* cities by total revenue.

    Parameters
    ----------
    n : int, optional
        Number of cities to return (default 15).

    Returns
    -------
    pd.DataFrame
        Columns: city, state, revenue, profit, order_count.
    """
    sql = """
    SELECT
        city,
        state,
        ROUND(SUM(revenue), 2)  AS revenue,
        ROUND(SUM(profit), 2)   AS profit,
        COUNT(*)                 AS order_count
    FROM sales_summary
    GROUP BY city, state
    ORDER BY revenue DESC
    LIMIT ?;
    """
    return run_query(sql, (n,))


# ---------------------------------------------------------------------------
# 7. Customer Segmentation
# ---------------------------------------------------------------------------


def get_customer_segmentation() -> pd.DataFrame:
    """Revenue distribution across customer segments.

    Returns
    -------
    pd.DataFrame
        Columns: segment, revenue, profit, customer_count, avg_revenue_per_customer.
    """
    sql = """
    SELECT
        segment,
        ROUND(SUM(revenue), 2)                                    AS revenue,
        ROUND(SUM(profit), 2)                                     AS profit,
        COUNT(DISTINCT customer_id)                                AS customer_count,
        ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2)      AS avg_revenue_per_customer
    FROM sales_summary
    GROUP BY segment
    ORDER BY revenue DESC;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 8. RFM Analysis
# ---------------------------------------------------------------------------


def get_rfm_analysis() -> pd.DataFrame:
    """RFM (Recency, Frequency, Monetary) segmentation for every customer.

    Scoring
    -------
    * Each dimension is split into 5 quintile buckets (NTILE).
    * Recency: lower days-since-last-order → higher score (5 = most recent).
    * Frequency & Monetary: higher values → higher score.

    Segment labels are derived from the combined R/F/M scores:
        Champions, Loyal Customers, Potential Loyalists, Recent Customers,
        Promising, Need Attention, About to Sleep, At Risk,
        Can't Lose Them, Hibernating, Lost.

    Returns
    -------
    pd.DataFrame
        Columns: customer_id, customer_name, recency_days, frequency,
        monetary, r_score, f_score, m_score, rfm_segment.
    """
    sql = """
    WITH rfm_base AS (
        SELECT
            customer_id,
            customer_name,
            CAST(julianday((SELECT MAX(order_date) FROM sales_summary))
                 - julianday(MAX(order_date)) AS INTEGER)   AS recency_days,
            COUNT(DISTINCT order_id)                        AS frequency,
            ROUND(SUM(revenue), 2)                          AS monetary
        FROM sales_summary
        GROUP BY customer_id, customer_name
    ),
    rfm_scored AS (
        SELECT
            *,
            NTILE(5) OVER (ORDER BY recency_days DESC)  AS r_score,
            NTILE(5) OVER (ORDER BY frequency    ASC)   AS f_score,
            NTILE(5) OVER (ORDER BY monetary     ASC)   AS m_score
        FROM rfm_base
    )
    SELECT
        customer_id,
        customer_name,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 4 AND m_score >= 4                  THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score >= 2 AND f_score <= 4 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score <= 2                  THEN 'Recent Customers'
            WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Promising'
            WHEN r_score  = 3 AND f_score <= 3                  THEN 'Need Attention'
            WHEN r_score  = 2 AND f_score >= 2                  THEN 'About to Sleep'
            WHEN r_score  = 2 AND f_score <= 2 AND m_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score >= 4                  THEN "Can't Lose Them"
            WHEN r_score  = 1 AND f_score >= 2                  THEN 'Hibernating'
            ELSE 'Lost'
        END AS rfm_segment
    FROM rfm_scored
    ORDER BY monetary DESC;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 9. Payment Method Analysis
# ---------------------------------------------------------------------------


def get_payment_method_analysis() -> pd.DataFrame:
    """Revenue distribution by payment method.

    Returns
    -------
    pd.DataFrame
        Columns: payment_method, revenue, profit, order_count, pct_of_revenue.
    """
    sql = """
    SELECT
        payment_method,
        ROUND(SUM(revenue), 2)                                              AS revenue,
        ROUND(SUM(profit), 2)                                               AS profit,
        COUNT(*)                                                            AS order_count,
        ROUND(SUM(revenue) * 100.0 / SUM(SUM(revenue)) OVER (), 2)         AS pct_of_revenue
    FROM sales_summary
    GROUP BY payment_method
    ORDER BY revenue DESC;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 10. Monthly Growth
# ---------------------------------------------------------------------------


def get_monthly_growth() -> pd.DataFrame:
    """Month-over-month revenue growth percentage.

    Uses a window function to compare each month's revenue with the
    previous month.

    Returns
    -------
    pd.DataFrame
        Columns: month, revenue, prev_month_revenue, growth_pct.
    """
    sql = """
    WITH monthly AS (
        SELECT
            strftime('%Y-%m', order_date)  AS month,
            ROUND(SUM(revenue), 2)         AS revenue
        FROM sales_summary
        GROUP BY month
        ORDER BY month
    )
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month)                                      AS prev_month_revenue,
        ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
              * 100.0 / LAG(revenue) OVER (ORDER BY month), 2)                 AS growth_pct
    FROM monthly
    ORDER BY month;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 11. Quarterly Revenue
# ---------------------------------------------------------------------------


def get_quarterly_revenue() -> pd.DataFrame:
    """Quarterly revenue breakdown.

    Returns
    -------
    pd.DataFrame
        Columns: year, quarter, quarter_label, revenue, profit.
    """
    sql = """
    SELECT
        strftime('%Y', order_date)  AS year,
        CASE
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1  AND 3  THEN 1
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4  AND 6  THEN 2
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7  AND 9  THEN 3
            ELSE 4
        END                                     AS quarter,
        strftime('%Y', order_date) || '-Q' ||
        CASE
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1  AND 3  THEN '1'
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4  AND 6  THEN '2'
            WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7  AND 9  THEN '3'
            ELSE '4'
        END                                     AS quarter_label,
        ROUND(SUM(revenue), 2)                  AS revenue,
        ROUND(SUM(profit), 2)                   AS profit
    FROM sales_summary
    GROUP BY year, quarter
    ORDER BY year, quarter;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 12. Discount Impact
# ---------------------------------------------------------------------------


def get_discount_impact() -> pd.DataFrame:
    """Analyse how different discount ranges affect revenue and profit margin.

    Discount buckets: 0%, 1-10%, 11-20%, 21-30%, >30%.

    Returns
    -------
    pd.DataFrame
        Columns: discount_range, order_count, revenue, profit,
        avg_discount_pct, profit_margin_pct.
    """
    sql = """
    SELECT
        CASE
            WHEN discount = 0                       THEN 'No Discount'
            WHEN discount > 0  AND discount <= 0.10 THEN '1-10%'
            WHEN discount > 0.10 AND discount <= 0.20 THEN '11-20%'
            WHEN discount > 0.20 AND discount <= 0.30 THEN '21-30%'
            ELSE '>30%'
        END                                                 AS discount_range,
        COUNT(*)                                            AS order_count,
        ROUND(SUM(revenue), 2)                              AS revenue,
        ROUND(SUM(profit), 2)                               AS profit,
        ROUND(AVG(discount) * 100, 2)                       AS avg_discount_pct,
        ROUND(SUM(profit) * 100.0 / SUM(revenue), 2)       AS profit_margin_pct
    FROM sales_summary
    GROUP BY discount_range
    ORDER BY avg_discount_pct;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 13. Seasonal Pattern
# ---------------------------------------------------------------------------


def get_seasonal_pattern() -> pd.DataFrame:
    """Average revenue by calendar month to reveal seasonality.

    Returns
    -------
    pd.DataFrame
        Columns: month_number, month_name, avg_revenue, total_revenue, year_count.
    """
    sql = """
    WITH monthly AS (
        SELECT
            CAST(strftime('%m', order_date) AS INTEGER) AS month_number,
            strftime('%Y', order_date)                  AS year,
            SUM(revenue)                                AS revenue
        FROM sales_summary
        GROUP BY month_number, year
    )
    SELECT
        month_number,
        CASE month_number
            WHEN 1  THEN 'January'   WHEN 2  THEN 'February'
            WHEN 3  THEN 'March'     WHEN 4  THEN 'April'
            WHEN 5  THEN 'May'       WHEN 6  THEN 'June'
            WHEN 7  THEN 'July'      WHEN 8  THEN 'August'
            WHEN 9  THEN 'September' WHEN 10 THEN 'October'
            WHEN 11 THEN 'November'  WHEN 12 THEN 'December'
        END                             AS month_name,
        ROUND(AVG(revenue), 2)          AS avg_revenue,
        ROUND(SUM(revenue), 2)          AS total_revenue,
        COUNT(*)                        AS year_count
    FROM monthly
    GROUP BY month_number
    ORDER BY month_number;
    """
    return run_query(sql)


# ---------------------------------------------------------------------------
# 14. Forecast Data
# ---------------------------------------------------------------------------


def get_forecast_data() -> pd.DataFrame:
    """Return monthly revenue suitable for simple time-series forecasting.

    The DataFrame includes a numeric month index (starting at 1) so that
    downstream code can feed it straight into a linear regression or
    moving-average model.

    Returns
    -------
    pd.DataFrame
        Columns: month, revenue, month_index.
    """
    sql = """
    WITH monthly AS (
        SELECT
            strftime('%Y-%m', order_date) AS month,
            ROUND(SUM(revenue), 2)        AS revenue
        FROM sales_summary
        GROUP BY month
        ORDER BY month
    )
    SELECT
        month,
        revenue,
        ROW_NUMBER() OVER (ORDER BY month) AS month_index
    FROM monthly
    ORDER BY month;
    """
    return run_query(sql)
