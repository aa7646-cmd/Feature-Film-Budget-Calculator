import streamlit as st
import pandas as pd
import plotly.express as px

# Set dark theme and wide layout
st.set_page_config(page_title="VRITHA Budget Dashboard", layout="wide")

st.title("🎬 VRITHA - Detailed Budget Calculator")
st.markdown("Adjust the granular variables below to see the real-time impact on your macro and micro budget allocations.")

# Sidebar for Core/Top-Level Controls
st.sidebar.header("Core Variables")
days = st.sidebar.slider("Shoot Days", min_value=20, max_value=40, value=30, step=1)
st.sidebar.markdown("---")
st.sidebar.subheader("Above-The-Line (Fixed)")
dir_fee = st.sidebar.number_input("Director Fee (₹)", value=300000, step=50000)
cast_fee = st.sidebar.number_input("Total Cast Fee (₹)", value=1000000, step=100000)

# Main Body: Granular Sliders
st.markdown("### Granular Department Controls")
col_sliders1, col_sliders2 = st.columns(2)

with col_sliders1:
    st.subheader("Daily Production Costs")
    st.caption("These values are multiplied by your Shoot Days automatically.")
    loc_day = st.slider("Location Charges / Day", 5000, 30000, 12000, step=1000)
    crew_day = st.slider("Crew Charges / Day", 20000, 80000, 40000, step=2000)
    equip_day = st.slider("Equipment Charges / Day", 10000, 40000, 18000, step=1000)
    food_day = st.slider("Food & Lodging / Day", 10000, 40000, 20000, step=1000)
    travel_day = st.slider("Travel & Fuel / Day", 2000, 15000, 5000, step=1000)

with col_sliders2:
    st.subheader("Fixed Departmental Costs")
    st.caption("These are one-time project fees.")
    prosthetics = st.slider("Prosthetics & SFX", 100000, 1000000, 600000, step=50000)
    foley = st.slider("Foley & Sound Design", 200000, 1500000, 800000, step=50000)
    music = st.slider("Original Score (Music)", 100000, 800000, 400000, step=50000)
    atmos = st.slider("Dolby Atmos Mix", 100000, 800000, 400000, step=50000)
    contingency_pct = st.slider("Contingency Buffer (%)", 5, 20, 10, step=1)

# Calculations
daily_burn = loc_day + crew_day + equip_day + food_day + travel_day
total_production = daily_burn * days
total_post = music + atmos + foley
total_art_sfx = prosthetics
atl_cost = dir_fee + cast_fee

subtotal = total_production + total_post + total_art_sfx + atl_cost
contingency = subtotal * (contingency_pct / 100.0)
total_budget = subtotal + contingency

# Formatting function for metric cards
def format_inr(number):
    return f"₹{number:,.0f}"

# Metric Cards Panel
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Budget (Inc. Contingency)", format_inr(total_budget))
c2.metric("Calculated Daily Burn", format_inr(daily_burn))
c3.metric("Total Post-Production", format_inr(total_post))
c4.metric("Total Production Phase", format_inr(total_production))

st.markdown("---")

# Visual Charts Section
chart_col1, chart_col2 = st.columns(2)

# Chart 1: Macro Budget Allocation (Pie Chart)
df_macro = pd.DataFrame({
    "Category": ["Above-The-Line", "Production (Shoot)", "Art & SFX", "Post-Production", "Contingency"],
    "Cost (₹)": [atl_cost, total_production, total_art_sfx, total_post, contingency]
})
fig1 = px.pie(df_macro, values="Cost (₹)", names="Category", title="Macro Budget Overview", 
              template="plotly_dark", hole=0.4)
fig1.update_traces(textposition='inside', textinfo='percent+label')
chart_col1.plotly_chart(fig1, use_container_width=True)

# Chart 2: Micro Departmental Breakdown (Bar Chart)
df_micro = pd.DataFrame({
    "Department": ["Location", "Crew", "Equipment", "Food/Lodging", "Travel", "Prosthetics", "Music", "Atmos", "Foley/Sound"],
    "Cost (₹)": [loc_day*days, crew_day*days, equip_day*days, food_day*days, travel_day*days, prosthetics, music, atmos, foley]
})
# Sort by highest cost for better visual hierarchy
df_micro = df_micro.sort_values(by="Cost (₹)", ascending=False)

fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", title="Granular Departmental Breakdown", 
              template="plotly_dark", color="Department")
fig2.update_traces(text_auto='.2s', showlegend=False, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
chart_col2.plotly_chart(fig2, use_container_width=True)
