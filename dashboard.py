"""
Sales Data Analysis — Interactive Streamlit Dashboard
======================================================

Launch with:
    streamlit run dashboard.py

Requires: streamlit, plotly, pandas, numpy
"""

import sys
import os

# Ensure project directory is on the path so we can import sql_analysis
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

import sql_analysis as sa

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="📊 Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* KPI cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: rgba(255,255,255,0.9) !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: white !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Smooth container borders */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }

    .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("# 📊 Sales Dashboard")
    st.markdown("---")
    st.markdown("### Navigation")

    page = st.radio(
        "Go to",
        [
            "🏠 Overview",
            "📈 Revenue Trends",
            "🛍️ Product Analysis",
            "🗺️ Regional Analysis",
            "👥 Customer Insights",
            "💳 Payment & Discounts",
            "🔮 Forecasting",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "Built with **Python**, **SQL**, **Streamlit** & **Plotly**. "
        "Data stored in **SQLite**."
    )
    st.markdown(f"📅 Data: Jan 2024 – Nov 2026")
    st.markdown("👨‍💻 Sales Data Analysis Project")


# ---------------------------------------------------------------------------
# Helper: Format Indian Rupees
# ---------------------------------------------------------------------------

def fmt_inr(value):
    """Format a number as ₹ with commas (Indian style approximation)."""
    if abs(value) >= 1e7:
        return f"₹{value / 1e7:.2f} Cr"
    elif abs(value) >= 1e5:
        return f"₹{value / 1e5:.2f} L"
    elif abs(value) >= 1e3:
        return f"₹{value / 1e3:.1f}K"
    else:
        return f"₹{value:,.0f}"


def fmt_inr_full(value):
    """Format as full ₹ number."""
    return f"₹{value:,.0f}"


# ---------------------------------------------------------------------------
# Plotly theme defaults
# ---------------------------------------------------------------------------

COLORS = px.colors.qualitative.Set2
TEMPLATE = "plotly_white"


# ===========================================================================
# PAGE: Overview
# ===========================================================================

if page == "🏠 Overview":
    st.markdown("# 🏠 Sales Dashboard — Overview")
    st.markdown("Real-time insights from **10,000 orders** across **500 customers** and **100 products**.")
    st.markdown("---")

    # --- KPIs ---
    kpi = sa.get_kpi_summary().iloc[0]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💰 Total Revenue", fmt_inr(kpi["total_revenue"]))
    k2.metric("📈 Total Profit", fmt_inr(kpi["total_profit"]))
    k3.metric("📦 Total Orders", f"{int(kpi['total_orders']):,}")
    k4.metric("🧾 Avg Order Value", fmt_inr(kpi["avg_order_value"]))
    k5.metric("📊 Profit Margin", f"{kpi['profit_margin_pct']:.1f}%")

    st.markdown("")

    # --- Quick Charts ---
    col1, col2 = st.columns(2)

    # Monthly revenue trend (mini)
    with col1:
        st.markdown("### 📈 Monthly Revenue Trend")
        trend = sa.get_monthly_revenue_trend()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend["month"], y=trend["revenue"],
            mode="lines+markers", name="Revenue",
            line=dict(color="#667eea", width=2.5),
            marker=dict(size=4),
            fill="tozeroy", fillcolor="rgba(102,126,234,0.1)",
        ))
        fig.add_trace(go.Scatter(
            x=trend["month"], y=trend["profit"],
            mode="lines+markers", name="Profit",
            line=dict(color="#f093fb", width=2),
            marker=dict(size=3),
        ))
        fig.update_layout(
            template=TEMPLATE, height=350,
            margin=dict(l=20, r=20, t=30, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_title="", yaxis_title="Amount (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Category breakdown
    with col2:
        st.markdown("### 🏷️ Revenue by Category")
        cat = sa.get_category_performance()
        fig = px.pie(
            cat, values="revenue", names="category",
            color_discrete_sequence=COLORS,
            hole=0.45,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(
            template=TEMPLATE, height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    # Regional split
    with col3:
        st.markdown("### 🗺️ Revenue by Region")
        reg = sa.get_regional_analysis()
        fig = px.bar(
            reg, x="region", y="revenue", color="region",
            color_discrete_sequence=COLORS,
            text_auto=".2s",
        )
        fig.update_layout(
            template=TEMPLATE, height=320,
            margin=dict(l=20, r=20, t=30, b=40),
            showlegend=False,
            xaxis_title="", yaxis_title="Revenue (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top 5 products
    with col4:
        st.markdown("### 🏆 Top 5 Products")
        top5 = sa.get_top_products(5)
        fig = px.bar(
            top5, x="revenue", y="product_name", orientation="h",
            color="category", color_discrete_sequence=COLORS,
            text_auto=".2s",
        )
        fig.update_layout(
            template=TEMPLATE, height=320,
            margin=dict(l=20, r=20, t=30, b=40),
            yaxis=dict(autorange="reversed"),
            xaxis_title="Revenue (₹)", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# PAGE: Revenue Trends
# ===========================================================================

elif page == "📈 Revenue Trends":
    st.markdown("# 📈 Revenue Trends")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Monthly Trend", "Month-over-Month Growth", "Quarterly Breakdown", "Seasonality"
    ])

    with tab1:
        trend = sa.get_monthly_revenue_trend()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=trend["month"], y=trend["revenue"], name="Revenue",
                   marker_color="#667eea", opacity=0.7),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=trend["month"], y=trend["profit"], name="Profit",
                       line=dict(color="#f093fb", width=3), mode="lines+markers"),
            secondary_y=True,
        )
        fig.update_layout(
            template=TEMPLATE, height=500, title="Monthly Revenue & Profit",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        fig.update_yaxes(title_text="Revenue (₹)", secondary_y=False)
        fig.update_yaxes(title_text="Profit (₹)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        growth = sa.get_monthly_growth()
        growth_clean = growth.dropna(subset=["growth_pct"])
        fig = go.Figure()
        colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in growth_clean["growth_pct"]]
        fig.add_trace(go.Bar(
            x=growth_clean["month"], y=growth_clean["growth_pct"],
            marker_color=colors, name="Growth %",
            text=[f"{v:+.1f}%" for v in growth_clean["growth_pct"]],
            textposition="outside",
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            template=TEMPLATE, height=500,
            title="Month-over-Month Revenue Growth (%)",
            xaxis_title="", yaxis_title="Growth %",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        qtr = sa.get_quarterly_revenue()
        fig = px.bar(
            qtr, x="quarter_label", y="revenue", color="year",
            barmode="group", text_auto=".2s",
            color_discrete_sequence=COLORS,
        )
        fig.update_layout(
            template=TEMPLATE, height=500,
            title="Quarterly Revenue by Year",
            xaxis_title="", yaxis_title="Revenue (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data table
        with st.expander("📋 Quarterly Data Table"):
            display_qtr = qtr.copy()
            display_qtr["revenue"] = display_qtr["revenue"].apply(fmt_inr_full)
            display_qtr["profit"] = display_qtr["profit"].apply(fmt_inr_full)
            st.dataframe(display_qtr, use_container_width=True, hide_index=True)

    with tab4:
        seasonal = sa.get_seasonal_pattern()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=seasonal["month_name"], y=seasonal["avg_revenue"],
            mode="lines+markers+text",
            line=dict(color="#667eea", width=3),
            marker=dict(size=10, color="#764ba2"),
            text=[fmt_inr(v) for v in seasonal["avg_revenue"]],
            textposition="top center",
            fill="tozeroy", fillcolor="rgba(102,126,234,0.1)",
        ))
        fig.update_layout(
            template=TEMPLATE, height=500,
            title="Seasonal Revenue Pattern (Avg per Month)",
            xaxis_title="", yaxis_title="Avg Revenue (₹)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Insight**: Notice the Diwali spike in October–November and the year-end spike in December, with a dip during summer months (May–June).")


# ===========================================================================
# PAGE: Product Analysis
# ===========================================================================

elif page == "🛍️ Product Analysis":
    st.markdown("# 🛍️ Product Analysis")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Category Performance", "Top Products"])

    with tab1:
        cat = sa.get_category_performance()

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                cat, x="category", y=["revenue", "profit"],
                barmode="group", color_discrete_sequence=["#667eea", "#f093fb"],
                text_auto=".2s",
            )
            fig.update_layout(
                template=TEMPLATE, height=450,
                title="Revenue & Profit by Category",
                xaxis_title="", yaxis_title="Amount (₹)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=cat["category"], y=cat["profit_margin_pct"],
                marker_color=COLORS[:len(cat)],
                text=[f"{v:.1f}%" for v in cat["profit_margin_pct"]],
                textposition="outside",
            ))
            fig.update_layout(
                template=TEMPLATE, height=450,
                title="Profit Margin % by Category",
                xaxis_title="", yaxis_title="Profit Margin %",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Category table
        with st.expander("📋 Category Performance Table"):
            display_cat = cat.copy()
            display_cat["revenue"] = display_cat["revenue"].apply(fmt_inr_full)
            display_cat["profit"] = display_cat["profit"].apply(fmt_inr_full)
            st.dataframe(display_cat, use_container_width=True, hide_index=True)

    with tab2:
        n = st.slider("Number of top products to show", 5, 25, 10)
        top = sa.get_top_products(n)

        fig = px.bar(
            top, x="revenue", y="product_name", orientation="h",
            color="category", color_discrete_sequence=COLORS,
            text_auto=".2s",
        )
        fig.update_layout(
            template=TEMPLATE, height=max(400, n * 35),
            title=f"Top {n} Products by Revenue",
            yaxis=dict(autorange="reversed"),
            xaxis_title="Revenue (₹)", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Top Products Data Table"):
            display_top = top.copy()
            display_top["revenue"] = display_top["revenue"].apply(fmt_inr_full)
            display_top["profit"] = display_top["profit"].apply(fmt_inr_full)
            st.dataframe(display_top, use_container_width=True, hide_index=True)


# ===========================================================================
# PAGE: Regional Analysis
# ===========================================================================

elif page == "🗺️ Regional Analysis":
    st.markdown("# 🗺️ Regional Analysis")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Region Overview", "City-wise Breakdown"])

    with tab1:
        reg = sa.get_regional_analysis()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                reg, values="revenue", names="region",
                color_discrete_sequence=COLORS, hole=0.4,
                title="Revenue Share by Region",
            )
            fig.update_traces(textposition="inside", textinfo="percent+label+value")
            fig.update_layout(template=TEMPLATE, height=420)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Revenue", x=reg["region"], y=reg["revenue"],
                marker_color="#667eea", text=[fmt_inr(v) for v in reg["revenue"]],
                textposition="outside",
            ))
            fig.add_trace(go.Bar(
                name="Profit", x=reg["region"], y=reg["profit"],
                marker_color="#f093fb", text=[fmt_inr(v) for v in reg["profit"]],
                textposition="outside",
            ))
            fig.update_layout(
                template=TEMPLATE, height=420, barmode="group",
                title="Revenue & Profit by Region",
                xaxis_title="", yaxis_title="Amount (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Profit margin comparison
        fig = go.Figure(go.Bar(
            x=reg["region"], y=reg["profit_margin_pct"],
            marker_color=["#2ecc71" if v > 30 else "#f39c12" if v > 25 else "#e74c3c"
                          for v in reg["profit_margin_pct"]],
            text=[f"{v:.1f}%" for v in reg["profit_margin_pct"]],
            textposition="outside",
        ))
        fig.update_layout(
            template=TEMPLATE, height=350,
            title="Profit Margin % by Region",
            xaxis_title="", yaxis_title="Profit Margin %",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        n_cities = st.slider("Number of cities to show", 5, 25, 15)
        cities = sa.get_city_wise_sales(n_cities)

        fig = px.bar(
            cities, x="city", y="revenue", color="state",
            color_discrete_sequence=COLORS,
            text_auto=".2s",
        )
        fig.update_layout(
            template=TEMPLATE, height=500,
            title=f"Top {n_cities} Cities by Revenue",
            xaxis_title="", yaxis_title="Revenue (₹)",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Treemap
        fig = px.treemap(
            cities, path=["state", "city"], values="revenue",
            color="profit", color_continuous_scale="RdYlGn",
            title="City Revenue Treemap (color = profit)",
        )
        fig.update_layout(template=TEMPLATE, height=500)
        st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# PAGE: Customer Insights
# ===========================================================================

elif page == "👥 Customer Insights":
    st.markdown("# 👥 Customer Insights")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Customer Segments", "RFM Analysis"])

    with tab1:
        seg = sa.get_customer_segmentation()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                seg, x="segment", y="revenue", color="segment",
                color_discrete_sequence=COLORS, text_auto=".2s",
            )
            fig.update_layout(
                template=TEMPLATE, height=400,
                title="Revenue by Customer Segment",
                showlegend=False,
                xaxis_title="", yaxis_title="Revenue (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                seg, x="segment", y="avg_revenue_per_customer", color="segment",
                color_discrete_sequence=COLORS, text_auto=".2s",
            )
            fig.update_layout(
                template=TEMPLATE, height=400,
                title="Avg Revenue per Customer by Segment",
                showlegend=False,
                xaxis_title="", yaxis_title="Avg Revenue (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Segment summary table
        with st.expander("📋 Segment Summary Table"):
            display_seg = seg.copy()
            display_seg["revenue"] = display_seg["revenue"].apply(fmt_inr_full)
            display_seg["profit"] = display_seg["profit"].apply(fmt_inr_full)
            display_seg["avg_revenue_per_customer"] = display_seg["avg_revenue_per_customer"].apply(fmt_inr_full)
            st.dataframe(display_seg, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### RFM (Recency, Frequency, Monetary) Customer Segmentation")
        st.markdown(
            "Each customer is scored **1–5** on Recency, Frequency, and Monetary value. "
            "Segments are derived from the combined scores."
        )

        rfm = sa.get_rfm_analysis()

        # Segment distribution
        rfm_seg_counts = rfm["rfm_segment"].value_counts().reset_index()
        rfm_seg_counts.columns = ["Segment", "Count"]

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                rfm_seg_counts, values="Count", names="Segment",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4, title="RFM Segment Distribution",
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(template=TEMPLATE, height=450)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Avg monetary by segment
            rfm_monetary = rfm.groupby("rfm_segment")["monetary"].mean().reset_index()
            rfm_monetary.columns = ["Segment", "Avg Monetary"]
            rfm_monetary = rfm_monetary.sort_values("Avg Monetary", ascending=True)

            fig = px.bar(
                rfm_monetary, x="Avg Monetary", y="Segment", orientation="h",
                color="Avg Monetary", color_continuous_scale="Viridis",
                text_auto=".2s",
            )
            fig.update_layout(
                template=TEMPLATE, height=450,
                title="Avg Monetary Value by RFM Segment",
                xaxis_title="Avg Revenue (₹)", yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

        # RFM Scatter
        st.markdown("### RFM Scatter Plot")
        fig = px.scatter(
            rfm, x="recency_days", y="frequency",
            size="monetary", color="rfm_segment",
            hover_data=["customer_name", "monetary"],
            color_discrete_sequence=px.colors.qualitative.Pastel,
            size_max=25, opacity=0.7,
        )
        fig.update_layout(
            template=TEMPLATE, height=550,
            title="Customers: Recency vs Frequency (size = Monetary Value)",
            xaxis_title="Recency (days since last order)",
            yaxis_title="Frequency (number of orders)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # RFM Table
        with st.expander("📋 Full RFM Customer Table"):
            display_rfm = rfm.copy()
            display_rfm["monetary"] = display_rfm["monetary"].apply(fmt_inr_full)
            st.dataframe(display_rfm, use_container_width=True, hide_index=True, height=400)


# ===========================================================================
# PAGE: Payment & Discounts
# ===========================================================================

elif page == "💳 Payment & Discounts":
    st.markdown("# 💳 Payment Methods & Discount Analysis")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Payment Methods", "Discount Impact"])

    with tab1:
        pay = sa.get_payment_method_analysis()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                pay, values="revenue", names="payment_method",
                color_discrete_sequence=COLORS, hole=0.45,
                title="Revenue by Payment Method",
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(template=TEMPLATE, height=420)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                pay, x="payment_method", y="order_count", color="payment_method",
                color_discrete_sequence=COLORS, text_auto=True,
            )
            fig.update_layout(
                template=TEMPLATE, height=420,
                title="Order Count by Payment Method",
                showlegend=False,
                xaxis_title="", yaxis_title="Orders",
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Payment Method Data"):
            display_pay = pay.copy()
            display_pay["revenue"] = display_pay["revenue"].apply(fmt_inr_full)
            display_pay["profit"] = display_pay["profit"].apply(fmt_inr_full)
            st.dataframe(display_pay, use_container_width=True, hide_index=True)

    with tab2:
        disc = sa.get_discount_impact()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                disc, x="discount_range", y="revenue",
                color="discount_range", color_discrete_sequence=COLORS,
                text_auto=".2s",
            )
            fig.update_layout(
                template=TEMPLATE, height=420,
                title="Revenue by Discount Range",
                showlegend=False,
                xaxis_title="", yaxis_title="Revenue (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=disc["discount_range"], y=disc["profit_margin_pct"],
                marker_color=["#2ecc71" if v > 30 else "#f39c12" if v > 20 else "#e74c3c"
                              for v in disc["profit_margin_pct"]],
                text=[f"{v:.1f}%" for v in disc["profit_margin_pct"]],
                textposition="outside",
            ))
            fig.update_layout(
                template=TEMPLATE, height=420,
                title="Profit Margin % by Discount Range",
                xaxis_title="", yaxis_title="Profit Margin %",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.warning("⚠️ **Insight**: Higher discounts lead to significantly lower profit margins. Orders with 21-30% discount have notably compressed margins compared to no-discount orders.")


# ===========================================================================
# PAGE: Forecasting
# ===========================================================================

elif page == "🔮 Forecasting":
    st.markdown("# 🔮 Revenue Forecasting")
    st.markdown("---")

    forecast_data = sa.get_forecast_data()

    # Simple linear regression for forecasting
    X = forecast_data["month_index"].values
    y = forecast_data["revenue"].values

    # Fit linear trend: y = a + b*x
    n_points = len(X)
    x_mean = X.mean()
    y_mean = y.mean()
    b = np.sum((X - x_mean) * (y - y_mean)) / np.sum((X - x_mean) ** 2)
    a = y_mean - b * x_mean

    # Generate predictions for existing + 6 future months
    future_months = 6
    all_indices = np.arange(1, n_points + future_months + 1)
    predictions = a + b * all_indices

    # Create future month labels
    last_month = pd.to_datetime(forecast_data["month"].iloc[-1] + "-01")
    future_dates = pd.date_range(start=last_month + pd.DateOffset(months=1), periods=future_months, freq="MS")
    future_labels = [d.strftime("%Y-%m") for d in future_dates]
    all_labels = list(forecast_data["month"]) + future_labels

    # Moving average (3-month)
    ma_3 = pd.Series(y).rolling(window=3).mean().values
    # Moving average (6-month)
    ma_6 = pd.Series(y).rolling(window=6).mean().values

    # --- Chart ---
    fig = go.Figure()

    # Actual revenue
    fig.add_trace(go.Scatter(
        x=forecast_data["month"], y=y,
        mode="lines+markers", name="Actual Revenue",
        line=dict(color="#667eea", width=2.5),
        marker=dict(size=5),
    ))

    # 3-month moving average
    fig.add_trace(go.Scatter(
        x=forecast_data["month"], y=ma_3,
        mode="lines", name="3-Month MA",
        line=dict(color="#f39c12", width=2, dash="dot"),
    ))

    # 6-month moving average
    fig.add_trace(go.Scatter(
        x=forecast_data["month"], y=ma_6,
        mode="lines", name="6-Month MA",
        line=dict(color="#e74c3c", width=2, dash="dash"),
    ))

    # Linear trend (full range including forecast)
    fig.add_trace(go.Scatter(
        x=all_labels, y=predictions,
        mode="lines", name="Linear Trend (Forecast)",
        line=dict(color="#2ecc71", width=2.5, dash="dashdot"),
    ))

    # Shade forecast region
    fig.add_vrect(
        x0=forecast_data["month"].iloc[-1], x1=future_labels[-1],
        fillcolor="rgba(46,204,113,0.1)", line_width=0,
        annotation_text="Forecast", annotation_position="top left",
    )

    fig.update_layout(
        template=TEMPLATE, height=550,
        title="Revenue Forecast — Linear Trend + Moving Averages",
        xaxis_title="Month", yaxis_title="Revenue (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Forecast Stats ---
    st.markdown("### 📊 Forecast Summary")

    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("📈 Trend Slope", f"{fmt_inr(b)}/month")
    fc2.metric("🎯 R² (Fit Quality)", f"{1 - np.sum((y - (a + b * X)) ** 2) / np.sum((y - y_mean) ** 2):.3f}")
    fc3.metric("📅 Next Month Est.", fmt_inr(predictions[n_points]))
    fc4.metric("📅 6-Month Est.", fmt_inr(predictions[n_points + future_months - 1]))

    st.info(
        "💡 **Note**: This is a simple linear trend forecast. For production use, "
        "consider ARIMA, Prophet, or machine learning models for better accuracy."
    )

    # Seasonal decomposition insight
    with st.expander("📋 Monthly Forecast Values"):
        forecast_table = pd.DataFrame({
            "Month": future_labels,
            "Forecasted Revenue": [fmt_inr_full(v) for v in predictions[n_points:]],
        })
        st.dataframe(forecast_table, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:0.85rem;'>"
    "📊 Sales Data Analysis Dashboard | Built with Python, SQL, Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True,
)
