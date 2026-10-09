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
    val = st.slider(label, min_v, max_v, default_v, step=step, disabled=disabled)
    st.query_params[param] = val
    return val

def url_toggle(label, default_v, param):
    if param in st.query_params:
        default_v = str(st.query_params[param]).lower() == "true"
    val = st.toggle(label, value=default_v)
    st.query_params[param] = val
    return val

def format_inr(number):
    num_str = str(int(number))
    if len(num_str) <= 3:
        return f"₹{num_str}"
    last_three = num_str[-3:]
    remaining = num_str[:-3]
    remaining_with_commas = ",".join([remaining[max(i-2, 0):i] for i in range(len(remaining), 0, -2)][::-1])
    return f"₹{remaining_with_commas},{last_three}"

st.title("🎬 VRITHA - Master Budget Dashboard")
st.markdown("Set your variables, then **copy the URL from your browser's address bar** to share this exact calculation.")

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
            days = url_slider("Shoot Days", 1, 100, 30, 1, "m_days")
            daily_burn = url_slider("Daily Burn Rate (₹)", 0, 5000000, 125000, 5000, "m_burn")
        with c2:
            pre_prod = url_slider("Pre-Production (₹)", 0, 50000000, 1000000, 50000, "m_pre")
            post_prod = url_slider("Post-Production (₹)", 0, 50000000, 3000000, 50000, "m_post")
        with c3:
            cast_fee = url_slider("Total Cast Fee (₹)", 0, 50000000, 1000000, 50000, "m_cast")
            dir_fee = url_slider("Director Fee (₹)", 0, 20000000, 300000, 50000, "m_dir")
            contingency_pct = url_slider("Contingency (%)", 0, 30, 10, 1, "m_cont")
    else:
        st.success("🔬 GRANULAR MODE: Daily Burn, Pre-Production, and Post-Production are currently locked. They are being calculated by your inputs in Section 2.")
        c1, c2, c3 = st.columns(3)
        with c1:
            days = url_slider("Shoot Days", 1, 100, 30, 1, "m_days")
        with c2:
            cast_fee = url_slider("Total Cast Fee (₹)", 0, 50000000, 1000000, 50000, "m_cast")
            dir_fee = url_slider("Director Fee (₹)", 0, 20000000, 300000, 50000, "m_dir")
        with c3:
            contingency_pct = url_slider("Contingency (%)", 0, 30, 10, 1, "m_cont")

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
        loc = url_slider("Location/Day", 0, 1000000, 12000, 1000, "g_loc", not use_granular)
        crew = url_slider("Crew/Day", 0, 2000000, 40000, 2000, "g_crew", not use_granular)
        equip = url_slider("Equipment/Day", 0, 1000000, 18000, 1000, "g_eq", not use_granular)
        food = url_slider("Food & Lodging/Day", 0, 1000000, 20000, 1000, "g_food", not use_granular)
        travel = url_slider("Travel/Day", 0, 500000, 5000, 1000, "g_trav", not use_granular)
    with g2:
        st.subheader("Pre-Production & SFX")
        pre_base = url_slider("Scouting & Sets", 0, 20000000, 400000, 50000, "g_pre", not use_granular)
        sfx = url_slider("Prosthetics & SFX", 0, 20000000, 600000, 50000, "g_sfx", not use_granular)
    with g3:
        st.subheader("Post-Production")
        edit = url_slider("Edit & DI/Color", 0, 20000000, 800000, 50000, "g_edit", not use_granular)
        foley = url_slider("Foley & Sound Design", 0, 20000000, 800000, 50000, "g_fol", not use_granular)
        score = url_slider("Original Score", 0, 20000000, 400000, 50000, "g_sco", not use_granular)
        atmos = url_slider("Dolby Atmos Mix", 0, 20000000, 400000, 50000, "g_atm", not use_granular)

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
    
    df_macro = pd.DataFrame({
        "Category": ["Above-The-Line", "Production Phase", "Pre-Production", "Post-Production", "Contingency"],
        "Cost (₹)": [atl_cost, calc_prod_phase, calc_pre_prod, calc_post_prod, contingency]
    })
    fig1 = px.bar(df_macro, x="Category", y="Cost (₹)", text=df_macro["Cost (₹)"].apply(format_inr), 
                  title="Macro Budget Overview", color="Category", template="plotly_dark")
    fig1.update_traces(showlegend=False, textfont_size=14, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=15)
    chart_col1.plotly_chart(fig1, use_container_width=True)

    df_micro = pd.DataFrame({
        "Department": ["Location", "Crew", "Equipment", "Food", "Travel", "Prosthetics", "Edit/DI", "Foley", "Score", "Atmos"],
        "Cost (₹)": [loc*days, crew*days, equip*days, food*days, travel*days, sfx, edit, foley, score, atmos]
    }).sort_values(by="Cost (₹)", ascending=False)
    
    fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", text=df_micro["Cost (₹)"].apply(format_inr),
                  title="Granular Department Breakdown", color="Department", template="plotly_dark")
    fig2.update_traces(showlegend=False, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=10)
    chart_col2.plotly_chart(fig2, use_container_width=True)

