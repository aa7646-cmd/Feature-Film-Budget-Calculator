import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="VRITHA Master Dashboard", layout="wide")

# ==========================================
# URL SYNC HELPERS & FORMATTING
# ==========================================
def url_slider(label, min_v, max_v, default_v, step, param, format_str="₹%,d"):
    if param in st.query_params:
        default_v = int(st.query_params[param])
    val = st.slider(label, min_v, max_v, default_v, step=step, format=format_str)
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
# LAYOUT CONTAINERS 
# ==========================================
header_container = st.container()
st.markdown("---")
metrics_container = st.container()
st.markdown("---")
charts_container = st.container()
st.markdown("---")
section1_container = st.container()
st.markdown("---")
section2_container = st.container()

# ==========================================
# SECTIONS 1 & 2: ALL SLIDERS ACTIVE
# ==========================================
with section1_container:
    st.header("Section 1: Major Budget Summary (Base Allocations)")
    st.info("💡 **Calculator Mode:** All sliders are active. These base amounts will add together with your granular adjustments below to create the final totals.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # %d removes the Rupee symbol for days
        m_days = url_slider("Shoot Days", 1, 100, 30, 1, "m_days", "%d")
        m_burn = url_slider("Base Daily Burn (₹)", 0, 5000000, 85000, 5000, "m_burn")
        m_crew = url_slider("Base Crew Cost (Lump Sum)", 0, 20000000, 1200000, 50000, "m_crew")
    with c2:
        m_pre = url_slider("Base Pre-Production (₹)", 0, 50000000, 1000000, 50000, "m_pre")
        m_post = url_slider("Base Post-Production (₹)", 0, 50000000, 3000000, 50000, "m_post")
    with c3:
        m_cast = url_slider("Total Cast Fee (₹)", 0, 50000000, 0, 50000, "m_cast")
        m_dir = url_slider("Director Fee (₹)", 0, 20000000, 0, 50000, "m_dir")
    with c4:
        m_mkt = url_slider("Base Marketing & PR (₹)", 0, 20000000, 500000, 50000, "m_mkt")
        # %d%% formats as a percentage
        m_cont = url_slider("Contingency Buffer (%)", 0, 30, 10, 1, "m_cont", "%d%%")

with section2_container:
    st.header("Section 2: Granular Department Adjustments")
    st.caption("These specific line items will add directly on top of the base amounts in Section 1.")
        
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.subheader("Daily Costs")
        g_loc = url_slider("Location/Day", 0, 1000000, 12000, 1000, "g_loc")
        g_crew = url_slider("Crew/Day", 0, 2000000, 40000, 2000, "g_crew")
        g_eq = url_slider("Equipment/Day", 0, 1000000, 18000, 1000, "g_eq")
        g_food = url_slider("Food & Lodging/Day", 0, 1000000, 20000, 1000, "g_food")
        g_trav = url_slider("Travel/Day", 0, 500000, 5000, 1000, "g_trav")
    with g2:
        st.subheader("Pre-Production")
        g_pre = url_slider("Scouting & Sets", 0, 20000000, 400000, 50000, "g_pre")
        g_sfx = url_slider("Prosthetics & SFX", 0, 20000000, 600000, 50000, "g_sfx")
    with g3:
        st.subheader("Post-Production")
        g_edit = url_slider("Edit & DI/Color", 0, 20000000, 800000, 50000, "g_edit")
        g_fol = url_slider("Foley & Sound Design", 0, 20000000, 800000, 50000, "g_fol")
        g_sco = url_slider("Original Score", 0, 20000000, 400000, 50000, "g_sco")
        g_atm = url_slider("Dolby Atmos Mix", 0, 20000000, 400000, 50000, "g_atm")
    with g4:
        st.subheader("Marketing")
        g_mkt = url_slider("Marketing Add-on", 0, 20000000, 0, 50000, "g_mkt2")

# ==========================================
# ADDITIVE MATH ENGINE (Unrestricted)
# ==========================================
# 1. Cast & Crew
calc_total_crew = m_crew + (g_crew * m_days)
calc_cast_crew = m_cast + m_dir + calc_total_crew

# 2. Production (Base burn + Granular daily items)
calc_daily_burn = m_burn + g_loc + g_eq + g_food + g_trav
calc_prod_phase = calc_daily_burn * m_days

# 3. Pre & Post Production
calc_pre_prod = m_pre + g_pre + g_sfx
calc_post_prod = m_post + g_edit + g_fol + g_sco + g_atm

# 4. Marketing
calc_total_mkt = m_mkt + g_mkt

# 5. Grand Totals
subtotal = calc_prod_phase + calc_cast_crew + calc_pre_prod + calc_post_prod + calc_total_mkt
contingency = subtotal * (m_cont / 100.0)
total_budget = subtotal + contingency

# ==========================================
# EXPORTS (CSV / PDF) & HEADER INJECTION
# ==========================================
export_data = {
    "Phase": ["Cast & Crew", "Cast & Crew", "Cast & Crew", "Production", "Production", "Production", "Production", "Production", "Pre-Production", "Pre-Production", "Pre-Production", "Post-Production", "Post-Production", "Post-Production", "Post-Production", "Post-Production", "Distribution", "Distribution", "Contingency", "TOTAL BUDGET"],
    "Department": ["Director Fee", "Cast Fee", "Total Crew (Base + Daily)", "Base Daily Burn (Total)", "Locations (Total)", "Equipment (Total)", "Food & Lodging (Total)", "Travel & Fuel (Total)", "Base Pre-Production", "Scouting & Sets", "Prosthetics & SFX", "Base Post-Production", "Edit & DI/Color", "Foley & Sound", "Original Score", "Dolby Atmos Mix", "Base Marketing & PR", "Marketing Add-on", f"Contingency ({m_cont}%)", "ALL DEPARTMENTS"],
    "Cost (INR)": [m_dir, m_cast, calc_total_crew, m_burn*m_days, g_loc*m_days, g_eq*m_days, g_food*m_days, g_trav*m_days, m_pre, g_pre, g_sfx, m_post, g_edit, g_fol, g_sco, g_atm, m_mkt, g_mkt, contingency, total_budget]
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

with header_container:
    title_col, empty_col, btn_col1, btn_col2 = st.columns([4, 1, 1.5, 1.5])
    with title_col:
        st.title("🎬 VRITHA - Master Dashboard")
        st.markdown("Set variables, then **copy the URL** to share this exact calculation.")
    with btn_col1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📊 CSV Export", data=csv_data, file_name="vritha_budget.csv", mime="text/csv", use_container_width=True)
    with btn_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📄 PDF Export", data=pdf_data, file_name="vritha_topsheet.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# POPULATE TOP METRICS (5 Columns Ordered)
# ==========================================
with metrics_container:
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.metric("💰 TOTAL BUDGET", format_inr(total_budget))
        st.caption("Includes all phases + Contingency buffer.")
        
    with m2:
        st.metric("📝 Total Pre-Production Cost", format_inr(calc_pre_prod))
        st.caption("Includes scouting, set builds, prosthetics, SFX & base pre-prod.")
        
    with m3:
        st.metric("🎥 Total Production Cost", format_inr(calc_prod_phase))
        st.caption("Principal photography, locations, gear, food, travel & base daily burn.")
        
    with m4:
        st.metric("🎬 Total Post-Production Cost", format_inr(calc_post_prod))
        st.caption("Editing, DI, Foley, original score, Atmos & base post-prod.")
        
    with m5:
        st.metric("🎭 Total Cost for Cast & Crew", format_inr(calc_cast_crew))
        st.caption("Director, acting talent, base crew & granular crew day-rates.")

# ==========================================
# POPULATE LOCKED CHARTS
# ==========================================
with charts_container:
    chart_col1, chart_col2 = st.columns(2)
    
    df_macro = pd.DataFrame({
        "Category": ["Cast & Crew", "Production", "Pre-Production", "Post-Production", "Marketing", "Contingency"],
        "Cost (₹)": [calc_cast_crew, calc_prod_phase, calc_pre_prod, calc_post_prod, calc_total_mkt, contingency]
    })
    df_macro = df_macro[df_macro["Cost (₹)"] > 0]
    
    fig1 = px.bar(df_macro, x="Category", y="Cost (₹)", text=df_macro["Cost (₹)"].apply(format_inr), 
                  title="Macro Budget Overview", color="Category", template="plotly_dark")
    fig1.update_layout(dragmode=False)
    fig1.update_xaxes(fixedrange=True)
    fig1.update_yaxes(fixedrange=True)
    fig1.update_traces(showlegend=False, textfont_size=14, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=15)
    chart_col1.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    # Detailed departmental breakdown
    df_micro = pd.DataFrame({
        "Department": ["Director", "Cast", "Crew (Total)", "Base Prod", "Location", "Equipment", "Food", "Travel", "Base Pre-Prod", "SFX & Sets", "Base Post-Prod", "Score/Audio", "Marketing"],
        "Cost (₹)": [m_dir, m_cast, calc_total_crew, m_burn*m_days, g_loc*m_days, g_eq*m_days, g_food*m_days, g_trav*m_days, m_pre, g_pre+g_sfx, m_post, g_edit+g_fol+g_sco+g_atm, calc_total_mkt]
    }).sort_values(by="Cost (₹)", ascending=False)
    
    df_micro = df_micro[df_micro["Cost (₹)"] > 0]
    
    fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", text=df_micro["Cost (₹)"].apply(format_inr),
                  title="Granular Item Breakdown", color="Department", template="plotly_dark")
    fig2.update_layout(dragmode=False)
    fig2.update_xaxes(fixedrange=True)
    fig2.update_yaxes(fixedrange=True)
    fig2.update_traces(showlegend=False, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=10)
    chart_col2.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
