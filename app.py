import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Clearly Better Books — Client Portal",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# BRAND STYLING
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');

/* ── App shell ── */
.stApp { background-color: #F7F4EF !important; }
.stMainBlockContainer { background-color: #FFFFFF !important; border: 1px solid #DADDD6 !important; border-radius: 4px !important; padding-top: 2.5rem !important; padding-bottom: 3rem !important; }
[data-testid="stSidebar"] { background-color: #F7F3EE !important; border-right: 1px solid #DADDD6 !important; }
[data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]):not([translate="no"]) { font-family: 'Lato', 'Montserrat', sans-serif !important; color: #333333 !important; }
html, body, .stApp { font-family: 'Lato', 'Montserrat', sans-serif !important; color: #333333 !important; }
.stMarkdown, p, label, div[data-testid="stMarkdownContainer"], div[data-testid="stText"] { font-family: 'Lato', 'Montserrat', sans-serif !important; color: #333333 !important; }
[data-testid="stIconMaterial"], [translate="no"], .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; font-style: normal !important; font-weight: normal !important; line-height: 1 !important; }

/* ── Expanders ── */
details summary { font-family: 'Lato', sans-serif !important; font-weight: 600 !important; color: #333333 !important; letter-spacing: 0.02em !important; display: flex !important; align-items: center !important; gap: 6px !important; }
details[open] summary { color: #A8B5A3 !important; }

/* ── Brand header ── */
h1.brand-title { font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important; font-size: 2.6rem !important; letter-spacing: 0.01em !important; color: #333333 !important; text-align: center !important; margin-bottom: 0.2rem !important; }
p.brand-tagline { font-family: 'Lato', sans-serif !important; font-style: italic !important; font-size: 1.0rem !important; color: #A8B5A3 !important; text-align: center !important; margin-top: 0 !important; letter-spacing: 0.02em !important; }
div.brand-divider { width: 60px !important; height: 1px !important; background-color: #A8B5A3 !important; margin: 1rem auto 1.5rem auto !important; }

/* ── Typography ── */
h2, h3, h4, h5, h6 { font-family: 'Playfair Display', Georgia, serif !important; font-weight: 400 !important; color: #333333 !important; }

/* ── Tabs ── */
button[data-baseweb="tab"] { font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.82rem !important; font-weight: 500 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; color: #888888 !important; background: transparent !important; border: none !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #A8B5A3 !important; border-bottom: 2px solid #A8B5A3 !important; }
div[data-baseweb="tab-highlight"] { background-color: #A8B5A3 !important; }
div[data-baseweb="tab-border"] { background-color: #DADDD6 !important; }

/* ── Buttons ── */
.stButton > button { background-color: #A8B5A3 !important; color: #FFFFFF !important; border: none !important; border-radius: 3px !important; font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; padding: 0.5rem 1.4rem !important; transition: background-color 0.2s ease !important; }
.stButton > button:hover { background-color: #8FA189 !important; }
.stFormSubmitButton > button { background-color: #A8B5A3 !important; color: #FFFFFF !important; border: none !important; border-radius: 3px !important; font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
.stFormSubmitButton > button:hover { background-color: #8FA189 !important; }
a.invoice-btn { display: inline-block !important; background-color: #A8B5A3 !important; color: #FFFFFF !important; text-decoration: none !important; padding: 7px 18px !important; border-radius: 3px !important; font-family: 'Montserrat', sans-serif !important; font-size: 0.76rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }

/* ── Inputs ── */
.stTextInput input, .stSelectbox select, .stTextArea textarea, div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { border: 1px solid #DADDD6 !important; border-radius: 3px !important; background-color: #FAFAF8 !important; color: #333333 !important; font-family: 'Lato', sans-serif !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #A8B5A3 !important; box-shadow: 0 0 0 2px rgba(168,181,163,0.18) !important; }

/* ── File uploader ── */
div[data-testid="stFileUploader"] section { background-color: #F7F3EE !important; border: 1px dashed #A8B5A3 !important; border-radius: 4px !important; }
div[data-testid="stFileUploader"] section:hover { border-color: #8FA189 !important; }

/* ── Metrics ── */
[data-testid="metric-container"] { background: #FAFAF8 !important; border: 1px solid #DADDD6 !important; border-radius: 4px !important; padding: 12px 16px !important; }

/* ── KPI stats ── */
.dashboard-stat { text-align: center; padding: 20px 10px; border-right: 1px solid #DADDD6; }
.dashboard-stat:last-child { border-right: none; }
.dashboard-stat-number { font-family: 'Playfair Display', Georgia, serif; font-size: 2.4em; font-weight: 600; color: #333333; display: block; line-height: 1.1; }
.dashboard-stat-label { font-family: 'Montserrat', sans-serif; font-size: 0.72em; color: #A8B5A3; letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-top: 4px; }

/* ── Cards ── */
div.portal-card { background: #FFFFFF !important; border: 1px solid #DADDD6 !important; border-radius: 4px !important; padding: 18px 22px !important; margin-bottom: 12px !important; }
.client-card { background: #FFFFFF; border: 1px solid #DADDD6; border-left: 3px solid #A8B5A3; border-radius: 4px; padding: 14px 18px; margin-bottom: 10px; font-family: 'Lato', sans-serif; }
.client-card-alert { background: #FDFAF7; border: 1px solid #DADDD6; border-left: 3px solid #EBC6C1; border-radius: 4px; padding: 14px 18px; margin-bottom: 10px; font-family: 'Lato', sans-serif; }

/* ── Status badges ── */
.status-badge { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 0.75em; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-family: 'Montserrat', sans-serif; }
.badge-open    { background: #F7F3EE; color: #A8B5A3; border: 1px solid #DADDD6; }
.badge-progress{ background: #EAF0E8; color: #6E8A69; border: 1px solid #C5D4C2; }
.badge-waiting { background: #FAF2F1; color: #C4878A; border: 1px solid #EBC6C1; }
.badge-done    { background: #F0F3EF; color: #7A9477; border: 1px solid #C2D1BF; }

/* ── Pipeline stages ── */
.pipeline-stage { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 0.75em; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-family: 'Montserrat', sans-serif; }
.stage-new        { background: #EEF0FA; color: #6678B1; border: 1px solid #C2CAE8; }
.stage-proposal   { background: #FFF4E6; color: #B87333; border: 1px solid #F0D4B0; }
.stage-accepted   { background: #EAF0E8; color: #6E8A69; border: 1px solid #C5D4C2; }
.stage-onboarding { background: #F0F3EF; color: #7A9477; border: 1px solid #C2D1BF; }

/* ── Profile fields ── */
.profile-field-label { font-family: 'Montserrat', sans-serif; font-size: 0.72em; letter-spacing: 0.1em; text-transform: uppercase; color: #A8B5A3; margin-bottom: 2px; }
.profile-field-value { font-family: 'Lato', sans-serif; font-size: 0.95em; color: #333333; margin-bottom: 12px; }

/* ── Alert chip / attention chip ── */
.attention-chip { display: inline-block; background: #FAF2F1; color: #C4878A; border: 1px solid #EBC6C1; border-radius: 2px; padding: 2px 8px; font-size: 0.72em; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-left: 8px; }
.unread-badge { display: inline-block; background: #C4878A; color: white; border-radius: 10px; padding: 1px 7px; font-size: 0.72em; font-family: 'Montserrat', sans-serif; font-weight: 600; margin-left: 6px; }

/* ── Activity log ── */
.activity-entry { padding: 10px 0; border-bottom: 1px solid #F0ECE7; font-family: 'Lato', sans-serif; font-size: 0.9em; }

/* ── Secure Messaging ── */
.msg-bubble { max-width: 78%; padding: 10px 14px; border-radius: 12px; font-family: 'Lato', sans-serif; font-size: 0.92em; line-height: 1.5; margin-bottom: 4px; }
.msg-bubble-firm { background: #EAF0E8; color: #2D4A2A; border-radius: 12px 12px 2px 12px; margin-left: auto; }
.msg-bubble-client { background: #F7F3EE; color: #333333; border: 1px solid #DADDD6; border-radius: 12px 12px 12px 2px; }
.msg-row { display: flex; flex-direction: column; margin: 8px 0; }
.msg-row-firm { align-items: flex-end; }
.msg-row-client { align-items: flex-start; }
.msg-meta { font-family: 'Montserrat', sans-serif; font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.07em; color: #A8B5A3; margin-bottom: 2px; }
.msg-area { border: 1px solid #DADDD6; border-radius: 4px; padding: 16px; background: #FAFAF8; min-height: 200px; max-height: 420px; overflow-y: auto; margin-bottom: 12px; }
.msg-no-messages { text-align: center; color: #A8B5A3; font-family: 'Lato', sans-serif; font-size: 0.9em; padding: 40px 0; }

/* ── Document Requests ── */
.doc-req-card { background: #FFFFFF; border: 1px solid #DADDD6; border-radius: 4px; padding: 14px 18px; margin-bottom: 10px; }
.doc-req-pending  { border-left: 3px solid #D4956A; }
.doc-req-uploaded { border-left: 3px solid #A8B5A3; }
.doc-req-approved { border-left: 3px solid #7A9477; opacity: 0.82; }
.doc-req-waived   { border-left: 3px solid #DADDD6; opacity: 0.55; }
.doc-req-name { font-family: 'Lato', sans-serif; font-weight: 600; font-size: 0.98em; color: #333333; margin-bottom: 2px; }
.doc-req-meta { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #888888; }

/* ── Client To-Do cards ── */
.todo-card { background: #FFFFFF; border: 1px solid #DADDD6; border-radius: 4px; padding: 16px 20px; margin-bottom: 12px; }
.todo-card-task    { border-left: 3px solid #A8B5A3; }
.todo-card-doc     { border-left: 3px solid #D4956A; }
.todo-card-invoice { border-left: 3px solid #C4878A; }
.todo-type { font-family: 'Montserrat', sans-serif; font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 3px; }
.todo-type-task    { color: #A8B5A3; }
.todo-type-doc     { color: #D4956A; }
.todo-type-invoice { color: #C4878A; }
.todo-title { font-family: 'Lato', sans-serif; font-size: 1.0em; font-weight: 600; color: #333333; margin-bottom: 2px; }
.todo-meta  { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #888888; }
.all-clear  { text-align: center; padding: 40px 0; }
.all-clear-icon { font-size: 2.5em; display: block; margin-bottom: 8px; }
.all-clear-text { font-family: 'Playfair Display', serif; font-size: 1.1em; color: #A8B5A3; }

/* ── Time Tracker ── */
.time-entry-row { padding: 8px 0; border-bottom: 1px solid #F0ECE7; font-family: 'Lato', sans-serif; font-size: 0.9em; }
.hours-big { font-family: 'Playfair Display', serif; font-size: 2.2em; font-weight: 600; color: #333333; }

/* ── Misc ── */
.section-divider { border: none; border-top: 1px solid #DADDD6; margin: 24px 0; }
.note-box { background: #F7F3EE; border: 1px solid #DADDD6; border-radius: 4px; padding: 12px 16px; font-size: 0.9em; color: #555; margin-top: 8px; font-family: 'Lato', sans-serif; }
.upload-zone { background: #F7F3EE; border: 1px dashed #A8B5A3; border-radius: 4px; padding: 20px 24px; text-align: center; margin-bottom: 14px; }
.custom-upload-title { font-family: 'Playfair Display', serif; font-size: 1.1em; color: #333333; margin-bottom: 4px; }
.custom-upload-subtitle { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #888888; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F7F4EF; }
::-webkit-scrollbar-thumb { background: #DADDD6; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A8B5A3; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
GOOGLE_SHEET_NAME   = "FirmLink_DB"
SHARED_DRIVE_ID     = "0AFQkhoAnS2U-Uk9PVA"
MAIN_FOLDER_ID      = "0AFQkhoAnS2U-Uk9PVA"
CLIENT_ROLE         = "client"

# ── Sheet names ──
SH_CLIENTS  = "Clients"
SH_USERS    = "Users"
SH_COMM_LOG = "CommLog"
SH_PIPELINE = "Pipeline"
SH_TIMELOG  = "TimeLog"
SH_DOC_REQ  = "DocRequests"
SH_MESSAGES = "Messages"

# ── Headers ──
CLIENTS_HEADERS = [
    "Client Name", "Contact Name", "Email", "Phone", "Date Added",
    "Service Tier", "Client Status", "Monthly Rate", "Contract Signed",
    "Engagement Start", "Referral Source", "Last Contacted", "Internal Notes",
]
USERS_HEADERS    = ["username", "password", "role", "client_association"]
COMM_LOG_HEADERS = ["Date", "Client", "Type", "Summary", "Logged By"]
PIPELINE_HEADERS = [
    "Lead Name", "Contact", "Email", "Service Interest", "Stage",
    "Est Monthly Value", "Follow Up Date", "Notes", "Date Added",
]
TIMELOG_HEADERS  = ["Date", "Client", "Service", "Hours", "Notes", "Logged By"]
DOC_REQ_HEADERS  = [
    "Req ID", "Client", "Request Name", "Category", "Description",
    "Due Date", "Status", "Drive File ID", "Uploaded Date", "Created Date",
]
MESSAGES_HEADERS = ["Date", "Client", "Sender Type", "Sender Name", "Message"]

# Column positions for fast cell updates (1-indexed)
# Clients
CLI_COL = {h: i+1 for i, h in enumerate(CLIENTS_HEADERS)}
# DocRequests
DR_COL  = {h: i+1 for i, h in enumerate(DOC_REQ_HEADERS)}
# Tasks: client=1, task=2, status=3, due=4
# Invoices: client=1, invoice_num=2, amount=3, due_date=4, pay_link=5, status=6

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Service options ──
SERVICE_TIERS = [
    "Monthly Bookkeeping", "Catch-Up / Cleanup",
    "AP / AR Management", "Sales Tax", "Advisory",
    "Payroll", "CFO Services", "Other",
]
TIME_SERVICES = [
    "Monthly Bookkeeping", "Catch-Up / Cleanup",
    "AP / AR Management", "Sales Tax", "Advisory",
    "Consultation", "Admin / Setup", "Other",
]
DOC_CATEGORIES = [
    "Bank Statements", "Credit Card Statements",
    "Tax Documents", "Business Records",
    "Payroll Records", "Receipts / Expenses", "Other",
]
PIPELINE_STAGES = [
    "New Lead", "Proposal Sent", "Proposal Accepted",
    "Onboarding", "Closed Lost",
]
CLIENT_STATUSES = ["Active", "Onboarding", "On Hold", "Offboarding", "Prospect"]

# ── Workflow templates ──
WORKFLOW_TEMPLATES = {
    "Monthly Bookkeeping Close": [
        ("Collect bank statements", 5),
        ("Collect credit card statements", 5),
        ("Categorize all transactions", 7),
        ("Reconcile bank accounts", 7),
        ("Reconcile credit card accounts", 8),
        ("Review uncategorized items with client", 10),
        ("Run P&L and Balance Sheet", 12),
        ("Deliver monthly financial package", 14),
    ],
    "New Client Onboarding": [
        ("Send welcome email and portal access", 1),
        ("Collect signed engagement letter", 3),
        ("Gather prior year financials", 7),
        ("QBO access and setup review", 7),
        ("Chart of accounts cleanup", 10),
        ("Onboarding call — review findings", 12),
        ("Set up recurring task schedule", 14),
    ],
    "Catch-Up / Cleanup Project": [
        ("Assess scope — months behind", 1),
        ("Collect all missing bank statements", 3),
        ("Enter and categorize historical transactions", 14),
        ("Reconcile all accounts by month", 21),
        ("Identify and resolve discrepancies", 25),
        ("Deliver cleanup summary report", 30),
    ],
    "Sales Tax Filing": [
        ("Pull sales data for period", 3),
        ("Verify taxable vs exempt sales", 4),
        ("Calculate tax owed by jurisdiction", 5),
        ("Client review and approval", 7),
        ("File return(s)", 8),
        ("Confirm filing receipt", 10),
    ],
    "Quarterly Review": [
        ("Pull quarterly financials from QBO", 2),
        ("Prepare P&L and Balance Sheet", 3),
        ("Draft variance commentary", 5),
        ("Schedule quarterly review call", 5),
        ("Deliver quarterly summary", 7),
    ],
}

# ── Document request quick-templates ──
DOC_REQUEST_TEMPLATES = {
    "Bank Statement": ("Bank Statements", "Please upload your bank statement for the period specified."),
    "Credit Card Statement": ("Credit Card Statements", "Please upload your credit card statement for the period specified."),
    "Payroll Summary": ("Payroll Records", "Please upload your payroll summary for the period specified."),
    "Receipts / Expenses": ("Receipts / Expenses", "Please upload any receipts or expense documentation."),
    "Prior Year Tax Return": ("Tax Documents", "Please upload a copy of last year's filed tax return."),
    "Sales Report": ("Business Records", "Please upload your sales or revenue report for the period."),
    "Custom Request": ("Other", ""),
}


# ═══════════════════════════════════════════════════════════════
# GOOGLE SERVICES  (cached for the lifetime of the server)
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def get_google_services():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            dict(st.secrets["gcp_service_account"]), SCOPES
        )
        gc = gspread.authorize(creds)
        ss = gc.open(GOOGLE_SHEET_NAME)

        def _ws(name, headers):
            """Get or create a worksheet with the given name and headers."""
            try:
                return ss.worksheet(name)
            except gspread.exceptions.WorksheetNotFound:
                w = ss.add_worksheet(title=name, rows=500, cols=max(len(headers), 10))
                w.append_row(headers)
                return w

        return {
            "ss":       ss,
            "tasks":    ss.sheet1,
            "invoices": _ws("Invoices", ["client","invoice_num","amount","due_date","pay_link","status"]),
            "clients":  _ws(SH_CLIENTS,  CLIENTS_HEADERS),
            "users":    _ws(SH_USERS,    USERS_HEADERS),
            "comm_log": _ws(SH_COMM_LOG, COMM_LOG_HEADERS),
            "pipeline": _ws(SH_PIPELINE, PIPELINE_HEADERS),
            "timelog":  _ws(SH_TIMELOG,  TIMELOG_HEADERS),
            "doc_req":  _ws(SH_DOC_REQ,  DOC_REQ_HEADERS),
            "messages": _ws(SH_MESSAGES, MESSAGES_HEADERS),
            "drive":    build("drive", "v3", credentials=creds),
        }
    except Exception as e:
        st.error(f"Google connection failed: {e}")
        return None


svc = get_google_services()


# ═══════════════════════════════════════════════════════════════
# DATA WRITE HELPERS
# ═══════════════════════════════════════════════════════════════
def _safe(val):
    """Return empty string for None/falsy, otherwise the value."""
    return val if val else ""


# ── Tasks ──
def add_task(client, task_name, status, due_date):
    if svc is None: return
    svc["tasks"].append_row([client, task_name, status, str(due_date)])

def update_task_status(row_num, new_status):
    if svc is None: return
    svc["tasks"].update_cell(row_num, 3, new_status)


# ── Invoices ──
def add_invoice(client, inv_num, amount, due_date, pay_link):
    if svc is None: return
    svc["invoices"].append_row([client, inv_num, amount, str(due_date), pay_link, "Unpaid"])

def mark_invoice_paid(row_num):
    if svc is None: return
    svc["invoices"].update_cell(row_num, 6, "Paid")


# ── Clients ──
def add_client(name, contact, email, phone, service_tier, status,
               monthly_rate, contract_signed, start_date, referral):
    if svc is None: return False
    today_str = date.today().strftime("%Y-%m-%d")
    svc["clients"].append_row([
        name, contact, email, phone, today_str,
        service_tier, status, monthly_rate, contract_signed,
        str(start_date), referral, today_str, "",
    ])
    return True

def update_client_col(client_name, col_name, value):
    if svc is None: return
    col = CLI_COL.get(col_name)
    if col is None: return
    try:
        records = svc["clients"].get_all_records()
        for i, r in enumerate(records):
            if str(r.get("Client Name", "")).strip() == client_name.strip():
                svc["clients"].update_cell(i + 2, col, value)
                return
    except Exception:
        pass


# ── Comm Log ──
def add_comm_log(client, entry_type, summary, logged_by="Firm"):
    if svc is None: return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    svc["comm_log"].append_row([ts, client, entry_type, summary, logged_by])
    update_client_col(client, "Last Contacted", date.today().strftime("%Y-%m-%d"))


# ── Pipeline ──
def add_pipeline_lead(lead_name, contact, email, service_interest,
                      stage, est_value, follow_up, notes):
    if svc is None: return False
    today_str = date.today().strftime("%Y-%m-%d")
    svc["pipeline"].append_row([
        lead_name, contact, email, service_interest, stage,
        est_value, str(follow_up), notes, today_str,
    ])
    return True

def update_pipeline_stage(lead_name, new_stage):
    if svc is None: return
    try:
        records = svc["pipeline"].get_all_records()
        for i, r in enumerate(records):
            if str(r.get("Lead Name", "")).strip() == lead_name.strip():
                svc["pipeline"].update_cell(i + 2, 5, new_stage)
                return
    except Exception:
        pass


# ── Time Log ──
def add_time_entry(client, service, hours, notes, logged_by):
    if svc is None: return
    today_str = date.today().strftime("%Y-%m-%d")
    svc["timelog"].append_row([today_str, client, service, hours, notes, logged_by])


# ── Document Requests ──
def add_doc_request(client, req_name, category, description, due_date):
    if svc is None: return
    req_id    = datetime.now().strftime("REQ-%Y%m%d-%H%M%S")
    today_str = date.today().strftime("%Y-%m-%d")
    svc["doc_req"].append_row([
        req_id, client, req_name, category, description,
        str(due_date), "Pending", "", "", today_str,
    ])

def update_doc_request(row_num, new_status, drive_file_id=""):
    if svc is None: return
    uploaded = date.today().strftime("%Y-%m-%d") if drive_file_id else ""
    svc["doc_req"].update(
        f"G{row_num}:I{row_num}",
        [[new_status, drive_file_id, uploaded]],
    )


# ── Messages ──
def send_message(client, sender_type, sender_name, message):
    if svc is None: return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    svc["messages"].append_row([ts, client, sender_type, sender_name, message])


# ═══════════════════════════════════════════════════════════════
# GOOGLE DRIVE HELPERS
# ═══════════════════════════════════════════════════════════════
def _get_or_create_folder(client_name):
    if svc is None: return None
    drive = svc["drive"]
    q = (
        f"name='{client_name}' and '{MAIN_FOLDER_ID}' in parents "
        f"and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    try:
        res = drive.files().list(
            q=q, fields="files(id)", corpora="drive",
            driveId=SHARED_DRIVE_ID, supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        items = res.get("files", [])
        if items:
            return items[0]["id"]
        meta = {
            "name": client_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [MAIN_FOLDER_ID],
        }
        f = drive.files().create(body=meta, fields="id", supportsAllDrives=True).execute()
        return f.get("id")
    except Exception as e:
        st.error(f"Drive folder error: {e}")
        return None


def upload_to_drive(client_name, uploaded_file):
    folder_id = _get_or_create_folder(client_name)
    if not folder_id:
        st.error("Could not resolve upload folder.")
        return None
    meta   = {"name": uploaded_file.name, "parents": [folder_id]}
    stream = io.BytesIO(uploaded_file.getvalue())
    media  = MediaIoBaseUpload(stream, mimetype=uploaded_file.type, resumable=True)
    try:
        f = svc["drive"].files().create(
            body=meta, media_body=media, fields="id", supportsAllDrives=True
        ).execute()
        return f.get("id")
    except Exception as e:
        st.error(f"File upload failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# UTILITY HELPERS
# ═══════════════════════════════════════════════════════════════
def _date_before(date_str, ref_date):
    """Return True if date_str parses to a date strictly before ref_date."""
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date() < ref_date
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════
def is_admin(role):
    return str(role).strip().lower() != CLIENT_ROLE

if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False,
        "user_role": None,
        "client_association": None,
        "username": None,
    })

def handle_logout():
    st.session_state.update({
        "authenticated": False,
        "user_role": None,
        "client_association": None,
        "username": None,
    })
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    st.markdown("<h1 class='brand-title'>Clearly Better Books</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='brand-tagline'>Bookkeeping that brings clarity, confidence, and calm to your business.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align:center;font-weight:normal;letter-spacing:0.02em;'>Secure Portal Login</h3>",
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form", clear_on_submit=False):
            u = st.text_input("Username / Email").strip()
            p = st.text_input("Password", type="password").strip()
            btn = st.form_submit_button("Sign In")
        if btn:
            users = svc["users"].get_all_records() if svc else []
            match = next(
                (r for r in users
                 if str(r.get("username","")).strip() == u
                 and str(r.get("password","")).strip() == p
                 and u),
                None,
            )
            if match:
                st.session_state.update({
                    "authenticated": True,
                    "username": match.get("username"),
                    "user_role": match.get("role"),
                    "client_association": match.get("client_association"),
                })
                st.rerun()
            else:
                st.error("Invalid username or password.")

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATED APP
# ═══════════════════════════════════════════════════════════════
else:
    admin = is_admin(st.session_state.user_role)

    # ── Build client list ──
    BASE_CLIENTS = ["Acme Corp", "Baker Street Cafe"]
    _cli_recs    = svc["clients"].get_all_records() if svc else []
    _cli_names   = [str(r.get("Client Name","")).strip() for r in _cli_recs if str(r.get("Client Name","")).strip()]
    CLIENT_LIST  = list(dict.fromkeys(BASE_CLIENTS + _cli_names))
    CLI_LOOKUP   = {str(r.get("Client Name","")).strip(): r for r in _cli_recs}

    # ── Sidebar ──
    if admin:
        st.sidebar.markdown(
            "<h3 style='text-align:center;margin-top:20px;font-weight:400;"
            "font-family:Playfair Display,Georgia,serif;color:#333333;"
            "letter-spacing:0.02em;'>Firm Controls</h3>",
            unsafe_allow_html=True,
        )
        firm_view    = st.sidebar.radio("View:", ["Practice Dashboard", "Client Workspace"], key="firm_view_mode")
        active_client = st.sidebar.selectbox("Manage Client:", CLIENT_LIST)
    else:
        firm_view     = "Client Workspace"
        active_client = str(st.session_state.client_association or "").strip()
        if active_client and active_client not in CLIENT_LIST:
            CLIENT_LIST.append(active_client)
        st.sidebar.markdown(
            "<h3 style='text-align:center;margin-top:20px;font-weight:400;"
            "font-family:Playfair Display,Georgia,serif;color:#333333;"
            "letter-spacing:0.02em;'>Client Account</h3>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown(
            f"<p style='text-align:center;font-size:1.1em;'><b>{active_client}</b></p>",
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("Log Out of Portal", key="logout_btn"):
        handle_logout()
    st.sidebar.markdown(
        "<br><hr style='border-color:#DADDD6;'><br>"
        f"<p style='font-size:0.76em;text-align:center;color:#A8B5A3;line-height:1.6;'>"
        f"Logged in as:<br><span style='color:#333333;font-weight:600;'>"
        f"{st.session_state.username}</span></p>",
        unsafe_allow_html=True,
    )

    # ── Brand header ──
    st.markdown("<h1 class='brand-title'>Clearly Better Books</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='brand-tagline'>Bookkeeping that brings clarity, confidence, and calm to your business.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # LOAD ALL DATA ONCE
    # ─────────────────────────────────────────────────────────
    if svc is None:
        st.info("Connecting to portal services...")
        st.stop()

    today         = date.today()
    all_tasks     = svc["tasks"].get_all_records()
    all_invoices  = svc["invoices"].get_all_records()
    all_pipeline  = svc["pipeline"].get_all_records()
    all_comm      = svc["comm_log"].get_all_records()
    all_timelog   = svc["timelog"].get_all_records()
    # store _row for sheets that need targeted cell updates
    all_doc_req   = [dict(r, _row=i+2) for i, r in enumerate(svc["doc_req"].get_all_records())]
    all_messages  = [dict(r, _row=i+2) for i, r in enumerate(svc["messages"].get_all_records())]

    # ── Derived KPIs ──
    open_tasks_all = [t for t in all_tasks if str(t.get("status","")).strip() != "Completed"]
    overdue_tasks  = []
    for t in open_tasks_all:
        try:
            if datetime.strptime(str(t.get("due","")).strip(), "%Y-%m-%d").date() < today:
                overdue_tasks.append(t)
        except Exception:
            pass

    unpaid_all  = [i for i in all_invoices if str(i.get("status","")).strip().lower() != "paid"]
    total_ar    = sum(
        float(str(inv.get("amount","")).replace("$","").replace(",","").strip() or 0)
        for inv in unpaid_all
        if str(inv.get("amount","")).replace("$","").replace(",","").strip()
    )
    mrr_total   = sum(
        float(str(r.get("Monthly Rate","")).replace("$","").replace(",","").strip() or 0)
        for r in _cli_recs
        if str(r.get("Monthly Rate","")).replace("$","").replace(",","").strip()
    )

    clients_needing_attn = set()
    for t in overdue_tasks:
        c = str(t.get("client","")).strip()
        if c: clients_needing_attn.add(c)
    for inv in unpaid_all:
        try:
            d = datetime.strptime(str(inv.get("due_date","")).strip(), "%Y-%m-%d").date()
            if (today - d).days > 30:
                clients_needing_attn.add(str(inv.get("client","")).strip())
        except Exception:
            pass

    active_leads  = [p for p in all_pipeline if str(p.get("Stage","")).strip() not in ("", "Closed Lost")]
    pipeline_mrr  = sum(
        float(str(p.get("Est Monthly Value","")).replace("$","").replace(",","").strip() or 0)
        for p in active_leads
        if str(p.get("Est Monthly Value","")).replace("$","").replace(",","").strip()
    )

    # Unread messages = client messages with no firm reply yet (last sender per client)
    def _last_sender(client_name):
        thread = [m for m in all_messages if str(m.get("Client","")).strip() == client_name]
        return str(thread[-1].get("Sender Type","")).strip() if thread else ""

    clients_with_unread = [c for c in CLIENT_LIST if _last_sender(c) == "client"]
    total_unread = len(clients_with_unread)

    # Hours this month
    this_month = today.strftime("%Y-%m")
    hours_this_month = sum(
        float(str(t.get("Hours",0)) or 0)
        for t in all_timelog
        if str(t.get("Date","")).startswith(this_month)
    )

    # Pending doc requests
    pending_doc_req_count = sum(1 for r in all_doc_req if str(r.get("Status","")).strip() == "Pending")

    # ══════════════════════════════════════════════════════════
    # PRACTICE DASHBOARD  (admin only)
    # ══════════════════════════════════════════════════════════
    if admin and firm_view == "Practice Dashboard":

        st.markdown(
            "<h5 style='font-family:Montserrat,Lato,sans-serif;letter-spacing:0.12em;"
            "text-transform:uppercase;color:#A8B5A3;font-size:0.78rem;font-weight:600;'>"
            "Practice Dashboard</h5>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # ── KPI Row 1 ──
        c1, c2, c3, c4 = st.columns(4)
        for col, num, label, color in [
            (c1, len(CLIENT_LIST), "Active Clients", "#333333"),
            (c2, len(open_tasks_all), "Open Tasks", "#333333"),
            (c3, len(overdue_tasks), "Overdue Tasks", "#C4878A" if overdue_tasks else "#333333"),
            (c4, f"${total_ar:,.2f}", "Total AR Outstanding", "#333333"),
        ]:
            with col:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number' style='color:{color}'>{num}</span>"
                    f"<span class='dashboard-stat-label'>{label}</span></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── KPI Row 2 ──
        c5, c6, c7, c8 = st.columns(4)
        for col, num, label, color in [
            (c5, f"${mrr_total:,.0f}", "Est. Monthly Revenue", "#333333"),
            (c6, f"{hours_this_month:.1f} hrs", "Hours This Month", "#333333"),
            (c7, total_unread, "Unread Messages", "#C4878A" if total_unread else "#7A9477"),
            (c8, pending_doc_req_count, "Docs Awaiting Upload", "#D4956A" if pending_doc_req_count else "#7A9477"),
        ]:
            with col:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number' style='color:{color}'>{num}</span>"
                    f"<span class='dashboard-stat-label'>{label}</span></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # ── Dashboard Tabs ──
        (
            tab_tasks, tab_ar, tab_time,
            tab_docs, tab_msgs, tab_profiles,
            tab_log, tab_pipe
        ) = st.tabs([
            "All Tasks", "AR Overview", "Time Tracker",
            "Document Requests", "Messages", "Client Profiles",
            "Activity Log", "Pipeline",
        ])

        # ──────────────────────────────────────────────────────
        # TAB 1 — ALL TASKS
        # ──────────────────────────────────────────────────────
        with tab_tasks:
            st.markdown("#### All Tasks")

            # Workflow launcher
            with st.expander("Launch Workflow Template", expanded=False):
                wc1, wc2, wc3 = st.columns([2, 2, 1])
                with wc1:
                    wf_tmpl = st.selectbox("Template", list(WORKFLOW_TEMPLATES.keys()), key="wf_tmpl")
                with wc2:
                    wf_cli  = st.selectbox("For Client", CLIENT_LIST, key="wf_cli")
                with wc3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Launch", key="wf_launch"):
                        for tname, offset in WORKFLOW_TEMPLATES[wf_tmpl]:
                            d = today + timedelta(days=offset)
                            add_task(wf_cli, tname, "Pending", d)
                        st.success(f"Launched '{wf_tmpl}' for {wf_cli} — {len(WORKFLOW_TEMPLATES[wf_tmpl])} tasks created.")
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # Filters
            fc1, fc2, fc3 = st.columns([2, 2, 2])
            with fc1:
                f_cli    = st.selectbox("Filter by Client", ["All Clients"] + CLIENT_LIST, key="ft_cli")
            with fc2:
                f_status = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Awaiting Client", "Completed"], key="ft_status")
            with fc3:
                f_over   = st.checkbox("Overdue Only", key="ft_over")

            tasks_view = list(all_tasks)
            if f_cli != "All Clients":
                tasks_view = [t for t in tasks_view if t.get("client") == f_cli]
            if f_status != "All":
                tasks_view = [t for t in tasks_view if str(t.get("status","")).strip() == f_status]
            if f_over:
                tasks_view = [
                    t for t in tasks_view
                    if str(t.get("status","")).strip() != "Completed"
                    and _date_before(str(t.get("due","")), today)
                ]

            st.markdown("<br>", unsafe_allow_html=True)

            if not tasks_view:
                st.info("No tasks match the current filters.")
            else:
                status_opts = ["Pending", "In Progress", "Awaiting Client", "Completed"]
                badge_map   = {"Pending":"badge-open","In Progress":"badge-progress",
                               "Awaiting Client":"badge-waiting","Completed":"badge-done"}
                for idx, task in enumerate(tasks_view):
                    status    = str(task.get("status","Pending")).strip()
                    task_name = str(task.get("task","")).strip() or "*(Untitled task)*"
                    due_str   = str(task.get("due","")).strip()
                    overdue   = _date_before(due_str, today) and status != "Completed"
                    badge     = badge_map.get(status, "badge-open")
                    flag      = " 🔴" if overdue else ""

                    tc1, tc2, tc3, tc4 = st.columns([3, 2, 2, 2])
                    with tc1:
                        st.markdown(f"**{task_name}**{flag}")
                        st.caption(f"Client: {task.get('client','')}")
                    with tc2:
                        st.markdown(f"<span class='status-badge {badge}'>{status}</span>", unsafe_allow_html=True)
                    with tc3:
                        st.caption(f"Due: {due_str or 'Not set'}")
                    with tc4:
                        new_s = st.selectbox(
                            "Status", status_opts,
                            index=status_opts.index(status) if status in status_opts else 0,
                            key=f"ts_{idx}", label_visibility="collapsed",
                        )
                        if new_s != status:
                            all_recs = svc["tasks"].get_all_records()
                            for si, rec in enumerate(all_recs):
                                if (rec.get("client") == task.get("client")
                                        and rec.get("task") == task.get("task")
                                        and rec.get("due") == task.get("due")):
                                    update_task_status(si + 2, new_s)
                                    st.rerun()
                    st.markdown("<hr style='border:none;border-top:1px solid #F0ECE7;margin:6px 0;'>", unsafe_allow_html=True)

        # ──────────────────────────────────────────────────────
        # TAB 2 — AR OVERVIEW
        # ──────────────────────────────────────────────────────
        with tab_ar:
            st.markdown("#### Accounts Receivable — All Clients")
            st.markdown("<br>", unsafe_allow_html=True)

            for client in CLIENT_LIST:
                cli_unpaid = [i for i in all_invoices
                              if i.get("client") == client
                              and str(i.get("status","")).strip().lower() != "paid"]
                cli_total = sum(
                    float(str(i.get("amount","")).replace("$","").replace(",","").strip() or 0)
                    for i in cli_unpaid
                    if str(i.get("amount","")).replace("$","").replace(",","").strip()
                )
                max_age = 0
                for inv in cli_unpaid:
                    try:
                        d   = datetime.strptime(str(inv.get("due_date","")).strip(), "%Y-%m-%d").date()
                        max_age = max(max_age, (today - d).days)
                    except Exception:
                        pass

                alert    = cli_total > 0
                card_cls = "client-card-alert" if alert else "client-card"
                ar_color = "#C4878A" if alert else "#7A9477"
                age_chip = ""
                if max_age > 60:
                    age_chip = "<span class='attention-chip'>60+ days</span>"
                elif max_age > 30:
                    age_chip = "<span class='attention-chip'>30+ days</span>"

                st.markdown(
                    f"<div class='{card_cls}'>"
                    f"<strong>{client}</strong>{age_chip}&nbsp;&nbsp;"
                    f"<span style='color:#A8B5A3;font-size:0.88em;'>{len(cli_unpaid)} unpaid</span>&nbsp;&nbsp;"
                    f"<strong style='color:{ar_color};'>${cli_total:,.2f} outstanding</strong>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            if unpaid_all:
                st.markdown("<br>")
                st.markdown("#### All Unpaid Invoices")
                rows = []
                for inv in unpaid_all:
                    try:
                        dd = datetime.strptime(str(inv.get("due_date","")).strip(), "%Y-%m-%d").date()
                        aging = f"{(today-dd).days}d overdue" if (today-dd).days > 0 else "Current"
                    except Exception:
                        aging = ""
                    rows.append({
                        "Client": inv.get("client",""),
                        "Invoice #": inv.get("invoice_num",""),
                        "Amount": inv.get("amount",""),
                        "Due Date": inv.get("due_date",""),
                        "Aging": aging,
                        "Status": inv.get("status","Unpaid"),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ──────────────────────────────────────────────────────
        # TAB 3 — TIME TRACKER
        # ──────────────────────────────────────────────────────
        with tab_time:
            st.markdown("#### Time Tracker")
            st.markdown("<br>", unsafe_allow_html=True)

            # Summary KPIs
            sk1, sk2, sk3 = st.columns(3)
            week_start    = today - timedelta(days=today.weekday())
            hours_this_wk = sum(
                float(str(t.get("Hours",0)) or 0)
                for t in all_timelog
                if str(t.get("Date","")) >= str(week_start)
            )
            top_client    = ""
            if all_timelog:
                from collections import Counter
                cli_hours = Counter()
                for t in all_timelog:
                    try:
                        cli_hours[str(t.get("Client",""))] += float(str(t.get("Hours",0)) or 0)
                    except Exception:
                        pass
                if cli_hours:
                    top_client = cli_hours.most_common(1)[0][0]

            with sk1:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>{hours_this_month:.1f}</span>"
                    f"<span class='dashboard-stat-label'>Hours This Month</span></div>",
                    unsafe_allow_html=True,
                )
            with sk2:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>{hours_this_wk:.1f}</span>"
                    f"<span class='dashboard-stat-label'>Hours This Week</span></div>",
                    unsafe_allow_html=True,
                )
            with sk3:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number' style='font-size:1.3em;'>{top_client or '—'}</span>"
                    f"<span class='dashboard-stat-label'>Most Hours — Client</span></div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

            # Log entry form
            st.markdown("**Log Time Entry**")
            with st.form("time_form", clear_on_submit=True):
                tf1, tf2, tf3 = st.columns([2, 2, 1])
                with tf1:
                    t_client  = st.selectbox("Client", CLIENT_LIST, key="tf_cli")
                    t_service = st.selectbox("Service", TIME_SERVICES, key="tf_svc")
                with tf2:
                    t_date    = st.date_input("Date", today, key="tf_date")
                    t_hours   = st.number_input("Hours", min_value=0.25, max_value=24.0, step=0.25, value=1.0, key="tf_hrs")
                with tf3:
                    st.markdown("<br><br><br>", unsafe_allow_html=True)
                    t_submit  = st.form_submit_button("Log")
                t_notes = st.text_input("Notes (optional)", key="tf_notes")
                if t_submit:
                    add_time_entry(t_client, t_service, t_hours, t_notes, st.session_state.username)
                    add_comm_log(t_client, "Time Log", f"{t_hours}h — {t_service}", st.session_state.username)
                    st.success(f"Logged {t_hours}h for {t_client}.")
                    st.rerun()

            st.markdown("<br>")

            # By-client summary table
            if all_timelog:
                st.markdown("**Hours by Client — This Month**")
                from collections import defaultdict
                mtd = [t for t in all_timelog if str(t.get("Date","")).startswith(this_month)]
                cli_sum = defaultdict(float)
                svc_sum = defaultdict(float)
                for t in mtd:
                    try:
                        h = float(str(t.get("Hours",0)) or 0)
                        cli_sum[str(t.get("Client",""))] += h
                        svc_sum[str(t.get("Service",""))] += h
                    except Exception:
                        pass

                if cli_sum:
                    df_cli = pd.DataFrame(
                        [{"Client": k, "Hours": round(v, 2)} for k, v in sorted(cli_sum.items(), key=lambda x: -x[1])]
                    )
                    st.dataframe(df_cli, use_container_width=True, hide_index=True)

                st.markdown("<br>")
                st.markdown("**Recent Time Entries**")
                recent = list(reversed(all_timelog[-20:]))
                for entry in recent:
                    ec1, ec2, ec3, ec4 = st.columns([2, 2, 1, 3])
                    with ec1: st.markdown(f"**{entry.get('Client','')}**")
                    with ec2: st.caption(entry.get("Service",""))
                    with ec3: st.markdown(f"**{entry.get('Hours','')}h**")
                    with ec4: st.caption(f"{entry.get('Date','')}  {entry.get('Notes','')}")
                    st.markdown("<hr style='border:none;border-top:1px solid #F0ECE7;margin:4px 0;'>", unsafe_allow_html=True)

        # ──────────────────────────────────────────────────────
        # TAB 4 — DOCUMENT REQUESTS
        # ──────────────────────────────────────────────────────
        with tab_docs:
            st.markdown("#### Document Requests")
            st.markdown("<br>", unsafe_allow_html=True)

            # Create request form
            with st.expander("Create New Document Request", expanded=False):
                with st.form("new_doc_req", clear_on_submit=True):
                    dr1, dr2 = st.columns(2)
                    with dr1:
                        dr_client   = st.selectbox("Client", CLIENT_LIST, key="dr_cli")
                        dr_template = st.selectbox("Request Template", list(DOC_REQUEST_TEMPLATES.keys()), key="dr_tmpl")
                    with dr2:
                        dr_due    = st.date_input("Due Date", today + timedelta(days=7), key="dr_due")
                        dr_custom = st.text_input("Custom Request Name (overrides template)", key="dr_name")

                    dr_cat, dr_default_desc = DOC_REQUEST_TEMPLATES[
                        st.session_state.get("dr_tmpl", "Custom Request")
                    ]
                    dr_desc = st.text_area("Description / Instructions", value=dr_default_desc, key="dr_desc", height=60)

                    if st.form_submit_button("Send Request"):
                        req_name = dr_custom.strip() or dr_template
                        add_doc_request(dr_client, req_name, dr_cat, dr_desc.strip(), dr_due)
                        add_comm_log(dr_client, "Document Request", f"Requested: {req_name}", st.session_state.username)
                        st.success(f"Document request sent to {dr_client}.")
                        st.rerun()

            st.markdown("<br>")

            # Filters
            df1, df2 = st.columns([2, 2])
            with df1:
                dr_f_cli    = st.selectbox("Filter by Client", ["All Clients"] + CLIENT_LIST, key="drf_cli")
            with df2:
                dr_f_status = st.selectbox("Filter by Status", ["All", "Pending", "Uploaded", "Approved", "Waived"], key="drf_status")

            doc_view = all_doc_req
            if dr_f_cli != "All Clients":
                doc_view = [r for r in doc_view if r.get("Client") == dr_f_cli]
            if dr_f_status != "All":
                doc_view = [r for r in doc_view if str(r.get("Status","")).strip() == dr_f_status]

            if not doc_view:
                st.info("No document requests match the current filters.")
            else:
                status_icon = {"Pending": "📄", "Uploaded": "✅", "Approved": "✔️", "Waived": "—"}
                status_class = {
                    "Pending": "doc-req-pending",
                    "Uploaded": "doc-req-uploaded",
                    "Approved": "doc-req-approved",
                    "Waived": "doc-req-waived",
                }
                for req in doc_view:
                    status   = str(req.get("Status","Pending")).strip()
                    card_cls = "doc-req-card " + status_class.get(status, "")
                    icon     = status_icon.get(status, "📄")
                    due_disp = req.get("Due Date","") or "No due date"
                    uploaded = req.get("Uploaded Date","")

                    rc1, rc2 = st.columns([5, 1])
                    with rc1:
                        st.markdown(
                            f"<div class='{card_cls}'>"
                            f"<div class='doc-req-name'>{icon}  {req.get('Request Name','')}"
                            f"  <span style='font-weight:400;color:#A8B5A3;font-size:0.85em;'>· {req.get('Client','')}</span></div>"
                            f"<div class='doc-req-meta'>{req.get('Category','')}  ·  Due: {due_disp}"
                            + (f"  ·  Uploaded: {uploaded}" if uploaded else "")
                            + f"  ·  {req.get('Description','')}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    with rc2:
                        if status == "Uploaded":
                            if st.button("Approve", key=f"dr_approve_{req['_row']}"):
                                update_doc_request(req["_row"], "Approved")
                                st.success("Marked Approved.")
                                st.rerun()
                        elif status == "Pending":
                            if st.button("Waive", key=f"dr_waive_{req['_row']}"):
                                update_doc_request(req["_row"], "Waived")
                                st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB 5 — MESSAGES
        # ──────────────────────────────────────────────────────
        with tab_msgs:
            st.markdown("#### Secure Messages")
            st.markdown("<br>", unsafe_allow_html=True)

            mc1, mc2 = st.columns([1, 2])
            with mc1:
                st.markdown("**Client Conversations**")
                for cli in CLIENT_LIST:
                    unread_marker = ""
                    if _last_sender(cli) == "client":
                        unread_marker = "<span class='unread-badge'>New</span>"
                    if st.button(
                        f"{cli}",
                        key=f"msg_cli_btn_{cli}",
                        use_container_width=True,
                    ):
                        st.session_state["msg_active_client"] = cli
                    if unread_marker:
                        st.markdown(
                            f"<p style='margin-top:-10px;font-size:0.75em;color:#C4878A;font-family:Montserrat,sans-serif;'>New message</p>",
                            unsafe_allow_html=True,
                        )

            with mc2:
                active_msg_client = st.session_state.get("msg_active_client", CLIENT_LIST[0] if CLIENT_LIST else "")
                if active_msg_client:
                    st.markdown(f"**Thread: {active_msg_client}**")
                    thread = [m for m in all_messages if str(m.get("Client","")).strip() == active_msg_client]

                    # Render chat bubbles
                    bubbles_html = "<div class='msg-area'>"
                    if not thread:
                        bubbles_html += "<div class='msg-no-messages'>No messages yet. Start the conversation below.</div>"
                    else:
                        for msg in thread:
                            stype = str(msg.get("Sender Type","")).strip()
                            sname = str(msg.get("Sender Name","")).strip()
                            mtext = str(msg.get("Message","")).strip()
                            mdate = str(msg.get("Date","")).strip()
                            if stype == "firm":
                                bubbles_html += (
                                    f"<div class='msg-row msg-row-firm'>"
                                    f"<div class='msg-meta' style='text-align:right;'>{sname}</div>"
                                    f"<div class='msg-bubble msg-bubble-firm'>{mtext}</div>"
                                    f"<div class='msg-meta' style='text-align:right;'>{mdate}</div>"
                                    f"</div>"
                                )
                            else:
                                bubbles_html += (
                                    f"<div class='msg-row msg-row-client'>"
                                    f"<div class='msg-meta'>{sname}</div>"
                                    f"<div class='msg-bubble msg-bubble-client'>{mtext}</div>"
                                    f"<div class='msg-meta'>{mdate}</div>"
                                    f"</div>"
                                )
                    bubbles_html += "</div>"
                    st.markdown(bubbles_html, unsafe_allow_html=True)

                    # Send form
                    with st.form(f"msg_firm_send_{active_msg_client}", clear_on_submit=True):
                        msg_text = st.text_area("Message", key="firm_msg_input", height=70, label_visibility="collapsed", placeholder="Type your message…")
                        if st.form_submit_button("Send"):
                            if msg_text.strip():
                                send_message(active_msg_client, "firm", st.session_state.username, msg_text.strip())
                                add_comm_log(active_msg_client, "Portal Message", msg_text.strip()[:80], st.session_state.username)
                                st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB 6 — CLIENT PROFILES
        # ──────────────────────────────────────────────────────
        with tab_profiles:
            st.markdown("#### Client Profiles")
            st.markdown("<br>", unsafe_allow_html=True)

            if "show_add_client" not in st.session_state:
                st.session_state.show_add_client = False
            if st.button("+ Add New Client", key="add_cli_btn"):
                st.session_state.show_add_client = not st.session_state.show_add_client

            if st.session_state.show_add_client:
                with st.form("add_client_form", clear_on_submit=True):
                    nc1, nc2 = st.columns(2)
                    with nc1:
                        nc_name    = st.text_input("Client / Business Name *")
                        nc_contact = st.text_input("Primary Contact")
                        nc_email   = st.text_input("Email")
                        nc_phone   = st.text_input("Phone")
                    with nc2:
                        nc_tier     = st.selectbox("Service Tier", SERVICE_TIERS)
                        nc_status   = st.selectbox("Client Status", CLIENT_STATUSES)
                        nc_rate     = st.text_input("Monthly Rate ($)")
                        nc_contract = st.selectbox("Contract Signed", ["No", "Yes"])
                    nf1, nf2 = st.columns(2)
                    with nf1:
                        nc_start = st.date_input("Engagement Start", today)
                    with nf2:
                        nc_ref = st.text_input("Referral Source")
                    if st.form_submit_button("Create Client"):
                        if not nc_name.strip():
                            st.warning("Client name required.")
                        elif nc_name.strip() in CLIENT_LIST:
                            st.warning("Client already exists.")
                        else:
                            ok = add_client(
                                nc_name.strip(), nc_contact.strip(), nc_email.strip(), nc_phone.strip(),
                                nc_tier, nc_status, nc_rate.strip(), nc_contract, nc_start, nc_ref.strip(),
                            )
                            if ok:
                                st.success(f"'{nc_name.strip()}' added.")
                                st.session_state.show_add_client = False
                                st.rerun()
                            else:
                                st.error("Could not add client.")

            st.markdown("<br>", unsafe_allow_html=True)

            status_badge_map = {
                "Active": "badge-done", "Onboarding": "badge-progress",
                "On Hold": "badge-waiting", "Offboarding": "badge-open",
                "Prospect": "badge-open",
            }

            for client in CLIENT_LIST:
                rec       = CLI_LOOKUP.get(client, {})
                cli_tasks = [t for t in all_tasks if t.get("client") == client and str(t.get("status","")).strip() != "Completed"]
                cli_inv   = [i for i in all_invoices if i.get("client") == client and str(i.get("status","")).strip().lower() != "paid"]
                cli_ar    = sum(float(str(i.get("amount","")).replace("$","").replace(",","").strip() or 0) for i in cli_inv)
                cli_hrs   = sum(float(str(t.get("Hours",0)) or 0) for t in all_timelog if t.get("Client") == client and str(t.get("Date","")).startswith(this_month))
                attn_chip = "<span class='attention-chip'>Needs Attention</span>" if client in clients_needing_attn else ""
                s_val     = str(rec.get("Client Status","Active")).strip()
                s_badge   = status_badge_map.get(s_val, "badge-open")

                with st.expander(client, expanded=False):
                    st.markdown(
                        f"<span class='status-badge {s_badge}'>{s_val}</span>{attn_chip}",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    pm1, pm2, pm3, pm4 = st.columns(4)
                    with pm1: st.metric("Open Tasks",      len(cli_tasks))
                    with pm2: st.metric("Unpaid Invoices", len(cli_inv))
                    with pm3: st.metric("AR Outstanding",  f"${cli_ar:,.2f}")
                    with pm4: st.metric("Hours This Month", f"{cli_hrs:.1f}h")

                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    pd1, pd2, pd3 = st.columns(3)
                    fields = [
                        ("Contact", "Contact Name"),
                        ("Email", "Email"),
                        ("Phone", "Phone"),
                        ("Service Tier", "Service Tier"),
                        ("Monthly Rate", "Monthly Rate"),
                        ("Contract Signed", "Contract Signed"),
                        ("Engagement Start", "Engagement Start"),
                        ("Referral Source", "Referral Source"),
                        ("Last Contacted", "Last Contacted"),
                    ]
                    for i, (label, key) in enumerate(fields):
                        val = str(rec.get(key, "") or "") or "—"
                        col = [pd1, pd2, pd3][i % 3]
                        with col:
                            st.markdown(
                                f"<div class='profile-field-label'>{label}</div>"
                                f"<div class='profile-field-value'>{val}</div>",
                                unsafe_allow_html=True,
                            )

                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    # Quick comm log
                    st.markdown("**Log Communication**")
                    lc1, lc2, lc3 = st.columns([2, 3, 1])
                    with lc1:
                        log_type = st.selectbox(
                            "Type", ["Email","Call","Meeting","Portal Message","Text","Other"],
                            key=f"lt_{client}", label_visibility="collapsed",
                        )
                    with lc2:
                        log_sum = st.text_input(
                            "Summary", key=f"ls_{client}",
                            placeholder="Brief note…", label_visibility="collapsed",
                        )
                    with lc3:
                        if st.button("Log", key=f"lb_{client}"):
                            if log_sum.strip():
                                add_comm_log(client, log_type, log_sum.strip(), st.session_state.username)
                                st.success("Logged.")
                                st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Internal notes
                    nk = f"notes_{client.replace(' ','_')}"
                    if nk not in st.session_state:
                        st.session_state[nk] = str(rec.get("Internal Notes","") or "")
                    st.markdown("**Internal Notes** *(firm-only)*")
                    new_note = st.text_area(
                        "Notes", value=st.session_state[nk],
                        key=f"ni_{client}", height=70,
                        label_visibility="collapsed",
                        placeholder="Add notes about this client…",
                    )
                    if new_note != st.session_state[nk]:
                        st.session_state[nk] = new_note
                        update_client_col(client, "Internal Notes", new_note)

        # ──────────────────────────────────────────────────────
        # TAB 7 — ACTIVITY LOG
        # ──────────────────────────────────────────────────────
        with tab_log:
            st.markdown("#### Activity Log")
            st.markdown("<br>", unsafe_allow_html=True)

            al1, al2 = st.columns([2, 2])
            with al1:
                al_cli  = st.selectbox("Filter by Client", ["All Clients"] + CLIENT_LIST, key="al_cli")
            with al2:
                al_type = st.selectbox(
                    "Filter by Type",
                    ["All","Email","Call","Meeting","Portal Message","Text",
                     "Time Log","Document Request","Task Update","Invoice","Other"],
                    key="al_type",
                )

            log_view = list(reversed(all_comm))
            if al_cli != "All Clients":
                log_view = [e for e in log_view if e.get("Client") == al_cli]
            if al_type != "All":
                log_view = [e for e in log_view if e.get("Type") == al_type]

            type_icons = {
                "Email":"📧","Call":"📞","Meeting":"🤝","Portal Message":"💬","Text":"📱",
                "Time Log":"⏱","Document Request":"📄","Task Update":"✅","Invoice":"🧾","Other":"📋",
            }

            if not log_view:
                st.info("No activity logged yet.")
            else:
                for entry in log_view[:60]:
                    icon = type_icons.get(str(entry.get("Type","")), "📋")
                    st.markdown(
                        f"<div class='activity-entry'>"
                        f"{icon}&nbsp; <strong>{entry.get('Client','')}</strong>"
                        f"&nbsp;·&nbsp;<span style='color:#A8B5A3;font-size:0.85em;'>{entry.get('Type','')}</span><br>"
                        f"<span style='color:#555;'>{entry.get('Summary','')}</span>"
                        f"&nbsp;&nbsp;<span style='color:#A8B5A3;font-size:0.82em;'>{entry.get('Date','')}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("**Log New Entry**")
            with st.form("global_log_form", clear_on_submit=True):
                gl1, gl2, gl3 = st.columns([2, 2, 3])
                with gl1: gl_cli  = st.selectbox("Client", CLIENT_LIST)
                with gl2: gl_type = st.selectbox("Type", ["Email","Call","Meeting","Portal Message","Text","Other"])
                with gl3: gl_sum  = st.text_input("Summary")
                if st.form_submit_button("Add to Log"):
                    if gl_sum.strip():
                        add_comm_log(gl_cli, gl_type, gl_sum.strip(), st.session_state.username)
                        st.success("Logged.")
                        st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB 8 — PIPELINE
        # ──────────────────────────────────────────────────────
        with tab_pipe:
            st.markdown("#### Prospect Pipeline")
            st.markdown("<br>", unsafe_allow_html=True)

            if "show_add_lead" not in st.session_state:
                st.session_state.show_add_lead = False
            if st.button("+ Add Lead", key="add_lead_btn"):
                st.session_state.show_add_lead = not st.session_state.show_add_lead

            if st.session_state.show_add_lead:
                with st.form("add_lead_form", clear_on_submit=True):
                    pl1, pl2 = st.columns(2)
                    with pl1:
                        pl_name    = st.text_input("Business / Lead Name *")
                        pl_contact = st.text_input("Contact Name")
                        pl_email   = st.text_input("Email")
                    with pl2:
                        pl_service = st.multiselect("Service Interest", SERVICE_TIERS)
                        pl_stage   = st.selectbox("Stage", PIPELINE_STAGES)
                        pl_value   = st.text_input("Est. Monthly Value ($)")
                    pl_follow = st.date_input("Follow-Up Date", today)
                    pl_notes  = st.text_area("Notes", height=60)
                    if st.form_submit_button("Add Lead"):
                        if not pl_name.strip():
                            st.warning("Lead name required.")
                        else:
                            ok = add_pipeline_lead(
                                pl_name.strip(), pl_contact.strip(), pl_email.strip(),
                                ", ".join(pl_service), pl_stage,
                                pl_value.strip(), pl_follow, pl_notes.strip(),
                            )
                            if ok:
                                st.success(f"'{pl_name.strip()}' added to pipeline.")
                                st.session_state.show_add_lead = False
                                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            stage_badge_cls = {
                "New Lead":"stage-new","Proposal Sent":"stage-proposal",
                "Proposal Accepted":"stage-accepted","Onboarding":"stage-onboarding",
                "Closed Lost":"badge-open",
            }

            for stage in PIPELINE_STAGES:
                leads = [p for p in all_pipeline if str(p.get("Stage","")).strip() == stage]
                if not leads: continue
                _sbadge = stage_badge_cls.get(stage, "badge-open")
                st.markdown(
                    f"<span class='pipeline-stage {_sbadge}'>{stage}</span>"
                    f"<span style='color:#A8B5A3;font-size:0.82em;margin-left:8px;'>{len(leads)} lead(s)</span>",
                    unsafe_allow_html=True,
                )
                for lead in leads:
                    lname = str(lead.get("Lead Name","")).strip()
                    with st.expander(lname, expanded=False):
                        lc1, lc2, lc3 = st.columns(3)
                        defs = [
                            ("Contact", "Contact"), ("Email", "Email"),
                            ("Service Interest", "Service Interest"),
                            ("Est. Monthly Value", "Est Monthly Value"),
                            ("Follow-Up Date", "Follow Up Date"),
                            ("Date Added", "Date Added"),
                        ]
                        for i, (lbl, key) in enumerate(defs):
                            val = str(lead.get(key,"") or "") or "—"
                            with [lc1,lc2,lc3][i % 3]:
                                st.markdown(
                                    f"<div class='profile-field-label'>{lbl}</div>"
                                    f"<div class='profile-field-value'>{val}</div>",
                                    unsafe_allow_html=True,
                                )
                        if lead.get("Notes"):
                            st.markdown(f"<div class='note-box'>{lead.get('Notes')}</div>", unsafe_allow_html=True)
                        new_stage = st.selectbox(
                            "Move to Stage", PIPELINE_STAGES,
                            index=PIPELINE_STAGES.index(stage) if stage in PIPELINE_STAGES else 0,
                            key=f"ps_{lname}",
                        )
                        if new_stage != stage and st.button("Update Stage", key=f"pu_{lname}"):
                            update_pipeline_stage(lname, new_stage)
                            st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # CLIENT WORKSPACE
    # ══════════════════════════════════════════════════════════
    else:
        st.markdown(
            f"<h5 style='font-family:Montserrat,Lato,sans-serif;letter-spacing:0.12em;"
            f"text-transform:uppercase;color:#A8B5A3;font-size:0.78rem;font-weight:600;'>"
            f"Workspace: {active_client}</h5>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Client-side data slices
        cli_tasks   = [dict(r, _row=i+2) for i, r in enumerate(all_tasks) if r.get("client") == active_client]
        cli_inv     = [dict(r, _row=i+2) for i, r in enumerate(all_invoices) if r.get("client") == active_client]
        cli_doc_req = [r for r in all_doc_req if str(r.get("Client","")).strip() == active_client]
        cli_msgs    = [r for r in all_messages if str(r.get("Client","")).strip() == active_client]
        unpaid_cli  = [i for i in cli_inv if str(i.get("status","")).strip().lower() != "paid"]
        paid_cli    = [i for i in cli_inv if str(i.get("status","")).strip().lower() == "paid"]
        pending_req = [r for r in cli_doc_req if str(r.get("Status","")).strip() == "Pending"]
        awaiting    = [t for t in cli_tasks if str(t.get("status","")).strip() == "Awaiting Client"]
        open_cli    = [t for t in cli_tasks if str(t.get("status","")).strip() not in ("Completed",)]

        # Count unread (firm messages client hasn't replied to - approximate)
        unread_for_client = sum(1 for m in cli_msgs if str(m.get("Sender Type","")).strip() == "firm")

        tab_todo, tab_cmsg, tab_cdocs, tab_cinv = st.tabs([
            "My To-Do", "Messages", "Documents", "Invoices & Payments",
        ])

        # ──────────────────────────────────────────────────────
        # CLIENT TAB 1 — MY TO-DO  (Hero view)
        # ──────────────────────────────────────────────────────
        with tab_todo:
            # Build the combined to-do list in priority order:
            # 1. Overdue invoices  2. Pending doc requests  3. Awaiting Client tasks  4. All open tasks
            todo_items = []

            # Invoices
            total_cli_ar = sum(
                float(str(i.get("amount","")).replace("$","").replace(",","").strip() or 0)
                for i in unpaid_cli
                if str(i.get("amount","")).replace("$","").replace(",","").strip()
            )
            if unpaid_cli:
                todo_items.append({"type":"invoice_summary","invoices":unpaid_cli,"total":total_cli_ar})

            # Document requests
            for req in pending_req:
                todo_items.append({"type":"doc","req":req})

            # Tasks awaiting client (priority)
            for t in awaiting:
                todo_items.append({"type":"task","task":t,"priority":True})

            # Other open tasks
            for t in open_cli:
                status = str(t.get("status","")).strip()
                if status not in ("Awaiting Client","Completed"):
                    todo_items.append({"type":"task","task":t,"priority":False})

            if not todo_items:
                st.markdown(
                    "<div class='all-clear'>"
                    "<span class='all-clear-icon'>✓</span>"
                    "<span class='all-clear-text'>You're all caught up — nothing needs your attention right now.</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.9em;margin-bottom:16px;'>"
                    f"You have <strong>{len(todo_items)}</strong> item(s) that need your attention.</p>",
                    unsafe_allow_html=True,
                )
                for item in todo_items:
                    # ── Invoice block ──
                    if item["type"] == "invoice_summary":
                        inv_list = item["invoices"]
                        total    = item["total"]
                        st.markdown(
                            f"<div class='todo-card todo-card-invoice'>"
                            f"<div class='todo-type todo-type-invoice'>Payment Due</div>"
                            f"<div class='todo-title'>Balance Outstanding — ${total:,.2f}</div>"
                            f"<div class='todo-meta'>{len(inv_list)} unpaid invoice(s)</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        for inv in inv_list:
                            ic1, ic2 = st.columns([3, 1])
                            with ic1:
                                st.markdown(
                                    f"<div class='portal-card' style='margin-bottom:6px;'>"
                                    f"<strong>Invoice #{inv.get('invoice_num','')}</strong>"
                                    f"&nbsp;&nbsp;<span style='color:#333;font-size:1.05em;'>{inv.get('amount','')}</span><br>"
                                    f"<span style='color:#A8B5A3;font-size:0.84em;'>Due: {inv.get('due_date','')}</span>"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )
                            with ic2:
                                pay_link = inv.get("pay_link","")
                                if pay_link:
                                    st.markdown(
                                        f"<a href='{pay_link}' target='_blank' class='invoice-btn'>Pay Now</a>",
                                        unsafe_allow_html=True,
                                    )
                                if admin:
                                    if st.button(f"Mark Paid #{inv.get('invoice_num','')}", key=f"cp_{inv['_row']}"):
                                        mark_invoice_paid(inv["_row"])
                                        st.rerun()

                    # ── Document request ──
                    elif item["type"] == "doc":
                        req     = item["req"]
                        due_str = str(req.get("Due Date","")).strip()
                        st.markdown(
                            f"<div class='todo-card todo-card-doc'>"
                            f"<div class='todo-type todo-type-doc'>Document Needed</div>"
                            f"<div class='todo-title'>{req.get('Request Name','')}</div>"
                            f"<div class='todo-meta'>{req.get('Category','')}  ·  Due: {due_str or 'No deadline'}  ·  {req.get('Description','')}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        up_key = f"todo_up_{req['_row']}"
                        if st.session_state.get(f"show_{up_key}"):
                            doc_file = st.file_uploader(
                                f"Upload for: {req.get('Request Name','')}",
                                key=up_key,
                                type=["pdf","png","jpg","csv","xlsx","docx"],
                            )
                            if doc_file:
                                with st.spinner("Uploading…"):
                                    fid = upload_to_drive(active_client, doc_file)
                                if fid:
                                    update_doc_request(req["_row"], "Uploaded", fid)
                                    add_comm_log(active_client, "Document Request", f"Uploaded: {req.get('Request Name','')}", active_client)
                                    st.success("Uploaded! Your accountant will review it shortly.")
                                    st.session_state[f"show_{up_key}"] = False
                                    st.rerun()
                        else:
                            if st.button("Upload Document", key=f"todo_show_{req['_row']}"):
                                st.session_state[f"show_{up_key}"] = True
                                st.rerun()

                    # ── Task ──
                    elif item["type"] == "task":
                        t      = item["task"]
                        status = str(t.get("status","")).strip()
                        due_s  = str(t.get("due","")).strip()
                        badgekey = {"Pending":"badge-open","In Progress":"badge-progress","Awaiting Client":"badge-waiting"}.get(status,"badge-open")
                        st.markdown(
                            f"<div class='todo-card todo-card-task'>"
                            f"<div class='todo-type todo-type-task'>"
                            + ("Action Required" if status=="Awaiting Client" else "In Progress")
                            + f"</div>"
                            f"<div class='todo-title'>{str(t.get('task','')) or '*(Untitled)*'}</div>"
                            f"<div class='todo-meta'><span class='status-badge {badgekey}'>{status}</span>"
                            + (f"  ·  Due: {due_s}" if due_s else "")
                            + f"</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        if status == "Awaiting Client":
                            mark_done = st.button("Mark Complete", key=f"cli_done_{t['_row']}")
                            if mark_done:
                                update_task_status(t["_row"], "Completed")
                                st.rerun()

        # ──────────────────────────────────────────────────────
        # CLIENT TAB 2 — MESSAGES
        # ──────────────────────────────────────────────────────
        with tab_cmsg:
            st.markdown("<h3>Messages</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.88em;'>"
                f"Send a message to your bookkeeper. We typically respond within one business day.</p>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # Thread display
            bubbles_html = "<div class='msg-area'>"
            if not cli_msgs:
                bubbles_html += "<div class='msg-no-messages'>No messages yet. Send us a note below!</div>"
            else:
                for msg in cli_msgs:
                    stype = str(msg.get("Sender Type","")).strip()
                    sname = str(msg.get("Sender Name","")).strip()
                    mtext = str(msg.get("Message","")).strip()
                    mdate = str(msg.get("Date","")).strip()
                    if stype == "firm":
                        bubbles_html += (
                            f"<div class='msg-row msg-row-firm'>"
                            f"<div class='msg-meta' style='text-align:right;'>Clearly Better Books</div>"
                            f"<div class='msg-bubble msg-bubble-firm'>{mtext}</div>"
                            f"<div class='msg-meta' style='text-align:right;'>{mdate}</div>"
                            f"</div>"
                        )
                    else:
                        bubbles_html += (
                            f"<div class='msg-row msg-row-client'>"
                            f"<div class='msg-meta'>{sname}</div>"
                            f"<div class='msg-bubble msg-bubble-client'>{mtext}</div>"
                            f"<div class='msg-meta'>{mdate}</div>"
                            f"</div>"
                        )
            bubbles_html += "</div>"
            st.markdown(bubbles_html, unsafe_allow_html=True)

            with st.form("cli_msg_form", clear_on_submit=True):
                cli_msg_text = st.text_area(
                    "Your message", height=90, label_visibility="collapsed",
                    placeholder="Type your message here…",
                )
                if st.form_submit_button("Send Message"):
                    if cli_msg_text.strip():
                        send_message(active_client, "client", active_client, cli_msg_text.strip())
                        add_comm_log(active_client, "Portal Message", cli_msg_text.strip()[:80], active_client)
                        st.success("Message sent!")
                        st.rerun()

        # ──────────────────────────────────────────────────────
        # CLIENT TAB 3 — DOCUMENTS
        # ──────────────────────────────────────────────────────
        with tab_cdocs:
            st.markdown("<h3>Documents</h3>", unsafe_allow_html=True)

            # Requested documents checklist
            if cli_doc_req:
                st.markdown("#### Requested Documents")
                st.markdown(
                    "<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.88em;'>"
                    "Your bookkeeper has requested the following documents. Please upload each item below.</p>",
                    unsafe_allow_html=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)

                status_icon  = {"Pending":"📄","Uploaded":"✅","Approved":"✔️","Waived":"—"}
                status_class = {"Pending":"doc-req-pending","Uploaded":"doc-req-uploaded","Approved":"doc-req-approved","Waived":"doc-req-waived"}

                for req in cli_doc_req:
                    status   = str(req.get("Status","Pending")).strip()
                    card_cls = "doc-req-card " + status_class.get(status,"")
                    icon     = status_icon.get(status,"📄")
                    due_disp = req.get("Due Date","") or "No deadline"

                    st.markdown(
                        f"<div class='{card_cls}'>"
                        f"<div class='doc-req-name'>{icon}  {req.get('Request Name','')}</div>"
                        f"<div class='doc-req-meta'>{req.get('Category','')}  ·  Due: {due_disp}"
                        + (f"  ·  <em>{req.get('Description','')}</em>" if req.get("Description") else "")
                        + f"</div></div>",
                        unsafe_allow_html=True,
                    )

                    if status == "Pending":
                        up_key = f"cdoc_up_{req['_row']}"
                        if not st.session_state.get(f"show_{up_key}"):
                            if st.button("Upload", key=f"cdoc_show_{req['_row']}"):
                                st.session_state[f"show_{up_key}"] = True
                                st.rerun()
                        else:
                            uf = st.file_uploader(
                                f"Upload: {req.get('Request Name','')}",
                                key=up_key,
                                type=["pdf","png","jpg","csv","xlsx","docx"],
                            )
                            if uf:
                                with st.spinner("Uploading to your secure folder…"):
                                    fid = upload_to_drive(active_client, uf)
                                if fid:
                                    update_doc_request(req["_row"], "Uploaded", fid)
                                    add_comm_log(active_client, "Document Request", f"Uploaded: {req.get('Request Name','')}", active_client)
                                    st.success("Uploaded successfully!")
                                    st.session_state[f"show_{up_key}"] = False
                                    st.rerun()
                    elif status == "Uploaded":
                        st.caption("Uploaded — awaiting your bookkeeper's review.")
                    elif status == "Approved":
                        st.caption("Approved — thank you!")

                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

            # General file upload
            st.markdown("#### Upload a Document")
            st.markdown(
                "<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.88em;'>"
                "Upload any additional files to your secure Google Drive folder below.</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='upload-zone'>"
                "<div class='custom-upload-title'>Secure File Drop</div>"
                "<div class='custom-upload-subtitle'>PDF, PNG, JPG, CSV, XLSX, DOCX · Max 200MB</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            if "show_general_up" not in st.session_state:
                st.session_state.show_general_up = False
            if st.button("Select File", key="gen_up_btn"):
                st.session_state.show_general_up = True
            if st.session_state.show_general_up:
                gen_file = st.file_uploader(
                    "File", label_visibility="collapsed",
                    type=["pdf","png","jpg","csv","xlsx","docx"],
                )
                if gen_file:
                    with st.spinner("Uploading to your secure Google Drive folder…"):
                        fid = upload_to_drive(active_client, gen_file)
                    if fid:
                        add_comm_log(active_client, "Document Request", f"General upload: {gen_file.name}", active_client)
                        st.success("File saved to your secure folder.")
                    else:
                        st.error("Upload failed. Please try again or contact support.")

        # ──────────────────────────────────────────────────────
        # CLIENT TAB 4 — INVOICES & PAYMENTS
        # ──────────────────────────────────────────────────────
        with tab_cinv:
            st.markdown("<h3>Invoices & Payments</h3>", unsafe_allow_html=True)

            total_cli_ar = sum(
                float(str(i.get("amount","")).replace("$","").replace(",","").strip() or 0)
                for i in unpaid_cli
                if str(i.get("amount","")).replace("$","").replace(",","").strip()
            )

            if unpaid_cli:
                st.markdown(
                    f"<p style='font-family:Lato,sans-serif;font-size:1.05em;'>"
                    f"<strong>Total Outstanding: ${total_cli_ar:,.2f}</strong></p>",
                    unsafe_allow_html=True,
                )

            st.markdown("#### Outstanding Balance")
            if not unpaid_cli:
                st.success("No unpaid invoices on your account.")
            else:
                for inv in unpaid_cli:
                    st.markdown(
                        f"<div class='portal-card'>"
                        f"<table style='width:100%;border:none;background:none;margin:0;padding:0;'>"
                        f"<tr style='background:none;border:none;'>"
                        f"<td style='border:none;width:45%;padding:0;'>"
                        f"<span style='font-family:Playfair Display,Georgia,serif;font-size:1.2em;font-weight:600;'>Invoice #{inv.get('invoice_num','')}</span><br>"
                        f"<span style='font-size:0.83rem;color:#A8B5A3;font-family:Lato,sans-serif;'>Due: {inv.get('due_date','')}</span>"
                        f"</td>"
                        f"<td style='border:none;width:25%;vertical-align:middle;padding:0;'>"
                        f"<span style='font-size:1.5em;font-weight:600;font-family:Playfair Display,Georgia,serif;'>{inv.get('amount','')}</span>"
                        f"</td>"
                        f"<td style='border:none;width:30%;text-align:right;vertical-align:middle;padding:0;'>"
                        f"<a href='{inv.get('pay_link','')}' target='_blank' class='invoice-btn'>Pay Invoice</a>"
                        f"</td>"
                        f"</tr></table></div>",
                        unsafe_allow_html=True,
                    )
                    if admin:
                        if st.button(f"Mark Paid — #{inv.get('invoice_num','')}", key=f"ip_{inv['_row']}"):
                            mark_invoice_paid(inv["_row"])
                            st.success("Marked as paid.")
                            st.rerun()

            if paid_cli:
                st.markdown("<br>")
                st.markdown("#### Payment History")
                for inv in paid_cli:
                    pc1, pc2, pc3 = st.columns([3, 2, 2])
                    with pc1: st.markdown(f"~~Invoice #{inv.get('invoice_num','')}~~")
                    with pc2: st.markdown(f"~~{inv.get('amount','')}~~")
                    with pc3: st.caption("Processed")

            if admin:
                st.markdown("<hr class='section-divider'>")
                st.markdown("<h3>Log New Invoice</h3>", unsafe_allow_html=True)
                with st.form("new_inv_form", clear_on_submit=True):
                    if1, if2 = st.columns(2)
                    with if1:
                        inv_num = st.text_input("Invoice Number")
                        inv_amt = st.text_input("Amount ($)")
                    with if2:
                        inv_due = st.date_input("Due Date", today)
                        inv_url = st.text_input("Payment Link URL")
                    if st.form_submit_button("Post Invoice") and inv_num and inv_amt:
                        add_invoice(active_client, inv_num, inv_amt, inv_due, inv_url)
                        st.success("Invoice logged.")
                        st.rerun()
