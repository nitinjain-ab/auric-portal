import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Auric Control Hub v4.0", layout="wide")

# Fetch clean credentials directly from your secrets box configuration layers
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["supabase_url"].strip().rstrip('/')
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["supabase_key"].strip()
except Exception:
    st.error("Missing configuration credentials inside the Streamlit Cloud Secrets box.")
    st.stop()

# Direct Endpoint Target Mappings
BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- INITIALIZE HYBRID TRANSACTION MEMORY VAULT ---
if "auric_master_dataframe" not in st.session_state:
    st.session_state["auric_master_dataframe"] = pd.DataFrame()

if "user_roles_db" not in st.session_state:
    st.session_state["user_roles_db"] = {
        "admin_master": {"allowed_parties": "All", "allowed_types": "All", "allowed_states": "All", "rights": ["View", "Edit", "Download"]},
        "regional_kerala": {"allowed_parties": "All", "allowed_types": ["Distributor"], "allowed_states": ["KERALA"], "rights": ["View", "Edit"]}
    }
if "current_logged_user" not in st.session_state:
    st.session_state["current_logged_user"] = "admin_master"

df = st.session_state["auric_master_dataframe"]

# Clean styling markup injection
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

app_col1, app_col2 = st.columns([3, 1])
with app_col1:
    st.title("Auric Dispatch Master Control Board")
    st.caption("Ver 4.0 Core Dashboard Engine • Hybrid High-Speed Memory Architecture")
with app_col2:
    user_options = list(st.session_state["user_roles_db"].keys())
    st.session_state["current_logged_user"] = st.selectbox(
        "👤 Active Login Session:", user_options, 
        index=user_options.index(st.session_state["current_logged_user"])
    )

current_user = st.session_state["current_logged_user"]
user_rules = st.session_state["user_roles_db"][current_user]

if "View" not in user_rules["rights"]:
    st.error("🚫 Access Denied: Your current role lacks dashboard viewing properties.")
    st.stop()

# --- DISPLAY CANVAS OR INGESTION PLACEHOLDER ---
if df.empty:
    st.warning("⚠️ High-Speed Operational Memory Active: Please upload your master Excel file in the processing panel below to instantly populate your dashboard grid canvas.")
else:
    # Row filters matrix execution guard checks
    if current_user != "admin_master":
        if user_rules["allowed_parties"] != "All" and 'party_name' in df.columns: df = df[df['party_name'].isin(user_rules["allowed_parties"])]
        if user_rules["allowed_types"] != "All" and 'party_type' in df.columns: df = df[df['party_type'].isin(user_rules["allowed_types"])]
        if user_rules["allowed_states"] != "All" and 'party_state' in df.columns: df = df[df['party_state'].isin(user_rules["allowed_states"])]

    st.markdown("### 🎛️ Active Dashboard Filters & Slicers")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_q = st.text_input("🔍 Search box filtering query engine:", "")
    with col2:
        ptype = st.selectbox("Party-Type", ["All"] + df['party_type'].dropna().unique().tolist() if 'party_type' in df.columns else ["All"])
    with col3:
        pstate = st.selectbox("State Zone", ["All"] + df['party_state'].dropna().unique().tolist() if 'party_state' in df.columns else ["All"])
    with col4:
        pname = st.selectbox("Party Name Selector", ["All"] + df['party_name'].dropna().unique().tolist() if 'party_name' in df.columns else ["All"])

    f_df = df.copy()
    if search_q:
        match_conditions = []
        for match_field in ['doc_number', 'party_name', 'lr_number', 'consignee_name']:
            if match_field in f_df.columns:
                match_conditions.append(f_df[match_field].astype(str).str.contains(search_q, case=False))
        if match_conditions:
            final_mask = match_conditions[0]
            for mask in match_conditions[1:]:
                final_mask = final_mask | mask
            f_df = f_df[final_mask]

    if ptype != "All" and 'party_type' in f_df.columns: f_df = f_df[f_df['party_type'] == ptype]
    if pstate != "All" and 'party_state' in f_df.columns: f_df = f_df[f_df['party_state'] == pstate]
    if pname != "All" and 'party_name' in f_df.columns: f_df = f_df[f_df['party_name'] == pname]

    st.markdown("### 📦 Active Shipments Log Manifest")
    ideal_cols =
