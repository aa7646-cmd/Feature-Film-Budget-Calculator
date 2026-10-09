import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="VRITHA Master Dashboard", layout="wide")

# ==========================================
# URL SYNC HELPERS & FORMATTING
# ==========================================
def url_slider(label, min_v, max_v, default_v, step, param, disabled=False):
    if param in st.query_params:
        default_v = int(st.query_params[param])
    # format="₹%,d" adds the currency and commas directly into the slider track
    val = st.slider(label, min_v, max_v, default_v, step=step, disabled=disabled, format="₹%,d")
    st.query_params[param] = val
    return val

def url_toggle(label, default_v, param):
    if param in st.query_params:
        default_v = str(st.query_params[param]).lower() == "true"
    val = st.toggle(label, value=default_v)
    st.query_params[param] = val
    return val

def format_inr(number):
    if int(number) == 0:
        return "Upon Negotiation"
        
    num_str = str(int(number))
    if len(num_str) <= 3:
        return f"₹{num_str}"
    last_three = num_str[-3:]
    remaining = num_str[:-3]
    remaining_with_commas = ",".join([remaining[max(i-2, 0):i] for i in range(len(remaining), 0, -2)][::-1])
    return f"₹{remaining_with_commas},{last_three}"

# ==========================================
# HEADER: TITLE & TOP-RIGHT EXPORT BUTTONS
# ==========================================
header_container = st.container()
with header_container:
    title_col, empty_col, btn_col1, btn_col2 = st.columns([4, 1, 1.5, 1.5])
    with title_col:
        st.title("🎬 Budget - Master Dashboard")
        st.markdown("Set variables, then **copy the URL** to share this exact calculation.")

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
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            days = url_slider("Shoot Days", 1, 100, 30, 1, "m_days")
            daily_burn = url_slider("Daily Burn (Excl. Crew)", 0, 5000000, 85000, 5000, "m_burn")
            macro_crew = url_slider("Total Crew Cost (₹)", 0, 20000000, 1200000, 50000, "m_crew")
        with c2:
            pre_prod = url_slider("Pre-Production (₹)", 0, 50000000, 1000000, 50000, "m_pre")
            post_prod = url_slider("Post-Production (₹)", 0, 50000000, 3000000, 50000, "m_post")
        with c3:
            cast_fee = url_slider("Total Cast Fee (₹)", 0, 50000000, 0, 50000, "m_cast")
            dir_fee = url_slider("Director Fee (₹)", 0, 20000000, 0, 50000, "m_dir")
        with c4:
            marketing = url_slider("Marketing & PR (₹)", 0, 20000000, 500000, 50000, "m_mkt")
            contingency_pct = url_slider("Contingency (%)", 0, 30, 10, 1, "m_cont")
    else:
        st.success("🔬 GRANULAR MODE: Daily Burn, Crew, and Pre/Post are locked. They are being calculated by Section 2.")
        c1, c2, c3 = st.columns(3)
        with c1:
            days = url_slider("Shoot Days", 1, 100, 30, 1, "m_days")
        with c2:
            cast_fee = url_slider("Total Cast Fee (₹)", 0, 50000000, 0, 50000, "m_cast")
            dir_fee = url_slider("Director Fee (₹)", 0, 20000000, 0, 50000, "m_dir")
        with c3:
            contingency_pct = url_slider("Contingency (%)", 0, 30, 10, 1, "m_cont")

# ==========================================
# SECTION 2: GRANULAR DEPARTMENT SLIDERS
# ==========================================
with section2_container:
    st.header("Section 2: Granular Department Adjustments")
    if not use_granular:
        st.caption("🔒 *These sliders are disabled. Toggle the switch at the top to unlock them.*")
        
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.subheader("Daily Costs")
        loc = url_slider("Location/Day", 0, 1000000, 12000, 1000, "g_loc", not use_granular)
        crew = url_slider("Crew/Day", 0, 2000000, 40000, 2000, "g_crew", not use_granular)
        equip = url_slider("Equipment/Day", 0, 1000000, 18000, 1000, "g_eq", not use_granular)
        food = url_slider("Food & Lodging/Day", 0, 1000000, 20000, 1000, "g_food", not use_granular)
        travel = url_slider("Travel/Day", 0, 500000, 5000, 1000, "g_trav", not use_granular)
    with g2:
        st.subheader("Pre-Production")
        pre_base = url_slider("Scouting & Sets", 0, 20000000, 400000, 50000, "g_pre", not use_granular)
        sfx = url_slider("Prosthetics & SFX", 0, 20000000, 600000, 50000, "g_sfx", not use_granular)
    with g3:
        st.subheader("Post-Production")
        edit = url_slider("Edit & DI/Color", 0, 20000000, 800000, 50000, "g_edit", not use_granular)
        foley = url_slider("Foley & Sound Design", 0, 20000000, 800000, 50000, "g_fol", not use_granular)
        score = url_slider("Original Score", 0, 20000000, 400000, 50000, "g_sco", not use_granular)
        atmos = url_slider("Dolby Atmos Mix", 0, 20000000, 400000, 50000, "g_atm", not use_granular)
    with g4:
        st.subheader("Marketing")
        marketing_g = url_slider("Marketing & PR", 0, 20000000, 500000, 50000, "g_mkt", not use_granular)

# ==========================================
# MATH ENGINE
# ==========================================
if use_granular:
    calc_total_crew = crew * days
    calc_daily_burn = loc + equip + food + travel  # Excludes crew
    calc_prod_phase = calc_daily_burn * days
    calc_pre_prod = pre_base + sfx
    calc_post_prod = edit + foley + score + atmos
    calc_mkt = marketing_g
