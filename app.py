import streamlit as st
import pandas as pd
import plotly.express as px

# Set dark theme and wide layout
st.set_page_config(page_title="VRITHA Master Dashboard", layout="wide")

st.title("🎬 VRITHA - Master Budget Dashboard")
st.markdown("Use **Section 1** for major macro estimates. Unlock **Section 2** below to fine-tune individual departments.")

# ==========================================
# THE TOGGLE SWITCH (The Logic Engine)
# ==========================================
use_granular = st.toggle("🔬 UNLOCK SECTION 2: Let Granular Department Sliders Drive the Total Budget", value=False)
st.markdown("---")

# We create empty containers to control the layout order visually
metrics_container = st.container()
charts_container = st.container()
st.markdown("---")
section1_container = st.container()
st.markdown("---")
section2_container = st.container()

# ==========================================
# SECTION 1: MAJOR MACRO SLIDERS
# ==========================================
with section1_container:
    st.header("Section 1: Major Budget Summary & Adjustments")
    
    if not use_granular:
        st.info("📊 MACRO MODE: You are currently driving the budget using these top-level sliders.")
        c1, c2, c3 = st.columns(3)
        with c1:
            days = st.slider("Shoot Days", 20, 40, 30, step=1)
            daily_burn = st.slider("Daily Burn Rate (₹)", 100000, 200000, 125000, step=5000)
        with c2:
            pre_prod = st.slider("Pre-Production (₹)", 500000, 2000000, 1000000, step=100000)
            post_prod = st.slider("Post-Production (₹)", 1500000, 4000000, 3000000, step=100000)
        with c3:
            cast_fee = st.slider("Total Cast Fee (₹)", 500000, 2000000, 1000000, step=100000)
            dir_fee = st.slider("Director Fee (₹)", 100000, 1000000, 300000, step=50000)
            contingency_pct = st.slider("Contingency (%)", 5, 20, 10, step=1)
    else:
        st.success("🔬 GRANULAR MODE: Daily Burn, Pre-Production, and Post-Production are currently locked. They are being calculated by your inputs in Section 2.")
        c1, c2, c3 = st.columns(3)
        with c1:
            days = st.slider("Shoot Days", 20, 40, 30, step=1)
        with c2:
            cast_fee = st.slider("Total Cast Fee (₹)", 500000, 2000000, 1000000, step=100000)
            dir_fee = st.slider("Director Fee (₹)", 100000, 1000000, 300000, step=50000)
        with c3:
            contingency_pct = st.slider("Contingency (%)", 5, 20, 10, step=1)

# ==========================================
# SECTION 2: GRANULAR DEPARTMENT SLIDERS
# ==========================================
with section2_container:
    st.header("Section 2: Granular Department-Wise Adjustments")
    if not use_granular:
        st.caption("🔒 *These sliders are disabled. Toggle the switch at the top of the page to unlock them.*")
        
    g1, g2, g3 = st.columns(3)
    with g1:
        st.subheader("Daily Shoot Costs")
        loc = st.slider("Location/Day", 5000, 30000, 12000, step=1000, disabled=not use_granular)
        crew = st.slider("Crew/Day", 20000, 80000, 40000, step=2000, disabled=not use_granular)
        equip = st.slider("Equipment/Day", 10000, 40000, 18000, step=1000, disabled=not use_granular)
        food = st.slider("Food & Lodging/Day", 10000, 40000, 20000, step=1000, disabled=not use_granular)
        travel = st.slider("Travel & Fuel/Day", 2000, 15000, 5000, step=1000, disabled=not use_granular)
    with g2:
        st.subheader("Pre-Production & SFX")
        pre_base = st.slider("Scouting & Sets", 200000, 1500000, 400000, step=50000, disabled=not use_granular)
        sfx = st.slider("Prosthetics & SFX", 100000, 1000000, 600000, step=50000, disabled=not use_granular)
    with g3:
        st.subheader("Post-Production")
        edit = st.slider("Edit & DI/Color", 200000, 1500000, 800000, step=50000, disabled=not use_granular)
        foley = st.slider("Foley & Sound Design", 200000, 1500000, 800000, step=50000, disabled=not use_granular)
        score = st.slider("Original Score", 100000, 800000, 400000, step=50000, disabled=not use_granular)
        atmos = st.slider("Dolby Atmos Mix", 100000, 800000, 400000, step=50000, disabled=not use_granular)

