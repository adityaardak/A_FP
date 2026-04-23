from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


APP_TITLE = "Payroll Command Studio"
DATA_FILE = Path(__file__).with_name("final_payroll_with_prediction.xlsx")
PBIX_FILE = Path(__file__).with_name("Final Dashboard.pbix")
POWER_BI_EMBED_URL = (
    "https://app.powerbi.com/reportEmbed"
    "?reportId=b53701f5-a0af-4687-8b8c-c0ff1b9ccc3d"
    "&autoAuth=true"
    "&ctid=aed43286-0f66-47d6-942b-d31a4b8addca"
)


THEME = {
    "page": "#F4F7FB",
    "panel": "#FFFFFF",
    "panel_alt": "#F9FBFD",
    "border": "#DCE6F2",
    "heading": "#173A63",
    "text": "#31465F",
    "muted": "#6A7D94",
    "teal": "#179B97",
    "green": "#2E9F62",
    "amber": "#D5901F",
    "red": "#C84B4B",
}


st.set_page_config(page_title=APP_TITLE, layout="wide")


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
            html, body, [class*="css"] {{
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            .stApp {{
                background: {THEME["page"]};
                color: {THEME["text"]};
            }}
            [data-testid="stHeader"], #MainMenu, footer {{
                display: none;
            }}
            .block-container {{
                max-width: 1420px;
                padding-top: 1.1rem;
                padding-bottom: 1.8rem;
            }}
            .hero {{
                background: {THEME["panel"]};
                border: 1px solid {THEME["border"]};
                border-radius: 18px;
                padding: 1.2rem 1.35rem;
                margin-bottom: 1rem;
            }}
            .hero-title {{
                color: {THEME["heading"]};
                font-size: 2rem;
                font-weight: 800;
                margin: 0;
            }}
            .hero-subtitle {{
                color: {THEME["muted"]};
                font-size: 0.98rem;
                line-height: 1.6;
                margin-top: 0.35rem;
                max-width: 950px;
            }}
            .side-panel, .dashboard-panel, .feature-panel {{
                background: {THEME["panel"]};
                border: 1px solid {THEME["border"]};
                border-radius: 18px;
                padding: 1rem;
                box-shadow: 0 8px 24px rgba(20, 42, 67, 0.05);
            }}
            .feature-panel {{
                margin-top: 1rem;
            }}
            .section-label {{
                color: {THEME["muted"]};
                font-size: 0.74rem;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }}
            .section-title {{
                color: {THEME["heading"]};
                font-size: 1.08rem;
                font-weight: 700;
                margin-bottom: 0.3rem;
            }}
            .section-copy {{
                color: {THEME["muted"]};
                font-size: 0.92rem;
                line-height: 1.58;
                margin-bottom: 0.85rem;
            }}
            .active-page {{
                background: #EDF7F7;
                border: 1px solid #CFECEA;
                color: {THEME["teal"]};
                border-radius: 12px;
                padding: 0.55rem 0.7rem;
                font-size: 0.9rem;
                font-weight: 700;
                margin-top: 0.6rem;
            }}
            .metric-card {{
                background: {THEME["panel_alt"]};
                border: 1px solid {THEME["border"]};
                border-radius: 16px;
                padding: 0.95rem 1rem;
                min-height: 108px;
            }}
            .metric-label {{
                color: {THEME["muted"]};
                font-size: 0.76rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
            .metric-value {{
                color: {THEME["heading"]};
                font-size: 1.45rem;
                font-weight: 800;
                margin-top: 0.35rem;
            }}
            .metric-sub {{
                color: {THEME["muted"]};
                font-size: 0.9rem;
                margin-top: 0.3rem;
                line-height: 1.5;
            }}
            .employee-check {{
                background: {THEME["panel_alt"]};
                border: 1px solid {THEME["border"]};
                border-radius: 16px;
                padding: 1rem;
            }}
            .check-line {{
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                padding: 0.5rem 0;
                border-bottom: 1px solid {THEME["border"]};
            }}
            .check-line:last-child {{
                border-bottom: none;
            }}
            .decision-box {{
                margin-top: 0.75rem;
                padding: 0.8rem 0.9rem;
                background: #F7FAFD;
                border: 1px solid {THEME["border"]};
                border-radius: 12px;
                color: {THEME["heading"]};
                font-weight: 600;
            }}
            .info-card {{
                background: {THEME["panel_alt"]};
                border: 1px solid {THEME["border"]};
                border-radius: 16px;
                padding: 1rem;
                height: 100%;
            }}
            .info-title {{
                color: {THEME["heading"]};
                font-size: 0.98rem;
                font-weight: 700;
                margin-bottom: 0.6rem;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.55rem 1rem;
            }}
            .info-line {{
                padding: 0.3rem 0;
            }}
            .info-key {{
                color: {THEME["muted"]};
                font-size: 0.73rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                margin-bottom: 0.05rem;
            }}
            .info-value {{
                color: {THEME["text"]};
                font-size: 0.95rem;
                font-weight: 600;
                line-height: 1.45;
            }}
            .summary-strip {{
                margin-top: 1rem;
                padding: 0.95rem 1rem;
                border-radius: 14px;
                border: 1px solid {THEME["border"]};
                background: #F7FAFD;
                color: {THEME["heading"]};
                font-weight: 700;
                font-size: 0.97rem;
            }}
            div.stButton > button {{
                width: 100%;
                justify-content: flex-start;
                border-radius: 12px;
                border: 1px solid {THEME["border"]};
                background: {THEME["panel"]};
                color: {THEME["heading"]};
                font-weight: 600;
                min-height: 2.8rem;
            }}
            div.stButton > button:hover {{
                border-color: #B8DAD7;
                background: #F4FBFB;
                color: {THEME["heading"]};
            }}
            .stSelectbox label {{
                color: {THEME["muted"]} !important;
                font-size: 0.76rem !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_column_name(value: object) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return re.sub(r"_+", "_", cleaned).strip("_")


def format_currency(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"Rs. {float(value):,.2f}"


def numeric_value(value: object) -> float:
    if pd.isna(value):
        return 0.0
    return float(value)


def severity_from_variance(expected: float, actual: float, relative_threshold: float = 0.02) -> str:
    variance = abs(actual - expected)
    base = max(abs(expected), 1.0)
    ratio = variance / base
    if ratio >= 0.15:
        return "High"
    if ratio >= relative_threshold:
        return "Medium"
    return "Low"


def status_color(status: str) -> str:
    if status in {"Correct", "Compliant"}:
        return THEME["green"]
    if status == "Warning":
        return THEME["amber"]
    return THEME["red"]


def prefix_sheet_columns(sheet_name: str, frame: pd.DataFrame) -> pd.DataFrame:
    prefix = normalize_column_name(sheet_name)
    renamed = frame.copy()
    renamed.columns = [f"{prefix}_{col}" if col != "emp_id" else col for col in renamed.columns]
    return renamed


def first_available(frame: pd.DataFrame, columns: list[str], default: object = pd.NA) -> pd.Series:
    available = [column for column in columns if column in frame.columns]
    if not available:
        return pd.Series([default] * len(frame), index=frame.index)
    result = frame[available].bfill(axis=1).iloc[:, 0]
    if default is pd.NA:
        return result
    return result.fillna(default)


@st.cache_data(show_spinner=False)
def load_workbook_sheets(workbook_path: Path) -> dict[str, pd.DataFrame]:
    workbook = pd.ExcelFile(workbook_path, engine="openpyxl")
    sheets: dict[str, pd.DataFrame] = {}
    for sheet_name in workbook.sheet_names:
        frame = workbook.parse(sheet_name)
        frame.columns = [normalize_column_name(column) for column in frame.columns]
        if "emp_id" in frame.columns:
            frame["emp_id"] = frame["emp_id"].astype(str).str.strip()
        sheets[sheet_name] = frame
    return sheets


def parse_rules(rule_frame: pd.DataFrame) -> dict[str, float]:
    lookup = {
        normalize_column_name(rule): str(detail).strip()
        for rule, detail in zip(rule_frame["rule"], rule_frame["details"])
        if pd.notna(rule)
    }

    def extract_number(key: str, pattern: str, fallback: float) -> float:
        match = re.search(pattern, lookup.get(key, ""))
        return float(match.group(1)) if match else fallback

    return {
        "metro_hra_ratio": extract_number("metro_hra", r"(\d+)%", 50.0) / 100,
        "non_metro_hra_ratio": extract_number("non_metro_hra", r"(\d+)%", 40.0) / 100,
        "pf_rate": extract_number("pf", r"(\d+)%", 12.0) / 100,
        "pf_cap": extract_number("pf", r"(\d{3,})", 1800.0),
        "hour_divisor": extract_number("hourly_rate_calculation", r"(\d+)\s*hours", 160.0),
        "overtime_multiplier": extract_number("overtime_rule", r"(\d+)x", 2.0),
    }


@st.cache_data(show_spinner=False)
def merge_employee_profile(workbook_path: Path) -> tuple[pd.DataFrame, dict[str, float]]:
    sheets = load_workbook_sheets(workbook_path)
    required = [
        "Employee_Info",
        "Final_Payroll",
        "Earnings",
        "Deductions",
        "Tax",
        "Overtime",
        "Performance",
        "Labour_Law_Rules",
    ]
    missing = [sheet for sheet in required if sheet not in sheets]
    if missing:
        raise ValueError(f"Missing workbook sheets: {', '.join(missing)}")

    merged = prefix_sheet_columns("Employee_Info", sheets["Employee_Info"])
    for sheet_name in required[1:-1]:
        merged = merged.merge(prefix_sheet_columns(sheet_name, sheets[sheet_name]), on="emp_id", how="left")

    merged["employee_name"] = first_available(
        merged,
        [column for column in merged.columns if column.endswith("_employee_name") or column.endswith("_name")],
        default="Not available",
    )
    merged["department"] = first_available(
        merged, ["employee_info_department", "final_payroll_dept"], default="Unknown"
    )
    merged["role"] = first_available(merged, ["employee_info_role", "final_payroll_role"], default="Unknown")
    merged["city"] = first_available(merged, ["employee_info_city", "final_payroll_city"], default="Unknown")
    merged["metro_type"] = first_available(merged, ["employee_info_metro_type"], default="Unknown")
    merged["join_date"] = pd.to_datetime(first_available(merged, ["employee_info_join_date"]), errors="coerce")

    numeric_map = {
        "basic": ["earnings_basic"],
        "hra": ["earnings_hra"],
        "allowance": ["earnings_allowance"],
        "bonus": ["earnings_bonus"],
        "earnings_gross": ["earnings_gross"],
        "payroll_gross": ["final_payroll_gross"],
        "payroll_deductions": ["final_payroll_deductions"],
        "net_salary": ["final_payroll_net"],
        "predicted_ctc": ["final_payroll_predicted_ctc"],
        "pf": ["deductions_pf"],
        "esi": ["deductions_esi"],
        "pt": ["deductions_pt"],
        "monthly_tds": ["tax_monthly_tds"],
        "overtime_hours": ["overtime_overtime_hours"],
        "hourly_rate": ["overtime_hourly_rate"],
        "overtime_paid": ["overtime_ot_pay", "final_payroll_overtime_pay"],
        "ctc": ["earnings_ctc"],
        "experience_raw": ["employee_info_experience", "final_payroll_exp"],
        "roi": ["performance_roi"],
        "employer_cost": ["performance_employer_cost"],
        "value_generated": ["performance_value_generated"],
    }
    for output, columns in numeric_map.items():
        merged[output] = pd.to_numeric(first_available(merged, columns), errors="coerce")

    merged["experience"] = merged.apply(
        lambda row: calculate_experience(row["join_date"], row["experience_raw"]), axis=1
    )
    merged["employee_label"] = merged.apply(
        lambda row: row["emp_id"]
        if str(row["employee_name"]).strip().lower() == "not available"
        else f"{row['emp_id']} - {row['employee_name']}",
        axis=1,
    )
    merged["fixed_salary_monthly"] = (merged["basic"] + merged["hra"] + merged["allowance"]).div(12)
    merged["variable_pay_monthly"] = merged["bonus"].div(12)
    merged["net_salary_ex_variable"] = (merged["net_salary"] - merged["bonus"]).div(12)
    merged["net_salary_including_variable"] = merged["net_salary"].div(12)
    merged["monthly_work_hours"] = 160.0
    merged["per_hour_regular_pay"] = merged["basic"] / 160.0
    merged["per_hour_overtime_pay"] = merged["hourly_rate"]
    merged["market_positioning_ratio"] = (
        merged["net_salary"] / merged.groupby(["department", "role"])["net_salary"].transform("median").replace({0: pd.NA})
    )
    merged["market_positioning_index"] = merged["market_positioning_ratio"] * 100
    merged["market_status"] = merged["market_positioning_ratio"].apply(classify_market_status)

    rules = parse_rules(sheets["Labour_Law_Rules"])
    return merged.sort_values(["department", "role", "emp_id"]).reset_index(drop=True), rules


def calculate_experience(join_date: pd.Timestamp | object, fallback_experience: object) -> float | None:
    if pd.notna(join_date):
        today = pd.Timestamp.now().normalize()
        return round((today - pd.Timestamp(join_date)).days / 365.25, 1)
    if pd.notna(fallback_experience):
        return round(float(fallback_experience), 1)
    return None


def classify_market_status(value: object) -> str:
    if pd.isna(value):
        return "Fair"
    if float(value) < 0.95:
        return "Underpaid"
    if float(value) > 1.08:
        return "Overpaid"
    return "Fair"


def compliance_status_label(is_issue: bool, is_warning: bool = False) -> str:
    if is_issue:
        return "Issue"
    if is_warning:
        return "Warning"
    return "Compliant"


def run_labour_rule_checks(employee_row: pd.Series, rules: dict[str, float]) -> pd.DataFrame:
    metro_ratio = (
        rules["metro_hra_ratio"]
        if str(employee_row["metro_type"]).strip().lower().startswith("metro")
        else rules["non_metro_hra_ratio"]
    )
    basic = numeric_value(employee_row["basic"])
    expected_hra = basic * metro_ratio
    expected_pf = min((basic / 12) * rules["pf_rate"], rules["pf_cap"])
    expected_ot_rate = numeric_value(employee_row["hourly_rate"]) if pd.notna(employee_row["hourly_rate"]) else basic / rules["hour_divisor"]
    expected_ot_pay = numeric_value(employee_row["overtime_hours"]) * expected_ot_rate
    component_total = sum(numeric_value(employee_row[field]) for field in ["basic", "hra", "allowance", "bonus"])

    rows = [
        {
            "Rule": "HRA expected rule",
            "Expected": format_currency(expected_hra),
            "Actual": format_currency(employee_row["hra"]),
            "Status": compliance_status_label(abs(numeric_value(employee_row["hra"]) - expected_hra) > 1),
        },
        {
            "Rule": "PF expected rule",
            "Expected": format_currency(expected_pf),
            "Actual": format_currency(employee_row["pf"]),
            "Status": compliance_status_label(abs(numeric_value(employee_row["pf"]) - expected_pf) > 15),
        },
        {
            "Rule": "Salary component rule",
            "Expected": format_currency(component_total),
            "Actual": format_currency(employee_row["payroll_gross"]),
            "Status": compliance_status_label(abs(numeric_value(employee_row["payroll_gross"]) - component_total) > 1),
        },
        {
            "Rule": "Overtime payment rule",
            "Expected": format_currency(expected_ot_pay),
            "Actual": format_currency(employee_row["overtime_paid"]),
            "Status": compliance_status_label(abs(numeric_value(employee_row["overtime_paid"]) - expected_ot_pay) > 1),
        },
    ]
    return pd.DataFrame(rows)


def build_employee_summary(employee_row: pd.Series, compliance_table: pd.DataFrame) -> str:
    issue_count = (compliance_table["Status"] == "Issue").sum()
    warning_count = (compliance_table["Status"] == "Warning").sum()
    market_status = str(employee_row["market_status"])

    if issue_count == 0 and warning_count == 0 and market_status == "Fair":
        return "This employee profile is payroll healthy and compliant."
    if issue_count == 0 and market_status == "Underpaid":
        return "This employee is under market but labour-law compliant."
    if issue_count > 0 and numeric_value(employee_row["overtime_hours"]) > 0:
        return "This employee has overtime or salary structure issues that need review."
    if market_status == "Overpaid" and warning_count + issue_count >= 1:
        return "This employee is over market and has one compliance warning."
    if issue_count > 0:
        return "This employee profile has payroll rule mismatches that should be reviewed."
    return "This employee profile looks stable with only limited review needs."


def render_employee_radar_or_profile_chart(employee_row: pd.Series, compliance_table: pd.DataFrame, population: pd.DataFrame) -> go.Figure:
    issue_count = (compliance_table["Status"] == "Issue").sum()
    compliance_health = max(0, 100 - issue_count * 25)
    market_ratio = numeric_value(employee_row["market_positioning_ratio"]) if pd.notna(employee_row["market_positioning_ratio"]) else 1.0
    market_position = max(0, 100 - min(abs(market_ratio - 1) * 100, 100))
    overtime_load = min((numeric_value(employee_row["overtime_hours"]) / 40) * 100, 100)
    deduction_pressure = min((((numeric_value(employee_row["pf"]) + numeric_value(employee_row["pt"]) + numeric_value(employee_row["monthly_tds"])) / max(numeric_value(employee_row["ctc"]), 1)) * 1200), 100)
    compensation_strength = min((numeric_value(employee_row["ctc"]) / population["ctc"].median()) * 50, 100) if population["ctc"].median() else 50

    labels = [
        "Compensation Strength",
        "Market Position",
        "Overtime Load",
        "Compliance Health",
        "Deduction Pressure",
    ]
    values = [compensation_strength, market_position, overtime_load, compliance_health, deduction_pressure]
    values.append(values[0])
    theta = labels + [labels[0]]

    chart = go.Figure(
        go.Scatterpolar(
            r=values,
            theta=theta,
            fill="toself",
            line=dict(color=THEME["teal"], width=3),
            fillcolor="rgba(23,155,151,0.18)",
            marker=dict(color=THEME["heading"], size=6),
        )
    )
    chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=10),
        showlegend=False,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], gridcolor="#DCE6F2", linecolor="#DCE6F2", tickfont=dict(color=THEME["muted"])),
            angularaxis=dict(gridcolor="#E5EDF6", linecolor="#DCE6F2", tickfont=dict(color=THEME["heading"], size=10)),
        ),
    )
    return chart


