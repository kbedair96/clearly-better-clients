import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Clearly Better Books - Client Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED BRAND STYLING ENGINE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');
.stApp { background-color: #F7F4EF !important; }
.stMainBlockContainer { background-color: #FFFFFF !important; border: 1px solid #DADDD6 !important; border-radius: 4px !important; padding-top: 2.5rem !important; padding-bottom: 3rem !important; }
[data-testid="stSidebar"] { background-color: #F7F3EE !important; border-right: 1px solid #DADDD6 !important; }
[data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]):not([translate="no"]) { font-family: 'Lato', 'Montserrat', sans-serif !important; color: #333333 !important; }
html, body, .stApp { font-family: 'Lato', 'Montserrat', sans-serif !important; color: #333333 !important; }
.stMarkdown, p, label, div[data-testid="stMarkdownContainer"], div[data-testid="stText"] { font-family: 'Lato', 'Montserrat', sans-serif !important; color: #333333 !important; }
[data-testid="stIconMaterial"], [translate="no"], .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; font-style: normal !important; font-weight: normal !important; line-height: 1 !important; }
details summary { font-family: 'Lato', sans-serif !important; font-weight: 600 !important; color: #333333 !important; letter-spacing: 0.02em !important; display: flex !important; align-items: center !important; gap: 6px !important; }
details summary [data-testid="stIconMaterial"], details summary [translate="no"] { font-family: 'Material Symbols Rounded' !important; color: #A8B5A3 !important; font-size: 1.1em !important; flex-shrink: 0 !important; }
details[open] summary { color: #A8B5A3 !important; }
details[open] summary [data-testid="stIconMaterial"], details[open] summary [translate="no"] { color: #A8B5A3 !important; }
h1.brand-title { font-family: 'Playfair Display', Georgia, serif !important; font-weight: 600 !important; font-size: 2.6rem !important; letter-spacing: 0.01em !important; color: #333333 !important; text-align: center !important; margin-bottom: 0.2rem !important; }
p.brand-tagline { font-family: 'Lato', sans-serif !important; font-style: italic !important; font-size: 1.0rem !important; color: #A8B5A3 !important; text-align: center !important; margin-top: 0 !important; letter-spacing: 0.02em !important; }
div.brand-divider { width: 60px !important; height: 1px !important; background-color: #A8B5A3 !important; margin: 1rem auto 1.5rem auto !important; }
h2, h3, h4, h5, h6 { font-family: 'Playfair Display', Georgia, serif !important; font-weight: 400 !important; color: #333333 !important; }
button[data-baseweb="tab"] { font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.85rem !important; font-weight: 500 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; color: #888888 !important; background: transparent !important; border: none !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #A8B5A3 !important; border-bottom: 2px solid #A8B5A3 !important; }
div[data-baseweb="tab-highlight"] { background-color: #A8B5A3 !important; }
div[data-baseweb="tab-border"] { background-color: #DADDD6 !important; }
.stButton > button { background-color: #A8B5A3 !important; color: #FFFFFF !important; border: none !important; border-radius: 3px !important; font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; padding: 0.5rem 1.4rem !important; transition: background-color 0.2s ease !important; }
.stButton > button:hover { background-color: #8FA189 !important; color: #FFFFFF !important; }
.stFormSubmitButton > button { background-color: #A8B5A3 !important; color: #FFFFFF !important; border: none !important; border-radius: 3px !important; font-family: 'Montserrat', 'Lato', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
.stFormSubmitButton > button:hover { background-color: #8FA189 !important; }
a.invoice-btn { display: inline-block !important; background-color: #A8B5A3 !important; color: #FFFFFF !important; text-decoration: none !important; padding: 7px 18px !important; border-radius: 3px !important; font-family: 'Montserrat', sans-serif !important; font-size: 0.76rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
a.invoice-btn:hover { background-color: #8FA189 !important; }
div.portal-card { background: #FFFFFF !important; border: 1px solid #DADDD6 !important; border-radius: 4px !important; padding: 18px 22px !important; margin-bottom: 12px !important; }
.stTextInput input, .stSelectbox select, .stTextArea textarea, div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { border: 1px solid #DADDD6 !important; border-radius: 3px !important; background-color: #FAFAF8 !important; color: #333333 !important; font-family: 'Lato', sans-serif !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #A8B5A3 !important; box-shadow: 0 0 0 2px rgba(168,181,163,0.18) !important; }
div[data-testid="stFileUploader"] section { background-color: #F7F3EE !important; border: 1px dashed #A8B5A3 !important; border-radius: 4px !important; }
div[data-testid="stFileUploader"] section:hover { border-color: #8FA189 !important; background-color: #F0EDE8 !important; }
.custom-upload-container { background: #F7F3EE !important; border: 1px dashed #A8B5A3 !important; border-radius: 4px !important; padding: 20px 24px !important; text-align: center !important; margin-bottom: 14px !important; }
.custom-upload-title { font-family: 'Playfair Display', serif !important; font-size: 1.1em !important; color: #333333 !important; margin-bottom: 4px !important; }
.custom-upload-subtitle { font-family: 'Lato', sans-serif !important; font-size: 0.82em !important; color: #888888 !important; }
div[data-testid="stFileUploader"] section small, div[data-testid="stFileUploader"] section span:not([translate="no"]) { color: #888888 !important; font-family: 'Lato', sans-serif !important; }
.dashboard-stat { text-align: center; padding: 20px 10px; border-right: 1px solid #DADDD6; }
.dashboard-stat:last-child { border-right: none; }
.dashboard-stat-number { font-family: 'Playfair Display', Georgia, serif; font-size: 2.4em; font-weight: 600; color: #333333; display: block; line-height: 1.1; }
.dashboard-stat-label { font-family: 'Montserrat', sans-serif; font-size: 0.72em; color: #A8B5A3; letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-top: 4px; }
.client-card { background: #FFFFFF; border: 1px solid #DADDD6; border-left: 3px solid #A8B5A3; border-radius: 4px; padding: 14px 18px; margin-bottom: 10px; font-family: 'Lato', sans-serif; }
.client-card-alert { background: #FDFAF7; border: 1px solid #DADDD6; border-left: 3px solid #EBC6C1; border-radius: 4px; padding: 14px 18px; margin-bottom: 10px; font-family: 'Lato', sans-serif; }
.status-badge { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 0.75em; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-family: 'Montserrat', sans-serif; }
.badge-open { background: #F7F3EE; color: #A8B5A3; border: 1px solid #DADDD6; }
.badge-progress { background: #EAF0E8; color: #6E8A69; border: 1px solid #C5D4C2; }
.badge-waiting { background: #FAF2F1; color: #C4878A; border: 1px solid #EBC6C1; }
.badge-done { background: #F0F3EF; color: #7A9477; border: 1px solid #C2D1BF; }
.badge-prospect { background: #EEF0FA; color: #6678B1; border: 1px solid #C2CAE8; }
.section-divider { border: none; border-top: 1px solid #DADDD6; margin: 24px 0; }
.note-box { background: #F7F3EE; border: 1px solid #DADDD6; border-radius: 4px; padding: 12px 16px; font-size: 0.9em; color: #555; margin-top: 8px; font-family: 'Lato', sans-serif; }
[data-testid="metric-container"] { background: #FAFAF8 !important; border: 1px solid #DADDD6 !important; border-radius: 4px !important; padding: 12px 16px !important; }
.activity-entry { padding: 10px 0; border-bottom: 1px solid #F0ECE7; font-family: 'Lato', sans-serif; font-size: 0.9em; }
.activity-icon { font-size: 1.1em; margin-right: 6px; }
.profile-field-label { font-family: 'Montserrat', sans-serif; font-size: 0.72em; letter-spacing: 0.1em; text-transform: uppercase; color: #A8B5A3; margin-bottom: 2px; }
.profile-field-value { font-family: 'Lato', sans-serif; font-size: 0.95em; color: #333333; margin-bottom: 12px; }
.attention-chip { display: inline-block; background: #FAF2F1; color: #C4878A; border: 1px solid #EBC6C1; border-radius: 2px; padding: 2px 8px; font-size: 0.72em; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-left: 8px; }
.pipeline-stage { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 0.75em; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; font-family: 'Montserrat', sans-serif; }
.stage-new { background: #EEF0FA; color: #6678B1; border: 1px solid #C2CAE8; }
.stage-proposal { background: #FFF4E6; color: #B87333; border: 1px solid #F0D4B0; }
.stage-accepted { background: #EAF0E8; color: #6E8A69; border: 1px solid #C5D4C2; }
.stage-onboarding { background: #F0F3EF; color: #7A9477; border: 1px solid #C2D1BF; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F7F4EF; }
::-webkit-scrollbar-thumb { background: #DADDD6; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A8B5A3; }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE CLOUD CONFIGURATION ---
GOOGLE_SHEET_NAME = "FirmLink_DB"
SHARED_DRIVE_ID = "0AFQkhoAnS2U-Uk9PVA"
MAIN_DRIVE_FOLDER_ID = "0AFQkhoAnS2U-Uk9PVA"
CLIENTS_SHEET_NAME = "Clients"
USERS_SHEET_NAME = "Users"
COMM_LOG_SHEET_NAME = "CommLog"
PIPELINE_SHEET_NAME = "Pipeline"

# Column headers for each sheet
CLIENTS_HEADERS = [
    "Client Name", "Contact Name", "Email", "Phone", "Date Added",
    "Service Tier", "Client Status", "Monthly Rate", "Contract Signed",
    "Engagement Start", "Referral Source", "Last Contacted", "Internal Notes"
]
COMM_LOG_HEADERS = ["Date", "Client", "Type", "Summary", "Logged By"]
PIPELINE_HEADERS = ["Lead Name", "Contact", "Email", "Service Interest", "Stage", "Est Monthly Value", "Follow Up Date", "Notes", "Date Added"]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CLIENT_ROLE = "client"

def is_admin_role(role):
    return str(role).strip().lower() != CLIENT_ROLE

# --- WORKFLOW TEMPLATES ---
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
        ("Send welcome email + portal access", 1),
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
        ("Pull Q financials from QBO", 2),
        ("Prepare Q P&L and Balance Sheet", 3),
        ("Draft variance commentary", 5),
        ("Schedule quarterly review call", 5),
        ("Deliver quarterly summary deck", 7),
    ],
}

# --- CONNECT TO GOOGLE SERVICES ---
@st.cache_resource
def get_google_services():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            dict(st.secrets["gcp_service_account"]), SCOPES
        )
        spreadsheet = gspread.authorize(creds).open(GOOGLE_SHEET_NAME)
        task_sheet = spreadsheet.sheet1
        invoice_sheet = spreadsheet.worksheet("Invoices")
        drive_service = build('drive', 'v3', credentials=creds)
        return spreadsheet, task_sheet, invoice_sheet, drive_service
    except Exception as e:
        st.error(f"Failed to connect to Google Services. Error: {e}")
        return None, None, None, None

spreadsheet, task_sheet, invoice_sheet, drive_service = get_google_services()

# --- USERS WORKSHEET HELPER ---
def get_user_records():
    if spreadsheet is None:
        return []
    try:
        ws = spreadsheet.worksheet(USERS_SHEET_NAME)
        return ws.get_all_records()
    except Exception:
        return []

# --- CLIENTS WORKSHEET HELPERS ---
def get_clients_worksheet():
    if spreadsheet is None:
        return None
    try:
        ws = spreadsheet.worksheet(CLIENTS_SHEET_NAME)
        return ws
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=CLIENTS_SHEET_NAME, rows=200, cols=len(CLIENTS_HEADERS))
        ws.append_row(CLIENTS_HEADERS)
        return ws

def get_client_records():
    ws = get_clients_worksheet()
    if ws is None:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []

def add_client(client_name, contact_name, email, phone,
               service_tier="", client_status="Active", monthly_rate="",
               contract_signed="No", engagement_start="", referral_source=""):
    ws = get_clients_worksheet()
    if ws is None:
        return False
    date_added = date.today().strftime("%Y-%m-%d")
    ws.append_row([
        client_name, contact_name, email, phone, date_added,
        service_tier, client_status, monthly_rate, contract_signed,
        engagement_start, referral_source, date_added, ""
    ])
    return True

def update_client_field(client_name, field_name, new_value):
    """Update a single field for a client row in the Clients sheet."""
    ws = get_clients_worksheet()
    if ws is None:
        return False
    try:
        headers = ws.row_values(1)
        if field_name not in headers:
            return False
        col_idx = headers.index(field_name) + 1
        all_records = ws.get_all_records()
        for i, rec in enumerate(all_records):
            if str(rec.get("Client Name", "")).strip() == client_name.strip():
                ws.update_cell(i + 2, col_idx, new_value)
                return True
        return False
    except Exception:
        return False

# --- COMMUNICATION LOG HELPERS ---
def get_comm_log_worksheet():
    if spreadsheet is None:
        return None
    try:
        ws = spreadsheet.worksheet(COMM_LOG_SHEET_NAME)
        return ws
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=COMM_LOG_SHEET_NAME, rows=500, cols=len(COMM_LOG_HEADERS))
        ws.append_row(COMM_LOG_HEADERS)
        return ws

def get_comm_log_records():
    ws = get_comm_log_worksheet()
    if ws is None:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []

def add_comm_log_entry(client, entry_type, summary, logged_by="Firm"):
    ws = get_comm_log_worksheet()
    if ws is None:
        return False
    entry_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.append_row([entry_date, client, entry_type, summary, logged_by])
    # Also update Last Contacted on the client record
    update_client_field(client, "Last Contacted", date.today().strftime("%Y-%m-%d"))
    return True

# --- PIPELINE HELPERS ---
def get_pipeline_worksheet():
    if spreadsheet is None:
        return None
    try:
        ws = spreadsheet.worksheet(PIPELINE_SHEET_NAME)
        return ws
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=PIPELINE_SHEET_NAME, rows=200, cols=len(PIPELINE_HEADERS))
        ws.append_row(PIPELINE_HEADERS)
        return ws

def get_pipeline_records():
    ws = get_pipeline_worksheet()
    if ws is None:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []

def add_pipeline_lead(lead_name, contact, email, service_interest, stage,
                      est_monthly_value, follow_up_date, notes):
    ws = get_pipeline_worksheet()
    if ws is None:
        return False
    date_added = date.today().strftime("%Y-%m-%d")
    ws.append_row([
        lead_name, contact, email, service_interest, stage,
        est_monthly_value, str(follow_up_date), notes, date_added
    ])
    return True

def update_pipeline_stage(lead_name, new_stage):
    ws = get_pipeline_worksheet()
    if ws is None:
        return False
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        stage_col = headers.index("Stage") + 1
        for i, rec in enumerate(records):
            if str(rec.get("Lead Name", "")).strip() == lead_name.strip():
                ws.update_cell(i + 2, stage_col, new_stage)
                return True
        return False
    except Exception:
        return False

# --- GOOGLE DRIVE HELPERS ---
def get_or_create_client_folder(client_name):
    query = (
        f"name = '{client_name}' and '{MAIN_DRIVE_FOLDER_ID}' in parents "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    try:
        results = drive_service.files().list(
            q=query, fields="files(id)", corpora="drive",
            driveId=SHARED_DRIVE_ID, supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']
        else:
            file_metadata = {
                'name': client_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [MAIN_DRIVE_FOLDER_ID]
            }
            folder = drive_service.files().create(
                body=file_metadata, fields='id', supportsAllDrives=True
            ).execute()
            return folder.get('id')
    except Exception as e:
        st.error(f"Google Drive folder path resolution error: {e}")
        return None

def upload_file_to_drive(client_name, uploaded_file):
    folder_id = get_or_create_client_folder(client_name)
    if not folder_id:
        st.error("Upload aborted: Parent workspace target directory could not be resolved.")
        return None
    file_metadata = {'name': uploaded_file.name, 'parents': [folder_id]}
    file_stream = io.BytesIO(uploaded_file.getvalue())
    media = MediaIoBaseUpload(file_stream, mimetype=uploaded_file.type, resumable=True)
    try:
        uploaded_drive_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id', supportsAllDrives=True
        ).execute()
        return uploaded_drive_file.get('id')
    except Exception as e:
        st.error(f"File upload failed: {e}")
        return None

# --- AUTHENTICATION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.client_association = None
    st.session_state.username = None

def handle_logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.client_association = None
    st.session_state.username = None
    st.rerun()

# =====================================
# LOGIN GATEWAY
# =====================================
if not st.session_state.authenticated:
    st.markdown("<h1 class='brand-title'>Clearly Better Books</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-tagline'>Bookkeeping that brings clarity, confidence, and calm to your business.</p>", unsafe_allow_html=True)
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: normal; letter-spacing: 0.02em;'>Secure Portal Login</h3>", unsafe_allow_html=True)

    login_left, login_mid, login_right = st.columns([1, 2, 1])
    with login_mid:
        with st.form("portal_login_form", clear_on_submit=False):
            input_user = st.text_input("Username / Email").strip()
            input_pass = st.text_input("Password", type="password").strip()
            login_btn = st.form_submit_button("Sign In")

        if login_btn:
            users_db = get_user_records()
            matched_profile = None
            for row in users_db:
                if (str(row.get("username", "")).strip() == input_user and
                        str(row.get("password", "")).strip() == input_pass and
                        input_user != ""):
                    matched_profile = row
                    break

            if matched_profile:
                st.session_state.authenticated = True
                st.session_state.username = matched_profile.get("username")
                st.session_state.user_role = matched_profile.get("role")
                st.session_state.client_association = matched_profile.get("client_association")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

# =====================================
# AUTHENTICATED APP
# =====================================
else:
    is_admin = is_admin_role(st.session_state.user_role)

    # --- DYNAMIC CLIENT LIST ---
    BASE_CLIENTS = ["Acme Corp", "Baker Street Cafe"]
    _client_records = get_client_records()
    _added_clients = [
        str(r.get("Client Name", "")).strip()
        for r in _client_records
        if str(r.get("Client Name", "")).strip()
    ]
    CLIENT_LIST = list(dict.fromkeys(BASE_CLIENTS + _added_clients))
    # Only active clients (not prospects) in the main client list
    _active_client_records = [
        r for r in _client_records
        if str(r.get("Client Status", "Active")).strip().lower() not in ("prospect", "churned")
    ]
    ACTIVE_CLIENT_NAMES = list(dict.fromkeys(
        BASE_CLIENTS + [str(r.get("Client Name", "")).strip() for r in _active_client_records if str(r.get("Client Name", "")).strip()]
    ))

    # --- SIDEBAR ---
    if is_admin:
        st.sidebar.markdown(
            "<h3 style='text-align: center; margin-top: 20px; font-weight: 400; "
            "font-family: Playfair Display, Georgia, serif; color: #333333; letter-spacing: 0.02em;'>"
            "Firm Controls</h3>",
            unsafe_allow_html=True
        )
        firm_view = st.sidebar.radio(
            "View:", ["Practice Dashboard", "Client Workspace"], key="firm_view_mode"
        )
        active_client = st.sidebar.selectbox("Manage Client:", CLIENT_LIST)
    else:
        firm_view = "Client Workspace"
        active_client = str(st.session_state.client_association or "").strip()
        if active_client and active_client not in CLIENT_LIST:
            CLIENT_LIST.append(active_client)
        st.sidebar.markdown(
            "<h3 style='text-align: center; margin-top: 20px; font-weight: 400; "
            "font-family: Playfair Display, Georgia, serif; color: #333333; letter-spacing: 0.02em;'>"
            "Client Account</h3>",
            unsafe_allow_html=True
        )
        st.sidebar.markdown(
            f"<p style='text-align: center; font-size:1.1em;'><b>{active_client}</b></p>",
            unsafe_allow_html=True
        )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("Log Out of Portal", key="portal_logout_btn"):
        handle_logout()

    st.sidebar.markdown(
        "<br><br><hr style='border-color: #DADDD6; border-width: 1px;'>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        f"<p style='font-size:0.76em; text-align:center; color:#A8B5A3; line-height: 1.6;'>"
        f"Logged in user:<br><span style='color:#333333; font-weight:600;'>"
        f"{st.session_state.username}</span></p>",
        unsafe_allow_html=True
    )

    # --- MAIN BRAND HEADER ---
    st.markdown("<h1 class='brand-title'>Clearly Better Books</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='brand-tagline'>Bookkeeping that brings clarity, confidence, and calm to your business.</p>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)

    if task_sheet is not None and invoice_sheet is not None and drive_service is not None:
        # ---- Load ALL sheet data ONCE here — no tab should re-fetch independently ----
        all_tasks    = task_sheet.get_all_records()
        all_invoices = invoice_sheet.get_all_records()
        pipeline_records = get_pipeline_records()
        comm_records     = get_comm_log_records()
        today = date.today()

        # =====================================
        # FIRM / PRACTICE DASHBOARD VIEW
        # =====================================
        if is_admin and firm_view == "Practice Dashboard":
            st.markdown(
                "<h5 style='font-family:Montserrat,Lato,sans-serif; letter-spacing:0.12em; "
                "text-transform:uppercase; color:#A8B5A3; font-size:0.78rem; font-weight:600;'>"
                "Practice Dashboard</h5>",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # ---- KPI CALCULATIONS ----
            open_tasks_all = [t for t in all_tasks if str(t.get("status", "")).strip() != "Completed"]
            overdue_tasks = []
            for t in open_tasks_all:
                try:
                    due = datetime.strptime(str(t.get("due", "")).strip(), "%Y-%m-%d").date()
                    if due < today:
                        overdue_tasks.append(t)
                except Exception:
                    pass

            unpaid_all = [
                i for i in all_invoices
                if str(i.get("status", "")).strip().lower() != "paid"
            ]
            total_ar = 0
            for inv in unpaid_all:
                try:
                    amt = str(inv.get("amount", "")).replace("$", "").replace(",", "").strip()
                    total_ar += float(amt)
                except Exception:
                    pass

            # MRR from client records
            mrr_total = 0
            for rec in _client_records:
                try:
                    rate = str(rec.get("Monthly Rate", "")).replace("$", "").replace(",", "").strip()
                    if rate:
                        mrr_total += float(rate)
                except Exception:
                    pass

            # Clients needing attention: overdue tasks OR AR > 30 days OR no contact in 30 days
            clients_needing_attention = set()
            for t in overdue_tasks:
                c = str(t.get("client", "")).strip()
                if c:
                    clients_needing_attention.add(c)
            for inv in unpaid_all:
                try:
                    due_str = str(inv.get("due_date", "")).strip()
                    due_d = datetime.strptime(due_str, "%Y-%m-%d").date()
                    if (today - due_d).days > 30:
                        c = str(inv.get("client", "")).strip()
                        if c:
                            clients_needing_attention.add(c)
                except Exception:
                    pass

            # ---- ROW 1: CORE KPIs ----
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>{len(CLIENT_LIST)}</span>"
                    f"<span class='dashboard-stat-label'>Active Clients</span></div>",
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>{len(open_tasks_all)}</span>"
                    f"<span class='dashboard-stat-label'>Open Tasks</span></div>",
                    unsafe_allow_html=True
                )
            with col3:
                ot_color = "#C4878A" if overdue_tasks else "#333333"
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number' style='color:{ot_color}'>{len(overdue_tasks)}</span>"
                    f"<span class='dashboard-stat-label'>Overdue Tasks</span></div>",
                    unsafe_allow_html=True
                )
            with col4:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>${total_ar:,.2f}</span>"
                    f"<span class='dashboard-stat-label'>Total AR Outstanding</span></div>",
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # ---- ROW 2: GROWTH KPIs ----
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>${mrr_total:,.0f}</span>"
                    f"<span class='dashboard-stat-label'>Est. Monthly Revenue</span></div>",
                    unsafe_allow_html=True
                )
            with col6:
                attn_color = "#C4878A" if clients_needing_attention else "#7A9477"
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number' style='color:{attn_color}'>"
                    f"{len(clients_needing_attention)}</span>"
                    f"<span class='dashboard-stat-label'>Needs Attention ⚠</span></div>",
                    unsafe_allow_html=True
                )
            with col7:
                active_pipeline = [
                    p for p in pipeline_records
                    if str(p.get("Stage", "")).strip().lower() not in ("", "closed lost")
                ]
                pipeline_value = 0
                for p in active_pipeline:
                    try:
                        v = str(p.get("Est Monthly Value", "")).replace("$", "").replace(",", "").strip()
                        if v:
                            pipeline_value += float(v)
                    except Exception:
                        pass
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>{len(active_pipeline)}</span>"
                    f"<span class='dashboard-stat-label'>Active Leads</span></div>",
                    unsafe_allow_html=True
                )
            with col8:
                st.markdown(
                    f"<div class='dashboard-stat'>"
                    f"<span class='dashboard-stat-number'>${pipeline_value:,.0f}</span>"
                    f"<span class='dashboard-stat-label'>Pipeline MRR</span></div>",
                    unsafe_allow_html=True
                )

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

            # ---- DASHBOARD TABS ----
            dash_tab1, dash_tab2, dash_tab3, dash_tab4, dash_tab5 = st.tabs([
                "All Tasks", "AR Overview", "Client Profiles", "Activity Log", "Pipeline"
            ])

            # ---- TAB 1: ALL TASKS ----
            with dash_tab1:
                st.markdown("#### Open Tasks Across All Clients")
                st.markdown("<br>", unsafe_allow_html=True)

                # Workflow template launcher
                with st.expander("🔁  Launch Workflow Template", expanded=False):
                    wf_col1, wf_col2, wf_col3 = st.columns([2, 2, 1])
                    with wf_col1:
                        wf_template = st.selectbox(
                            "Template", list(WORKFLOW_TEMPLATES.keys()), key="wf_template_select"
                        )
                    with wf_col2:
                        wf_client = st.selectbox(
                            "For Client", CLIENT_LIST, key="wf_client_select"
                        )
                    with wf_col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Launch", key="wf_launch_btn"):
                            template_tasks = WORKFLOW_TEMPLATES[wf_template]
                            start = date.today()
                            for task_name, days_offset in template_tasks:
                                due_date_wf = date(start.year, start.month, min(start.day + days_offset, 28))
                                task_sheet.append_row([
                                    wf_client, task_name, "Pending", str(due_date_wf)
                                ])
                            st.success(
                                f"✓ Launched '{wf_template}' for {wf_client} — "
                                f"{len(template_tasks)} tasks created."
                            )
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
                with f_col1:
                    filter_client = st.selectbox(
                        "Filter by Client", ["All Clients"] + CLIENT_LIST, key="dash_filter_client"
                    )
                with f_col2:
                    filter_status = st.selectbox(
                        "Filter by Status",
                        ["All", "Pending", "In Progress", "Awaiting Client", "Completed"],
                        key="dash_filter_status"
                    )
                with f_col3:
                    filter_overdue = st.checkbox("Show Overdue Only", key="dash_filter_overdue")

                st.markdown("<br>", unsafe_allow_html=True)

                tasks_to_show = list(all_tasks)
                if filter_client != "All Clients":
                    tasks_to_show = [t for t in tasks_to_show if t.get("client") == filter_client]
                if filter_status != "All":
                    tasks_to_show = [
                        t for t in tasks_to_show
                        if str(t.get("status", "")).strip() == filter_status
                    ]
                if filter_overdue:
                    _filtered = []
                    for t in tasks_to_show:
                        try:
                            due = datetime.strptime(
                                str(t.get("due", "")).strip(), "%Y-%m-%d"
                            ).date()
                            if due < today and str(t.get("status", "")).strip() != "Completed":
                                _filtered.append(t)
                        except Exception:
                            pass
                    tasks_to_show = _filtered

                if not tasks_to_show:
                    st.info("No tasks match the current filters.")
                else:
                    status_options = ["Pending", "In Progress", "Awaiting Client", "Completed"]
                    for idx, task in enumerate(tasks_to_show):
                        status = str(task.get("status", "Pending")).strip()
                        task_name = str(task.get("task", "")).strip() or "*(Untitled task)*"
                        is_overdue = False
                        try:
                            due_d = datetime.strptime(
                                str(task.get("due", "")).strip(), "%Y-%m-%d"
                            ).date()
                            is_overdue = due_d < today and status != "Completed"
                        except Exception:
                            pass

                        badge = {
                            "Pending": "badge-open",
                            "In Progress": "badge-progress",
                            "Awaiting Client": "badge-waiting",
                            "Completed": "badge-done"
                        }.get(status, "badge-open")
                        overdue_note = " 🔴" if is_overdue else ""

                        tc1, tc2, tc3, tc4 = st.columns([3, 2, 2, 2])
                        with tc1:
                            st.markdown(f"**{task_name}**{overdue_note}")
                            st.caption(f"Client: {task.get('client', '')}")
                        with tc2:
                            st.markdown(
                                f"<span class='status-badge {badge}'>{status}</span>",
                                unsafe_allow_html=True
                            )
                        with tc3:
                            due_display = task.get("due", "")
                            st.caption(f"Due: {due_display}" if due_display else "No due date")
                        with tc4:
                            new_status = st.selectbox(
                                "Update", status_options,
                                index=status_options.index(status) if status in status_options else 0,
                                key=f"dash_task_status_{idx}",
                                label_visibility="collapsed"
                            )
                            if new_status != status:
                                all_recs = task_sheet.get_all_records()
                                for si, rec in enumerate(all_recs):
                                    if (rec.get("client") == task.get("client") and
                                            rec.get("task") == task.get("task") and
                                            rec.get("due") == task.get("due")):
                                        task_sheet.update_cell(si + 2, 3, new_status)
                                        st.rerun()
                        st.markdown(
                            "<hr style='border:none;border-top:1px solid #F0ECE7;margin:6px 0;'>",
                            unsafe_allow_html=True
                        )

            # ---- TAB 2: AR OVERVIEW ----
            with dash_tab2:
                st.markdown("#### Accounts Receivable — All Clients")
                st.markdown("<br>", unsafe_allow_html=True)

                for client in CLIENT_LIST:
                    client_unpaid = [
                        i for i in all_invoices
                        if i.get("client") == client
                        and str(i.get("status", "")).strip().lower() != "paid"
                    ]
                    client_total = 0
                    days_overdue_max = 0
                    for inv in client_unpaid:
                        try:
                            amt = str(inv.get("amount", "")).replace("$", "").replace(",", "").strip()
                            client_total += float(amt)
                        except Exception:
                            pass
                        try:
                            due_d = datetime.strptime(
                                str(inv.get("due_date", "")).strip(), "%Y-%m-%d"
                            ).date()
                            days_overdue_max = max(days_overdue_max, (today - due_d).days)
                        except Exception:
                            pass

                    alert = client_total > 0
                    card_c = "client-card-alert" if alert else "client-card"
                    color_ar = "#C4878A" if alert else "#7A9477"
                    aging_label = ""
                    if days_overdue_max > 60:
                        aging_label = "<span class='attention-chip'>60+ days</span>"
                    elif days_overdue_max > 30:
                        aging_label = "<span class='attention-chip'>30+ days</span>"

                    st.markdown(
                        f"<div class='{card_c}'>"
                        f"<strong style='font-family:Lato,sans-serif;'>{client}</strong>"
                        f"{aging_label} &nbsp;&nbsp;"
                        f"<span style='color:#A8B5A3;font-size:0.88em;font-family:Lato,sans-serif;'>"
                        f"{len(client_unpaid)} unpaid invoice(s)</span> &nbsp;&nbsp;"
                        f"<strong style='color:{color_ar};'>${client_total:,.2f} outstanding</strong>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                if unpaid_all:
                    st.markdown("<br>")
                    st.markdown("#### All Unpaid Invoices")
                    inv_data = []
                    for inv in unpaid_all:
                        # Calculate days overdue
                        days_due = ""
                        try:
                            due_d = datetime.strptime(
                                str(inv.get("due_date", "")).strip(), "%Y-%m-%d"
                            ).date()
                            diff = (today - due_d).days
                            days_due = f"{diff} days overdue" if diff > 0 else "Current"
                        except Exception:
                            days_due = ""

                        inv_data.append({
                            "Client": inv.get("client", ""),
                            "Invoice #": inv.get("invoice_num", ""),
                            "Amount": inv.get("amount", ""),
                            "Due Date": inv.get("due_date", ""),
                            "Aging": days_due,
                            "Status": inv.get("status", "Unpaid"),
                        })
                    st.dataframe(
                        pd.DataFrame(inv_data),
                        use_container_width=True,
                        hide_index=True
                    )

            # ---- TAB 3: CLIENT PROFILES (ENRICHED) ----
            with dash_tab3:
                st.markdown("#### Client Profiles")
                st.markdown("<br>", unsafe_allow_html=True)

                if "show_add_client" not in st.session_state:
                    st.session_state.show_add_client = False

                if st.button("+ Add New Client", key="add_client_btn"):
                    st.session_state.show_add_client = not st.session_state.show_add_client

                if st.session_state.show_add_client:
                    with st.form("add_client_form", clear_on_submit=True):
                        st.markdown("**New Client Details**")
                        nc1, nc2 = st.columns(2)
                        with nc1:
                            nc_name = st.text_input("Client / Business Name *")
                            nc_contact = st.text_input("Primary Contact Name")
                            nc_email = st.text_input("Email")
                            nc_phone = st.text_input("Phone")
                        with nc2:
                            nc_service = st.selectbox(
                                "Service Tier",
                                ["Monthly Bookkeeping", "Catch-Up / Cleanup",
                                 "AP/AR Management", "Sales Tax", "Advisory", "Other"]
                            )
                            nc_status = st.selectbox(
                                "Client Status",
                                ["Active", "Onboarding", "On Hold", "Offboarding"]
                            )
                            nc_rate = st.text_input("Monthly Rate ($)")
                            nc_contract = st.selectbox("Contract Signed", ["No", "Yes"])
                        ncf1, ncf2 = st.columns(2)
                        with ncf1:
                            nc_start = st.date_input("Engagement Start Date", date.today())
                        with ncf2:
                            nc_referral = st.text_input("Referral Source")
                        nc_submit = st.form_submit_button("Create Client")

                        if nc_submit:
                            if not nc_name.strip():
                                st.warning("Client Name is required.")
                            elif nc_name.strip() in CLIENT_LIST:
                                st.warning(f"A client named '{nc_name.strip()}' already exists.")
                            else:
                                ok = add_client(
                                    nc_name.strip(), nc_contact.strip(), nc_email.strip(),
                                    nc_phone.strip(), nc_service, nc_status, nc_rate.strip(),
                                    nc_contract, str(nc_start), nc_referral.strip()
                                )
                                if ok:
                                    st.success(f"Client '{nc_name.strip()}' added successfully.")
                                    st.session_state.show_add_client = False
                                    st.rerun()
                                else:
                                    st.error("Could not add client. Check the Google Sheets connection.")

                st.markdown("<br>", unsafe_allow_html=True)

                # Build a lookup dict from client records for enriched fields
                client_record_lookup = {
                    str(r.get("Client Name", "")).strip(): r
                    for r in _client_records
                }

                for client in CLIENT_LIST:
                    rec = client_record_lookup.get(client, {})
                    open_tasks = [
                        t for t in all_tasks
                        if t.get("client") == client
                        and str(t.get("status", "")).strip() != "Completed"
                    ]
                    unpaid_invs = [
                        i for i in all_invoices
                        if i.get("client") == client
                        and str(i.get("status", "")).strip().lower() != "paid"
                    ]
                    client_ar = 0
                    for inv in unpaid_invs:
                        try:
                            client_ar += float(
                                str(inv.get("amount", "")).replace("$", "").replace(",", "").strip()
                            )
                        except Exception:
                            pass

                    # Attention flag
                    needs_attn = client in clients_needing_attention
                    attn_chip = "<span class='attention-chip'>Needs Attention</span>" if needs_attn else ""
                    client_status_val = str(rec.get("Client Status", "Active")).strip()
                    status_badge_map = {
                        "Active": "badge-done",
                        "Onboarding": "badge-progress",
                        "On Hold": "badge-waiting",
                        "Offboarding": "badge-open",
                    }
                    status_badge = status_badge_map.get(client_status_val, "badge-open")

                    with st.expander(f"{client}", expanded=False):
                        # Status row
                        st.markdown(
                            f"<span class='status-badge {status_badge}'>{client_status_val}</span>"
                            f"{attn_chip}",
                            unsafe_allow_html=True
                        )
                        st.markdown("<br>", unsafe_allow_html=True)

                        # KPI row
                        pc1, pc2, pc3 = st.columns(3)
                        with pc1:
                            st.metric("Open Tasks", len(open_tasks))
                        with pc2:
                            st.metric("Unpaid Invoices", len(unpaid_invs))
                        with pc3:
                            st.metric("AR Outstanding", f"${client_ar:,.2f}")

                        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                        # Contact & Engagement details
                        d1, d2, d3 = st.columns(3)
                        with d1:
                            st.markdown(
                                f"<div class='profile-field-label'>Contact</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Contact Name', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='profile-field-label'>Email</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Email', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='profile-field-label'>Phone</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Phone', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                        with d2:
                            st.markdown(
                                f"<div class='profile-field-label'>Service Tier</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Service Tier', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='profile-field-label'>Monthly Rate</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Monthly Rate', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='profile-field-label'>Contract Signed</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Contract Signed', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                        with d3:
                            st.markdown(
                                f"<div class='profile-field-label'>Engagement Start</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Engagement Start', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='profile-field-label'>Referral Source</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Referral Source', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='profile-field-label'>Last Contacted</div>"
                                f"<div class='profile-field-value'>"
                                f"{rec.get('Last Contacted', '—') or '—'}</div>",
                                unsafe_allow_html=True
                            )

                        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                        # Quick log a communication entry
                        st.markdown("**Log Communication**")
                        log_c1, log_c2, log_c3 = st.columns([2, 3, 1])
                        with log_c1:
                            log_type = st.selectbox(
                                "Type",
                                ["Email", "Call", "Meeting", "Portal Message", "Text", "Other"],
                                key=f"log_type_{client}",
                                label_visibility="collapsed"
                            )
                        with log_c2:
                            log_summary = st.text_input(
                                "Summary",
                                key=f"log_summary_{client}",
                                placeholder="Brief note about this interaction...",
                                label_visibility="collapsed"
                            )
                        with log_c3:
                            if st.button("Log", key=f"log_btn_{client}"):
                                if log_summary.strip():
                                    add_comm_log_entry(
                                        client, log_type, log_summary.strip(),
                                        st.session_state.username
                                    )
                                    st.success("Logged.")
                                    st.rerun()
                                else:
                                    st.warning("Enter a summary first.")

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Internal Notes
                        note_key = f"notes_{client.replace(' ', '_')}"
                        if note_key not in st.session_state:
                            st.session_state[note_key] = str(rec.get("Internal Notes", "") or "")
                        st.markdown("**Internal Notes** (firm-only, not visible to client)")
                        new_note = st.text_area(
                            "Notes", value=st.session_state[note_key],
                            key=f"note_input_{client}", height=80,
                            label_visibility="collapsed",
                            placeholder="Add internal notes about this client..."
                        )
                        if new_note != st.session_state[note_key]:
                            st.session_state[note_key] = new_note
                            update_client_field(client, "Internal Notes", new_note)

            # ---- TAB 4: ACTIVITY LOG ----
            with dash_tab4:
                st.markdown("#### Activity Log")
                st.markdown("<br>", unsafe_allow_html=True)

                # Filters
                al_col1, al_col2 = st.columns([2, 2])
                with al_col1:
                    al_client_filter = st.selectbox(
                        "Filter by Client",
                        ["All Clients"] + CLIENT_LIST,
                        key="al_client_filter"
                    )
                with al_col2:
                    al_type_filter = st.selectbox(
                        "Filter by Type",
                        ["All", "Email", "Call", "Meeting", "Portal Message", "Text",
                         "Task Update", "Invoice", "Other"],
                        key="al_type_filter"
                    )

                filtered_log = list(reversed(comm_records))  # newest first
                if al_client_filter != "All Clients":
                    filtered_log = [e for e in filtered_log if e.get("Client") == al_client_filter]
                if al_type_filter != "All":
                    filtered_log = [e for e in filtered_log if e.get("Type") == al_type_filter]

                if not filtered_log:
                    st.info("No activity logged yet. Use the communication log buttons in Client Profiles to start tracking interactions.")
                else:
                    type_icons = {
                        "Email": "📧", "Call": "📞", "Meeting": "🤝",
                        "Portal Message": "💬", "Text": "📱",
                        "Task Update": "✅", "Invoice": "🧾", "Other": "📋"
                    }
                    for entry in filtered_log[:50]:  # show latest 50
                        icon = type_icons.get(str(entry.get("Type", "")), "📋")
                        st.markdown(
                            f"<div class='activity-entry'>"
                            f"<span class='activity-icon'>{icon}</span>"
                            f"<strong style='font-family:Lato,sans-serif;'>"
                            f"{entry.get('Client', '')}</strong> &nbsp;·&nbsp; "
                            f"<span style='color:#A8B5A3;font-size:0.85em;'>"
                            f"{entry.get('Type', '')}</span>"
                            f"<br>"
                            f"<span style='color:#555555;'>{entry.get('Summary', '')}</span>"
                            f"&nbsp;&nbsp;"
                            f"<span style='color:#A8B5A3;font-size:0.82em;'>"
                            f"{entry.get('Date', '')}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                # Quick global log entry
                st.markdown("<br><hr class='section-divider'>", unsafe_allow_html=True)
                st.markdown("**Log New Entry**")
                with st.form("global_log_form", clear_on_submit=True):
                    gl1, gl2, gl3 = st.columns([2, 2, 3])
                    with gl1:
                        gl_client = st.selectbox("Client", CLIENT_LIST, key="gl_client")
                    with gl2:
                        gl_type = st.selectbox(
                            "Type",
                            ["Email", "Call", "Meeting", "Portal Message",
                             "Text", "Task Update", "Invoice", "Other"],
                            key="gl_type"
                        )
                    with gl3:
                        gl_summary = st.text_input("Summary", key="gl_summary")
                    gl_submit = st.form_submit_button("Add to Log")
                    if gl_submit:
                        if gl_summary.strip():
                            add_comm_log_entry(
                                gl_client, gl_type, gl_summary.strip(),
                                st.session_state.username
                            )
                            st.success("Entry logged.")
                            st.rerun()
                        else:
                            st.warning("Please enter a summary.")

            # ---- TAB 5: PIPELINE ----
            with dash_tab5:
                st.markdown("#### Prospect Pipeline")
                st.markdown("<br>", unsafe_allow_html=True)

                if "show_add_lead" not in st.session_state:
                    st.session_state.show_add_lead = False

                if st.button("+ Add Lead", key="add_lead_btn"):
                    st.session_state.show_add_lead = not st.session_state.show_add_lead

                if st.session_state.show_add_lead:
                    with st.form("add_lead_form", clear_on_submit=True):
                        st.markdown("**New Lead Details**")
                        pl1, pl2 = st.columns(2)
                        with pl1:
                            pl_name = st.text_input("Business / Lead Name *")
                            pl_contact = st.text_input("Contact Name")
                            pl_email = st.text_input("Email")
                        with pl2:
                            pl_service = st.multiselect(
                                "Service Interest",
                                ["Monthly Bookkeeping", "Catch-Up / Cleanup",
                                 "AP/AR Management", "Sales Tax", "Advisory"]
                            )
                            pl_stage = st.selectbox(
                                "Stage",
                                ["New Lead", "Proposal Sent", "Proposal Accepted",
                                 "Onboarding", "Closed Lost"]
                            )
                            pl_value = st.text_input("Est. Monthly Value ($)")
                        pl_follow = st.date_input("Follow-Up Date", date.today())
                        pl_notes = st.text_area("Notes", height=60)
                        pl_submit = st.form_submit_button("Add Lead")
                        if pl_submit:
                            if not pl_name.strip():
                                st.warning("Lead name is required.")
                            else:
                                ok = add_pipeline_lead(
                                    pl_name.strip(), pl_contact.strip(), pl_email.strip(),
                                    ", ".join(pl_service), pl_stage, pl_value.strip(),
                                    pl_follow, pl_notes.strip()
                                )
                                if ok:
                                    st.success(f"Lead '{pl_name.strip()}' added to pipeline.")
                                    st.session_state.show_add_lead = False
                                    st.rerun()
                                else:
                                    st.error("Could not add lead. Check the Google Sheets connection.")

                st.markdown("<br>", unsafe_allow_html=True)

                stage_order = ["New Lead", "Proposal Sent", "Proposal Accepted", "Onboarding", "Closed Lost"]
                stage_badge = {
                    "New Lead": "stage-new",
                    "Proposal Sent": "stage-proposal",
                    "Proposal Accepted": "stage-accepted",
                    "Onboarding": "stage-onboarding",
                    "Closed Lost": "badge-open",
                }

                if not pipeline_records:
                    st.info("No leads in the pipeline yet. Click '+ Add Lead' to get started.")
                else:
                    # Group by stage
                    for stage in stage_order:
                        stage_leads = [
                            p for p in pipeline_records
                            if str(p.get("Stage", "")).strip() == stage
                        ]
                        if not stage_leads:
                            continue

                        badge_cls = stage_badge.get(stage, "badge-open")
                        st.markdown(
                            f"<span class='pipeline-stage {badge_cls}'>{stage}</span>"
                            f"<span style='color:#A8B5A3; font-size:0.82em; margin-left:8px;'>"
                            f"{len(stage_leads)} lead(s)</span>",
                            unsafe_allow_html=True
                        )

                        for lead in stage_leads:
                            lead_name = str(lead.get("Lead Name", "")).strip()
                            with st.expander(lead_name, expanded=False):
                                lc1, lc2, lc3 = st.columns(3)
                                with lc1:
                                    st.markdown(
                                        f"<div class='profile-field-label'>Contact</div>"
                                        f"<div class='profile-field-value'>"
                                        f"{lead.get('Contact', '—') or '—'}</div>",
                                        unsafe_allow_html=True
                                    )
                                    st.markdown(
                                        f"<div class='profile-field-label'>Email</div>"
                                        f"<div class='profile-field-value'>"
                                        f"{lead.get('Email', '—') or '—'}</div>",
                                        unsafe_allow_html=True
                                    )
                                with lc2:
                                    st.markdown(
                                        f"<div class='profile-field-label'>Service Interest</div>"
                                        f"<div class='profile-field-value'>"
                                        f"{lead.get('Service Interest', '—') or '—'}</div>",
                                        unsafe_allow_html=True
                                    )
                                    st.markdown(
                                        f"<div class='profile-field-label'>Est. Monthly Value</div>"
                                        f"<div class='profile-field-value'>"
                                        f"${lead.get('Est Monthly Value', '—') or '—'}</div>",
                                        unsafe_allow_html=True
                                    )
                                with lc3:
                                    st.markdown(
                                        f"<div class='profile-field-label'>Follow-Up Date</div>"
                                        f"<div class='profile-field-value'>"
                                        f"{lead.get('Follow Up Date', '—') or '—'}</div>",
                                        unsafe_allow_html=True
                                    )
                                    st.markdown(
                                        f"<div class='profile-field-label'>Date Added</div>"
                                        f"<div class='profile-field-value'>"
                                        f"{lead.get('Date Added', '—') or '—'}</div>",
                                        unsafe_allow_html=True
                                    )

                                if lead.get("Notes"):
                                    st.markdown(
                                        f"<div class='note-box'>{lead.get('Notes')}</div>",
                                        unsafe_allow_html=True
                                    )

                                # Stage update
                                new_stage = st.selectbox(
                                    "Move to Stage",
                                    stage_order,
                                    index=stage_order.index(stage) if stage in stage_order else 0,
                                    key=f"pipeline_stage_{lead_name}"
                                )
                                if new_stage != stage:
                                    if st.button("Update Stage", key=f"update_stage_{lead_name}"):
                                        update_pipeline_stage(lead_name, new_stage)
                                        st.rerun()

                        st.markdown("<br>", unsafe_allow_html=True)

        # =====================================
        # CLIENT WORKSPACE VIEW
        # =====================================
        else:
            st.markdown(
                f"<h5 style='font-family:Montserrat,Lato,sans-serif; letter-spacing:0.12em; "
                f"text-transform:uppercase; color:#A8B5A3; font-size:0.78rem; font-weight:600;'>"
                f"Workspace: {active_client}</h5>",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            tab_tasks, tab_invoices, tab_documents = st.tabs([
                "Action Items", "Invoices & Payments", "Document Center"
            ])

            # --- TAB 1: ACTION ITEMS ---
            with tab_tasks:
                st.markdown("<h3>Open Requests & Tasks</h3>", unsafe_allow_html=True)
                client_tasks = [
                    dict(row, sheet_row=idx + 2)
                    for idx, row in enumerate(all_tasks)
                    if row["client"] == active_client
                ]

                if not client_tasks:
                    st.info("All caught up! No pending action items.")
                else:
                    status_opts = ["Pending", "In Progress", "Awaiting Client", "Completed"]
                    for task in client_tasks:
                        row_num = task["sheet_row"]
                        curr_status = str(task.get("status", "Pending")).strip()
                        task_name = str(task.get("task", "")).strip() or "*(Untitled task)*"
                        col_cb, col_txt, col_st, col_dt = st.columns([1, 4, 2, 2])
                        with col_cb:
                            is_done = st.checkbox(
                                "Done", key=f"check_{row_num}",
                                value=(curr_status == "Completed")
                            )
                            if is_done and curr_status != "Completed":
                                task_sheet.update_cell(row_num, 3, "Completed")
                                st.rerun()
                            elif not is_done and curr_status == "Completed":
                                task_sheet.update_cell(row_num, 3, "Pending")
                                st.rerun()
                        with col_txt:
                            if curr_status == "Completed":
                                st.markdown(f"~~{task_name}~~")
                            else:
                                st.markdown(f"**{task_name}**")
                        with col_st:
                            if is_admin:
                                idx_v = status_opts.index(curr_status) if curr_status in status_opts else 0
                                new_s = st.selectbox(
                                    "Status", status_opts, index=idx_v,
                                    key=f"status_{row_num}", label_visibility="collapsed"
                                )
                                if new_s != curr_status:
                                    task_sheet.update_cell(row_num, 3, new_s)
                                    st.rerun()
                            else:
                                badge = {
                                    "Pending": "badge-open", "In Progress": "badge-progress",
                                    "Awaiting Client": "badge-waiting", "Completed": "badge-done"
                                }.get(curr_status, "badge-open")
                                st.markdown(
                                    f"<span class='status-badge {badge}'>{curr_status}</span>",
                                    unsafe_allow_html=True
                                )
                        with col_dt:
                            st.caption(f"Due: {task.get('due', '')}")

                if is_admin:
                    st.markdown("<br><hr style='border-color: #DADDD6;'><br>", unsafe_allow_html=True)
                    st.markdown("<h3>Create New Request</h3>", unsafe_allow_html=True)
                    with st.form("new_task_form", clear_on_submit=True):
                        new_task_text = st.text_input("What do you need from the client?")
                        fc1, fc2 = st.columns(2)
                        with fc1:
                            task_status_new = st.selectbox(
                                "Initial Status", ["Pending", "In Progress", "Awaiting Client"]
                            )
                        with fc2:
                            due_date = st.date_input("Due Date", datetime.now())
                        submit_button = st.form_submit_button("Send Request")
                        if submit_button and new_task_text:
                            task_sheet.append_row(
                                [active_client, new_task_text, task_status_new, str(due_date)]
                            )
                            st.success("Request saved to Google Sheets.")
                            st.rerun()

            # --- TAB 2: INVOICES & PAYMENTS ---
            with tab_invoices:
                st.markdown("<h3>Accounts Receivable & Invoices</h3>", unsafe_allow_html=True)
                client_invoices = [
                    dict(row, sheet_row=idx + 2)
                    for idx, row in enumerate(all_invoices)
                    if row["client"] == active_client
                ]
                unpaid_invoices = [
                    i for i in client_invoices
                    if str(i.get("status", "")).strip().lower() != "paid"
                ]
                paid_invoices = [
                    i for i in client_invoices
                    if str(i.get("status", "")).strip().lower() == "paid"
                ]

                total_client_ar = 0
                for inv in unpaid_invoices:
                    try:
                        total_client_ar += float(
                            str(inv.get("amount", "")).replace("$", "").replace(",", "").strip()
                        )
                    except Exception:
                        pass

                if unpaid_invoices:
                    st.markdown(
                        f"<p style='font-family:Lato,sans-serif; font-size:1.05em; "
                        f"color:#333333; margin-bottom:0;'>"
                        f"<strong>Total Outstanding: ${total_client_ar:,.2f}</strong></p>",
                        unsafe_allow_html=True
                    )

                st.markdown("#### Outstanding Balance")
                if not unpaid_invoices:
                    st.success("There are no unpaid invoices for this account.")
                else:
                    for inv in unpaid_invoices:
                        st.markdown(
                            f"""
                            <div class="portal-card">
                            <table style="width:100%; border:none; background:none; margin:0; padding:0;">
                            <tr style="background:none; border:none;">
                            <td style="border:none; width:45%; padding:0;">
                            <span style="font-family:'Playfair Display',Georgia,serif; font-size:1.2em;
                            font-weight:600; color:#333333;">Invoice #{inv['invoice_num']}</span><br>
                            <span style="font-size:0.83rem; color:#A8B5A3; font-family:'Lato',sans-serif;
                            letter-spacing:0.02em;">Due: {inv['due_date']}</span>
                            </td>
                            <td style="border:none; width:25%; vertical-align:middle; padding:0;">
                            <span style="font-size:1.5em; font-weight:600; color:#333333;
                            font-family:'Playfair Display',Georgia,serif;">{inv['amount']}</span>
                            </td>
                            <td style="border:none; width:30%; text-align:right;
                            vertical-align:middle; padding:0;">
                            <a href="{inv['pay_link']}" target="_blank" class="invoice-btn">Pay Invoice</a>
                            </td>
                            </tr>
                            </table>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        if is_admin:
                            if st.button(
                                f"Mark as Paid — Invoice #{inv['invoice_num']}",
                                key=f"mark_paid_{inv['sheet_row']}"
                            ):
                                invoice_sheet.update_cell(inv['sheet_row'], 6, "paid")
                                st.success(f"Invoice #{inv['invoice_num']} marked as paid.")
                                st.rerun()

                if paid_invoices:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### Paid History")
                    for inv in paid_invoices:
                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.markdown(f"~~Invoice #{inv['invoice_num']}~~")
                        with c2:
                            st.markdown(f"~~{inv['amount']}~~")
                        with c3:
                            st.caption("Processed")

                if is_admin:
                    st.markdown("<br><hr style='border-color: #DADDD6;'><br>", unsafe_allow_html=True)
                    st.markdown("<h3>Log New Invoice</h3>", unsafe_allow_html=True)
                    with st.form("new_invoice_form", clear_on_submit=True):
                        inv_num = st.text_input("Invoice Number")
                        inv_amt = st.text_input("Invoice Amount")
                        inv_due = st.date_input("Invoice Due Date", datetime.now())
                        inv_url = st.text_input("Payment Link URL")
                        submit_inv = st.form_submit_button("Post Invoice")
                        if submit_inv and inv_num and inv_amt:
                            invoice_sheet.append_row(
                                [active_client, inv_num, inv_amt, str(inv_due), inv_url, "Unpaid"]
                            )
                            st.success("Invoice logged successfully.")
                            st.rerun()

            # --- TAB 3: DOCUMENT CENTER ---
            with tab_documents:
                st.markdown("<h3>Secure File Drop</h3>", unsafe_allow_html=True)
                st.write("Upload statements, receipts, or invoices requested by your accountant.")
                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown(
                    """
                    <div class="custom-upload-container">
                    <div class="custom-upload-title">Upload Client Documents</div>
                    <div class="custom-upload-subtitle">
                    Supported formats: PDF, PNG, JPG, CSV &nbsp;&middot;&nbsp; Max: 200MB
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if "show_uploader" not in st.session_state:
                    st.session_state.show_uploader = False

                if st.button("Select File", key="open_uploader_btn"):
                    st.session_state.show_uploader = True

                if st.session_state.show_uploader:
                    uploaded_file = st.file_uploader(
                        label="File upload",
                        label_visibility="collapsed",
                        type=["pdf", "png", "jpg", "csv"]
                    )
                    if uploaded_file is not None:
                        with st.spinner("Uploading to your secure Google Drive folder..."):
                            file_id = upload_file_to_drive(active_client, uploaded_file)
                        if file_id:
                            st.success("File saved to your secure Google Drive folder.")
                        else:
                            st.error("Upload failed. Please try again or contact support.")

    else:
        st.info("Connecting to portal services...")
