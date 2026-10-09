import streamlit as st
import pandas as pd
import plotly.express as px

# Set dark theme and wide layout
st.set_page_config(page_title="VRITHA Budget Dashboard", layout="wide")

st.title("🎬 VRITHA - Film Production Budget Calculator")
st.markdown("Adjust the macro variables in the sidebar and the granular variables at the bottom to see real-time impact.")

# ==========================================
# 1. SIDEBAR (Core Fixed Variables)
# ==========================================
st.sidebar.header("Core Variables")
days = st.sidebar.slider("Shoot Days", min_value=20, max_value=40, value=30, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Above-The-Line")
dir_fee = st.sidebar.number_input("Director Fee (₹)", value=300000, step=50000)
cast_fee = st.sidebar.number_input("Total Cast Fee (₹)", value=1000000, step=100000)

contingency_pct = st.sidebar.slider("Contingency Buffer (%)", 5, 20, 10, step=1)

# ==========================================
# 2. CREATE LAYOUT CONTAINERS
# ==========================================
# We define containers so we can render the sliders at the bottom, 
# but still use their math to draw the charts at the top.
dashboard_container = st.container()
st.markdown("---")
controls_container = st.container()

# ==========================================
# 3. BOTTOM SECTION: GRANULAR SLIDERS
# ==========================================
with controls_container:
    st.header("Granular Department Controls")
    
    col_sliders1, col_sliders2 = st.columns(2)
    
    with col_sliders1:
        st.subheader("Daily Shoot Costs")
        st.caption("These amounts multiply by your Shoot Days.")
        loc_day = st.slider("Location Charges / Day", 5000, 30000, 12000, step=1000)
        crew_day = st.slider("Crew Charges / Day", 20000, 80000, 40000, step=2000)
        equip_day = st.slider("Equipment Charges / Day", 10000, 40000, 18000, step=1000)
        food_day = st.slider("Food & Lodging / Day", 10000, 40000, 20000, step=1000)
        travel_day = st.slider("Travel & Fuel / Day", 2000, 15000, 5000, step=1000)
        
    with col_sliders2:
        st.subheader("Pre/Post-Production Add-ons")
        st.caption("These are lump-sum fixed costs.")
        base_pre = st.slider("Base Pre-Production (Scouting, Sets)", 200000, 1500000, 400000, step=50000)
        prosthetics = st.slider("Prosthetics & SFX", 100000, 1000000, 600000, step=50000)
        
        base_post = st.slider("Base Post (Editing & Color/DI)", 300000, 1500000, 800000, step=50000)
        foley = st.slider("Foley & Sound Design", 200000, 1500000, 800000, step=50000)
        music = st.slider("Original Score (Music)", 100000, 800000, 400000, step=50000)
        atmos = st.slider("Dolby Atmos Mix", 100000, 800000, 400000, step=50000)

# ==========================================
# 4. THE MATH (Calculated from sliders)
# ==========================================
daily_burn = loc_day + crew_day + equip_day + food_day + travel_day
total_production = daily_burn * days

total_pre = base_pre + prosthetics
total_post = base_post + foley + music + atmos
atl_cost = dir_fee + cast_fee

subtotal = total_production + total_pre + total_post + atl_cost
contingency = subtotal * (contingency_pct / 100.0)
total_budget = subtotal + contingency

def format_inr(number):
    return f"₹{number:,.0f}"

# ==========================================
# 5. TOP SECTION: CHARTS & METRICS
# ==========================================
with dashboard_container:
    # Top Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Budget (Inc. Contingency)", format_inr(total_budget))
    c2.metric("Calculated Daily Burn", format_inr(daily_burn))
    c3.metric("Total Production (Shoot)", format_inr(total_production))
    c4.metric("Total Post-Production", format_inr(total_post))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Original Bar Chart Logic
    df_macro = pd.DataFrame({
        "Category": ["Pre-Production", "Production Phase", "Post-Production", "Director Fee", "Cast Fee"],
        "Cost (₹)": [total_pre, total_production, total_post, dir_fee, cast_fee]
    })
    
    fig = px.bar(df_macro, x="Category", y="Cost (₹)", text_auto='.2s', 
                 title="Macro Budget Allocation", 
                 color="Category", template="plotly_dark")
    fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
