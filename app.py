import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="VRITHA Master Dashboard", layout="wide")

# ==========================================
# URL SYNC HELPERS (Saves state to the web address)
# ==========================================
def url_slider(label, min_v, max_v, default_v, step, param, disabled=False):
    # Check if this specific slider has a saved value in the URL
    if param in st.query_params:
        default_v = int(st.query_params[param])
    # Create the slider
    val = st.slider(label, min_v, max_v, default_v, step=step, disabled=disabled)
    # Update the URL with the new value
    st.query_params[param] = val
    return val

def url_toggle(label, default_v, param):
    if param in st.query_params:
        default_v = str(st.query_params[param]).lower() == "true"
    val = st.toggle(label, value=default_v)
    st.query_params[param] = val
    return val

st.title("🎬 VRITHA - Master Budget Dashboard")
st.markdown("Set your variables, then **copy the URL from your browser's address bar** to share this exact calculation.")

# ==========================================
# THE TOGGLE SWITCH
# ==========================================
use_granular = url_toggle("🔬 UNLOCK SECTION 2: Let Granular Department Sliders Drive the Total Budget", False, "granular_mode")
st.markdown("---")

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
    st.header("Section 1: Major Budget Summary")
    
    if not use_granular:
        st.info("📊 MACRO MODE: You are currently driving the budget using these top-level sliders.")
        c1, c2, c3 = st.columns(3)
        with c1:
            days = url_slider("Shoot Days", 20, 40, 30, 1, "m_days")
            daily_burn = url_slider("Daily Burn Rate (₹)", 100000, 200000, 125000, 5000, "m_burn")
        with c2:
            pre_prod = url_slider("Pre-Production (₹)", 500000, 2000000, 1000000, 100000, "m_pre")
            post_prod = url_slider("Post-Production (₹)", 1500000, 4000000, 3000000, 100000, "m_post")
        with c3:
            cast_fee = url_slider("Total Cast Fee (₹)", 500000, 2000000, 1000000, 100000, "m_cast")
            dir_fee = url_slider("Director Fee (₹)", 100000, 1000000, 300000, 50000, "m_dir")
            contingency_pct = url_slider("Contingency (%)", 5, 20, 10, 1, "m_cont")
    else:
        st.success("🔬 GRANULAR MODE: Daily Burn, Pre-Production, and Post-Production are currently locked. They are being calculated by your inputs in Section 2.")
        c1, c2, c3 = st.columns(3)
        with c1:
            days = url_slider("Shoot Days", 20, 40, 30, 1, "m_days")
        with c2:
            cast_fee = url_slider("Total Cast Fee (₹)", 500000, 2000000, 1000000, 100000, "m_cast")
            dir_fee = url_slider("Director Fee (₹)", 100000, 1000000, 300000, 50000, "m_dir")
        with c3:
            contingency_pct = url_slider("Contingency (%)", 5, 20, 10, 1, "m_cont")

# ==========================================
# SECTION 2: GRANULAR DEPARTMENT SLIDERS
# ==========================================
with section2_container:
    st.header("Section 2: Granular Department Adjustments")
    if not use_granular:
        st.caption("🔒 *These sliders are disabled. Toggle the switch at the top to unlock them.*")
        
    g1, g2, g3 = st.columns(3)
    with g1:
        st.subheader("Daily Shoot Costs")
        loc = url_slider("Location/Day", 5000, 30000, 12000, 1000, "g_loc", not use_granular)
        crew = url_slider("Crew/Day", 20000, 80000, 40000, 2000, "g_crew", not use_granular)
        equip = url_slider("Equipment/Day", 10000, 40000, 18000, 1000, "g_eq", not use_granular)
        food = url_slider("Food & Lodging/Day", 10000, 40000, 20000, 1000, "g_food", not use_granular)
        travel = url_slider("Travel/Day", 2000, 15000, 5000, 1000, "g_trav", not use_granular)
    with g2:
        st.subheader("Pre-Production & SFX")
        pre_base = url_slider("Scouting & Sets", 200000, 1500000, 400000, 50000, "g_pre", not use_granular)
        sfx = url_slider("Prosthetics & SFX", 100000, 1000000, 600000, 50000, "g_sfx", not use_granular)
    with g3:
        st.subheader("Post-Production")
        edit = url_slider("Edit & DI/Color", 200000, 1500000, 800000, 50000, "g_edit", not use_granular)
        foley = url_slider("Foley & Sound Design", 200000, 1500000, 800000, 50000, "g_fol", not use_granular)
        score = url_slider("Original Score", 100000, 800000, 400000, 50000, "g_sco", not use_granular)
        atmos = url_slider("Dolby Atmos Mix", 100000, 800000, 400000, 50000, "g_atm", not use_granular)

# ==========================================
# MATH ENGINE
# ==========================================
if use_granular:
    calc_daily_burn = loc + crew + equip + food + travel
    calc_prod_phase = calc_daily_burn * days
    calc_pre_prod = pre_base + sfx
    calc_post_prod = edit + foley + score + atmos
else:
    calc_daily_burn = daily_burn
    calc_prod_phase = daily_burn * days
    calc_pre_prod = pre_prod
    calc_post_prod = post_prod
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
# RENDER METRICS & CHARTS
# ==========================================
with metrics_container:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Budget (Inc. Contingency)", format_inr(total_budget))
    m2.metric("Calculated Daily Burn", format_inr(calc_daily_burn))
    m3.metric("Total Production (Shoot)", format_inr(calc_prod_phase))
    m4.metric("Total Post-Production", format_inr(calc_post_prod))

with charts_container:
    chart_col1, chart_col2 = st.columns(2)
    
    # Chart 1: Macro Budget Bar
    df_macro = pd.DataFrame({
        "Category": ["Above-The-Line", "Production Phase", "Pre-Production", "Post-Production", "Contingency"],
        "Cost (₹)": [atl_cost, calc_prod_phase, calc_pre_prod, calc_post_prod, contingency]
    })
    fig1 = px.bar(df_macro, x="Category", y="Cost (₹)", text_auto='.2s', 
                  title="Macro Budget Overview", color="Category", template="plotly_dark")
    fig1.update_traces(showlegend=False, textfont_size=14, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=15)
    chart_col1.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Granular Breakdown Bar
    df_micro = pd.DataFrame({
        "Department": ["Location", "Crew", "Equipment", "Food", "Travel", "Prosthetics", "Edit/DI", "Foley", "Score", "Atmos"],
        "Cost (₹)": [loc*days, crew*days, equip*days, food*days, travel*days, sfx, edit, foley, score, atmos]
    }).sort_values(by="Cost (₹)", ascending=False)
    
    fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", text_auto='.2s',
                  title="Granular Department Breakdown", color="Department", template="plotly_dark")
    fig2.update_traces(showlegend=False, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=10)
    chart_col2.plotly_chart(fig2, use_container_width=True)
