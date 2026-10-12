import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="VRITHA Master Dashboard", layout="wide")

# ==========================================
# URL SYNC HELPERS & SMART FORMATTING
# ==========================================
def url_slider(label, min_v, max_v, default_v, step, param, format_str="₹%,d"):
    if param in st.query_params:
        default_v = int(st.query_params[param])
    val = st.slider(label, min_v, max_v, default_v, step=step, format=format_str)
    st.query_params[param] = val
    return val

def url_toggle(label, default_v, param):
    if param in st.query_params:
        default_v = str(st.query_params[param]).lower() == "true"
    val = st.toggle(label, value=default_v)
    st.query_params[param] = val
    return val

def format_inr(number, is_talent=False):
    if int(number) == 0 and is_talent:
        return "Upon Negotiation"
    elif int(number) == 0:
        return "₹0"
        
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
section_breakdown = st.container()
section2_container = st.container()

# ==========================================
# SECTION 1: BASE BUDGET (Primary Drivers)
# ==========================================
with section1_container:
    st.header("Section 1: Base Budget Allocations")
    st.info("💡 **Calculator Mode:** These are your primary budget drivers.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        m_days = url_slider("Shoot Days", 1, 100, 30, 1, "m_days", "%d")
        m_burn = url_slider("Base Daily Burn (₹)", 0, 5000000, 85000, 5000, "m_burn")
    with c2:
        m_pre = url_slider("Base Pre-Production (₹)", 0, 50000000, 1000000, 50000, "m_pre")
        m_post = url_slider("Base Post-Production (₹)", 0, 50000000, 3000000, 50000, "m_post")
    with c3:
        m_dir = url_slider("Director Fee (₹)", 0, 20000000, 0, 50000, "m_dir")
        m_lead = url_slider("Main Lead Fee (₹)", 0, 50000000, 0, 50000, "m_lead")
        m_cast = url_slider("Supporting Cast Fee (₹)", 0, 20000000, 0, 50000, "m_cast")
    with c4:
        m_crew = url_slider("Base Crew Cost (Lump Sum)", 0, 20000000, 1200000, 50000, "m_crew")
        m_cont = url_slider("Contingency Buffer (%)", 0, 30, 10, 1, "m_cont", "%d%%")

# ==========================================
# TENTATIVE BREAKDOWN SECTION
# ==========================================
with section_breakdown:
    st.markdown("---")
    st.subheader("📊 Tentative Department Breakdown")
    st.warning("⚠️ **TENTATIVE FIGURES:** These are auto-calculated industry averages based on your Base Allocations above. They are strictly estimates for visualization, not actual final quotes.")

    est_col1, est_col2, est_col3 = st.columns(3)
    with est_col1:
        st.markdown(f"**Daily Burn (Based on {format_inr(m_burn)}/day):**")
        st.markdown(f"- **Camera/Grip/Eq (35%):** {format_inr(m_burn * 0.35)}")
        st.markdown(f"- **Locations (15%):** {format_inr(m_burn * 0.15)}")
        st.markdown(f"- **Food/Crafty (20%):** {format_inr(m_burn * 0.20)}")
        st.markdown(f"- **Travel/Transpo (10%):** {format_inr(m_burn * 0.10)}")
        st.markdown(f"- **Misc/Art (20%):** {format_inr(m_burn * 0.20)}")
    with est_col2:
        st.markdown(f"**Pre-Production (Based on {format_inr(m_pre)}):**")
        st.markdown(f"- **Scouting & Sets (40%):** {format_inr(m_pre * 0.40)}")
        st.markdown(f"- **Prosthetics & SFX (60%):** {format_inr(m_pre * 0.60)}")
    with est_col3:
        st.markdown(f"**Post-Production (Based on {format_inr(m_post)}):**")
        st.markdown(f"- **Edit & DI (35%):** {format_inr(m_post * 0.35)}")
        st.markdown(f"- **Sound Design/Foley (35%):** {format_inr(m_post * 0.35)}")
        st.markdown(f"- **Original Score (15%):** {format_inr(m_post * 0.15)}")
        st.markdown(f"- **Atmos Mix (15%):** {format_inr(m_post * 0.15)}")

# ==========================================
# SECTION 2: GRANULAR ADD-ONS (Toggleable)
# ==========================================
with section2_container:
    st.markdown("---")
    show_granular = url_toggle("🔬 Show Granular Add-on Adjustments", False, "show_gran")
    
    g_loc = g_crew = g_eq = g_food = g_trav = 0
    g_pre = g_sfx = 0
    g_edit = g_fol = g_sco = g_atm = 0
    
    if show_granular:
        st.caption("Amounts selected here will automatically be added on top of the base amounts.")
        g1, g2, g3 = st.columns(3)
        with g1:
            st.subheader("Daily Production Add-ons")
            g_loc = url_slider("Extra Location/Day", 0, 1000000, 0, 1000, "g_loc")
            g_eq = url_slider("Extra Equipment/Day", 0, 1000000, 0, 1000, "g_eq")
            g_food = url_slider("Extra Food/Day", 0, 1000000, 0, 1000, "g_food")
            g_trav = url_slider("Extra Travel/Day", 0, 500000, 0, 1000, "g_trav")
        with g2:
            st.subheader("Pre-Prod & Crew Add-ons")
            g_pre = url_slider("Extra Sets/Scouting", 0, 20000000, 0, 50000, "g_pre")
            g_sfx = url_slider("Extra SFX/Prosthetics", 0, 20000000, 0, 50000, "g_sfx")
            g_crew = url_slider("Extra Crew/Day", 0, 200000, 0, 2000, "g_crew")
        with g3:
            st.subheader("Post-Production Add-ons")
            g_edit = url_slider("Extra Edit & DI", 0, 20000000, 0, 50000, "g_edit")
            g_fol = url_slider("Extra Foley/Sound", 0, 20000000, 0, 50000, "g_fol")
            g_sco = url_slider("Extra Score", 0, 20000000, 0, 50000, "g_sco")
            g_atm = url_slider("Extra Atmos Mix", 0, 20000000, 0, 50000, "g_atm")

# ==========================================
# ADDITIVE MATH ENGINE
# ==========================================
calc_cast_crew = m_dir + m_lead + m_cast + m_crew + (g_crew * m_days)

calc_daily_burn = m_burn + g_loc + g_eq + g_food + g_trav
calc_prod_phase = calc_daily_burn * m_days

calc_pre_prod = m_pre + g_pre + g_sfx
calc_post_prod = m_post + g_edit + g_fol + g_sco + g_atm

subtotal = calc_prod_phase + calc_cast_crew + calc_pre_prod + calc_post_prod
contingency = subtotal * (m_cont / 100.0)
total_budget = subtotal + contingency

# ==========================================
# EXPORTS (CSV / PDF) - EXECUTIVE SUMMARY MODE
# ==========================================
export_data = {
    "Project Phase": ["Pre-Production", "Production", "Post-Production", "Cast & Crew (Inc. Director/Lead)", f"Contingency ({m_cont}%)", "FINAL TOTAL BUDGET"],
    "Total Allocated Cost": [
        format_inr(calc_pre_prod), 
        format_inr(calc_prod_phase), 
        format_inr(calc_post_prod), 
        format_inr(calc_cast_crew, is_talent=True), 
        format_inr(contingency), 
        format_inr(total_budget)
    ]
}
df_export = pd.DataFrame(export_data)
csv_data = df_export.to_csv(index=False).encode('utf-8')

def create_pdf(dataframe, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "VRITHA - Executive Budget Top Sheet", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    
    pdf.ln(10)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Project Phase", border=1, fill=True, align='L')
    pdf.cell(90, 10, "Total Allocated Cost", border=1, ln=True, fill=True, align='R')
    
    pdf.set_font("Arial", '', 12)
    for i in range(len(dataframe)):
        if dataframe.iloc[i]['Project Phase'] == "FINAL TOTAL BUDGET":
            pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 12, str(dataframe.iloc[i]['Project Phase']), border=1)
        
        safe_cost = dataframe.iloc[i]['Total Allocated Cost'].replace("₹", "Rs. ")
        pdf.cell(90, 12, safe_cost, border=1, ln=True, align='R')
        
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
        st.download_button("📊 CSV Export", data=csv_data, file_name="vritha_executive_budget.csv", mime="text/csv", use_container_width=True)
    with btn_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📄 PDF Export", data=pdf_data, file_name="vritha_executive_topsheet.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# POPULATE TOP METRICS (6 Columns Ordered)
# ==========================================
with metrics_container:
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        st.metric("💰 TOTAL BUDGET", format_inr(total_budget))
        st.caption("Includes all phases + Contingency.")
        
    with m2:
        st.metric("⏱️ Daily Shoot Cost", format_inr(calc_daily_burn))
        st.caption("Varies per schedule. Loc, gear, food, misc.")
        
    with m3:
        st.metric("📝 Total Pre-Production", format_inr(calc_pre_prod))
        st.caption("Scouting, set builds, prosthetics, SFX.")
        
    with m4:
        st.metric("🎥 Total Production", format_inr(calc_prod_phase))
        st.caption("Principal photography, locations, gear, food.")
        
    with m5:
        st.metric("🎬 Total Post-Production", format_inr(calc_post_prod))
        st.caption("Editing, DI, Foley, original score, Atmos.")
        
    with m6:
        st.metric("🎭 Cast & Crew Totals", format_inr(calc_cast_crew, is_talent=True))
        st.caption("Director, acting talent, base & extra crew.")

# ==========================================
# POPULATE LOCKED CHARTS
# ==========================================
with charts_container:
    chart_col1, chart_col2 = st.columns([1, 1])
    
    df_macro = pd.DataFrame({
        "Category": ["Production", "Pre-Production", "Post-Production", "Contingency"],
        "Cost (₹)": [calc_prod_phase, calc_pre_prod, calc_post_prod, contingency]
    })
    if calc_cast_crew > 0:
        df_macro.loc[len(df_macro)] = ["Cast & Crew", calc_cast_crew]
        
    df_macro = df_macro[df_macro["Cost (₹)"] > 0]
    
    fig1 = px.bar(df_macro, x="Category", y="Cost (₹)", text=df_macro["Cost (₹)"].apply(lambda x: format_inr(x)), 
                  title="Macro Budget Overview", color="Category", template="plotly_dark")
    fig1.update_layout(dragmode=False)
    fig1.update_xaxes(fixedrange=True)
    fig1.update_yaxes(fixedrange=True)
    fig1.update_traces(showlegend=False, textfont_size=14, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=15)
    chart_col1.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    df_micro = pd.DataFrame({
        "Department": ["Director/Lead", "Base Crew", "Base Prod", "Location/Gear", "Base Pre-Prod", "SFX & Sets", "Base Post-Prod", "Score/Audio"],
        "Cost (₹)": [m_dir+m_lead+m_cast, m_crew+(g_crew*m_days), m_burn*m_days, (g_loc+g_eq)*m_days, m_pre, g_pre+g_sfx, m_post, g_edit+g_fol+g_sco+g_atm]
    }).sort_values(by="Cost (₹)", ascending=False)
    
    df_micro = df_micro[df_micro["Cost (₹)"] > 0]
    
    fig2 = px.bar(df_micro, x="Department", y="Cost (₹)", text=df_micro["Cost (₹)"].apply(lambda x: format_inr(x)),
                  title="Granular Source Breakdown", color="Department", template="plotly_dark")
    fig2.update_layout(dragmode=False)
    fig2.update_xaxes(fixedrange=True)
    fig2.update_yaxes(fixedrange=True)
    fig2.update_traces(showlegend=False, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_cornerradius=10)
    chart_col2.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