@st.cache_data(show_spinner=False)
def extract_powerbi_pages(pbix_path: Path) -> list[dict[str, str]]:
    fallback = [
        {"label": "Executive Summary", "id": "23048d742f987e134430"},
        {"label": "Salary & Remuneration Analysis", "id": "27dc3b1cb6f06a1bf9f7"},
        {"label": "Compliance & Deductions", "id": "f2097a24f83043d94344"},
        {"label": "Performance & Value Analysis", "id": "c2250141de73d9180ea7"},
        {"label": "Overtime Analysis", "id": "7e1c48f726fac68e93c7"},
        {"label": "Predictive Analysis", "id": "aa1349ce1370731a4cc7"},
        {"label": "Employee Insights", "id": "801b20524734a1ae49f1"},
    ]
    if not pbix_path.exists():
        return fallback
    try:
        with zipfile.ZipFile(pbix_path) as archive:
            layout = json.loads(archive.read("Report/Layout").decode("utf-16le"))
        sections = sorted(layout.get("sections", []), key=lambda item: item.get("ordinal", 0))
        pages = []
        for section in sections:
            page_id = str(section.get("name", "")).strip()
            if page_id:
                pages.append({"label": section.get("displayName", page_id), "id": page_id})
        return pages or fallback
    except Exception:
        return fallback


