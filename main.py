import streamlit as st
import pandas as pd
import plotly.express as px
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide")

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
            st.success(f"Welcome {u} ({st.session_state.role})")
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------
# ROLE-BASED SHEETS
# -----------------------------
def get_allowed_sheets(all_sheets, role):

    if role == "Admin":
        return [s for s in all_sheets if "labour" not in s.lower()]

    elif role == "HR Head":
        return [s for s in all_sheets if s.lower() in ["employee_info", "performance"]]

    elif role == "Finance Head":
        return [s for s in all_sheets if s.lower() in [
            "final_payroll", "earnings", "deductions", "tax", "overtime"
        ]]

    return []

@st.cache_data
def load_sheets(role):
    xls = pd.ExcelFile("final_payroll_with_prediction.xlsx")
    allowed = get_allowed_sheets(xls.sheet_names, role)

    sheets = {}
    for sheet in allowed:
        df = xls.parse(sheet)
        df.columns = [c.strip().lower() for c in df.columns]
        sheets[sheet] = df

    return sheets

sheets = load_sheets(st.session_state.role)

# -----------------------------
# DATA MODEL
# -----------------------------
st.sidebar.header("🔗 Data Model")

sheet_names = list(sheets.keys())

if len(sheet_names) == 0:
    st.error("No sheets available")
    st.stop()

base_sheet = st.sidebar.selectbox("Base Sheet", sheet_names)
base_df = sheets[base_sheet]

join_key = st.sidebar.selectbox("Join Key", base_df.columns)

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
# NAV
# -----------------------------
page = st.sidebar.radio("Navigation", ["Home", "Dashboard"])

st.sidebar.write(f"👤 {st.session_state.username}")
st.sidebar.write(f"🔑 {st.session_state.role}")

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
    # FILTERS
    # -----------------------------
    st.sidebar.header("🎛️ Filters")

    def find_col(keyword):
        for col in data.columns:
            if keyword in col:
                return col
        return None

    for keyword in ["department", "gender", "role", "city"]:
        col = find_col(keyword)
        if col:
            vals = st.sidebar.multiselect(col, data[col].dropna().unique())
            if vals:
                data = data[data[col].isin(vals)]

    # -----------------------------
    # CHART BUILDER
    # -----------------------------
    cols = list(data.columns)

    if len(cols) == 0:
        st.warning("No data available")
        st.stop()

    x = st.selectbox("X-axis", cols)
    y = st.selectbox("Y-axis", ["None"] + cols)

    chart = st.selectbox("Chart Type", ["Bar", "Line", "Pie", "Histogram"])
    agg = st.selectbox("Aggregation", ["Mean", "Sum", "Median", "Count"])

    def aggregate(df, x, y, agg):
        if y == "None":
            return df

        if agg == "Mean":
            return df.groupby(x)[y].mean().reset_index()
        elif agg == "Sum":
            return df.groupby(x)[y].sum().reset_index()
        elif agg == "Median":
            return df.groupby(x)[y].median().reset_index()
        elif agg == "Count":
            return df.groupby(x)[y].count().reset_index()

    # -----------------------------
    # ADD CHART
    # -----------------------------
    if st.button("➕ Add Chart"):

        plot_df = aggregate(data, x, y, agg)

        if chart == "Bar":
            fig = px.bar(plot_df, x=x, y=None if y == "None" else y)

        elif chart == "Line":
            fig = px.line(plot_df, x=x, y=None if y == "None" else y)

        elif chart == "Pie":
            fig = px.pie(data, names=x)

        elif chart == "Histogram":
            fig = px.histogram(data, x=x)

        # 🔥 DARK THEME FIX
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#2A2E39"),
            yaxis=dict(gridcolor="#2A2E39")
        )

        st.session_state.charts.append(fig)

    # -----------------------------
    # DISPLAY
    # -----------------------------
    st.subheader("Dashboard")

    for fig in st.session_state.charts:
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑 Clear Charts"):
        st.session_state.charts = []

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
            fig.write_image(path, engine="kaleido", scale=2)
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