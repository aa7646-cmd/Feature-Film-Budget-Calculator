import streamlit as st
import pandas as pd
import plotly.express as px

# Set dark theme and wide layout
st.set_page_config(page_title="VRITHA Budget Dashboard", layout="wide")

st.title("🎬 VRITHA - Film Production Budget Calculator")
st.markdown("Adjust the core variables on the left to see real-time impact on the project runway.")

# Sidebar for controls
st.sidebar.header("Control Panel")
days = st.sidebar.slider("Shoot Days", min_value=20, max_value=40, value=30, step=1)
burn_rate = st.sidebar.slider("Daily Burn Rate (₹)", min_value=100000, max_value=200000, value=125000, step=5000)

st.sidebar.markdown("---")
st.sidebar.subheader("Fixed Costs")
pre_prod = st.sidebar.number_input("Pre-Production (₹)", value=1000000, step=100000)
post_prod = st.sidebar.number_input("Post-Production (₹)", value=3000000, step=100000)
dir_fee = st.sidebar.number_input("Director Fee (₹)", value=300000, step=50000)
cast_fee = st.sidebar.number_input("Total Cast Fee (₹)", value=1000000, step=100000)

# Calculations
production_cost = days * burn_rate
atl_cost = dir_fee + cast_fee
subtotal = production_cost + atl_cost + pre_prod + post_prod
contingency = subtotal * 0.10
total_budget = subtotal + contingency

# Formatting function for metric cards
def format_inr(number):
    return f"₹{number:,.0f}"

# Metric Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Budget (Inc. Contingency)", format_inr(total_budget))
col2.metric("Production Phase (Shoot)", format_inr(production_cost))
col3.metric("Above-The-Line (Cast & Dir)", format_inr(atl_cost))

st.markdown("---")

# Data preparation for the chart
data = {
    "Category": ["Pre-Production", "Production Phase", "Post-Production", "Above-The-Line", "Contingency (10%)"],
    "Cost (₹)": [pre_prod, production_cost, post_prod, atl_cost, contingency]
}
df = pd.DataFrame(data)

# Render Chart
fig = px.bar(df, x="Category", y="Cost (₹)", text_auto='.2s', 
             title="Budget Allocation Breakdown", 
             color="Category", template="plotly_dark")
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
st.plotly_chart(fig, use_container_width=True)