else:
    calc_total_crew = macro_crew
    calc_daily_burn = daily_burn
    calc_prod_phase = daily_burn * days
    calc_pre_prod = pre_prod
    calc_post_prod = post_prod
    calc_mkt = marketing
    
    # Estimate the granular split for visual charts
    loc, equip, food, travel = [int(daily_burn * p) for p in (0.22, 0.38, 0.30, 0.10)]
    crew = int(macro_crew / days) if days > 0 else 0
    pre_base, sfx = [int(pre_prod * p) for p in (0.40, 0.60)]
    edit, foley, score, atmos = [int(post_prod * p) for p in (0.35, 0.35, 0.15, 0.15)]

atl_cost = dir_fee + cast_fee
subtotal = calc_prod_phase + calc_total_crew + calc_pre_prod + calc_post_prod + calc_mkt + atl_cost
contingency = subtotal * (contingency_pct / 100.0)
total_budget = subtotal + contingency

# ==========================================
# RENDER METRICS & CHARTS
# ==========================================
with metrics_container:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Budget (Inc. Contingency)", format_inr(total_budget))
    m2.metric("Total Crew Cost", format_inr(calc_total_crew))
    m3.metric("Director Fee", format_inr(dir_fee))
    m4.metric("Total Cast Fee", format_inr(cast_fee))

with charts_container:
    chart_col1, chart_col2 = st.columns(2)
    
    df_macro = pd.DataFrame({
        "Category": ["Above-The-Line", "Total Crew", "Production", "Pre-Production", "Post-Production", "Marketing", "Contingency"],
        "Cost (₹)": [atl_cost, calc_total_crew, calc_prod_phase, calc_pre_prod, calc_post_prod, calc_mkt, contingency]
    })
    
    # Filter out 0 values so they don't clog up the chart
    df_macro = df_macro[df_macro["Cost (₹)"] > 0]
    
    fig1 = px.bar(df_macro, x="Category", y="Cost (₹)", text=df_macro["Cost (₹)"].apply(format_inr), 
                  title="Macro Budget Overview", color="Category", template="plotly_dark")
    fig1.update_traces(showlegend=False, textfont_size=14, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=15)
    chart_col1.plotly_chart(fig1, use_container_width=True)

    df_micro = pd.DataFrame({
        "Department": ["Location", "Crew", "Equipment", "Food", "Travel", "Prosthetics", "Edit/DI", "Foley", "Score", "Atmos", "Marketing"],
        "Cost (₹)": [loc*days, calc_total_crew, equip*days, food*days, travel*days, sfx, edit, foley, score, atmos, calc_mkt]
    }).sort_values(by="Cost (₹)", ascending=False)
    
    df_micro = df_micro[df_micro["Cost (₹)"] > 0]
    
    fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", text=df_micro["Cost (₹)"].apply(format_inr),
                  title="Granular Department Breakdown", color="Department", template="plotly_dark")
    fig2.update_traces(showlegend=False, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=10)
    chart_col2.plotly_chart(fig2, use_container_width=True)

# ==========================================
# GENERATE EXPORTS & INJECT INTO TOP RIGHT
# ==========================================
export_data = {
    "Phase": ["Above-The-Line", "Above-The-Line", "Production", "Production", "Production", "Production", "Production", "Pre-Production", "Pre-Production", "Post-Production", "Post-Production", "Post-Production", "Post-Production", "Distribution", "Contingency", "TOTAL BUDGET"],
    "Department": ["Director Fee", "Cast Fee", "Location", "Crew", "Equipment", "Food & Lodging", "Travel & Fuel", "Scouting & Sets", "Prosthetics & SFX", "Edit & DI/Color", "Foley & Sound", "Original Score", "Dolby Atmos Mix", "Marketing & PR", f"Contingency ({contingency_pct}%)", "ALL DEPARTMENTS"],
    "Cost (INR)": [dir_fee, cast_fee, loc*days, calc_total_crew, equip*days, food*days, travel*days, pre_base, sfx, edit, foley, score, atmos, calc_mkt, contingency, total_budget]
}
df_export = pd.DataFrame(export_data)

csv_data = df_export.to_csv(index=False).encode('utf-8')

def create_pdf(dataframe, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "VRITHA - Feature Film Budget Top Sheet", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    
    safe_total = format_inr(total).replace("₹", "Rs. ")
    pdf.cell(0, 10, f"Total Approved Budget: {safe_total}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(50, 10, "Phase", border=1, fill=True, align='C')
    pdf.cell(80, 10, "Department", border=1, fill=True, align='C')
    pdf.cell(60, 10, "Allocated Cost", border=1, ln=True, fill=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    for i in range(len(dataframe)):
        if dataframe.iloc[i]['Phase'] == "TOTAL BUDGET":
            pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 10, str(dataframe.iloc[i]['Phase']), border=1)
        pdf.cell(80, 10, str(dataframe.iloc[i]['Department']), border=1)
        
        safe_cost = format_inr(dataframe.iloc[i]['Cost (INR)']).replace("₹", "Rs. ")
        pdf.cell(60, 10, safe_cost, border=1, ln=True, align='R')
        
    try:
        return bytes(pdf.output(dest='S'), 'latin1')
    except:
        return bytes(pdf.output(dest='S'))

pdf_data = create_pdf(df_export, total_budget)

with btn_col1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("📊 CSV Export", data=csv_data, file_name="vritha_budget.csv", mime="text/csv", use_container_width=True)

with btn_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("📄 PDF Export", data=pdf_data, file_name="vritha_topsheet.pdf", mime="application/pdf", use_container_width=True)
