import streamlit as st
import pandas as pd
import requests
import urllib.parse
from collections import defaultdict, Counter
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
details summary { font-family: 'Lato', sans-serif !important; font-weight: 600 !important; color: #333333 !important; letter-spacing: 0.02em !important; }
details[open] summary { color: #A8B5A3 !important; }

/* ── Brand header ── */
h1.brand-title { font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important; font-size: 2.6rem !important; letter-spacing: 0.01em !important; color: #333333 !important; text-align: center !important; margin-bottom: 0.2rem !important; }
p.brand-tagline { font-family: 'Lato', sans-serif !important; font-style: italic !important; font-size: 1.0rem !important; color: #A8B5A3 !important; text-align: center !important; margin-top: 0 !important; letter-spacing: 0.02em !important; }
div.brand-divider { width: 60px !important; height: 1px !important; background-color: #A8B5A3 !important; margin: 1rem auto 1.5rem auto !important; }
h2, h3, h4, h5, h6 { font-family: 'Playfair Display', Georgia, serif !important; font-weight: 400 !important; color: #333333 !important; }

/* ── Tabs ── */
button[data-baseweb="tab"] { font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 500 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; color: #888888 !important; background: transparent !important; border: none !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #A8B5A3 !important; border-bottom: 2px solid #A8B5A3 !important; }
div[data-baseweb="tab-highlight"] { background-color: #A8B5A3 !important; }
div[data-baseweb="tab-border"] { background-color: #DADDD6 !important; }

/* ── Buttons ── */
.stButton > button { background-color: #A8B5A3 !important; color: #FFFFFF !important; border: none !important; border-radius: 3px !important; font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; padding: 0.5rem 1.4rem !important; transition: background-color 0.2s ease !important; }
.stButton > button:hover { background-color: #8FA189 !important; }
.stFormSubmitButton > button { background-color: #A8B5A3 !important; color: #FFFFFF !important; border: none !important; border-radius: 3px !important; font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
a.invoice-btn { display: inline-block !important; background-color: #A8B5A3 !important; color: #FFFFFF !important; text-decoration: none !important; padding: 7px 18px !important; border-radius: 3px !important; font-family: 'Montserrat', sans-serif !important; font-size: 0.76rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
a.link-btn { display: inline-block !important; background-color: #F7F3EE !important; color: #A8B5A3 !important; text-decoration: none !important; padding: 5px 14px !important; border-radius: 3px !important; border: 1px solid #DADDD6 !important; font-family: 'Montserrat', sans-serif !important; font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }

/* ── Inputs ── */
.stTextInput input, .stSelectbox select, .stTextArea textarea, div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { border: 1px solid #DADDD6 !important; border-radius: 3px !important; background-color: #FAFAF8 !important; color: #333333 !important; font-family: 'Lato', sans-serif !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #A8B5A3 !important; box-shadow: 0 0 0 2px rgba(168,181,163,0.18) !important; }
div[data-testid="stFileUploader"] section { background-color: #F7F3EE !important; border: 1px dashed #A8B5A3 !important; border-radius: 4px !important; }
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

/* ── Badges ── */
.status-badge { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 0.75em; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-family: 'Montserrat', sans-serif; }
.badge-open     { background: #F7F3EE; color: #A8B5A3; border: 1px solid #DADDD6; }
.badge-progress { background: #EAF0E8; color: #6E8A69; border: 1px solid #C5D4C2; }
.badge-waiting  { background: #FAF2F1; color: #C4878A; border: 1px solid #EBC6C1; }
.badge-done     { background: #F0F3EF; color: #7A9477; border: 1px solid #C2D1BF; }
.attention-chip { display: inline-block; background: #FAF2F1; color: #C4878A; border: 1px solid #EBC6C1; border-radius: 2px; padding: 2px 8px; font-size: 0.72em; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-left: 8px; }
.unread-badge { display: inline-block; background: #C4878A; color: white; border-radius: 10px; padding: 1px 7px; font-size: 0.72em; font-family: 'Montserrat', sans-serif; font-weight: 600; margin-left: 6px; }

/* ── Pipeline ── */
.pipeline-stage { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 0.75em; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-family: 'Montserrat', sans-serif; }
.stage-new        { background: #EEF0FA; color: #6678B1; border: 1px solid #C2CAE8; }
.stage-proposal   { background: #FFF4E6; color: #B87333; border: 1px solid #F0D4B0; }
.stage-accepted   { background: #EAF0E8; color: #6E8A69; border: 1px solid #C5D4C2; }
.stage-onboarding { background: #F0F3EF; color: #7A9477; border: 1px solid #C2D1BF; }

/* ── Profile fields ── */
.profile-field-label { font-family: 'Montserrat', sans-serif; font-size: 0.72em; letter-spacing: 0.1em; text-transform: uppercase; color: #A8B5A3; margin-bottom: 2px; }
.profile-field-value { font-family: 'Lato', sans-serif; font-size: 0.95em; color: #333333; margin-bottom: 12px; }

/* ── Today's Focus ── */
.focus-panel { background: linear-gradient(135deg, #FFFFFF 0%, #F7F3EE 100%); border: 1px solid #DADDD6; border-left: 4px solid #A8B5A3; border-radius: 4px; padding: 20px 24px; margin-bottom: 24px; }
.focus-greeting { font-family: 'Playfair Display', Georgia, serif; font-size: 1.25em; font-weight: 600; color: #333333; margin-bottom: 2px; }
.focus-date-line { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #A8B5A3; margin-bottom: 14px; }
.focus-item { display: flex; align-items: flex-start; gap: 10px; padding: 7px 0; border-bottom: 1px solid #F0ECE7; font-family: 'Lato', sans-serif; font-size: 0.9em; }
.focus-item:last-child { border-bottom: none; }
.focus-clear { font-family: 'Lato', sans-serif; font-size: 0.9em; color: #7A9477; padding: 4px 0; }

/* ── Health score ── */
.health-green { color: #7A9477; font-weight: 700; }
.health-amber { color: #D4956A; font-weight: 700; }
.health-red   { color: #C4878A; font-weight: 700; }

/* ── Global search ── */
.search-result { background: #FAFAF8; border: 1px solid #DADDD6; border-radius: 3px; padding: 10px 14px; margin-bottom: 8px; }
.search-type  { font-family: 'Montserrat', sans-serif; font-size: 0.65em; text-transform: uppercase; letter-spacing: 0.1em; color: #A8B5A3; margin-bottom: 2px; }
.search-title { font-family: 'Lato', sans-serif; font-size: 0.92em; font-weight: 600; color: #333; }
.search-meta  { font-family: 'Lato', sans-serif; font-size: 0.8em; color: #888; }

/* ── AI draft box ── */
.ai-box { background: #F3EEF8; border: 1px solid #D4C5E8; border-radius: 4px; padding: 14px 16px; margin-top: 8px; font-family: 'Lato', sans-serif; font-size: 0.88em; line-height: 1.6; white-space: pre-wrap; }
.ai-label { font-family: 'Montserrat', sans-serif; font-size: 0.7em; text-transform: uppercase; letter-spacing: 0.1em; color: #9B85B3; font-weight: 700; margin-bottom: 6px; }

/* ── Month close ── */
.close-done    { background: #EAF0E8; border-left: 3px solid #7A9477; border-radius: 3px; padding: 10px 14px; margin-bottom: 6px; }
.close-active  { background: #FFF9F5; border-left: 3px solid #D4956A; border-radius: 3px; padding: 10px 14px; margin-bottom: 6px; }
.close-pending { background: #FAFAF8; border-left: 3px solid #DADDD6; border-radius: 3px; padding: 10px 14px; margin-bottom: 6px; }
.close-label   { font-family: 'Montserrat', sans-serif; font-size: 0.7em; text-transform: uppercase; letter-spacing: 0.1em; color: #A8B5A3; }
.close-name    { font-family: 'Lato', sans-serif; font-weight: 600; font-size: 0.95em; color: #333; }

/* ── Messaging ── */
.msg-area { border: 1px solid #DADDD6; border-radius: 4px; padding: 16px; background: #FAFAF8; min-height: 200px; max-height: 420px; overflow-y: auto; margin-bottom: 12px; }
.msg-bubble { max-width: 78%; padding: 10px 14px; border-radius: 12px; font-family: 'Lato', sans-serif; font-size: 0.92em; line-height: 1.5; margin-bottom: 4px; }
.msg-bubble-firm   { background: #EAF0E8; color: #2D4A2A; border-radius: 12px 12px 2px 12px; margin-left: auto; }
.msg-bubble-client { background: #F7F3EE; color: #333333; border: 1px solid #DADDD6; border-radius: 12px 12px 12px 2px; }
.msg-row        { display: flex; flex-direction: column; margin: 8px 0; }
.msg-row-firm   { align-items: flex-end; }
.msg-row-client { align-items: flex-start; }
.msg-meta { font-family: 'Montserrat', sans-serif; font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.07em; color: #A8B5A3; margin-bottom: 2px; }
.msg-no-messages { text-align: center; color: #A8B5A3; font-family: 'Lato', sans-serif; font-size: 0.9em; padding: 40px 0; }

/* ── Document requests ── */
.doc-req-card     { background: #FFFFFF; border: 1px solid #DADDD6; border-radius: 4px; padding: 14px 18px; margin-bottom: 10px; }
.doc-req-pending  { border-left: 3px solid #D4956A; }
.doc-req-uploaded { border-left: 3px solid #A8B5A3; }
.doc-req-approved { border-left: 3px solid #7A9477; opacity: 0.82; }
.doc-req-waived   { border-left: 3px solid #DADDD6; opacity: 0.55; }
.doc-req-name     { font-family: 'Lato', sans-serif; font-weight: 600; font-size: 0.98em; color: #333333; margin-bottom: 2px; }
.doc-req-meta     { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #888888; }

/* ── Client To-Do ── */
.todo-card         { background: #FFFFFF; border: 1px solid #DADDD6; border-radius: 4px; padding: 16px 20px; margin-bottom: 12px; }
.todo-card-task    { border-left: 3px solid #A8B5A3; }
.todo-card-doc     { border-left: 3px solid #D4956A; }
.todo-card-invoice { border-left: 3px solid #C4878A; }
.todo-type         { font-family: 'Montserrat', sans-serif; font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 3px; }
.todo-type-task    { color: #A8B5A3; }
.todo-type-doc     { color: #D4956A; }
.todo-type-invoice { color: #C4878A; }
.todo-title        { font-family: 'Lato', sans-serif; font-size: 1.0em; font-weight: 600; color: #333333; margin-bottom: 2px; }
.todo-meta         { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #888888; }
.all-clear         { text-align: center; padding: 40px 0; }
.all-clear-icon    { font-size: 2.5em; display: block; margin-bottom: 8px; }
.all-clear-text    { font-family: 'Playfair Display', serif; font-size: 1.1em; color: #A8B5A3; }

/* ── Upload ── */
.upload-zone { background: #F7F3EE; border: 1px dashed #A8B5A3; border-radius: 4px; padding: 20px 24px; text-align: center; margin-bottom: 14px; }
.custom-upload-title    { font-family: 'Playfair Display', serif; font-size: 1.1em; color: #333333; margin-bottom: 4px; }
.custom-upload-subtitle { font-family: 'Lato', sans-serif; font-size: 0.82em; color: #888888; }

/* ── Misc ── */
.section-divider { border: none; border-top: 1px solid #DADDD6; margin: 24px 0; }
.note-box   { background: #F7F3EE; border: 1px solid #DADDD6; border-radius: 4px; padding: 12px 16px; font-size: 0.9em; color: #555; margin-top: 8px; font-family: 'Lato', sans-serif; }
.time-entry-row { padding: 8px 0; border-bottom: 1px solid #F0ECE7; font-family: 'Lato', sans-serif; font-size: 0.9em; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F7F4EF; }
::-webkit-scrollbar-thumb { background: #DADDD6; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A8B5A3; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
GOOGLE_SHEET_NAME = "FirmLink_DB"
SHARED_DRIVE_ID   = "0AFQkhoAnS2U-Uk9PVA"
MAIN_FOLDER_ID    = "0AFQkhoAnS2U-Uk9PVA"
CLIENT_ROLE       = "client"

SH_CLIENTS   = "Clients"
SH_USERS     = "Users"
SH_COMM_LOG  = "CommLog"
SH_PIPELINE  = "Pipeline"
SH_TIMELOG   = "TimeLog"
SH_DOC_REQ   = "DocRequests"
SH_MESSAGES  = "Messages"
SH_RECURRING = "RecurringTasks"
SH_CLOSE     = "MonthClose"

CLIENTS_HEADERS   = ["Client Name","Contact Name","Email","Phone","Date Added","Service Tier","Client Status","Monthly Rate","Contract Signed","Engagement Start","Referral Source","Last Contacted","Internal Notes"]
USERS_HEADERS     = ["username","password","role","client_association","display_name"]
SH_SETTINGS       = "FirmSettings"
SETTINGS_HEADERS  = ["Setting","Value"]
COMM_LOG_HEADERS  = ["Date","Client","Type","Summary","Logged By"]
PIPELINE_HEADERS  = ["Lead Name","Contact","Email","Service Interest","Stage","Est Monthly Value","Follow Up Date","Notes","Date Added"]
TIMELOG_HEADERS   = ["Date","Client","Service","Hours","Notes","Logged By"]
DOC_REQ_HEADERS   = ["Req ID","Client","Request Name","Category","Description","Due Date","Status","Drive File ID","Uploaded Date","Created Date"]
MESSAGES_HEADERS  = ["Date","Client","Sender Type","Sender Name","Message"]
RECURRING_HEADERS = ["Name","Client","Template","Frequency","Day","Last Run","Active"]
CLOSE_HEADERS     = ["Month","Client","Phase","Status","Notes","Completed Date"]

CLI_COL = {h: i+1 for i, h in enumerate(CLIENTS_HEADERS)}
DR_COL  = {h: i+1 for i, h in enumerate(DOC_REQ_HEADERS)}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

SERVICE_TIERS   = ["Monthly Bookkeeping","Catch-Up / Cleanup","AP / AR Management","Sales Tax","Advisory","Payroll","CFO Services","Other"]
TIME_SERVICES   = ["Monthly Bookkeeping","Catch-Up / Cleanup","AP / AR Management","Sales Tax","Advisory","Consultation","Admin / Setup","Other"]
DOC_CATEGORIES  = ["Bank Statements","Credit Card Statements","Tax Documents","Business Records","Payroll Records","Receipts / Expenses","Other"]
PIPELINE_STAGES = ["New Lead","Proposal Sent","Proposal Accepted","Onboarding","Closed Lost"]
CLIENT_STATUSES = ["Active","Onboarding","On Hold","Offboarding","Prospect"]

CLOSE_PHASES = [
    "Data Collection",
    "Transaction Categorization",
    "Bank Reconciliation",
    "Review with Client",
    "Financial Report Delivery",
]

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
# GOOGLE SERVICES
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
            try:
                return ss.worksheet(name)
            except gspread.exceptions.WorksheetNotFound:
                w = ss.add_worksheet(title=name, rows=500, cols=max(len(headers), 10))
                w.append_row(headers)
                return w

        return {
            "ss":        ss,
            "tasks":     ss.sheet1,
            "invoices":  _ws("Invoices",  ["client","invoice_num","amount","due_date","pay_link","status"]),
            "clients":   _ws(SH_CLIENTS,  CLIENTS_HEADERS),
            "users":     _ws(SH_USERS,    USERS_HEADERS),
            "comm_log":  _ws(SH_COMM_LOG, COMM_LOG_HEADERS),
            "pipeline":  _ws(SH_PIPELINE, PIPELINE_HEADERS),
            "timelog":   _ws(SH_TIMELOG,  TIMELOG_HEADERS),
            "doc_req":   _ws(SH_DOC_REQ,  DOC_REQ_HEADERS),
            "messages":  _ws(SH_MESSAGES, MESSAGES_HEADERS),
            "recurring": _ws(SH_RECURRING,RECURRING_HEADERS),
            "close":     _ws(SH_CLOSE,    CLOSE_HEADERS),
            "settings":  _ws(SH_SETTINGS, SETTINGS_HEADERS),
            "drive":     build("drive","v3",credentials=creds),
        }
    except Exception as e:
        st.error(f"Google connection failed: {e}")
        return None


svc = get_google_services()

# ═══════════════════════════════════════════════════════════════
# GSPREAD RETRY WRAPPER — absorbs transient 429 rate-limit errors
# ═══════════════════════════════════════════════════════════════
import time as _time

def _safe_read(fn, *args, retries=4, base_delay=1.0, **kwargs):
    """Call a gspread read with exponential backoff on 429 quota errors."""
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except gspread.exceptions.APIError as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code == 429 and attempt < retries - 1:
                _time.sleep(base_delay * (2 ** attempt))
                continue
            raise



# ═══════════════════════════════════════════════════════════════
# AI HELPER  (requires ANTHROPIC_API_KEY in Streamlit secrets)
# ═══════════════════════════════════════════════════════════════
def ai_complete(prompt, system_prompt=None, max_tokens=1500):
    """Call Claude API. Returns (text, error_message)."""
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None, "Add ANTHROPIC_API_KEY to your Streamlit secrets to enable AI features."
    sys_msg = system_prompt or (
        "You are a professional assistant for Clearly Better Books, a boutique bookkeeping firm. "
        "Your tone is warm, calm, professional, and non-jargon-heavy. "
        "Write concisely in the firm's voice."
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": max_tokens,
                "system": sys_msg,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code == 200 and data.get("content"):
            return data["content"][0].get("text", ""), None
        return None, data.get("error", {}).get("message", f"API error {resp.status_code}")
    except Exception as e:
        return None, str(e)


# ═══════════════════════════════════════════════════════════════
# INTEGRATION URL HELPERS
# ═══════════════════════════════════════════════════════════════
def gcal_url(title, date_str, description=""):
    """Return a Google Calendar 'Add Event' link."""
    try:
        d = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        s = d.strftime("%Y%m%d")
        e = (d + timedelta(days=1)).strftime("%Y%m%d")
        return (
            "https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={urllib.parse.quote(str(title))}"
            f"&dates={s}/{e}"
            f"&details={urllib.parse.quote(str(description))}"
        )
    except Exception:
        return ""


def gmail_compose_url(to_email, subject, body):
    """Return a Gmail compose URL."""
    p = urllib.parse.urlencode({"to": to_email, "su": subject, "body": body})
    return f"https://mail.google.com/mail/?view=cm&{p}"


# ═══════════════════════════════════════════════════════════════
# CLIENT HEALTH SCORE
# ═══════════════════════════════════════════════════════════════
def compute_health(client, all_tasks, all_invoices, all_doc_req, cli_lookup, today):
    """Return (score 0-100, emoji, css_class, [reason strings])."""
    score   = 100
    reasons = []

    overdue = [t for t in all_tasks
               if t.get("client") == client
               and str(t.get("status","")).strip() != "Completed"
               and _date_before(str(t.get("due","")), today)]
    if overdue:
        penalty = min(45, len(overdue) * 15)
        score  -= penalty
        reasons.append(f"{len(overdue)} overdue task(s)")

    unpaid = [i for i in all_invoices
              if i.get("client") == client
              and str(i.get("status","")).strip().lower() != "paid"]
    for inv in unpaid:
        try:
            d = datetime.strptime(str(inv.get("due_date","")), "%Y-%m-%d").date()
            if (today - d).days > 30:
                score -= 20
                reasons.append("AR > 30 days overdue")
                break
        except Exception:
            pass

    rec          = cli_lookup.get(client, {})
    last_contact = str(rec.get("Last Contacted","") or "")
    if last_contact:
        try:
            lc = datetime.strptime(last_contact, "%Y-%m-%d").date()
            if (today - lc).days > 30:
                score -= 15
                reasons.append("No contact in 30+ days")
        except Exception:
            pass
    else:
        score -= 10
        reasons.append("No contact recorded")

    pending_dr = [r for r in all_doc_req
                  if str(r.get("Client","")).strip() == client
                  and str(r.get("Status","")).strip() == "Pending"]
    if pending_dr:
        score  -= min(20, len(pending_dr) * 10)
        reasons.append(f"{len(pending_dr)} pending doc request(s)")

    if str(rec.get("Contract Signed","")).strip().lower() in ("no",""):
        score -= 5
        reasons.append("No contract on file")

    score = max(0, score)
    if score >= 80:
        return score, "●", "health-green", reasons
    elif score >= 50:
        return score, "●", "health-amber", reasons
    else:
        return score, "●", "health-red", reasons


# ═══════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════
def _clear_data_cache():
    """Invalidate the sheet data cache. Called by every write helper."""
    try:
        load_sheet_data.clear()
    except Exception:
        pass  # Safe no-op if called before load_sheet_data is defined


def _date_before(date_str, ref_date):
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date() < ref_date
    except Exception:
        return False


def _fmt_money(val_str):
    try:
        return float(str(val_str).replace("$","").replace(",","").strip() or 0)
    except Exception:
        return 0.0


def profile_completeness(rec):
    """Return (pct 0-100, filled_count, total_count) for a client record."""
    fields = ["Contact Name","Email","Phone","Service Tier","Monthly Rate","Contract Signed","Engagement Start","Referral Source"]
    filled = sum(1 for f in fields if str(rec.get(f,"")).strip())
    pct    = int(filled / len(fields) * 100)
    return pct, filled, len(fields)


# ═══════════════════════════════════════════════════════════════
# DATA WRITE HELPERS
# Each one calls _clear_data_cache() so the next page load
# fetches fresh data instead of serving stale cached results.
# ═══════════════════════════════════════════════════════════════
def add_task(client, task_name, status, due_date):
    if svc and task_name and task_name.strip():
        svc["tasks"].append_row([client, task_name.strip(), status, str(due_date)])
        _clear_data_cache()

def update_task_status(row_num, new_status):
    if svc:
        svc["tasks"].update_cell(row_num, 3, new_status)
        _clear_data_cache()

def delete_task_row(row_num):
    if svc:
        svc["tasks"].delete_rows(row_num)
        _clear_data_cache()

def add_invoice(client, inv_num, amount, due_date, pay_link):
    if svc:
        svc["invoices"].append_row([client, inv_num, amount, str(due_date), pay_link, "Unpaid"])
        _clear_data_cache()

def mark_invoice_paid(row_num):
    if svc:
        svc["invoices"].update_cell(row_num, 6, "Paid")
        _clear_data_cache()

def add_client(name, contact, email, phone, service_tier, status,
               monthly_rate, contract_signed, start_date, referral):
    if svc is None: return False
    today_str = date.today().strftime("%Y-%m-%d")
    svc["clients"].append_row([name, contact, email, phone, today_str, service_tier, status,
                                monthly_rate, contract_signed, str(start_date), referral, today_str, ""])
    _clear_data_cache()
    return True

def update_client_col(client_name, col_name, value):
    if svc is None: return
    col = CLI_COL.get(col_name)
    if col is None: return
    try:
        recs = _safe_read(svc["clients"].get_all_records)
        for i, r in enumerate(recs):
            if str(r.get("Client Name", "")).strip() == client_name.strip():
                svc["clients"].update_cell(i + 2, col, value)
                _clear_data_cache()
                return
    except Exception:
        pass

def add_comm_log(client, entry_type, summary, logged_by="Firm"):
    if svc is None: return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    svc["comm_log"].append_row([ts, client, entry_type, summary, logged_by])
    update_client_col(client, "Last Contacted", date.today().strftime("%Y-%m-%d"))
    _clear_data_cache()

def add_pipeline_lead(lead_name, contact, email, service_interest, stage, est_value, follow_up, notes):
    if svc is None: return False
    today_str = date.today().strftime("%Y-%m-%d")
    svc["pipeline"].append_row([lead_name, contact, email, service_interest, stage,
                                 est_value, str(follow_up), notes, today_str])
    _clear_data_cache()
    return True

def update_pipeline_stage(lead_name, new_stage):
    if svc is None: return
    try:
        recs = _safe_read(svc["pipeline"].get_all_records)
        for i, r in enumerate(recs):
            if str(r.get("Lead Name", "")).strip() == lead_name.strip():
                svc["pipeline"].update_cell(i + 2, 5, new_stage)
                _clear_data_cache()
                return
    except Exception:
        pass

def add_time_entry(client, service, hours, notes, logged_by):
    if svc:
        svc["timelog"].append_row([date.today().strftime("%Y-%m-%d"), client, service, hours, notes, logged_by])
        _clear_data_cache()

def add_doc_request(client, req_name, category, description, due_date):
    if svc is None: return
    req_id    = datetime.now().strftime("REQ-%Y%m%d-%H%M%S")
    today_str = date.today().strftime("%Y-%m-%d")
    svc["doc_req"].append_row([req_id, client, req_name, category, description,
                                str(due_date), "Pending", "", "", today_str])
    _clear_data_cache()

def update_doc_request(row_num, new_status, drive_file_id=""):
    if svc is None: return
    uploaded = date.today().strftime("%Y-%m-%d") if drive_file_id else ""
    svc["doc_req"].update(f"G{row_num}:I{row_num}", [[new_status, drive_file_id, uploaded]])
    _clear_data_cache()

def send_message(client, sender_type, sender_name, message):
    if svc:
        svc["messages"].append_row([datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    client, sender_type, sender_name, message])
        _clear_data_cache()

def add_recurring(name, client, template, frequency, day):
    if svc:
        svc["recurring"].append_row([name, client, template, frequency, str(day), "", "Yes"])
        _clear_data_cache()

def update_recurring_last_run(row_num, today_str):
    if svc:
        svc["recurring"].update_cell(row_num, 6, today_str)
        _clear_data_cache()

def add_close_phase(month, client, phase, status="Pending", notes=""):
    if svc:
        svc["close"].append_row([month, client, phase, status, notes, ""])
        _clear_data_cache()

def update_close_row(row_num, status, notes, completed_date=""):
    if svc:
        svc["close"].update(f"D{row_num}:F{row_num}", [[status, notes, completed_date]])
        _clear_data_cache()


# ── Firm Settings ──
def get_firm_setting(key, default=""):
    """Read a single setting from FirmSettings sheet."""
    if svc is None: return default
    try:
        recs = _safe_read(svc["settings"].get_all_records)
        for r in recs:
            if str(r.get("Setting","")).strip() == key:
                return str(r.get("Value","")).strip() or default
    except Exception:
        pass
    return default

def set_firm_setting(key, value):
    """Write/update a setting in FirmSettings sheet."""
    if svc is None: return
    try:
        recs = _safe_read(svc["settings"].get_all_records)
        for i, r in enumerate(recs):
            if str(r.get("Setting","")).strip() == key:
                svc["settings"].update_cell(i + 2, 2, value)
                return
        svc["settings"].append_row([key, value])
    except Exception:
        pass


# ── Portal Users ──
def add_portal_user(username, password, role, client_assoc, display_name=""):
    """Add a new user to the Users sheet."""
    if svc is None: return False
    try:
        svc["users"].append_row([username, password, role, client_assoc, display_name])
        return True
    except Exception:
        return False

def update_user_display_name(username, display_name):
    """Update the display name for a user."""
    if svc is None: return
    try:
        recs = _safe_read(svc["users"].get_all_records)
        for i, r in enumerate(recs):
            if str(r.get("username","")).strip() == username:
                svc["users"].update_cell(i + 2, 5, display_name)
                return
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# GOOGLE DRIVE HELPERS
# ═══════════════════════════════════════════════════════════════
def _get_or_create_folder(client_name):
    if svc is None: return None
    drive = svc["drive"]
    q = (f"name='{client_name}' and '{MAIN_FOLDER_ID}' in parents "
         f"and mimeType='application/vnd.google-apps.folder' and trashed=false")
    try:
        res   = drive.files().list(q=q, fields="files(id)", corpora="drive",
                                   driveId=SHARED_DRIVE_ID, supportsAllDrives=True,
                                   includeItemsFromAllDrives=True).execute()
        items = res.get("files", [])
        if items:
            return items[0]["id"]
        meta = {"name": client_name, "mimeType": "application/vnd.google-apps.folder", "parents": [MAIN_FOLDER_ID]}
        f    = drive.files().create(body=meta, fields="id", supportsAllDrives=True).execute()
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
        f = svc["drive"].files().create(body=meta, media_body=media, fields="id", supportsAllDrives=True).execute()
        return f.get("id")
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════
def is_admin(role):
    return str(role).strip().lower() != CLIENT_ROLE

if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None,
                              "client_association": None, "username": None,
                              "display_name": None})

def handle_logout():
    st.session_state.update({"authenticated": False, "user_role": None,
                              "client_association": None, "username": None,
                              "display_name": None})
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    st.markdown("<h1 class='brand-title'>Clearly Better Books</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-tagline'>Bookkeeping that brings clarity, confidence, and calm to your business.</p>", unsafe_allow_html=True)
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;font-weight:normal;letter-spacing:0.02em;'>Secure Portal Login</h3>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form"):
            u   = st.text_input("Username / Email").strip()
            p   = st.text_input("Password", type="password").strip()
            btn = st.form_submit_button("Sign In")
        if btn:
            users = _safe_read(svc["users"].get_all_records) if svc else []
            match = next((r for r in users if str(r.get("username","")).strip()==u and str(r.get("password","")).strip()==p and u), None)
            if match:
                st.session_state.update({
                    "authenticated": True,
                    "username":     match.get("username"),
                    "user_role":    match.get("role"),
                    "client_association": match.get("client_association"),
                    "display_name": str(match.get("display_name","")).strip(),
                })
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ═══════════════════════════════════════════════════════════════
# AUTHENTICATED APP
# ═══════════════════════════════════════════════════════════════
else:
    admin = is_admin(st.session_state.user_role)

    # ── Client list ──
    BASE_CLIENTS = ["Acme Corp", "Baker Street Cafe"]
    _cli_recs    = _safe_read(svc["clients"].get_all_records) if svc else []
    _cli_names   = [str(r.get("Client Name","")).strip() for r in _cli_recs if str(r.get("Client Name","")).strip()]
    CLIENT_LIST  = list(dict.fromkeys(BASE_CLIENTS + _cli_names))
    CLI_LOOKUP   = {str(r.get("Client Name","")).strip(): r for r in _cli_recs}

    # ── Sidebar ──
    if admin:
        st.sidebar.markdown("<h3 style='text-align:center;margin-top:20px;font-weight:400;font-family:Playfair Display,Georgia,serif;color:#333333;letter-spacing:0.02em;'>Firm Controls</h3>", unsafe_allow_html=True)
        firm_view     = st.sidebar.radio("View:", ["Practice Dashboard","Client Workspace"], key="firm_view_mode")
        active_client = st.sidebar.selectbox("Manage Client:", CLIENT_LIST)
    else:
        firm_view     = "Client Workspace"
        active_client = str(st.session_state.client_association or "").strip()
        if active_client and active_client not in CLIENT_LIST:
            CLIENT_LIST.append(active_client)
        st.sidebar.markdown(f"<h3 style='text-align:center;margin-top:20px;font-weight:400;font-family:Playfair Display,Georgia,serif;color:#333333;'>Client Account</h3>", unsafe_allow_html=True)
        st.sidebar.markdown(f"<p style='text-align:center;font-size:1.1em;'><b>{active_client}</b></p>", unsafe_allow_html=True)

    # ── Global search (firm only) ──
    search_q = ""
    if admin:
        st.sidebar.markdown("<hr style='border-color:#DADDD6;margin:10px 0;'>", unsafe_allow_html=True)
        search_q = st.sidebar.text_input("Search", placeholder="Tasks, clients, notes…", key="global_search", label_visibility="collapsed")
        if search_q:
            st.sidebar.caption("Searching across all records…")

        # ── Firm Settings (sidebar) ──
        with st.sidebar.expander("Firm Settings", expanded=False):
            _cur_display = st.session_state.get("display_name","") or st.session_state.get("username","")
            _new_display = st.text_input("Your Display Name", value=_cur_display, key="sidebar_display_name",
                                          placeholder="e.g. Kay")
            if st.button("Save Name", key="save_display_name"):
                update_user_display_name(st.session_state.username, _new_display.strip())
                st.session_state["display_name"] = _new_display.strip()
                st.success("Name updated!")

            _firm_name  = st.text_input("Firm Name",  value=get_firm_setting("firm_name","Clearly Better Books"), key="sf_name")
            _firm_email = st.text_input("Firm Email", value=get_firm_setting("firm_email",""), key="sf_email")
            _hourly_rate= st.text_input("Default Hourly Rate ($)", value=get_firm_setting("hourly_rate",""), key="sf_rate")
            if st.button("Save Firm Info", key="save_firm_info"):
                set_firm_setting("firm_name",  _firm_name.strip())
                set_firm_setting("firm_email", _firm_email.strip())
                set_firm_setting("hourly_rate",_hourly_rate.strip())
                st.success("Firm info saved!")

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("Log Out of Portal", key="logout_btn"):
        handle_logout()
    st.sidebar.markdown(f"<hr style='border-color:#DADDD6;'><p style='font-size:0.76em;text-align:center;color:#A8B5A3;line-height:1.6;'>Logged in as:<br><span style='color:#333333;font-weight:600;'>{st.session_state.username}</span></p>", unsafe_allow_html=True)

    # ── Brand header ──
    st.markdown("<h1 class='brand-title'>Clearly Better Books</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-tagline'>Bookkeeping that brings clarity, confidence, and calm to your business.</p>", unsafe_allow_html=True)
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)

    if svc is None:
        st.info("Connecting to portal services…")
        st.stop()

    # ─────────────────────────────────────────────────────────
    # CACHED DATA LOADER  — prevents Google Sheets 429 quota
    # All 10 sheets loaded in one cache entry; TTL = 30 seconds.
    # Call load_sheet_data.clear() anywhere a write needs
    # to force an immediate refresh on the next rerun.
    # ─────────────────────────────────────────────────────────
    @st.cache_data(ttl=60, show_spinner=False)
    def load_sheet_data(_cache_key):
        """_cache_key is a dummy hashable arg so Streamlit can key the cache.
        Reads are retried with backoff to stay under the Sheets quota."""
        return {
            "tasks":     _safe_read(svc["tasks"].get_all_records),
            "invoices":  _safe_read(svc["invoices"].get_all_records),
            "clients":   _safe_read(svc["clients"].get_all_records),
            "pipeline":  _safe_read(svc["pipeline"].get_all_records),
            "comm_log":  _safe_read(svc["comm_log"].get_all_records),
            "timelog":   _safe_read(svc["timelog"].get_all_records),
            "recurring": _safe_read(svc["recurring"].get_all_records),
            "close":     _safe_read(svc["close"].get_all_records),
            "doc_req":   _safe_read(svc["doc_req"].get_all_records),
            "messages":  _safe_read(svc["messages"].get_all_records),
        }

    # Stable cache key so the cache survives service-resource recreation
    _raw = load_sheet_data("sheet_data_v1")

    # ─────────────────────────────────────────────────────────
    # UNPACK DATA
    # ─────────────────────────────────────────────────────────
    today        = date.today()
    all_tasks    = _raw.get("tasks", [])
    all_invoices = _raw.get("invoices", [])
    _cli_recs2   = _raw.get("clients", [])   # merged with _cli_recs below
    all_pipeline = _raw.get("pipeline", [])
    all_comm     = _raw.get("comm_log", [])
    all_timelog  = _raw.get("timelog", [])
    all_recurring= [dict(r, _row=i+2) for i, r in enumerate(_raw.get("recurring", []))]
    all_close    = [dict(r, _row=i+2) for i, r in enumerate(_raw.get("close", []))]
    all_doc_req  = [dict(r, _row=i+2) for i, r in enumerate(_raw.get("doc_req", []))]
    all_messages = [dict(r, _row=i+2) for i, r in enumerate(_raw.get("messages", []))]

    # Merge cached clients into _cli_recs (the version used for CLIENT_LIST above)
    if _cli_recs2:
        _cli_recs  = _cli_recs2
        CLI_LOOKUP = {str(r.get("Client Name","")).strip(): r for r in _cli_recs}
        _cli_names = [str(r.get("Client Name","")).strip() for r in _cli_recs if str(r.get("Client Name","")).strip()]
        CLIENT_LIST= list(dict.fromkeys(BASE_CLIENTS + _cli_names))

    # ── Filter out blank/malformed rows ──
    all_tasks    = [t for t in all_tasks if str(t.get("client","")).strip() or str(t.get("task","")).strip()]
    all_invoices = [i for i in all_invoices if str(i.get("invoice_num","")).strip() or str(i.get("amount","")).strip()]

    # ─────────────────────────────────────────────────────────
    # AUTO-RUN RECURRING TASKS
    # ─────────────────────────────────────────────────────────
    if admin:
        month_start = today.replace(day=1)
        for rec in all_recurring:
            if str(rec.get("Active","")).strip().lower() != "yes":
                continue
            template = str(rec.get("Template","")).strip()
            client   = str(rec.get("Client","")).strip()
            freq     = str(rec.get("Frequency","")).strip()
            try:
                day_num = int(str(rec.get("Day","1")).strip() or "1")
            except Exception:
                day_num = 1
            last_run = str(rec.get("Last Run","")).strip()

            if freq == "Monthly":
                run_date = today.replace(day=min(day_num, 28))
                already_ran = False
                if last_run:
                    try:
                        lr = datetime.strptime(last_run, "%Y-%m-%d").date()
                        already_ran = lr >= month_start
                    except Exception:
                        pass
                if today >= run_date and not already_ran and template in WORKFLOW_TEMPLATES:
                    for tname, offset in WORKFLOW_TEMPLATES[template]:
                        add_task(client, tname, "Pending", today + timedelta(days=offset))
                    update_recurring_last_run(rec["_row"], today.strftime("%Y-%m-%d"))
                    st.toast(f"Auto-created '{template}' tasks for {client}.", icon="🔁")

    # ─────────────────────────────────────────────────────────
    # DERIVED KPIs
    # ─────────────────────────────────────────────────────────
    open_tasks_all = [t for t in all_tasks if str(t.get("status","")).strip() != "Completed"]
    overdue_tasks  = [t for t in open_tasks_all if _date_before(str(t.get("due","")), today)]

    unpaid_all = [i for i in all_invoices if str(i.get("status","")).strip().lower() != "paid"]
    total_ar   = sum(_fmt_money(i.get("amount","")) for i in unpaid_all)
    mrr_total  = sum(_fmt_money(r.get("Monthly Rate","")) for r in _cli_recs)

    clients_needing_attn = set()
    for t in overdue_tasks:
        c = str(t.get("client","")).strip()
        if c: clients_needing_attn.add(c)
    for inv in unpaid_all:
        try:
            d = datetime.strptime(str(inv.get("due_date","")), "%Y-%m-%d").date()
            if (today - d).days > 30:
                clients_needing_attn.add(str(inv.get("client","")).strip())
        except Exception:
            pass

    active_leads = [p for p in all_pipeline if str(p.get("Stage","")).strip() not in ("","Closed Lost")]
    pipeline_mrr = sum(_fmt_money(p.get("Est Monthly Value","")) for p in active_leads)

    this_month       = today.strftime("%Y-%m")
    hours_this_month = sum(float(str(t.get("Hours",0)) or 0) for t in all_timelog if str(t.get("Date","")).startswith(this_month))

    pending_dr_count = sum(1 for r in all_doc_req if str(r.get("Status","")).strip() == "Pending")

    def _last_sender(cli):
        thread = [m for m in all_messages if str(m.get("Client","")).strip() == cli]
        return str(thread[-1].get("Sender Type","")).strip() if thread else ""

    clients_with_unread = [c for c in CLIENT_LIST if _last_sender(c) == "client"]
    total_unread        = len(clients_with_unread)

    # ─────────────────────────────────────────────────────────
    # GLOBAL SEARCH  (replaces main view when active)
    # ─────────────────────────────────────────────────────────
    if search_q and search_q.strip():
        q = search_q.strip().lower()
        st.markdown(f"### Search results for &ldquo;{search_q}&rdquo;", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        found = 0

        for t in all_tasks:
            if q in str(t.get("task","")).lower() or q in str(t.get("client","")).lower():
                status = str(t.get("status","")).strip()
                st.markdown(
                    f"<div class='search-result'>"
                    f"<div class='search-type'>Task</div>"
                    f"<div class='search-title'>{t.get('task','')}</div>"
                    f"<div class='search-meta'>{t.get('client','')}  ·  {status}  ·  Due {t.get('due','')}</div>"
                    f"</div>", unsafe_allow_html=True)
                found += 1

        for r in _cli_recs:
            name = str(r.get("Client Name","")).strip()
            if q in name.lower() or q in str(r.get("Contact Name","")).lower() or q in str(r.get("Email","")).lower():
                st.markdown(
                    f"<div class='search-result'>"
                    f"<div class='search-type'>Client</div>"
                    f"<div class='search-title'>{name}</div>"
                    f"<div class='search-meta'>{r.get('Contact Name','')}  ·  {r.get('Email','')}  ·  {r.get('Client Status','')}</div>"
                    f"</div>", unsafe_allow_html=True)
                found += 1

        for e in reversed(all_comm):
            if q in str(e.get("Summary","")).lower() or q in str(e.get("Client","")).lower():
                st.markdown(
                    f"<div class='search-result'>"
                    f"<div class='search-type'>Activity Log · {e.get('Type','')}</div>"
                    f"<div class='search-title'>{e.get('Client','')}</div>"
                    f"<div class='search-meta'>{e.get('Summary','')}  ·  {e.get('Date','')}</div>"
                    f"</div>", unsafe_allow_html=True)
                found += 1

        for m in reversed(all_messages):
            if q in str(m.get("Message","")).lower() or q in str(m.get("Client","")).lower():
                st.markdown(
                    f"<div class='search-result'>"
                    f"<div class='search-type'>Message · {m.get('Sender Type','')}</div>"
                    f"<div class='search-title'>{m.get('Client','')} — {m.get('Sender Name','')}</div>"
                    f"<div class='search-meta'>{m.get('Message','')}  ·  {m.get('Date','')}</div>"
                    f"</div>", unsafe_allow_html=True)
                found += 1

        for r in all_doc_req:
            if q in str(r.get("Request Name","")).lower() or q in str(r.get("Client","")).lower():
                st.markdown(
                    f"<div class='search-result'>"
                    f"<div class='search-type'>Document Request</div>"
                    f"<div class='search-title'>{r.get('Request Name','')}</div>"
                    f"<div class='search-meta'>{r.get('Client','')}  ·  {r.get('Status','')}  ·  Due {r.get('Due Date','')}</div>"
                    f"</div>", unsafe_allow_html=True)
                found += 1

        if found == 0:
            st.info("No results found. Try a different keyword.")
        else:
            st.caption(f"{found} result(s) found.")
        st.stop()

    # ══════════════════════════════════════════════════════════
    # PRACTICE DASHBOARD
    # ══════════════════════════════════════════════════════════
    if admin and firm_view == "Practice Dashboard":

        st.markdown("<h5 style='font-family:Montserrat,Lato,sans-serif;letter-spacing:0.12em;text-transform:uppercase;color:#A8B5A3;font-size:0.78rem;font-weight:600;'>Practice Dashboard</h5>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── TODAY'S FOCUS PANEL ──
        hour     = datetime.now().hour
        greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
        uname    = st.session_state.get("display_name","").strip() or st.session_state.get("username","Kay")
        day_str  = today.strftime("%A, %B %-d, %Y")
        due_today= [t for t in all_tasks if str(t.get("due","")).strip()==str(today) and str(t.get("status","")).strip()!="Completed"]

        focus_html = (
            f"<div class='focus-panel'>"
            f"<div class='focus-greeting'>{greeting}, {uname}</div>"
            f"<div class='focus-date-line'>{day_str}</div>"
        )
        all_clear = not overdue_tasks and not due_today and not total_unread and not pending_dr_count
        if all_clear:
            focus_html += "<div class='focus-clear'>All clear — no urgent items today. Great work!</div>"
        else:
            items = []
            if overdue_tasks:
                by_cli = Counter(str(t.get("client","")) for t in overdue_tasks)
                clients_str = ", ".join(f"{c} ({n})" for c, n in by_cli.most_common(3))
                items.append(f"<span style='color:#C4878A;font-weight:600;'>🔴 {len(overdue_tasks)} overdue task(s)</span> — {clients_str}")
            if due_today:
                items.append(f"<span style='color:#D4956A;font-weight:600;'>📅 {len(due_today)} task(s) due today</span>")
            if total_unread:
                cli_str = ", ".join(clients_with_unread[:3])
                items.append(f"<span style='color:#7891B3;font-weight:600;'>💬 {total_unread} client(s) awaiting reply</span> — {cli_str}")
            if pending_dr_count:
                items.append(f"<span style='color:#D4956A;font-weight:600;'>📄 {pending_dr_count} document request(s) pending upload</span>")
            for it in items:
                focus_html += f"<div class='focus-item'>{it}</div>"
        focus_html += "</div>"
        st.markdown(focus_html, unsafe_allow_html=True)

        # ── KPI ROW 1 ──
        c1, c2, c3, c4 = st.columns(4)
        for col, num, label, color in [
            (c1, len(CLIENT_LIST),        "Active Clients",       "#333333"),
            (c2, len(open_tasks_all),     "Open Tasks",           "#333333"),
            (c3, len(overdue_tasks),      "Overdue Tasks",        "#C4878A" if overdue_tasks else "#333333"),
            (c4, f"${total_ar:,.2f}",     "Total AR Outstanding", "#333333"),
        ]:
            with col:
                st.markdown(f"<div class='dashboard-stat'><span class='dashboard-stat-number' style='color:{color}'>{num}</span><span class='dashboard-stat-label'>{label}</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── KPI ROW 2 ──
        c5, c6, c7, c8 = st.columns(4)
        for col, num, label, color in [
            (c5, f"${mrr_total:,.0f}",     "Est. Monthly Revenue",   "#333333"),
            (c6, f"{hours_this_month:.1f}h","Hours This Month",       "#333333"),
            (c7, total_unread,             "Unread Messages",         "#C4878A" if total_unread else "#7A9477"),
            (c8, pending_dr_count,         "Docs Awaiting Upload",    "#D4956A" if pending_dr_count else "#7A9477"),
        ]:
            with col:
                st.markdown(f"<div class='dashboard-stat'><span class='dashboard-stat-number' style='color:{color}'>{num}</span><span class='dashboard-stat-label'>{label}</span></div>", unsafe_allow_html=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # ── TABS ──
        (tab_tasks, tab_ar, tab_time, tab_close, tab_recurring,
         tab_docs, tab_msgs, tab_profiles, tab_log, tab_pipe) = st.tabs([
            "All Tasks", "AR & Revenue", "Time Tracker",
            "Month Close", "Recurring", "Doc Requests",
            "Messages", "Client Profiles", "Activity Log", "Pipeline",
        ])

        # ──────────────────────────────────────────────────────
        # TAB: ALL TASKS
        # ──────────────────────────────────────────────────────
        with tab_tasks:
            st.markdown("#### All Tasks")

            # Due Today strip
            due_today_tasks = [t for t in all_tasks if str(t.get("due","")).strip()==str(today) and str(t.get("status","")).strip()!="Completed"]
            if due_today_tasks:
                st.markdown(
                    f"<div style='background:#FFF9F5;border:1px solid #F0D4B0;border-left:3px solid #D4956A;border-radius:4px;padding:10px 16px;margin-bottom:16px;'>"
                    f"<span style='font-family:Montserrat,sans-serif;font-size:0.7em;text-transform:uppercase;letter-spacing:0.1em;color:#D4956A;font-weight:700;'>Due Today — {len(due_today_tasks)} task(s)</span><br>"
                    + "  &nbsp;·&nbsp;  ".join(f"<strong>{str(t.get('task','')) or '(Untitled)'}</strong> <span style='color:#A8B5A3;font-size:0.85em;'>({t.get('client','')})</span>" for t in due_today_tasks[:5])
                    + f"</div>",
                    unsafe_allow_html=True)

            # Workflow launcher
            with st.expander("Launch Workflow Template", expanded=False):
                wc1, wc2, wc3 = st.columns([2, 2, 1])
                with wc1: wf_tmpl = st.selectbox("Template", list(WORKFLOW_TEMPLATES.keys()), key="wf_tmpl")
                with wc2: wf_cli  = st.selectbox("Client", CLIENT_LIST, key="wf_cli")
                with wc3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Launch", key="wf_launch"):
                        for tname, offset in WORKFLOW_TEMPLATES[wf_tmpl]:
                            add_task(wf_cli, tname, "Pending", today + timedelta(days=offset))
                        st.success(f"Launched '{wf_tmpl}' for {wf_cli} — {len(WORKFLOW_TEMPLATES[wf_tmpl])} tasks created.")
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # Filters
            fc1, fc2, fc3, fc4 = st.columns([2, 2, 1, 1])
            with fc1: f_cli    = st.selectbox("Filter Client", ["All Clients"]+CLIENT_LIST, key="ft_cli")
            with fc2: f_status = st.selectbox("Filter Status", ["All","Pending","In Progress","Awaiting Client","Completed"], key="ft_status")
            with fc3: f_over   = st.checkbox("Overdue Only", key="ft_over")
            with fc4: f_hide_done = st.checkbox("Hide Completed", value=True, key="ft_hide_done")

            # Bulk actions
            ba1, ba2 = st.columns([2, 1])
            with ba1:
                if st.button("Clear All Completed Tasks", key="bulk_clear"):
                    recs = svc["tasks"].get_all_records()
                    rows_to_del = [i+2 for i, r in enumerate(recs) if str(r.get("status","")).strip() == "Completed"]
                    for row in sorted(rows_to_del, reverse=True):
                        svc["tasks"].delete_rows(row)
                    st.success(f"Cleared {len(rows_to_del)} completed task(s).")
                    st.rerun()

            tasks_view = list(all_tasks)
            if f_cli != "All Clients":   tasks_view = [t for t in tasks_view if t.get("client") == f_cli]
            if f_status != "All":        tasks_view = [t for t in tasks_view if str(t.get("status","")).strip() == f_status]
            if f_hide_done:              tasks_view = [t for t in tasks_view if str(t.get("status","")).strip() != "Completed"]
            if f_over:                   tasks_view = [t for t in tasks_view if _date_before(str(t.get("due","")), today) and str(t.get("status","")).strip() != "Completed"]

            st.markdown("<br>", unsafe_allow_html=True)

            if not tasks_view:
                st.info("No tasks match the current filters.")
            else:
                status_opts = ["Pending","In Progress","Awaiting Client","Completed"]
                badge_map   = {"Pending":"badge-open","In Progress":"badge-progress","Awaiting Client":"badge-waiting","Completed":"badge-done"}
                for idx, task in enumerate(tasks_view):
                    status    = str(task.get("status","Pending")).strip()
                    task_name = str(task.get("task","")).strip() or "*(Untitled)*"
                    due_str   = str(task.get("due","")).strip()
                    overdue   = _date_before(due_str, today) and status != "Completed"
                    badge     = badge_map.get(status, "badge-open")
                    flag      = " 🔴" if overdue else ""

                    tc1, tc2, tc3, tc4, tc5 = st.columns([3, 2, 2, 2, 1])
                    with tc1:
                        st.markdown(f"**{task_name}**{flag}")
                        st.caption(f"Client: {task.get('client','')}")
                    with tc2:
                        st.markdown(f"<span class='status-badge {badge}'>{status}</span>", unsafe_allow_html=True)
                    with tc3:
                        st.caption(f"Due: {due_str or 'Not set'}")
                        if due_str:
                            cal_link = gcal_url(task_name, due_str, f"Client: {task.get('client','')}")
                            if cal_link:
                                st.markdown(f"<a href='{cal_link}' target='_blank' class='link-btn'>+ Cal</a>", unsafe_allow_html=True)
                    with tc4:
                        new_s = st.selectbox("Status", status_opts,
                                             index=status_opts.index(status) if status in status_opts else 0,
                                             key=f"ts_{idx}", label_visibility="collapsed")
                        if new_s != status:
                            recs = svc["tasks"].get_all_records()
                            for si, rec in enumerate(recs):
                                if rec.get("client")==task.get("client") and rec.get("task")==task.get("task") and rec.get("due")==task.get("due"):
                                    update_task_status(si+2, new_s)
                                    st.rerun()
                    with tc5:
                        # AI reminder draft on overdue/awaiting tasks
                        if overdue or status == "Awaiting Client":
                            ai_key = f"ai_draft_{idx}"
                            if st.button("Draft", key=f"ai_btn_{idx}"):
                                cli_rec  = CLI_LOOKUP.get(str(task.get("client","")), {})
                                cli_email= str(cli_rec.get("Email","")).strip() or "client@email.com"
                                prompt   = (
                                    f"Write a short, warm reminder email for a bookkeeping client.\n"
                                    f"Client: {task.get('client','')}\n"
                                    f"Task: {task_name}\n"
                                    f"Due: {due_str}\n"
                                    f"Status: {status}\n"
                                    f"Keep it brief (3-4 sentences), professional, non-pushy. "
                                    f"Sign off as 'Kay | Clearly Better Books'."
                                )
                                draft, err = ai_complete(prompt)
                                if draft:
                                    st.session_state[ai_key] = draft
                                elif err:
                                    st.session_state[ai_key] = f"Error: {err}"

                            if ai_key in st.session_state and st.session_state[ai_key]:
                                cli_rec  = CLI_LOOKUP.get(str(task.get("client","")), {})
                                cli_email= str(cli_rec.get("Email","")).strip() or ""
                                gmail    = gmail_compose_url(cli_email, f"Follow-up: {task_name}", st.session_state[ai_key])
                                st.markdown(f"<div class='ai-label'>AI Draft</div><div class='ai-box'>{st.session_state[ai_key]}</div>", unsafe_allow_html=True)
                                if cli_email:
                                    st.markdown(f"<a href='{gmail}' target='_blank' class='link-btn'>Open in Gmail</a>", unsafe_allow_html=True)

                    st.markdown("<hr style='border:none;border-top:1px solid #F0ECE7;margin:6px 0;'>", unsafe_allow_html=True)

            # AI: Extract tasks from meeting notes
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            with st.expander("Extract Tasks from Meeting Notes (AI)", expanded=False):
                mt_client = st.selectbox("Assign to Client", CLIENT_LIST, key="mt_cli")
                mt_notes  = st.text_area("Paste meeting notes or transcript", height=120, key="mt_notes")
                if st.button("Extract Tasks", key="mt_extract"):
                    if mt_notes.strip():
                        prompt = (
                            f"Extract actionable tasks from these meeting notes for client: {mt_client}.\n\n"
                            f"{mt_notes}\n\n"
                            f"Return ONLY a numbered list of tasks, one per line, with a suggested due date in parentheses like (due: YYYY-MM-DD). "
                            f"Base due dates on today being {today}. Be concise."
                        )
                        result, err = ai_complete(prompt)
                        if result:
                            st.session_state["mt_result"] = result
                        elif err:
                            st.warning(err)

                if "mt_result" in st.session_state:
                    st.markdown(f"<div class='ai-label'>Extracted Tasks</div><div class='ai-box'>{st.session_state['mt_result']}</div>", unsafe_allow_html=True)
                    if st.button("Add All to Task Sheet", key="mt_add"):
                        lines = [l.strip() for l in st.session_state["mt_result"].split("\n") if l.strip()]
                        count = 0
                        for line in lines:
                            import re
                            date_match = re.search(r"\(due:\s*(\d{4}-\d{2}-\d{2})\)", line)
                            due        = date_match.group(1) if date_match else str(today + timedelta(days=7))
                            task_text  = re.sub(r"^\d+[\.\)]\s*", "", line)
                            task_text  = re.sub(r"\s*\(due:.*?\)", "", task_text).strip()
                            if task_text:
                                add_task(st.session_state.get("mt_cli", CLIENT_LIST[0]), task_text, "Pending", due)
                                count += 1
                        st.success(f"Added {count} tasks to the sheet.")
                        del st.session_state["mt_result"]
                        st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB: AR & REVENUE
        # ──────────────────────────────────────────────────────
        with tab_ar:
            st.markdown("#### Accounts Receivable — All Clients")

            # Bulk reminder option
            overdue_cli = [c for c in CLIENT_LIST if any(
                (today - datetime.strptime(str(i.get("due_date","")),"%Y-%m-%d").date()).days > 0
                for i in all_invoices if i.get("client")==c and str(i.get("status","")).lower()!="paid"
                and str(i.get("due_date","")).strip()
            )]
            if overdue_cli:
                st.markdown(
                    f"<div style='background:#FAF2F1;border:1px solid #EBC6C1;border-radius:4px;padding:10px 16px;margin-bottom:16px;'>"
                    f"<span style='font-family:Montserrat,sans-serif;font-size:0.7em;text-transform:uppercase;letter-spacing:0.1em;color:#C4878A;font-weight:700;'>Overdue AR — {len(overdue_cli)} client(s)</span><br>"
                    f"<span style='font-family:Lato,sans-serif;font-size:0.88em;color:#555;'>{', '.join(overdue_cli[:5])}</span></div>",
                    unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            for client in CLIENT_LIST:
                cli_unpaid = [i for i in all_invoices if i.get("client")==client and str(i.get("status","")).strip().lower()!="paid"]
                cli_total  = sum(_fmt_money(i.get("amount","")) for i in cli_unpaid)
                max_age    = 0
                for inv in cli_unpaid:
                    try:
                        d       = datetime.strptime(str(inv.get("due_date","")), "%Y-%m-%d").date()
                        max_age = max(max_age, (today-d).days)
                    except Exception:
                        pass
                alert     = cli_total > 0
                card_cls  = "client-card-alert" if alert else "client-card"
                ar_color  = "#C4878A" if alert else "#7A9477"
                age_chip  = ""
                if max_age > 60:   age_chip = "<span class='attention-chip'>60+ days</span>"
                elif max_age > 30: age_chip = "<span class='attention-chip'>30+ days</span>"
                st.markdown(
                    f"<div class='{card_cls}'><strong>{client}</strong>{age_chip}&nbsp;&nbsp;"
                    f"<span style='color:#A8B5A3;font-size:0.88em;'>{len(cli_unpaid)} unpaid</span>&nbsp;&nbsp;"
                    f"<strong style='color:{ar_color};'>${cli_total:,.2f} outstanding</strong></div>",
                    unsafe_allow_html=True)

            if unpaid_all:
                st.markdown("<br>")
                st.markdown("#### All Unpaid Invoices")
                rows = []
                for inv in unpaid_all:
                    try:
                        dd    = datetime.strptime(str(inv.get("due_date","")), "%Y-%m-%d").date()
                        aging = f"{(today-dd).days}d overdue" if (today-dd).days>0 else "Current"
                    except Exception:
                        aging = ""
                    # AI reminder draft for overdue invoices
                    cli_rec   = CLI_LOOKUP.get(str(inv.get("client","")), {})
                    cli_email = str(cli_rec.get("Email","")).strip()
                    rows.append({"Client": inv.get("client",""), "Invoice #": inv.get("invoice_num",""),
                                 "Amount": inv.get("amount",""), "Due Date": inv.get("due_date",""),
                                 "Aging": aging, "Email": cli_email})
                df_inv = pd.DataFrame(rows)
                st.dataframe(df_inv.drop(columns=["Email"]), use_container_width=True, hide_index=True)

                # Invoice reminder drafts
                with st.expander("Draft Payment Reminder Email", expanded=False):
                    ir_inv = st.selectbox("Select Invoice", [f"{r['Client']} — Invoice #{r['Invoice #']} ({r['Amount']})" for r in rows], key="ir_inv_sel")
                    if st.button("Generate Reminder", key="ir_gen"):
                        sel = rows[[f"{r['Client']} — Invoice #{r['Invoice #']} ({r['Amount']})" for r in rows].index(ir_inv)]
                        prompt = (
                            f"Write a warm, professional payment reminder email.\n"
                            f"Client: {sel['Client']}\n"
                            f"Invoice #: {sel['Invoice #']}  Amount: {sel['Amount']}  Due: {sel['Due Date']}\n"
                            f"Keep it brief (3-4 sentences), non-confrontational. "
                            f"Mention they can pay via the portal link. Sign off as 'Kay | Clearly Better Books'."
                        )
                        draft, err = ai_complete(prompt)
                        if draft:
                            st.session_state["ir_draft"] = (draft, sel.get("Email",""), sel["Client"])
                        elif err:
                            st.warning(err)

                    if "ir_draft" in st.session_state:
                        draft_text, to_email, cli = st.session_state["ir_draft"]
                        st.markdown(f"<div class='ai-label'>Payment Reminder Draft</div><div class='ai-box'>{draft_text}</div>", unsafe_allow_html=True)
                        if to_email:
                            gmail = gmail_compose_url(to_email, f"Invoice Payment Reminder — {cli}", draft_text)
                            st.markdown(f"<a href='{gmail}' target='_blank' class='link-btn'>Open in Gmail</a>", unsafe_allow_html=True)

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("#### Revenue by Month")
            inv_by_month = defaultdict(float)
            for inv in all_invoices:
                mo = str(inv.get("due_date",""))[:7]
                if mo and len(mo)==7:
                    inv_by_month[mo] += _fmt_money(inv.get("amount",""))
            if inv_by_month:
                df_rev = pd.DataFrame([{"Month": k, "Total Invoiced ($)": round(v,2)}
                                        for k,v in sorted(inv_by_month.items())])
                st.bar_chart(df_rev.set_index("Month"))
            else:
                st.info("No invoice data yet to chart.")

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("#### Export Data")
            ex1, ex2, ex3 = st.columns(3)
            with ex1:
                if _cli_recs:
                    st.download_button("Export Clients CSV",
                        data=pd.DataFrame(_cli_recs).to_csv(index=False),
                        file_name=f"clients_{today}.csv", mime="text/csv")
            with ex2:
                if all_invoices:
                    st.download_button("Export Invoices CSV",
                        data=pd.DataFrame(all_invoices).to_csv(index=False),
                        file_name=f"invoices_{today}.csv", mime="text/csv")
            with ex3:
                if all_timelog:
                    st.download_button("Export Time Log CSV",
                        data=pd.DataFrame(all_timelog).to_csv(index=False),
                        file_name=f"timelog_{today}.csv", mime="text/csv")

        # ──────────────────────────────────────────────────────
        # TAB: TIME TRACKER
        # ──────────────────────────────────────────────────────
        with tab_time:
            st.markdown("#### Time Tracker")
            st.markdown("<br>", unsafe_allow_html=True)

            week_start    = today - timedelta(days=today.weekday())
            hours_this_wk = sum(float(str(t.get("Hours",0)) or 0) for t in all_timelog if str(t.get("Date",""))>=str(week_start))
            cli_hours_ctr = Counter()
            for t in all_timelog:
                try: cli_hours_ctr[str(t.get("Client",""))] += float(str(t.get("Hours",0)) or 0)
                except Exception: pass
            top_client = cli_hours_ctr.most_common(1)[0][0] if cli_hours_ctr else "—"

            sk1, sk2, sk3 = st.columns(3)
            for col, num, label in [(sk1, f"{hours_this_month:.1f}", "Hours This Month"),
                                    (sk2, f"{hours_this_wk:.1f}", "Hours This Week"),
                                    (sk3, top_client, "Top Client")]:
                with col:
                    st.markdown(f"<div class='dashboard-stat'><span class='dashboard-stat-number' style='font-size:1.6em;'>{num}</span><span class='dashboard-stat-label'>{label}</span></div>", unsafe_allow_html=True)

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("**Log Time Entry**")
            with st.form("time_form", clear_on_submit=True):
                tf1, tf2 = st.columns(2)
                with tf1:
                    t_client  = st.selectbox("Client", CLIENT_LIST, key="tf_cli")
                    t_service = st.selectbox("Service", TIME_SERVICES, key="tf_svc")
                with tf2:
                    t_date  = st.date_input("Date", today, key="tf_date")
                    t_hours = st.number_input("Hours", min_value=0.25, max_value=24.0, step=0.25, value=1.0, key="tf_hrs")
                t_notes = st.text_input("Notes (optional)", key="tf_notes")
                if st.form_submit_button("Log Time"):
                    add_time_entry(t_client, t_service, t_hours, t_notes, st.session_state.username)
                    add_comm_log(t_client, "Time Log", f"{t_hours}h — {t_service}", st.session_state.username)
                    st.success(f"Logged {t_hours}h for {t_client}.")
                    st.rerun()

            # ── Compute cli_sum ALWAYS (needed by capacity chart below) ──
            mtd     = [t for t in all_timelog if str(t.get("Date","")).startswith(this_month)]
            cli_sum = defaultdict(float)
            for t in mtd:
                try: cli_sum[str(t.get("Client",""))] += float(str(t.get("Hours",0)) or 0)
                except Exception: pass

            if all_timelog:
                st.markdown("<br>**Hours by Client — This Month**")
                if cli_sum:
                    df_cli = pd.DataFrame([{"Client": k, "Hours": round(v,2)} for k,v in sorted(cli_sum.items(), key=lambda x:-x[1])])
                    st.dataframe(df_cli, use_container_width=True, hide_index=True)

                st.markdown("<br>**Recent Entries**")
                for entry in reversed(all_timelog[-15:]):
                    ec1, ec2, ec3, ec4 = st.columns([2, 2, 1, 3])
                    with ec1: st.markdown(f"**{entry.get('Client','')}**")
                    with ec2: st.caption(entry.get("Service",""))
                    with ec3: st.markdown(f"**{entry.get('Hours','')}h**")
                    with ec4: st.caption(f"{entry.get('Date','')}  {entry.get('Notes','')}")
                    st.markdown("<hr style='border:none;border-top:1px solid #F0ECE7;margin:4px 0;'>", unsafe_allow_html=True)

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("#### Capacity Overview — This Month")
            target_hrs = float(get_firm_setting("monthly_hours_target","160") or 160)
            t1, t2 = st.columns([3,1])
            with t1:
                st.progress(min(1.0, hours_this_month / target_hrs),
                            text=f"{hours_this_month:.1f}h logged of {target_hrs:.0f}h target ({int(hours_this_month/target_hrs*100)}%)")
            with t2:
                new_target = st.number_input("Monthly Target (hrs)", value=int(target_hrs), min_value=1, max_value=300, step=10, key="hrs_target")
                if new_target != int(target_hrs):
                    set_firm_setting("monthly_hours_target", str(new_target))

            # Hours by client this month (bar chart)
            if cli_sum:
                df_cap = pd.DataFrame([{"Client": k[:20], "Hours": round(v,1)} for k,v in sorted(cli_sum.items(), key=lambda x:-x[1])])
                st.bar_chart(df_cap.set_index("Client"))

        # ──────────────────────────────────────────────────────
        # TAB: MONTH CLOSE TRACKER
        # ──────────────────────────────────────────────────────
        with tab_close:
            st.markdown("#### Monthly Close Tracker")
            st.markdown("<br>", unsafe_allow_html=True)

            mc1, mc2, mc3 = st.columns([2, 2, 1])
            with mc1:
                close_month = st.selectbox("Month", [
                    (today.replace(day=1) - timedelta(days=30*i)).strftime("%Y-%m")
                    for i in range(6)
                ], key="close_month_sel")
            with mc2:
                close_client = st.selectbox("Client", CLIENT_LIST, key="close_cli_sel")
            with mc3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Init Checklist", key="close_init"):
                    existing = [r for r in all_close if r.get("Month")==close_month and r.get("Client")==close_client]
                    existing_phases = {str(r.get("Phase","")) for r in existing}
                    added = 0
                    for phase in CLOSE_PHASES:
                        if phase not in existing_phases:
                            add_close_phase(close_month, close_client, phase)
                            added += 1
                    if added:
                        st.success(f"Created {added} phase(s) for {close_client} — {close_month}.")
                        st.rerun()
                    else:
                        st.info("Checklist already exists for this client/month.")

            st.markdown("<br>", unsafe_allow_html=True)

            close_view = [r for r in all_close if r.get("Month")==close_month and r.get("Client")==close_client]
            if not close_view:
                st.info("No close checklist for this client/month. Click 'Init Checklist' to create one.")
            else:
                done_count  = sum(1 for r in close_view if str(r.get("Status","")).strip()=="Complete")
                total_count = len(close_view)
                pct         = done_count / total_count if total_count else 0
                st.progress(pct, text=f"{done_count}/{total_count} phases complete")
                st.markdown("<br>", unsafe_allow_html=True)

                phase_order = {p: i for i, p in enumerate(CLOSE_PHASES)}
                close_view.sort(key=lambda r: phase_order.get(str(r.get("Phase","")), 99))

                for phase_rec in close_view:
                    ph_name   = str(phase_rec.get("Phase","")).strip()
                    ph_status = str(phase_rec.get("Status","Pending")).strip()
                    ph_notes  = str(phase_rec.get("Notes","")).strip()
                    ph_date   = str(phase_rec.get("Completed Date","")).strip()
                    ph_row    = phase_rec["_row"]

                    ph_css = {"Complete":"close-done", "In Progress":"close-active", "Pending":"close-pending"}.get(ph_status, "close-pending")
                    ph_icon = {"Complete":"✓","In Progress":"→","Pending":"○"}.get(ph_status,"○")

                    cp1, cp2, cp3 = st.columns([3, 2, 1])
                    with cp1:
                        st.markdown(f"<div class='{ph_css}'><span class='close-label'>{ph_status}</span><br><span class='close-name'>{ph_icon} {ph_name}</span>{('<br><span style=\"color:#888;font-size:0.82em;\">'+ ph_notes+'</span>') if ph_notes else ''}</div>", unsafe_allow_html=True)
                    with cp2:
                        new_ph_status = st.selectbox("Status", ["Pending","In Progress","Complete"],
                            index=["Pending","In Progress","Complete"].index(ph_status) if ph_status in ["Pending","In Progress","Complete"] else 0,
                            key=f"ph_s_{ph_row}", label_visibility="collapsed")
                    with cp3:
                        if st.button("Update", key=f"ph_u_{ph_row}"):
                            comp_date = str(today) if new_ph_status=="Complete" else ""
                            update_close_row(ph_row, new_ph_status, ph_notes, comp_date)
                            st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB: RECURRING TASKS
        # ──────────────────────────────────────────────────────
        with tab_recurring:
            st.markdown("#### Recurring Task Scheduler")
            st.markdown(
                "<p style='font-family:Lato,sans-serif;color:#888;font-size:0.88em;'>"
                "Set up automatic monthly task creation per client. Tasks are generated on the scheduled day each month.</p>",
                unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("add_recurring_form", clear_on_submit=True):
                st.markdown("**Add Recurring Schedule**")
                rr1, rr2 = st.columns(2)
                with rr1:
                    rr_name   = st.text_input("Schedule Name (e.g. Monthly Close — Acme)")
                    rr_client = st.selectbox("Client", CLIENT_LIST, key="rr_cli")
                    rr_tmpl   = st.selectbox("Workflow Template", list(WORKFLOW_TEMPLATES.keys()), key="rr_tmpl")
                with rr2:
                    rr_freq = st.selectbox("Frequency", ["Monthly","Quarterly"], key="rr_freq")
                    rr_day  = st.number_input("Day of Month to Run", min_value=1, max_value=28, value=1, key="rr_day")
                if st.form_submit_button("Add Schedule"):
                    if rr_name.strip():
                        add_recurring(rr_name.strip(), rr_client, rr_tmpl, rr_freq, rr_day)
                        st.success(f"Schedule '{rr_name.strip()}' added. Tasks will auto-generate on day {rr_day} of each month.")
                        st.rerun()
                    else:
                        st.warning("Please enter a schedule name.")

            st.markdown("<br>")
            if not all_recurring:
                st.info("No recurring schedules set up yet.")
            else:
                for r in all_recurring:
                    is_active = str(r.get("Active","")).strip().lower() == "yes"
                    indicator = "🟢" if is_active else "⚪"
                    last_run  = str(r.get("Last Run","") or "Never")
                    st.markdown(
                        f"<div class='client-card'>"
                        f"{indicator} <strong>{r.get('Name','')}</strong>"
                        f"<span style='color:#A8B5A3;font-size:0.85em;'> — {r.get('Client','')} — {r.get('Template','')}</span><br>"
                        f"<span style='font-size:0.82em;color:#888;'>{r.get('Frequency','')} on day {r.get('Day','')}  ·  Last run: {last_run}</span>"
                        f"</div>",
                        unsafe_allow_html=True)
                    toggle_label = "Deactivate" if is_active else "Activate"
                    if st.button(toggle_label, key=f"rr_tog_{r['_row']}"):
                        new_val = "No" if is_active else "Yes"
                        svc["recurring"].update_cell(r["_row"], 7, new_val)
                        st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB: DOCUMENT REQUESTS
        # ──────────────────────────────────────────────────────
        with tab_docs:
            st.markdown("#### Document Requests")
            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("Create New Document Request", expanded=False):
                with st.form("new_doc_req", clear_on_submit=True):
                    dr1, dr2 = st.columns(2)
                    with dr1:
                        dr_client   = st.selectbox("Client", CLIENT_LIST, key="dr_cli")
                        dr_template = st.selectbox("Template", list(DOC_REQUEST_TEMPLATES.keys()), key="dr_tmpl")
                        dr_custom   = st.text_input("Custom Name (overrides template)", key="dr_name")
                    with dr2:
                        dr_due  = st.date_input("Due Date", today + timedelta(days=7), key="dr_due")
                    tmpl_cat, tmpl_desc = DOC_REQUEST_TEMPLATES.get(
                        st.session_state.get("dr_tmpl","Custom Request"), ("Other",""))
                    dr_desc = st.text_area("Description", value=tmpl_desc, key="dr_desc", height=60)
                    if st.form_submit_button("Send Request"):
                        req_name = dr_custom.strip() or dr_template
                        add_doc_request(dr_client, req_name, tmpl_cat, dr_desc.strip(), dr_due)
                        add_comm_log(dr_client, "Document Request", f"Requested: {req_name}", st.session_state.username)
                        st.success(f"Request sent to {dr_client}.")
                        st.rerun()

            st.markdown("<br>")
            df1, df2 = st.columns([2, 2])
            with df1: dr_f_cli    = st.selectbox("Filter Client", ["All Clients"]+CLIENT_LIST, key="drf_cli")
            with df2: dr_f_status = st.selectbox("Filter Status", ["All","Pending","Uploaded","Approved","Waived"], key="drf_status")

            doc_view = all_doc_req
            if dr_f_cli != "All Clients":   doc_view = [r for r in doc_view if r.get("Client")==dr_f_cli]
            if dr_f_status != "All":        doc_view = [r for r in doc_view if str(r.get("Status","")).strip()==dr_f_status]

            if not doc_view:
                st.info("No document requests match the current filters.")
            else:
                status_icon  = {"Pending":"📄","Uploaded":"✅","Approved":"✔️","Waived":"—"}
                status_cls   = {"Pending":"doc-req-pending","Uploaded":"doc-req-uploaded","Approved":"doc-req-approved","Waived":"doc-req-waived"}
                for req in doc_view:
                    status   = str(req.get("Status","Pending")).strip()
                    card_cls = "doc-req-card " + status_cls.get(status, "")
                    due_disp = req.get("Due Date","") or "No deadline"
                    icon     = status_icon.get(status,"📄")
                    rc1, rc2 = st.columns([5, 1])
                    with rc1:
                        st.markdown(
                            f"<div class='{card_cls}'>"
                            f"<div class='doc-req-name'>{icon}  {req.get('Request Name','')} <span style='font-weight:400;color:#A8B5A3;font-size:0.85em;'>· {req.get('Client','')}</span></div>"
                            f"<div class='doc-req-meta'>{req.get('Category','')}  ·  Due: {due_disp}"
                            + (f"  ·  Uploaded: {req.get('Uploaded Date','')}" if req.get("Uploaded Date") else "")
                            + f"</div></div>",
                            unsafe_allow_html=True)
                    with rc2:
                        if status == "Uploaded":
                            if st.button("Approve", key=f"dr_approve_{req['_row']}"):
                                update_doc_request(req["_row"], "Approved")
                                st.rerun()
                        elif status == "Pending":
                            if st.button("Waive", key=f"dr_waive_{req['_row']}"):
                                update_doc_request(req["_row"], "Waived")
                                st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB: MESSAGES
        # ──────────────────────────────────────────────────────
        with tab_msgs:
            st.markdown("#### Secure Messages")
            st.markdown("<br>", unsafe_allow_html=True)
            mc1, mc2 = st.columns([1, 2])
            with mc1:
                st.markdown("**Conversations**")
                for cli in CLIENT_LIST:
                    unread = _last_sender(cli) == "client"
                    label  = f"{cli} 🔵" if unread else cli
                    if st.button(label, key=f"msg_cli_{cli}", use_container_width=True):
                        st.session_state["msg_active"] = cli
            with mc2:
                active_msg = st.session_state.get("msg_active", CLIENT_LIST[0] if CLIENT_LIST else "")
                if active_msg:
                    st.markdown(f"**Thread: {active_msg}**")
                    thread = [m for m in all_messages if str(m.get("Client","")).strip()==active_msg]
                    bubbles = "<div class='msg-area'>"
                    if not thread:
                        bubbles += "<div class='msg-no-messages'>No messages yet. Start the conversation below.</div>"
                    else:
                        for msg in thread:
                            stype = str(msg.get("Sender Type","")).strip()
                            mtext = str(msg.get("Message","")).strip()
                            mdate = str(msg.get("Date","")).strip()
                            sname = str(msg.get("Sender Name","")).strip()
                            if stype == "firm":
                                bubbles += f"<div class='msg-row msg-row-firm'><div class='msg-meta' style='text-align:right;'>{sname}</div><div class='msg-bubble msg-bubble-firm'>{mtext}</div><div class='msg-meta' style='text-align:right;'>{mdate}</div></div>"
                            else:
                                bubbles += f"<div class='msg-row msg-row-client'><div class='msg-meta'>{sname}</div><div class='msg-bubble msg-bubble-client'>{mtext}</div><div class='msg-meta'>{mdate}</div></div>"
                    bubbles += "</div>"
                    st.markdown(bubbles, unsafe_allow_html=True)
                    with st.form(f"firm_msg_{active_msg}", clear_on_submit=True):
                        msg_text = st.text_area("Message", height=70, label_visibility="collapsed", placeholder="Type your message…")
                        if st.form_submit_button("Send"):
                            if msg_text.strip():
                                send_message(active_msg, "firm", st.session_state.username, msg_text.strip())
                                add_comm_log(active_msg, "Portal Message", msg_text.strip()[:80], st.session_state.username)
                                st.rerun()

        # ──────────────────────────────────────────────────────
        # TAB: CLIENT PROFILES
        # ──────────────────────────────────────────────────────
        with tab_profiles:
            st.markdown("#### Client Profiles")
            st.markdown("<br>", unsafe_allow_html=True)

            if "show_add_client" not in st.session_state: st.session_state.show_add_client = False
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
                        nc_contract = st.selectbox("Contract Signed", ["No","Yes"])
                    nf1, nf2 = st.columns(2)
                    with nf1: nc_start = st.date_input("Engagement Start", today)
                    with nf2: nc_ref   = st.text_input("Referral Source")
                    if st.form_submit_button("Create Client"):
                        if not nc_name.strip():         st.warning("Name required.")
                        elif nc_name.strip() in CLIENT_LIST: st.warning("Client already exists.")
                        else:
                            ok = add_client(nc_name.strip(),nc_contact.strip(),nc_email.strip(),nc_phone.strip(),nc_tier,nc_status,nc_rate.strip(),nc_contract,nc_start,nc_ref.strip())
                            if ok:
                                st.success(f"'{nc_name.strip()}' added.")
                                st.session_state.show_add_client = False
                                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            status_badge_map = {"Active":"badge-done","Onboarding":"badge-progress","On Hold":"badge-waiting","Offboarding":"badge-open","Prospect":"badge-open"}

            for client in CLIENT_LIST:
                rec       = CLI_LOOKUP.get(client, {})
                score, dot, dot_cls, reasons = compute_health(client, all_tasks, all_invoices, all_doc_req, CLI_LOOKUP, today)
                cli_tasks  = [t for t in all_tasks if t.get("client")==client and str(t.get("status","")).strip()!="Completed"]
                cli_inv    = [i for i in all_invoices if i.get("client")==client and str(i.get("status","")).strip().lower()!="paid"]
                cli_ar     = sum(_fmt_money(i.get("amount","")) for i in cli_inv)
                cli_hrs    = sum(float(str(t.get("Hours",0)) or 0) for t in all_timelog if t.get("Client")==client and str(t.get("Date","")).startswith(this_month))
                s_val      = str(rec.get("Client Status","Active")).strip()
                s_badge    = status_badge_map.get(s_val,"badge-open")
                attn_chip  = "<span class='attention-chip'>Needs Attention</span>" if client in clients_needing_attn else ""

                with st.expander(client, expanded=False):
                    hdr1, hdr2 = st.columns([4, 1])
                    with hdr1:
                        st.markdown(f"<span class='status-badge {s_badge}'>{s_val}</span>{attn_chip}", unsafe_allow_html=True)
                    with hdr2:
                        reason_tip = " · ".join(reasons) if reasons else "All good"
                        st.markdown(f"<div style='text-align:right;'><span class='{dot_cls}' style='font-size:1.4em;' title='{reason_tip}'>{dot}</span> <span style='font-family:Montserrat,sans-serif;font-size:0.8em;color:#888;'>{score}/100</span></div>", unsafe_allow_html=True)
                    if reasons:
                        st.caption("Flags: " + " · ".join(reasons))

                    st.markdown("<br>", unsafe_allow_html=True)

                    pm1, pm2, pm3, pm4 = st.columns(4)
                    with pm1: st.metric("Open Tasks",       len(cli_tasks))
                    with pm2: st.metric("Unpaid Invoices",  len(cli_inv))
                    with pm3: st.metric("AR Outstanding",   f"${cli_ar:,.2f}")
                    with pm4: st.metric("Hours This Month", f"{cli_hrs:.1f}h")

                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    pd1, pd2, pd3 = st.columns(3)
                    fields = [("Contact","Contact Name"),("Email","Email"),("Phone","Phone"),
                              ("Service Tier","Service Tier"),("Monthly Rate","Monthly Rate"),("Contract Signed","Contract Signed"),
                              ("Engagement Start","Engagement Start"),("Referral Source","Referral Source"),("Last Contacted","Last Contacted")]
                    for i, (lbl, key) in enumerate(fields):
                        val = str(rec.get(key,"") or "") or "—"
                        with [pd1,pd2,pd3][i%3]:
                            st.markdown(f"<div class='profile-field-label'>{lbl}</div><div class='profile-field-value'>{val}</div>", unsafe_allow_html=True)

                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    # AI Engagement Letter
                    with st.expander("Generate Engagement Letter (AI)", expanded=False):
                        el_services = st.multiselect("Services", SERVICE_TIERS, key=f"el_svc_{client}")
                        el_rate     = st.text_input("Monthly Rate", value=str(rec.get("Monthly Rate","") or ""), key=f"el_rate_{client}")
                        el_start    = st.date_input("Start Date", today, key=f"el_start_{client}")
                        if st.button("Generate Letter", key=f"el_gen_{client}"):
                            prompt = (
                                f"Write a professional engagement letter for a bookkeeping services agreement.\n"
                                f"Firm: Clearly Better Books by KB\nBookkeeper: Kay Bedair\n"
                                f"Client: {client}\nContact: {str(rec.get('Contact Name','')) or client}\n"
                                f"Services: {', '.join(el_services)}\nMonthly Rate: ${el_rate}\nStart Date: {el_start}\n\n"
                                f"Include: scope of services, monthly fee, payment terms (due on receipt), "
                                f"confidentiality clause, termination clause (30 days notice), acceptance signature block. "
                                f"Tone: professional, warm, clear. Format as a letter ready to send."
                            )
                            letter, err = ai_complete(prompt, max_tokens=2500)
                            if letter:
                                st.session_state[f"el_result_{client}"] = letter
                            elif err:
                                st.warning(err)

                        if f"el_result_{client}" in st.session_state:
                            st.text_area("Engagement Letter", value=st.session_state[f"el_result_{client}"], height=300, key=f"el_txt_{client}")
                            cli_email = str(rec.get("Email","")).strip()
                            if cli_email:
                                gmail = gmail_compose_url(cli_email, f"Engagement Letter — Clearly Better Books", st.session_state[f"el_result_{client}"])
                                st.markdown(f"<a href='{gmail}' target='_blank' class='link-btn'>Open in Gmail</a>", unsafe_allow_html=True)

                    # Comm log
                    st.markdown("**Log Communication**")
                    lc1, lc2, lc3 = st.columns([2, 3, 1])
                    with lc1: log_type = st.selectbox("Type",["Email","Call","Meeting","Portal Message","Text","Other"],key=f"lt_{client}",label_visibility="collapsed")
                    with lc2: log_sum  = st.text_input("Summary",key=f"ls_{client}",placeholder="Brief note…",label_visibility="collapsed")
                    with lc3:
                        if st.button("Log",key=f"lb_{client}"):
                            if log_sum.strip():
                                add_comm_log(client,log_type,log_sum.strip(),st.session_state.username)
                                st.success("Logged.")
                                st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Internal notes
                    nk = f"notes_{client.replace(' ','_')}"
                    if nk not in st.session_state:
                        st.session_state[nk] = str(rec.get("Internal Notes","") or "")
                    st.markdown("**Internal Notes** *(firm-only)*")
                    new_note = st.text_area("Notes",value=st.session_state[nk],key=f"ni_{client}",height=70,label_visibility="collapsed",placeholder="Add notes about this client…")
                    if new_note != st.session_state[nk]:
                        st.session_state[nk] = new_note
                        update_client_col(client,"Internal Notes",new_note)

                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    # Profile Completeness
                    pct, filled, total = profile_completeness(rec)
                    st.markdown(f"**Profile Completeness — {pct}% ({filled}/{total} fields)**")
                    st.progress(pct / 100)
                    missing = [f for f in ["Contact Name","Email","Phone","Service Tier","Monthly Rate","Contract Signed","Engagement Start","Referral Source"] if not str(rec.get(f,"")).strip()]
                    if missing:
                        st.caption("Missing: " + ", ".join(missing))

                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    # Client Portal Invite
                    with st.expander("Generate Portal Invite (Create Client Login)", expanded=False):
                        inv_email = str(rec.get("Email","")).strip()
                        inv1, inv2 = st.columns(2)
                        with inv1:
                            inv_username = st.text_input("Portal Username", value=inv_email, key=f"inv_user_{client}")
                        with inv2:
                            import secrets as _sec
                            inv_password = st.text_input("Temporary Password",
                                                          value=st.session_state.get(f"inv_pw_{client}", _sec.token_hex(4)),
                                                          key=f"inv_pw_input_{client}")

                        if st.button("Create Portal Login", key=f"inv_create_{client}"):
                            if inv_username.strip():
                                ok = add_portal_user(inv_username.strip(), inv_password.strip(), "client", client, client)
                                if ok:
                                    st.session_state[f"inv_created_{client}"] = (inv_username.strip(), inv_password.strip())
                                    st.success(f"Portal login created for {client}.")
                                else:
                                    st.error("Could not create login. Check Google Sheets connection.")

                        if f"inv_created_{client}" in st.session_state:
                            inv_u, inv_p = st.session_state[f"inv_created_{client}"]
                            firm_name  = get_firm_setting("firm_name","Clearly Better Books")
                            portal_url = "https://clearly-better-clients.streamlit.app"
                            invite_msg = (
                                f"Hi {str(rec.get('Contact Name','')) or client},\n\n"
                                f"Your {firm_name} client portal is ready! You can log in to view your tasks, "
                                f"upload documents, send messages, and check your invoices.\n\n"
                                f"Portal: {portal_url}\n"
                                f"Username: {inv_u}\n"
                                f"Password: {inv_p}\n\n"
                                f"Please change your password after your first login by letting me know "
                                f"a new one and I'll update it for you.\n\n"
                                f"Best,\nKay | {firm_name}"
                            )
                            st.markdown(f"<div class='ai-label'>Portal Invite Email</div><div class='ai-box'>{invite_msg}</div>", unsafe_allow_html=True)
                            if inv_email:
                                gmail = gmail_compose_url(inv_email, f"Your {firm_name} Client Portal is Ready", invite_msg)
                                st.markdown(f"<a href='{gmail}' target='_blank' class='link-btn'>Open in Gmail</a>", unsafe_allow_html=True)

                    # AI Monthly Report Generator
                    with st.expander("Generate Monthly Client Report (AI)", expanded=False):
                        rep_month = st.selectbox("Report Month",
                            [(today.replace(day=1) - timedelta(days=30*i)).strftime("%B %Y") for i in range(6)],
                            key=f"rep_month_{client}")
                        rep_months_ago = [(today.replace(day=1) - timedelta(days=30*i)).strftime("%Y-%m") for i in range(6)]
                        sel_month_str  = rep_months_ago[[(today.replace(day=1) - timedelta(days=30*i)).strftime("%B %Y") for i in range(6)].index(rep_month)]

                        # Gather data for the report
                        cli_tasks_done = [t for t in all_tasks if t.get("client")==client and str(t.get("status",""))=="Completed"]
                        cli_hours_mo   = sum(float(str(t.get("Hours",0)) or 0) for t in all_timelog if t.get("Client")==client and str(t.get("Date","")).startswith(sel_month_str))
                        cli_inv_mo     = [i for i in all_invoices if i.get("client")==client and str(i.get("due_date","")).startswith(sel_month_str)]
                        cli_service    = str(rec.get("Service Tier","")) or "bookkeeping services"

                        if st.button("Generate Report", key=f"rep_gen_{client}"):
                            prompt = (
                                f"Write a professional monthly summary email from a bookkeeper to their client.\n\n"
                                f"Bookkeeper: Kay (Clearly Better Books)\n"
                                f"Client: {client}\n"
                                f"Service: {cli_service}\n"
                                f"Month: {rep_month}\n"
                                f"Tasks completed: {len(cli_tasks_done)}\n"
                                f"Hours logged: {cli_hours_mo:.1f}h\n"
                                f"Invoices this month: {len(cli_inv_mo)}\n\n"
                                f"Write a warm, professional 3-paragraph monthly recap covering:\n"
                                f"1. What was accomplished this month\n"
                                f"2. Key items to note or action items for the client\n"
                                f"3. What's coming next month\n\n"
                                f"Keep it friendly, concise, and non-jargon-heavy. Sign off as 'Kay | Clearly Better Books'."
                            )
                            report, err = ai_complete(prompt)
                            if report:
                                st.session_state[f"rep_result_{client}"] = report
                            elif err:
                                st.warning(err)

                        if f"rep_result_{client}" in st.session_state:
                            st.text_area("Monthly Report", value=st.session_state[f"rep_result_{client}"], height=250, key=f"rep_txt_{client}")
                            cli_email_rep = str(rec.get("Email","")).strip()
                            if cli_email_rep:
                                gmail = gmail_compose_url(cli_email_rep, f"{rep_month} Bookkeeping Summary — Clearly Better Books", st.session_state[f"rep_result_{client}"])
                                st.markdown(f"<a href='{gmail}' target='_blank' class='link-btn'>Open in Gmail</a>", unsafe_allow_html=True)

        # ──────────────────────────────────────────────────────
        # TAB: ACTIVITY LOG
        # ──────────────────────────────────────────────────────
        with tab_log:
            st.markdown("#### Activity Log")
            st.markdown("<br>", unsafe_allow_html=True)
            al1, al2 = st.columns([2, 2])
            with al1: al_cli  = st.selectbox("Filter Client",["All Clients"]+CLIENT_LIST,key="al_cli")
            with al2: al_type = st.selectbox("Filter Type",["All","Email","Call","Meeting","Portal Message","Text","Time Log","Document Request","Task Update","Invoice","Other"],key="al_type")
            log_view = list(reversed(all_comm))
            if al_cli  != "All Clients": log_view = [e for e in log_view if e.get("Client")==al_cli]
            if al_type != "All":         log_view = [e for e in log_view if e.get("Type")==al_type]
            type_icons = {"Email":"📧","Call":"📞","Meeting":"🤝","Portal Message":"💬","Text":"📱","Time Log":"⏱","Document Request":"📄","Task Update":"✅","Invoice":"🧾","Other":"📋"}
            if not log_view:
                st.info("No activity logged yet.")
            else:
                for entry in log_view[:60]:
                    icon = type_icons.get(str(entry.get("Type","")), "📋")
                    st.markdown(
                        f"<div class='activity-entry'>{icon}&nbsp;<strong>{entry.get('Client','')}</strong>&nbsp;·&nbsp;<span style='color:#A8B5A3;font-size:0.85em;'>{entry.get('Type','')}</span><br><span style='color:#555;'>{entry.get('Summary','')}</span>&nbsp;&nbsp;<span style='color:#A8B5A3;font-size:0.82em;'>{entry.get('Date','')}</span></div>",
                        unsafe_allow_html=True)
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
        # TAB: PIPELINE
        # ──────────────────────────────────────────────────────
        with tab_pipe:
            st.markdown("#### Prospect Pipeline")
            st.markdown("<br>", unsafe_allow_html=True)
            if "show_add_lead" not in st.session_state: st.session_state.show_add_lead = False
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
                        if pl_name.strip():
                            add_pipeline_lead(pl_name.strip(),pl_contact.strip(),pl_email.strip(),
                                              ", ".join(pl_service),pl_stage,pl_value.strip(),pl_follow,pl_notes.strip())
                            st.session_state.show_add_lead = False
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            stage_badge_cls = {"New Lead":"stage-new","Proposal Sent":"stage-proposal","Proposal Accepted":"stage-accepted","Onboarding":"stage-onboarding","Closed Lost":"badge-open"}
            for stage in PIPELINE_STAGES:
                leads = [p for p in all_pipeline if str(p.get("Stage","")).strip()==stage]
                if not leads: continue
                _sbadge = stage_badge_cls.get(stage,"badge-open")
                st.markdown(f"<span class='pipeline-stage {_sbadge}'>{stage}</span><span style='color:#A8B5A3;font-size:0.82em;margin-left:8px;'>{len(leads)} lead(s)</span>", unsafe_allow_html=True)
                for lead in leads:
                    lname = str(lead.get("Lead Name","")).strip()
                    with st.expander(lname, expanded=False):
                        lc1, lc2, lc3 = st.columns(3)
                        defs = [("Contact","Contact"),("Email","Email"),("Service Interest","Service Interest"),("Est. Monthly Value","Est Monthly Value"),("Follow-Up Date","Follow Up Date"),("Date Added","Date Added")]
                        for i, (lbl, key) in enumerate(defs):
                            with [lc1,lc2,lc3][i%3]:
                                st.markdown(f"<div class='profile-field-label'>{lbl}</div><div class='profile-field-value'>{str(lead.get(key,'') or '—')}</div>", unsafe_allow_html=True)
                        if lead.get("Notes"):
                            st.markdown(f"<div class='note-box'>{lead.get('Notes')}</div>", unsafe_allow_html=True)
                        new_stage = st.selectbox("Move to Stage", PIPELINE_STAGES,
                                                  index=PIPELINE_STAGES.index(stage) if stage in PIPELINE_STAGES else 0,
                                                  key=f"ps_{lname}")
                        if new_stage != stage and st.button("Update Stage", key=f"pu_{lname}"):
                            update_pipeline_stage(lname, new_stage)
                            st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # CLIENT WORKSPACE
    # ══════════════════════════════════════════════════════════
    else:
        st.markdown(f"<h5 style='font-family:Montserrat,Lato,sans-serif;letter-spacing:0.12em;text-transform:uppercase;color:#A8B5A3;font-size:0.78rem;font-weight:600;'>Workspace: {active_client}</h5>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        cli_tasks   = [dict(r, _row=i+2) for i, r in enumerate(all_tasks)    if r.get("client")==active_client]
        cli_inv     = [dict(r, _row=i+2) for i, r in enumerate(all_invoices)  if r.get("client")==active_client]
        cli_doc_req = [r for r in all_doc_req  if str(r.get("Client","")).strip()==active_client]
        cli_msgs    = [r for r in all_messages if str(r.get("Client","")).strip()==active_client]
        unpaid_cli  = [i for i in cli_inv if str(i.get("status","")).strip().lower()!="paid"]
        paid_cli    = [i for i in cli_inv if str(i.get("status","")).strip().lower()=="paid"]
        pending_req = [r for r in cli_doc_req if str(r.get("Status","")).strip()=="Pending"]
        awaiting    = [t for t in cli_tasks if str(t.get("status","")).strip()=="Awaiting Client"]
        open_cli    = [t for t in cli_tasks if str(t.get("status","")).strip() not in ("Completed",)]

        tab_todo, tab_cmsg, tab_cdocs, tab_cinv = st.tabs(["My To-Do","Messages","Documents","Invoices & Payments"])

        # CLIENT: MY TO-DO
        with tab_todo:
            todo_items = []
            total_cli_ar = sum(_fmt_money(i.get("amount","")) for i in unpaid_cli)
            if unpaid_cli:
                todo_items.append({"type":"invoice_summary","invoices":unpaid_cli,"total":total_cli_ar})
            for req in pending_req:
                todo_items.append({"type":"doc","req":req})
            for t in awaiting:
                todo_items.append({"type":"task","task":t,"priority":True})
            for t in open_cli:
                if str(t.get("status","")).strip() not in ("Awaiting Client","Completed"):
                    todo_items.append({"type":"task","task":t,"priority":False})

            if not todo_items:
                st.markdown("<div class='all-clear'><span class='all-clear-icon'>✓</span><span class='all-clear-text'>You're all caught up — nothing needs your attention right now.</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.9em;margin-bottom:16px;'>You have <strong>{len(todo_items)}</strong> item(s) that need your attention.</p>", unsafe_allow_html=True)
                for item in todo_items:
                    if item["type"] == "invoice_summary":
                        st.markdown(f"<div class='todo-card todo-card-invoice'><div class='todo-type todo-type-invoice'>Payment Due</div><div class='todo-title'>Balance Outstanding — ${item['total']:,.2f}</div><div class='todo-meta'>{len(item['invoices'])} unpaid invoice(s)</div></div>", unsafe_allow_html=True)
                        for inv in item["invoices"]:
                            ic1, ic2 = st.columns([3,1])
                            with ic1:
                                st.markdown(f"<div class='portal-card' style='margin-bottom:6px;'><strong>Invoice #{inv.get('invoice_num','')}</strong>&nbsp;&nbsp;<span style='color:#333;font-size:1.05em;'>{inv.get('amount','')}</span><br><span style='color:#A8B5A3;font-size:0.84em;'>Due: {inv.get('due_date','')}</span></div>", unsafe_allow_html=True)
                            with ic2:
                                pay_link = inv.get("pay_link","")
                                if pay_link:
                                    st.markdown(f"<a href='{pay_link}' target='_blank' class='invoice-btn'>Pay Now</a>", unsafe_allow_html=True)
                                if admin:
                                    if st.button(f"Mark Paid #{inv.get('invoice_num','')}", key=f"cp_{inv['_row']}"):
                                        mark_invoice_paid(inv["_row"])
                                        st.rerun()

                    elif item["type"] == "doc":
                        req     = item["req"]
                        due_str = str(req.get("Due Date","")).strip()
                        st.markdown(f"<div class='todo-card todo-card-doc'><div class='todo-type todo-type-doc'>Document Needed</div><div class='todo-title'>{req.get('Request Name','')}</div><div class='todo-meta'>{req.get('Category','')}  ·  Due: {due_str or 'No deadline'}  ·  {req.get('Description','')}</div></div>", unsafe_allow_html=True)
                        up_key = f"todo_up_{req['_row']}"
                        if not st.session_state.get(f"show_{up_key}"):
                            if st.button("Upload Document", key=f"todo_show_{req['_row']}"):
                                st.session_state[f"show_{up_key}"] = True
                                st.rerun()
                        else:
                            doc_file = st.file_uploader(f"Upload: {req.get('Request Name','')}", key=up_key, type=["pdf","png","jpg","csv","xlsx","docx"])
                            if doc_file:
                                with st.spinner("Uploading…"):
                                    fid = upload_to_drive(active_client, doc_file)
                                if fid:
                                    update_doc_request(req["_row"], "Uploaded", fid)
                                    add_comm_log(active_client, "Document Request", f"Uploaded: {req.get('Request Name','')}", active_client)
                                    st.success("Uploaded! Your bookkeeper will review it shortly.")
                                    st.session_state[f"show_{up_key}"] = False
                                    st.rerun()

                    elif item["type"] == "task":
                        t      = item["task"]
                        status = str(t.get("status","")).strip()
                        due_s  = str(t.get("due","")).strip()
                        bk     = {"Pending":"badge-open","In Progress":"badge-progress","Awaiting Client":"badge-waiting"}.get(status,"badge-open")
                        st.markdown(
                            f"<div class='todo-card todo-card-task'>"
                            f"<div class='todo-type todo-type-task'>{'Action Required' if status=='Awaiting Client' else 'In Progress'}</div>"
                            f"<div class='todo-title'>{str(t.get('task','')) or '*(Untitled)*'}</div>"
                            f"<div class='todo-meta'><span class='status-badge {bk}'>{status}</span>"
                            + (f"  ·  Due: {due_s}" if due_s else "") + f"</div></div>",
                            unsafe_allow_html=True)
                        if status == "Awaiting Client":
                            if st.button("Mark Complete", key=f"cli_done_{t['_row']}"):
                                update_task_status(t["_row"], "Completed")
                                st.rerun()

        # CLIENT: MESSAGES
        with tab_cmsg:
            st.markdown("<h3>Messages</h3>", unsafe_allow_html=True)
            st.markdown("<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.88em;'>Send a message to your bookkeeper. We typically respond within one business day.</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            bubbles = "<div class='msg-area'>"
            if not cli_msgs:
                bubbles += "<div class='msg-no-messages'>No messages yet. Send us a note below!</div>"
            else:
                for msg in cli_msgs:
                    stype = str(msg.get("Sender Type","")).strip()
                    mtext = str(msg.get("Message","")).strip()
                    mdate = str(msg.get("Date","")).strip()
                    sname = str(msg.get("Sender Name","")).strip()
                    if stype == "firm":
                        bubbles += f"<div class='msg-row msg-row-firm'><div class='msg-meta' style='text-align:right;'>Clearly Better Books</div><div class='msg-bubble msg-bubble-firm'>{mtext}</div><div class='msg-meta' style='text-align:right;'>{mdate}</div></div>"
                    else:
                        bubbles += f"<div class='msg-row msg-row-client'><div class='msg-meta'>{sname}</div><div class='msg-bubble msg-bubble-client'>{mtext}</div><div class='msg-meta'>{mdate}</div></div>"
            bubbles += "</div>"
            st.markdown(bubbles, unsafe_allow_html=True)
            with st.form("cli_msg_form", clear_on_submit=True):
                cli_msg_text = st.text_area("Your message", height=90, label_visibility="collapsed", placeholder="Type your message here…")
                if st.form_submit_button("Send Message"):
                    if cli_msg_text.strip():
                        send_message(active_client, "client", active_client, cli_msg_text.strip())
                        add_comm_log(active_client, "Portal Message", cli_msg_text.strip()[:80], active_client)
                        st.success("Message sent!")
                        st.rerun()

        # CLIENT: DOCUMENTS
        with tab_cdocs:
            st.markdown("<h3>Documents</h3>", unsafe_allow_html=True)
            if cli_doc_req:
                st.markdown("#### Requested Documents")
                st.markdown("<p style='font-family:Lato,sans-serif;color:#888888;font-size:0.88em;'>Your bookkeeper has requested the following documents.</p>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                status_icon = {"Pending":"📄","Uploaded":"✅","Approved":"✔️","Waived":"—"}
                status_cls  = {"Pending":"doc-req-pending","Uploaded":"doc-req-uploaded","Approved":"doc-req-approved","Waived":"doc-req-waived"}
                for req in cli_doc_req:
                    status   = str(req.get("Status","Pending")).strip()
                    card_cls = "doc-req-card " + status_cls.get(status,"")
                    due_disp = req.get("Due Date","") or "No deadline"
                    icon     = status_icon.get(status,"📄")
                    st.markdown(f"<div class='{card_cls}'><div class='doc-req-name'>{icon}  {req.get('Request Name','')}</div><div class='doc-req-meta'>{req.get('Category','')}  ·  Due: {due_disp}" + (f"  ·  <em>{req.get('Description','')}</em>" if req.get("Description") else "") + f"</div></div>", unsafe_allow_html=True)
                    if status == "Pending":
                        up_key = f"cdoc_up_{req['_row']}"
                        if not st.session_state.get(f"show_{up_key}"):
                            if st.button("Upload", key=f"cdoc_show_{req['_row']}"):
                                st.session_state[f"show_{up_key}"] = True
                                st.rerun()
                        else:
                            uf = st.file_uploader(f"Upload: {req.get('Request Name','')}", key=up_key, type=["pdf","png","jpg","csv","xlsx","docx"])
                            if uf:
                                with st.spinner("Uploading to your secure folder…"):
                                    fid = upload_to_drive(active_client, uf)
                                if fid:
                                    update_doc_request(req["_row"],"Uploaded",fid)
                                    add_comm_log(active_client,"Document Request",f"Uploaded: {req.get('Request Name','')}",active_client)
                                    st.success("Uploaded!")
                                    st.session_state[f"show_{up_key}"] = False
                                    st.rerun()
                    elif status == "Uploaded":
                        st.caption("Uploaded — awaiting your bookkeeper's review.")
                    elif status == "Approved":
                        st.caption("Approved — thank you!")
                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

            st.markdown("#### Upload a Document")
            st.markdown("<div class='upload-zone'><div class='custom-upload-title'>Secure File Drop</div><div class='custom-upload-subtitle'>PDF, PNG, JPG, CSV, XLSX, DOCX · Max 200MB</div></div>", unsafe_allow_html=True)
            if "show_general_up" not in st.session_state: st.session_state.show_general_up = False
            if st.button("Select File", key="gen_up_btn"):
                st.session_state.show_general_up = True
            if st.session_state.show_general_up:
                gen_file = st.file_uploader("File", label_visibility="collapsed", type=["pdf","png","jpg","csv","xlsx","docx"])
                if gen_file:
                    with st.spinner("Uploading…"):
                        fid = upload_to_drive(active_client, gen_file)
                    if fid:
                        add_comm_log(active_client,"Document Request",f"General upload: {gen_file.name}",active_client)
                        st.success("File saved to your secure folder.")

        # CLIENT: INVOICES & PAYMENTS
        with tab_cinv:
            st.markdown("<h3>Invoices & Payments</h3>", unsafe_allow_html=True)
            total_cli_ar = sum(_fmt_money(i.get("amount","")) for i in unpaid_cli)
            if unpaid_cli:
                st.markdown(f"<p style='font-family:Lato,sans-serif;font-size:1.05em;'><strong>Total Outstanding: ${total_cli_ar:,.2f}</strong></p>", unsafe_allow_html=True)
            st.markdown("#### Outstanding Balance")
            if not unpaid_cli:
                st.success("No unpaid invoices on your account.")
            else:
                for inv in unpaid_cli:
                    st.markdown(
                        f"<div class='portal-card'><table style='width:100%;border:none;background:none;margin:0;padding:0;'><tr style='background:none;border:none;'>"
                        f"<td style='border:none;width:45%;padding:0;'><span style='font-family:Playfair Display,Georgia,serif;font-size:1.2em;font-weight:600;'>Invoice #{inv.get('invoice_num','')}</span><br><span style='font-size:0.83rem;color:#A8B5A3;font-family:Lato,sans-serif;'>Due: {inv.get('due_date','')}</span></td>"
                        f"<td style='border:none;width:25%;vertical-align:middle;padding:0;'><span style='font-size:1.5em;font-weight:600;font-family:Playfair Display,Georgia,serif;'>{inv.get('amount','')}</span></td>"
                        f"<td style='border:none;width:30%;text-align:right;vertical-align:middle;padding:0;'><a href='{inv.get('pay_link','')}' target='_blank' class='invoice-btn'>Pay Invoice</a></td>"
                        f"</tr></table></div>",
                        unsafe_allow_html=True)
                    if admin:
                        if st.button(f"Mark Paid — #{inv.get('invoice_num','')}", key=f"ip_{inv['_row']}"):
                            mark_invoice_paid(inv["_row"])
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
                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
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
