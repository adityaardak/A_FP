# 📊 Payroll Analytics & Performance Intelligence System

## Overview
This project transforms traditional employee payroll data into actionable insights using data analytics, business intelligence, and a Streamlit web application. It integrates salary, performance, and workforce data to enable smarter and more efficient HR decision-making.

---

## 🖥️ Web Application — Payroll Command Studio

The repository includes **two Streamlit apps**:

### `app.py` — Payroll Command Studio (Main App)
A production-ready payroll intelligence web app with two core sections:

**1. Embedded Power BI Dashboard**
- Navigates across 7 report pages via Streamlit sidebar buttons:
  - Executive Summary
  - Salary & Remuneration Analysis
  - Compliance & Deductions
  - Performance & Value Analysis
  - Overtime Analysis
  - Predictive Analysis
  - Employee Insights

**2. Employee 360 — Digital Employee Intelligence**
Select any employee to view a complete profile broken into layers:
- **Identity Layer** – Employee ID, name, role, department, city, join date, experience
- **Compensation Layer** – CTC, fixed/variable salary, basic, HRA, allowances, PF, professional tax, net salary (with and without variable pay)
- **Work Pattern Layer** – Monthly work hours, overtime hours, per-hour pay rates, overtime compliance status
- **Market Position Layer** – Market positioning ratio & index, market status (Underpaid / Fair / Overpaid), ROI
- **Radar Chart** – Visual profile across Compensation Strength, Market Position, Overtime Load, Compliance Health, and Deduction Pressure
- **Labour Law Rules Layer** – Automated compliance checks for HRA, PF, salary structure, and overtime payment against configurable rules
- **Final Intelligence Strip** – One-line AI-style summary of the employee's payroll health

### `main.py` — Payroll BI Dashboard (RBAC App)
A role-based access control dashboard for internal use:

**Login credentials:**
| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Admin |
| `HR_head` | `hrhead123` | HR Head |
| `Finance_head` | `financehead123` | Finance Head |

**Role-based sheet access:**
- **Admin** – All sheets except Labour Law Rules
- **HR Head** – Employee Info and Performance sheets
- **Finance Head** – Final Payroll, Earnings, Deductions, Tax, and Overtime sheets

**Features:** dynamic chart builder (Bar, Line, Pie, Histogram with Mean/Sum/Median/Count aggregation), multi-column filters, and PDF dashboard export.

---

## 🚀 How to Run

### Prerequisites
```
pip install -r requirements.txt
```

`requirements.txt` includes: `streamlit`, `pandas`, `plotly`, `openpyxl`

> **Note:** `app.py` also requires `reportlab` and `kaleido` for PDF export in `main.py`.

### Run the main app
```bash
streamlit run app.py
```

### Run the RBAC dashboard
```bash
streamlit run main.py
```

---

## 📁 Repository Structure

| File | Description |
|---|---|
| `app.py` | Payroll Command Studio — main Streamlit web app |
| `main.py` | RBAC Payroll BI Dashboard — login-protected Streamlit app |
| `final_payroll_with_prediction.xlsx` | Synthetic payroll dataset (~900 employees) |
| `Final Dashboard.pbix` | Power BI report file |
| `Final Automation flow.html` | Power Automate workflow export |
| `requirements.txt` | Python dependencies |
| `Project Report.pdf` | Full project report |
| `Project PPT.pptx` | Project presentation |
| `Project Video.mp4` | Project demo video |
| `Final Project Synopsis.pdf` | Project synopsis |

---

## Objectives
1) Analyze employee payroll data in a structured manner
2) Link compensation with employee performance (ROI-based analysis)
3) Identify salary trends, gender pay gap, and overtime impact
4) Build predictive insights for future salary estimation
5) Develop an interactive dashboard for decision-making

---

## Tools & Technologies
1) **Python / Streamlit** – Web application framework
2) **Pandas / Plotly** – Data processing and interactive charts
3) **Microsoft Excel** – Data cleaning, preprocessing, and calculations
4) **Microsoft Power BI** – Dashboard creation and visualization
5) **Power Automate** – Workflow automation for report sharing
6) **AI Tools (Copilot / ChatGPT)** – Dataset generation and insights

---

## Dataset
Synthetic payroll dataset (~900 employees)

Includes:
- Employee details (Department, Gender, Experience, City, Metro Type)
- Salary components (CTC, Basic, HRA, Allowances, Bonus)
- Deductions (PF, ESI, Professional Tax, TDS)
- Overtime details (hours, hourly rate, OT pay)
- Performance metrics (ROI, Value Generated, Employer Cost)
- Labour Law Rules (HRA ratios, PF rate/cap, overtime multiplier)

---

## Key Features
1) Salary structure & distribution analysis
2) Gender pay gap identification
3) ROI-based performance evaluation
4) Overtime analysis across departments
5) Predictive salary modeling
6) Labour law compliance checks (HRA, PF, overtime rules)
7) Market positioning analysis per employee
8) Natural language Q&A (Power BI)
9) Automated report sharing (Power Automate)
10) Role-Based Access Control (RBAC) with per-role sheet visibility

---

## Power BI Dashboard Pages
1) Executive Summary
2) Salary & Remuneration Analysis
3) Compliance & Deductions
4) Performance & Value Analysis
5) Overtime Analysis
6) Predictive Analysis
7) Employee Insights

---

## Key Insights
1) High-performing employees identified using ROI
2) Salary variation across departments and experience levels
3) Overtime imbalance in specific departments
4) Performance-based salary trends observed
5) Market positioning gaps (Underpaid / Fair / Overpaid) flagged per employee

---

## Limitations
1) Dataset is synthetic (not real-world data)
2) No real-time data integration
3) Predictive model is rule-based
4) Power BI embed requires an active Microsoft account with report access
5) Automation limited due to platform restrictions

---

## Future Scope
1) Real-time data integration using APIs
2) Advanced machine learning models for salary prediction
3) AI chatbot for payroll queries
4) Enhanced automation workflows
5) Expanded RBAC with audit logging

---

## Conclusion
This project demonstrates how payroll systems can be enhanced using data analytics, business intelligence, and a purpose-built web application. By integrating performance, compliance checking, market positioning, and automated insights, it provides a more efficient and insight-driven approach to workforce management.

---

## Author
**Anvi Jain**
AICW Fellowship Project | 2026

⭐ If you like this project, consider giving it a star!