# ==========================================
# EXPORT TO CSV & PDF
# ==========================================
st.markdown("---")
st.subheader("📥 Export Your Adjusted Budget")

# Data preparation
export_data = {
    "Phase": ["Above-The-Line", "Above-The-Line", "Production", "Production", "Production", "Production", "Production", "Pre-Production", "Pre-Production", "Post-Production", "Post-Production", "Post-Production", "Post-Production", "Contingency", "TOTAL BUDGET"],
    "Department": ["Director Fee", "Cast Fee", "Location", "Crew", "Equipment", "Food & Lodging", "Travel & Fuel", "Scouting & Sets", "Prosthetics & SFX", "Edit & DI/Color", "Foley & Sound", "Original Score", "Dolby Atmos Mix", f"Contingency ({contingency_pct}%)", "ALL DEPARTMENTS"],
    "Cost (INR)": [dir_fee, cast_fee, loc*days, crew*days, equip*days, food*days, travel*days, pre_base, sfx, edit, foley, score, atmos, contingency, total_budget]
}
df_export = pd.DataFrame(export_data)

# CSV Generation
csv_data = df_export.to_csv(index=False).encode('utf-8')

# PDF Generation Function
def create_pdf(dataframe, total):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "VRITHA - Feature Film Budget Top Sheet", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Total Approved Budget: {format_inr(total)}", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(50, 10, "Phase", border=1, fill=True, align='C')
    pdf.cell(80, 10, "Department", border=1, fill=True, align='C')
    pdf.cell(60, 10, "Allocated Cost (INR)", border=1, ln=True, fill=True, align='C')
    
    # Table Rows
    pdf.set_font("Arial", '', 10)
    for i in range(len(dataframe)):
        # Make the final Total row bold
        if dataframe.iloc[i]['Phase'] == "TOTAL BUDGET":
            pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 10, str(dataframe.iloc[i]['Phase']), border=1)
        pdf.cell(80, 10, str(dataframe.iloc[i]['Department']), border=1)
        pdf.cell(60, 10, format_inr(dataframe.iloc[i]['Cost (INR)']), border=1, ln=True, align='R')
        
    # Return as bytes so Streamlit can download it
    return bytes(pdf.output(dest='S'), 'latin1')

pdf_data = create_pdf(df_export, total_budget)

# Render the download buttons side-by-side
dl_col1, dl_col2 = st.columns(2)
with dl_col1:
    st.download_button(
        label="📊 Download CSV (Spreadsheet)",
        data=csv_data,
        file_name="vritha_budget_export.csv",
        mime="text/csv",
        use_container_width=True
    )
with dl_col2:
    st.download_button(
        label="📄 Download PDF (Fine Print)",
        data=pdf_data,
        file_name="vritha_budget_topsheet.pdf",
        mime="application/pdf",
        use_container_width=True
    )