def build_powerbi_embed_url(page_id: str) -> str:
    parsed = urlparse(POWER_BI_EMBED_URL)
    params = dict(parse_qsl(parsed.query))
    params.update(
        {
            "pageName": page_id,
            "actionBarEnabled": "false",
            "navContentPaneEnabled": "false",
            "filterPaneEnabled": "false",
            "reportCopilotInEmbed": "false",
        }
    )
    return urlunparse(parsed._replace(query=urlencode(params)))


def render_header() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{APP_TITLE}</div>
            <div class="hero-subtitle">
                A simple payroll intelligence app that keeps the Power BI dashboard central and adds one practical feature for payroll risk and compliance checking.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, subtext: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, rows: list[tuple[str, str]]) -> None:
    content = "".join(
        f"""
        <div class="info-line">
            <div class="info-key">{label}</div>
            <div class="info-value">{value}</div>
        </div>
        """
        for label, value in rows
    )
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">{title}</div>
            <div class="info-grid">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_buttons(pages: list[dict[str, str]]) -> str:
    if "selected_page_id" not in st.session_state:
        st.session_state.selected_page_id = pages[0]["id"]

    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Dashboard Pages</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Power BI navigation</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-copy'>Use these Streamlit buttons to switch report pages. Native Power BI tabs are intentionally not the main navigation.</div>",
        unsafe_allow_html=True,
    )

    for page in pages:
        button_type = "primary" if st.session_state.selected_page_id == page["id"] else "secondary"
        if st.button(page["label"], key=f"page_{page['id']}", use_container_width=True, type=button_type):
            st.session_state.selected_page_id = page["id"]

    active_label = next(page["label"] for page in pages if page["id"] == st.session_state.selected_page_id)
    st.markdown(
        f"<div class='active-page'>Active page: {active_label}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return active_label


def render_dashboard(page_id: str, page_label: str) -> None:
    embed_url = build_powerbi_embed_url(page_id)
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Embedded Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{page_label}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-copy'>The dashboard stays in a medium-sized centered box for a clean and balanced screen.</div>",
        unsafe_allow_html=True,
    )
    components.html(
        f"""
        <div style="max-width: 900px; margin: 0 auto;">
            <div style="
                background: #ffffff;
                border: 1px solid {THEME["border"]};
                border-radius: 16px;
                overflow: hidden;
            ">
                <iframe
                    title="Final Dashboard"
                    width="100%"
                    height="430"
                    src="{embed_url}"
                    frameborder="0"
                    allowfullscreen="true"
                    style="display:block;background:#ffffff;"
                ></iframe>
            </div>
        </div>
        """,
        height=458,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_employee_check(selected_row: pd.Series) -> None:
    hra_status = "Correct" if not bool(selected_row["hra_issue"]) else "Mismatch"
    pf_status = "Correct" if not bool(selected_row["pf_issue"]) else "Mismatch"
    overtime_status = "Correct" if not bool(selected_row["overtime_issue"]) else "Mismatch"

    if hra_status == pf_status == overtime_status == "Correct" and not bool(selected_row["salary_structure_issue"]):
        message = "No major payroll issue found."
        final_status = "Correct"
    elif bool(selected_row["hra_issue"]):
        message = "HRA mismatch detected."
        final_status = "Mismatch"
    elif bool(selected_row["overtime_issue"]):
        message = "Overtime payment appears inconsistent."
        final_status = "Mismatch"
    elif bool(selected_row["pf_issue"]):
        message = "PF deduction appears inconsistent."
        final_status = "Mismatch"
    else:
        message = "Salary structure mismatch detected."
        final_status = "Warning"

    st.markdown("<div class='employee-check'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="check-line">
            <strong>HRA check</strong>
            <span style="color:{status_color(hra_status)};font-weight:700;">{hra_status}</span>
        </div>
        <div class="check-line">
            <strong>PF check</strong>
            <span style="color:{status_color(pf_status)};font-weight:700;">{pf_status}</span>
        </div>
        <div class="check-line">
            <strong>Overtime payment check</strong>
            <span style="color:{status_color(overtime_status)};font-weight:700;">{overtime_status}</span>
        </div>
        <div class="check-line">
            <strong>Final issue status</strong>
            <span style="color:{status_color(final_status)};font-weight:700;">{final_status}</span>
        </div>
        <div class="decision-box">{message}</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    inject_styles()
    render_header()

    if not DATA_FILE.exists():
        st.error(f"Workbook not found: {DATA_FILE.name}")
        st.stop()

    try:
        employee_frame, rules = merge_employee_profile(DATA_FILE)
    except Exception as exc:
        st.error(f"Unable to build employee intelligence data: {exc}")
        st.stop()

    pages = extract_powerbi_pages(PBIX_FILE)

    top_left, top_center = st.columns([0.95, 2.55], gap="medium")
    with top_left:
        active_page_label = render_page_buttons(pages)
    with top_center:
        render_dashboard(st.session_state.selected_page_id, active_page_label)

    st.markdown("<div class='feature-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Main Feature</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Employee 360 → Digital Employee Intelligence</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-copy'>Select an employee to view identity, compensation, work pattern, market position, labour-law checks, and one concise employee intelligence summary.</div>",
        unsafe_allow_html=True,
    )

    selected_employee = st.selectbox("Employee selector", employee_frame["employee_label"].tolist())
    selected_row = employee_frame.loc[employee_frame["employee_label"] == selected_employee].iloc[0]
    compliance_table = run_labour_rule_checks(selected_row, rules)
    employee_summary = build_employee_summary(selected_row, compliance_table)

    identity_col, market_col = st.columns([1.5, 1], gap="medium")
    with identity_col:
        render_info_card(
            "Identity Layer",
            [
                ("Employee ID", str(selected_row["emp_id"])),
                ("Employee Name", str(selected_row["employee_name"])),
                ("Role", str(selected_row["role"])),
                ("Department", str(selected_row["department"])),
                ("Location", str(selected_row["city"])),
                (
                    "Date of Joining",
                    selected_row["join_date"].strftime("%d %b %Y") if pd.notna(selected_row["join_date"]) else "NA",
                ),
                ("Experience", f"{selected_row['experience']:.1f} years" if pd.notna(selected_row["experience"]) else "NA"),
            ],
        )
    with market_col:
        render_info_card(
            "Market Position Layer",
            [
                ("Market positioning ratio", f"{numeric_value(selected_row['market_positioning_ratio']):.2f}"),
                ("Market positioning index", f"{numeric_value(selected_row['market_positioning_index']):.1f}"),
                ("Status", str(selected_row["market_status"])),
                ("ROI", f"{numeric_value(selected_row['roi']):.2f}x"),
            ],
        )

    compensation_col, work_col = st.columns(2, gap="medium")
    with compensation_col:
        render_info_card(
            "Compensation Layer",
            [
                ("CTC Annual", format_currency(selected_row["ctc"])),
                ("Fixed Salary Monthly", format_currency(selected_row["fixed_salary_monthly"])),
                ("Variable Pay Monthly", format_currency(selected_row["variable_pay_monthly"])),
                ("Basic Salary", format_currency(selected_row["basic"])),
                ("HRA", format_currency(selected_row["hra"])),
                ("Allowances", format_currency(selected_row["allowance"])),
                ("PF Deduction", format_currency(selected_row["pf"])),
                ("Professional Tax", format_currency(selected_row["pt"])),
                ("Net Salary excluding variable pay", format_currency(selected_row["net_salary_ex_variable"])),
                ("Net Salary including variable pay", format_currency(selected_row["net_salary_including_variable"])),
            ],
        )
    with work_col:
        overtime_expected_status = compliance_table.loc[
            compliance_table["Rule"] == "Overtime payment rule", "Status"
        ].iloc[0]
        render_info_card(
            "Work Pattern Layer",
            [
                ("Monthly work hours", f"{numeric_value(selected_row['monthly_work_hours']):.0f}"),
                ("Monthly overtime hours", f"{numeric_value(selected_row['overtime_hours']):.1f}"),
                ("Per hour regular pay", format_currency(selected_row["per_hour_regular_pay"])),
                ("Per hour overtime pay", format_currency(selected_row["per_hour_overtime_pay"])),
                ("Overtime paid", format_currency(selected_row["overtime_paid"])),
                ("Overtime compliance", overtime_expected_status),
            ],
        )

    chart_col, compliance_col = st.columns([1.15, 1], gap="medium")
    with chart_col:
        st.plotly_chart(
            render_employee_radar_or_profile_chart(selected_row, compliance_table, employee_frame),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with compliance_col:
        styled_compliance = compliance_table.copy()
        styled_compliance["Status"] = styled_compliance["Status"].apply(
            lambda value: f"{value}"
        )
        st.markdown("#### Labour Law Rules Layer")
        st.dataframe(styled_compliance, use_container_width=True, hide_index=True)

    st.markdown("#### Final Intelligence Strip")
    st.markdown(
        f"<div class='summary-strip'>{employee_summary}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