# ==========================================
# MATH ENGINE (Processes the active inputs)
# ==========================================
if use_granular:
    # Math is driven by Section 2
    calc_daily_burn = loc + crew + equip + food + travel
    calc_prod_phase = calc_daily_burn * days
    calc_pre_prod = pre_base + sfx
    calc_post_prod = edit + foley + score + atmos
else:
    # Math is driven by Section 1
    calc_daily_burn = daily_burn
    calc_prod_phase = daily_burn * days
    calc_pre_prod = pre_prod
    calc_post_prod = post_prod
    
    # Estimate the granular split for visual charts
    loc, crew, equip, food, travel = [int(daily_burn * p) for p in (0.12, 0.45, 0.20, 0.18, 0.05)]
    pre_base, sfx = [int(pre_prod * p) for p in (0.40, 0.60)]
    edit, foley, score, atmos = [int(post_prod * p) for p in (0.35, 0.35, 0.15, 0.15)]

atl_cost = dir_fee + cast_fee
subtotal = calc_prod_phase + calc_pre_prod + calc_post_prod + atl_cost
contingency = subtotal * (contingency_pct / 100.0)
total_budget = subtotal + contingency

def format_inr(number):
    return f"₹{number:,.0f}"

# ==========================================
# 5. TOP SECTION: CHARTS & METRICS
# ==========================================
with metrics_container:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Budget (Inc. Contingency)", format_inr(total_budget))
    m2.metric("Calculated Daily Burn", format_inr(calc_daily_burn))
    m3.metric("Total Production (Shoot)", format_inr(calc_prod_phase))
    m4.metric("Total Post-Production", format_inr(calc_post_prod))

with charts_container:
    chart_col1, chart_col2 = st.columns(2)
    
    # Chart 1: Macro Budget Bar Chart (Replaced Pie Chart)
    df_macro = pd.DataFrame({
        "Category": ["Above-The-Line", "Production Phase", "Pre-Production", "Post-Production", "Contingency"],
        "Cost (₹)": [atl_cost, calc_prod_phase, calc_pre_prod, calc_post_prod, contingency]
    })
    
    # Notice we pass text_auto inside px.bar directly
    fig1 = px.bar(df_macro, x="Category", y="Cost (₹)", text_auto='.2s', 
                  title="Macro Budget Overview", 
                  color="Category", template="plotly_dark")
    
    # Apply rounded edges and clean up the labels
    fig1.update_traces(
        showlegend=False, 
        textfont_size=14, 
        textangle=0, 
        textposition="outside", 
        cliponaxis=False,
        marker_cornerradius=15  # Gives the bars nice rounded edges
    )
    chart_col1.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Granular Department Bar Chart
    df_micro = pd.DataFrame({
        "Department": ["Location", "Crew", "Equipment", "Food/Lodging", "Travel", "Prosthetics", "Edit/DI", "Foley", "Score", "Atmos"],
        "Cost (₹)": [loc*days, crew*days, equip*days, food*days, travel*days, sfx, edit, foley, score, atmos]
    }).sort_values(by="Cost (₹)", ascending=False)
    
    # Fixed the text_auto placement here as well
    fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", text_auto='.2s',
                  title="Granular Department Breakdown", 
                  template="plotly_dark", color="Department")
    
    # Apply rounded edges
    fig2.update_traces(
        showlegend=False, 
        textfont_size=12, 
        textangle=0, 
        textposition="outside", 
        cliponaxis=False,
        marker_cornerradius=10  # Rounded edges for the smaller bars
    )
    chart_col2.plotly_chart(fig2, use_container_width=True)
