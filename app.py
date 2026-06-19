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

# Build direct API request endpoints natively
BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Data rows natively using clean direct API requests loops
def load_db_data():
    try:
        url = f"{BASE_API_ROUTE}?select=*"
        response = requests.get(url, headers=HTTP_HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Initialize localized state permissions data map variables if empty
if "user_roles_db" not in st.session_state:
    st.session_state["user_roles_db"] = {
        "admin_master": {"allowed_parties": "All", "allowed_types": "All", "allowed_states": "All", "rights": ["View", "Edit", "Download"]},
        "regional_kerala": {"allowed_parties": "All", "allowed_types": ["Distributor"], "allowed_states": ["KERALA"], "rights": ["View", "Edit"]}
    }
if "current_logged_user" not in st.session_state:
    st.session_state["current_logged_user"] = "admin_master"

df = load_db_data()

st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

app_col1, app_col2 = st.columns([3, 1])
with app_col1:
    st.title("Auric Dispatch Master Control Board")
    st.caption("Ver 4.0 Core Dashboard Engine • Direct Row Injection Matrix")
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

# --- DYNAMIC GRID RENDER LOGIC BLOCK ---
if df.empty:
    st.warning("⚠️ Cloud Table Connection Active: No records found in the database. Please drop your Excel sheet below to populate the grid.")
else:
    # Row filters matrix execution guard checks
    if current_user != "admin_master":
        if user_rules["allowed_parties"] != "All" and 'party_name' in df.columns: df = df[df['party_name'].isin(user_rules["allowed_parties"])]
        if user_rules["allowed_types"] != "All" and 'party_type' in df.columns: df = df[df['party_type'].isin(user_rules["allowed_types"])]
        if user_rules["allowed_states"] != "All" and 'party_state' in df.columns: df = df[df['party_state'].isin(user_rules["allowed_states"])]

    st.markdown("### 🎛️ Active Dashboard Filters & Slicers")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_q = st.text_input("🔍 Search box query filter:", "")
    with col2:
        ptype = st.selectbox("Party-Type", ["All"] + df['party_type'].dropna().unique().tolist() if 'party_type' in df.columns else ["All"])
    with col3:
        pstate = st.selectbox("State Zone", ["All"] + df['party_state'].dropna().unique().tolist() if 'party_state' in df.columns else ["All"])
    with col4:
        pname = st.selectbox("Party Name", ["All"] + df['party_name'].dropna().unique().tolist() if 'party_name' in df.columns else ["All"])

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
    ideal_cols = ['consignee_name', 'party_name', 'party_code', 'party_type', 'doc_number', 'doc_date', 'doc_net_value', 'lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_date']
    render_cols = [c for c in ideal_cols if c in f_df.columns]
    if not render_cols:
        render_cols = f_df.columns.tolist()
        
    st.dataframe(f_df[render_cols], use_container_width=True, hide_index=True)

    if "Download" in user_rules["rights"]:
        csv_buffer = f_df[render_cols].to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Selected Entries as Matrix CSV Report", data=csv_buffer, file_name="auric_tracker_report.csv", mime="text/csv")

# DIRECT FLAT-LINE BULK PROCESSING PANEL
st.markdown("---")
st.markdown("### 📥 Bulk Processing Upload Panel")
if "Edit" in user_rules["rights"]:
    upload_mode = st.selectbox("Select Excel Bulk upload engine type context target rules:", ["Bulk Ingest Fresh Orders", "Bulk Update LR Section Only"])
    uploaded_file = st.file_uploader("Drop master spreadsheet here to execute bulk processing logs:", type=["xlsx"])
    
    if uploaded_file:
        try:
            with st.spinner("Decoding sheet data matrices..."):
                excel_df = pd.read_excel(uploaded_file, header=2)
            
            excel_df.columns = [str(c).strip().lower().replace('.', '').replace(' ', '_') for c in excel_df.columns]
            
            # Direct database matrix translation table references
            col_translations = {
                'party_type': ['party_type', 'partytype'],
                'doc_number': ['doc_number', 'doc_no', 'document_number', 'document_no'],
                'doc_date': ['doc_date', 'date', 'document_date'],
                'consignee_name': ['consignee_name', 'consignee'],
                'party_name': ['party_name', 'party'],
                'party_code': ['party_code', 'partycode'],
                'party_state': ['party_state', 'state', 'partystate'],
                'doc_net_value': ['doc_net_value', 'bill_net_value', 'net_value'],
                'lr_number': ['lr_number', 'lr_no', 'lrnumber'],
                'final_lr_date': ['final_lr_date', 'lrdate(pickupdt)', 'lr_date'],
                'lr_current_status': ['lr_current_status', 'current_status'],
                'lr_status_date': ['lr_status_date', 'status_date']
            }
            
            final_mapped_df = pd.DataFrame()
            for db_field, potential_matches in col_translations.items():
                matched_col = next((c for c in excel_df.columns if c in potential_matches or any(pm in c for pm in potential_matches)), None)
                if matched_col:
                    final_mapped_df[db_field] = excel_df[matched_col]
            
            if 'doc_number' not in final_mapped_df.columns and len(excel_df.columns) > 1:
                final_mapped_df['doc_number'] = excel_df.iloc[:, 1]
            if 'party_name' not in final_mapped_df.columns and len(excel_df.columns) > 5:
                final_mapped_df['party_name'] = excel_df.iloc[:, 5]
                
            final_mapped_df = final_mapped_df.dropna(subset=['doc_number'])
            total_extracted = len(final_mapped_df)
            
            if total_extracted > 0:
                success_count = 0
                st.info(f"Writing {total_extracted} rows directly into table grids using transaction arrays...")
                
                # Convert rows to standard sanitized JSON arrays natively
                payload_list = []
                for _, row in final_mapped_df.iterrows():
                    rd = row.to_dict()
                    cleaned_row = {}
                    for k, v in rd.items():
                        if pd.isna(v) or str(v).strip().lower() in ['nan', 'nat', '#ref!', '#value!']:
                            cleaned_row[k] = None
                        elif hasattr(v, 'strftime'):
                            cleaned_row[k] = v.strftime('%Y-%m-%d')
                        else:
                            if k == 'doc_net_value':
                                try: cleaned_row[k] = float(v)
                                except: cleaned_row[k] = 0.0
                            else:
                                cleaned_row[k] = str(v).strip()
                    payload_list.append(cleaned_row)
                
                # --- CHUNK INSERTION DRIVER (Forces commit states via standard PostgREST calls) ---
                BATCH_SIZE = 100
                for i in range(0, len(payload_list), BATCH_SIZE):
                    chunk = payload_list[i:i + BATCH_SIZE]
                    if upload_mode == "Bulk Ingest Fresh Orders":
                        # Explicit header parameters to force data visibility in display calls
                        headers_post = {
                            **HTTP_HEADERS,
                            "Prefer": "return=minimal, resolution=merge-duplicates"
                        }
                        res = requests.post(BASE_API_ROUTE, headers=headers_post, data=json.dumps(chunk))
                        if res.status_code in [200, 201]:
                            success_count += len(chunk)
                    else:
                        for r in chunk:
                            if r.get('doc_number'):
                                res = requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json=r)
                                if res.status_code == 200: success_count += 1
                
                st.success(f"🎉 Success! Completely synchronized {success_count} rows across tracker records.")
                st.rerun()
            else:
                st.error("No row matching indices extracted. Ensure your tracking columns contain active numeric elements.")
        except Exception as global_err:
            st.error(f"Ingestion Error: {global_err}")
