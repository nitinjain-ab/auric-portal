import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="Auric Control Hub v4.0", layout="wide")

# Natively initialize cloud database connection pipeline
@st.cache_resource
def init_supabase():
    url = st.secrets["connections"]["supabase"]["supabase_url"]
    key = st.secrets["connections"]["supabase"]["supabase_key"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Database handshake failed: {e}. Please check your variables inside Streamlit Cloud Secrets box configuration.")
    st.stop()

# Load Data rows from active Supabase table
def load_db_data():
    try:
        response = supabase.table("shipments").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

# Initialize localized state permissions data map variables if empty
if "user_roles_db" not in st.session_state:
    st.session_state["user_roles_db"] = {
        "admin_master": {"allowed_parties": "All", "allowed_types": "All", "allowed_states": "All", "rights": ["View", "Edit", "Download"]},
        "regional_kerala": {
            "allowed_parties": "All",
            "allowed_types": ["Distributor", "GT-Direct"],
            "allowed_states": ["KERALA"],
            "rights": ["View", "Edit"]
        }
    }
if "current_logged_user" not in st.session_state:
    st.session_state["current_logged_user"] = "admin_master"

df = load_db_data()

st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

app_col1, app_col2 = st.columns([3, 1])
with app_col1:
    st.title("Auric Dispatch Master Control Board")
    st.caption("Ver 4.0 Core Dashboard Engine • Multi-Header Intelligent Parsing Array")
with app_col2:
    user_options = list(st.session_state["user_roles_db"].keys())
    st.session_state["current_logged_user"] = st.selectbox(
        "👤 Active Login Session Tier:", user_options, 
        index=user_options.index(st.session_state["current_logged_user"])
    )

current_user = st.session_state["current_logged_user"]
user_rules = st.session_state["user_roles_db"][current_user]

# SIDEBAR CONFIGURATION TABS (Admin Only Module Access)
with st.sidebar:
    st.header("⚙️ Portal System Controls")
    if current_user != "admin_master":
        st.warning("🔒 Administrative panels are locked for restricted user profiles.")
    else:
        setting_tab = st.radio("System Control Panel", ["Dynamic User Creation", "Link Multiple APIs"])
        
        if setting_tab == "Dynamic User Creation":
            st.markdown("#### 👤 Setup Customized Access Role")
            new_role_name = st.text_input("Role Custom Name", placeholder="e.g., west_warehouse_restricted")
            map_parties = st.multiselect("Assign Selected Parties (Empty for All)", options=["All"] + (df['party_name'].dropna().unique().tolist() if not df.empty and 'party_name' in df.columns else []))
            map_types = st.multiselect("Restrict to Selected Party-Types", options=df['party_type'].dropna().unique().tolist() if not df.empty and 'party_type' in df.columns else ["Distributor", "Vendor", "Warehouse"])
            map_states = st.multiselect("Restrict to Selected States", options=df['party_state'].dropna().unique().tolist() if not df.empty and 'party_state' in df.columns else [])
            
            st.markdown("**Functional Scope Properties:**")
            r_view = st.checkbox("Enable Records Viewing", value=True)
            r_edit = st.checkbox("Enable Cells Modification", value=False)
            r_down = st.checkbox("Enable Spreadsheet Exporting", value=False)
            
            if st.button("Commit New User Role Settings"):
                if new_role_name:
                    rights_list = []
                    if r_view: rights_list.append("View")
                    if r_edit: rights_list.append("Edit")
                    if r_down: rights_list.append("Download")
                    st.session_state["user_roles_db"][new_role_name] = {
                        "allowed_parties": "All" if "All" in map_parties or not map_parties else map_parties,
                        "allowed_types": map_types if map_types else "All",
                        "allowed_states": map_states if map_states else "All",
                        "rights": rights_list
                    }
                    st.success(f"Custom user type role '{new_role_name}' generated successfully.")
                    st.rerun()
                    
        elif setting_tab == "Link Multiple APIs":
            st.markdown("#### 🔑 Global Carrier Gateway Vault")
            st.text_input("Bluedart Webhook key Link Token", type="password", value="AURIC_BLUEDART_PRODUCTION_TOKEN_991823")
            st.text_input("DTDC Webhook key Link Token", type="password", value="AURIC_DTDC_PRODUCTION_TOKEN_004123")
            st.button("Synchronize Carrier Links")

if "View" not in user_rules["rights"]:
    st.error("🚫 Access Denied: Your current User-Type role lacks clear dashboard viewing properties.")
    st.stop()

if df.empty:
    st.info("The live database table is currently unpopulated. Seed it via the bulk upload panel below.")
else:
    st.markdown("### 🎛️ Active Dashboard Filters & Slicers")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        search_q = st.text_input("🔍 Search box query (Doc Number / Party Name / LR Number)", "")
    with col2:
        ptype = st.selectbox("Party-Type", ["All"] + df['party_type'].dropna().unique().tolist() if 'party_type' in df.columns else ["All"])
    with col3:
        pstate = st.selectbox("State Zone", ["All"] + df['party_state'].dropna().unique().tolist() if 'party_state' in df.columns else ["All"])
    with col4:
        pname = st.selectbox("Party Name Selector", ["All"] + df['party_name'].dropna().unique().tolist() if 'party_name' in df.columns else ["All"])
    with col5:
        lrs = st.selectbox("LR-Final Status", ["All"] + df['lr_final_status'].dropna().unique().tolist() if 'lr_final_status' in df.columns else ["All"])

    f_df = df.copy()
    if search_q:
        f_df = f_df[f_df['doc_number'].astype(str).str.contains(search_q, case=False) | 
                    f_df['party_name'].astype(str).str.contains(search_q, case=False) | 
                    f_df['lr_number'].astype(str).str.contains(search_q, case=False)]
    if ptype != "All": f_df = f_df[f_df['party_type'] == ptype]
    if pstate != "All": f_df = f_df[f_df['party_state'] == pstate]
    if pname != "All": f_df = f_df[f_df['party_name'] == pname]
    if lrs != "All": f_df = f_df[f_df['lr_final_status'] == lrs]

    st.markdown("### 📦 Active Operational Records Log")
    dashboard_cols = ['consignee_name', 'party_name', 'party_code', 'party_type', 'doc_number', 'doc_date', 'doc_net_value', 'lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_date', 'distributor_approval_date_time']
    st.dataframe(f_df[dashboard_cols], use_container_width=True, hide_index=True)

    if "Download" in user_rules["rights"]:
        csv_buffer = f_df[dashboard_cols].to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Selected Entries as Matrix CSV Report", data=csv_buffer, file_name="auric_tracker_report.csv", mime="text/csv")

# INTELLIGENT MULTI-HEADER INGESTION PIPELINE
st.markdown("---")
st.markdown("### 📥 Bulk Processing Upload Panel")
if "Edit" in user_rules["rights"]:
    upload_mode = st.selectbox("Select Excel Bulk upload engine type context target rules:", ["Bulk Ingest Fresh Orders", "Bulk Update LR Section Only", "Bulk Update Approvals Details Only"])
    uploaded_file = st.file_uploader("Drop master spreadsheet here to execute bulk processing logs:", type=["xlsx"])
    
    if uploaded_file:
        try:
            excel_file_object = pd.ExcelFile(uploaded_file)
            target_sheet = "Master File1" if "Master File1" in excel_file_object.sheet_names else excel_file_object.sheet_names[0]
            
            # Smart Scan: Test headers rows dynamically across indexes 0, 1, 2, 3
            parsed_successfully = False
            excel_df = pd.DataFrame()
            
            for test_header in [2, 1, 0, 3]:
                test_df = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=test_header)
                col_sample = " ".join([str(x).lower() for x in test_df.columns])
                if "doc" in col_sample or "party" in col_sample or "number" in col_sample or "consignee" in col_sample:
                    excel_df = test_df
                    parsed_successfully = True
                    break
            
            if parsed_successfully and not excel_df.empty:
                excel_df.columns = [str(c).strip().lower().replace('.', '').replace(' ', '_') for c in excel_df.columns]
                
                # Dynamic matching framework translations
                col_translations = {
                    'party_type': ['party_type', 'partytype'],
                    'doc_number': ['doc_number', 'doc_no', 'document_number', 'doc_number', 'document_no'],
                    'doc_date': ['doc_date', 'date', 'document_date'],
                    'consignee_name': ['consignee_name', 'consignee'],
                    'party_name': ['party_name', 'party'],
                    'party_code': ['party_code', 'partycode'],
                    'party_state': ['party_state', 'state', 'partystate'],
                    'doc_net_value': ['doc_net_value', 'bill_net_value', 'net_value'],
                    'lr_number': ['lr_number', 'lr_no', 'lrnumber'],
                    'final_lr_date': ['final_lr_date', 'lrdate(pickupdt)', 'lr_date']
                }
                
                final_mapped_df = pd.DataFrame()
                for db_field, potential_matches in col_translations.items():
                    matched_col = next((c for c in excel_df.columns if c in potential_matches or any(pm in c for pm in potential_matches)), None)
                    if matched_col:
                        final_mapped_df[db_field] = excel_df[matched_col]
                
                # Check for position index drop-backs if text strings miss matches entirely
                if 'doc_number' not in final_mapped_df.columns and len(excel_df.columns) > 1:
                    final_mapped_df['doc_number'] = excel_df.iloc[:, 1]
                if 'party_name' not in final_mapped_df.columns and len(excel_df.columns) > 5:
                    final_mapped_df['party_name'] = excel_df.iloc[:, 5]
                
                final_mapped_df = final_mapped_df.dropna(subset=['doc_number'])
                total_extracted = len(final_mapped_df)
                
                if total_extracted > 0:
                    st.info(f"⚡ Ingesting {total_extracted} entries from sheet tab '{target_sheet}'...")
                    batch_container = []
                    
                    for _, row in final_mapped_df.iterrows():
                        row_dict = row.to_dict()
                        cleaned_data = {}
                        for k, v in row_dict.items():
                            if pd.isna(v) or str(v).strip().lower() in ['nan', 'nat', '#ref!', '#value!', '00/01/1900']:
                                cleaned_data[k] = None
                            elif hasattr(v, 'strftime'):
                                cleaned_data[k] = v.strftime('%Y-%m-%d')
                            else:
                                if k == 'doc_net_value':
                                    try: cleaned_data[k] = float(v)
                                    except: cleaned_data[k] = 0.0
                                else:
                                    cleaned_data[k] = str(v).strip()
                        batch_container.append(cleaned_data)
                    
                    BATCH_SIZE = 100
                    success_count = 0
                    for i in range(0, len(batch_container), BATCH_SIZE):
                        chunk = batch_container[i:i + BATCH_SIZE]
                        if upload_mode == "Bulk Ingest Fresh Orders":
                            supabase.table("shipments").upsert(chunk).execute()
                        success_count += len(chunk)
                        
                    st.success(f"🎉 Success! Synchronized {success_count} rows across structural tables.")
                    st.button("🔄 Reload App Grid")
                else:
                    st.error("No row matching indices extracted. Ensure your primary tracking cells contain records numbers.")
            else:
                st.error("Failed to detect shipment column structures inside this file. Please ensure your sheet columns contain text headers.")
        except Exception as global_err:
            st.error(f"Ingestion Exception: {global_err}")
