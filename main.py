import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide")

# -----------------------------
# 🔥 CUSTOM SIDEBAR STYLING
# -----------------------------
st.markdown("""
<style>

/* Sidebar background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f2430, #2b2f3a);
    color: white;
}

/* Section card */
.sidebar-card {
    background: #0e1117;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}

/* Headings */
.sidebar-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}

/* Dropdown styling */
div[data-baseweb="select"] {
    background-color: #0e1117 !important;
    border-radius: 10px !important;
}

/* Radio buttons */
div[role="radiogroup"] {
    padding: 10px;
    border-radius: 10px;
    background: #0e1117;
}

/* User info */
.user-info {
    padding: 10px;
    border-radius: 10px;
    background: #0e1117;
    margin-top: 10px;
}

/* Remove default padding */
.css-1d391kg {
    padding-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# USERS
# -----------------------------
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "HR_head": {"password": "hrhead123", "role": "HR Head"},
    "Finance_head": {"password": "financehead123", "role": "Finance Head"},
}

# -----------------------------
# SESSION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "charts" not in st.session_state:
    st.session_state.charts = []

# -----------------------------
# LOGIN
# -----------------------------
def login():
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.role = USERS[u]["role"]
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_sheets():
    xls = pd.ExcelFile("final_payroll_with_prediction.xlsx")
    sheets = {}
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        df.columns = [c.strip().lower() for c in df.columns]
        sheets[sheet] = df
    return sheets

sheets = load_sheets()

# -----------------------------
# SIDEBAR UI (🔥 NEW PANEL)
# -----------------------------
st.sidebar.markdown('<div class="sidebar-title">🔗 Data Model</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)

sheet_names = list(sheets.keys())
base_sheet = st.sidebar.selectbox("Base Sheet", sheet_names)
base_df = sheets[base_sheet]

join_key = st.sidebar.selectbox("Join Key", base_df.columns)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# NAVIGATION
# -----------------------------
st.sidebar.markdown('<div class="sidebar-title">📌 Navigation</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)

page = st.sidebar.radio("", ["Home", "Dashboard"])

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# USER INFO
# -----------------------------
st.sidebar.markdown(f"""
<div class="user-info">
👤 {st.session_state.username}<br>
🔑 {st.session_state.role}
</div>
""", unsafe_allow_html=True)

# -----------------------------
# DATA MERGE
# -----------------------------
def merge_all():
    df = base_df.copy()
    df.columns = [f"{base_sheet}.{c}" for c in df.columns]

    for sheet, temp in sheets.items():
        if sheet == base_sheet:
            continue

        if join_key not in temp.columns:
            continue

        temp = temp.copy()
        temp.columns = [f"{sheet}.{c}" for c in temp.columns]

        df = df.merge(
            temp,
            left_on=f"{base_sheet}.{join_key}",
            right_on=f"{sheet}.{join_key}",
            how="left"
        )

    return df

df = merge_all()

# -----------------------------
# HOME
# -----------------------------
if page == "Home":
    st.title("📊 Payroll BI Dashboard")

# -----------------------------
# DASHBOARD
# -----------------------------
elif page == "Dashboard":

    st.title("📈 Dashboard Builder")

    data = df.copy()

    # -----------------------------
    # FILTER PANEL (🔥 Styled)
    # -----------------------------
    st.sidebar.markdown('<div class="sidebar-title">🎛 Filters</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)

    for col in data.columns:
        if any(k in col for k in ["department", "gender", "role", "city"]):
            vals = st.sidebar.multiselect(col, data[col].dropna().unique())
            if vals:
                data = data[data[col].isin(vals)]

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # CHART BUILDER
    # -----------------------------
    cols = list(data.columns)

    x = st.selectbox("X-axis", cols)
    y = st.selectbox("Y-axis", ["None"] + cols)
    chart = st.selectbox("Chart Type", ["Bar", "Line", "Pie", "Histogram"])

    if st.button("➕ Add Chart"):

        color_seq = px.colors.qualitative.Bold

        if chart == "Bar":
            fig = px.bar(data, x=x, y=None if y == "None" else y,
                         color=x, color_discrete_sequence=color_seq)

        elif chart == "Line":
            fig = px.line(data, x=x, y=None if y == "None" else y,
                          color=x, color_discrete_sequence=color_seq)

        elif chart == "Pie":
            fig = px.pie(data, names=x,
                         color_discrete_sequence=color_seq)

        elif chart == "Histogram":
            fig = px.histogram(data, x=x,
                               color_discrete_sequence=color_seq)

        # Force colors
        for i, trace in enumerate(fig.data):
            trace.marker.color = color_seq[i % len(color_seq)]

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white")
        )

        st.session_state.charts.append(fig)

    # -----------------------------
    # DISPLAY
    # -----------------------------
    for fig in st.session_state.charts:
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # PDF EXPORT
    # -----------------------------
    def generate_pdf():

        doc = SimpleDocTemplate("report.pdf")
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Dashboard Report", styles['Title']))
        elements.append(Spacer(1, 20))

        img_paths = []

        for i, fig in enumerate(st.session_state.charts):

            path = f"chart_{i}.png"

            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="black")
            )

            pio.write_image(fig, path, scale=3, width=1200, height=700)

            img_paths.append(path)

        for path in img_paths:
            elements.append(Image(path, width=500, height=300))
            elements.append(Spacer(1, 20))

        doc.build(elements)

        for path in img_paths:
            os.remove(path)

    if st.button("📥 Download Report"):
        generate_pdf()

        with open("report.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="dashboard_report.pdf")