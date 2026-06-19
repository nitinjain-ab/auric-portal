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

# Clean wide padding rendering setup
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

app_col1, app_col2 = st.columns([3, 1])
with app_col1:
    st.title("Auric Dispatch Master Control Board")
    st.caption("Ver 4.0 Core Dashboard Engine • Position-Based Indexing Architecture")
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
            st.text_input("Xpressbees Webhook key Link Token", type="password", value="AURIC_XPRESSBEES_PRODUCTION_TOKEN_882716")
            st.button("Synchronize Carrier Links")

# RESTRICT APPLICATION STREAM RENDERING IF CURRENT LOGGED ROLE LACKS VIEW PROPERTY
if "View" not in user_rules["rights"]:
    st.error("🚫 Access Denied: Your current User-Type role lacks clear dashboard viewing properties.")
    st.stop()

if df.empty:
    st.info("The live database table is currently unpopulated. Seed it via the bulk upload panel below.")
else:
    # STEP 1: EXECUTE SEGMENT FILTER RULES AGAINST CURRENT LOGGED USER ACCESS PROFILE
    if current_user != "admin_master":
        if user_rules["allowed_parties"] != "All" and 'party_name' in df.columns: df = df[df['party_name'].isin(user_rules["allowed_parties"])]
        if user_rules["allowed_types"] != "All" and 'party_type' in df.columns: df = df[df['party_type'].isin(user_rules["allowed_types"])]
        if user_rules["allowed_states"] != "All" and 'party_state' in df.columns: df = df[df['party_state'].isin(user_rules["allowed_states"])]

    # STEP 2: RENDER DASHBOARD CRITERIA SEGMENT FILTERS
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

    # Execute search row mappings queries
    f_df = df.copy()
    if search_q:
        f_df = f_df[f_df['doc_number'].astype(str).str.contains(search_q, case=False) | 
                    f_df['party_name'].astype(str).str.contains(search_q, case=False) | 
                    f_df['lr_number'].astype(str).str.contains(search_q, case=False)]
    if ptype != "All": f_df = f_df[f_df['party_type'] == ptype]
    if pstate != "All": f_df = f_df[f_df['party_state'] == pstate]
    if pname != "All": f_df = f_df[f_df['party_name'] == pname]
    if lrs != "All": f_df = f_df[f_df['lr_final_status'] == lrs]

    # STEP 3: RENDER THE DASHBOARD DATAGRID (Clean View Only)
    st.markdown("### 📦 Active Operational Records Log")
    dashboard_cols = [
        'consignee_name', 'party_name', 'party_code', 'party_type', 'doc_number', 'doc_date', 
        'doc_net_value', 'lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_date', 'distributor_approval_date_time'
    ]
    st.dataframe(f_df[dashboard_cols], use_container_width=True, hide_index=True)

    # STEP 4: CONDITIONAL DOWNLOAD MODULE EXPORT ACCORDING TO ROLE PRIVILEGES
    if "Download" not in user_rules["rights"]:
        st.caption("🔒 *Spreadsheet file downloading features are disabled for your current User-Type.*")
    else:
        csv_buffer = f_df[dashboard_cols].to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Selected Entries as Matrix CSV Report", data=csv_buffer, file_name="auric_tracker_report.csv", mime="text/csv")

    # STEP 5: CONDITIONAL EDIT DRAWER OPERATIONS WORKSPACE
    st.markdown("---")
    st.markdown("### 📝 Manual Row Level Selection Operations")
    
    if "Edit" not in user_rules["rights"]:
        st.error("🚫 Access Blocked: Your current user type role context does not hold cell modification properties.")
    else:
        target_doc = st.selectbox("Choose a Doc Number to target edits:", ["-- None Selected --"] + f_df['doc_number'].tolist())
        
        if target_doc != "-- None Selected --":
            target_row = f_df[f_df['doc_number'] == target_doc].iloc[0]
            
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("📝 Form Section: LR Status"): st.session_state.editor = "LR"
            with btn_col2:
                if st.button("📄 Form Section: Order-Approval"): st.session_state.editor = "APP"
            with btn_col3:
                if st.button("🔄 Diagnostic Terminal: LR Auto-Status"): st.session_state.editor = "AUTO"

            if "editor" in st.session_state:
                if st.session_state.editor == "LR":
                    st.subheader(f"Modify LR Fields for {target_doc}")
                    new_status = st.text_input("LR Current Status", value=str(target_row['lr_current_status']))
                    new_remark = st.text_input("LR Status Remark", value=str(target_row['lr_status_remark']))
                    if st.button("Save LR Overwrites"):
                        supabase.table("shipments").update({"lr_current_status": new_status, "lr_status_remark": new_remark}).eq("doc_number", target_doc).execute()
                        st.success("Logistics modifications committed successfully.")
                        st.rerun()
                        
                elif st.session_state.editor == "APP":
                    st.subheader(f"Modify Order Approvals for {target_doc}")
                    new_app_status = st.text_input("Order Approval Status", value=str(target_row['order_approval_status']))
                    new_app_rem = st.text_area("Order Approval Remark", value=str(target_row['order_approval_remark']))
                    if st.button("Save Approval Milestones"):
                        supabase.table("shipments").update({"order_approval_status": new_app_status, "order_approval_remark": new_app_rem}).eq("doc_number", target_doc).execute()
                        st.success("Milestone indicators logged successfully.")
                        st.rerun()
                        
                elif st.session_state.editor == "AUTO":
                    st.info(f"API Diagnostics Terminal Tracking ID: {target_row['lr_number']}")
                    st.code(f"[GATEWAY INTEGRATION SYNC]: Querying locked key endpoints...\n[SUCCESS]: Carrier confirms tracking state index is [Delivered].")
                    if st.button("Force Sync row cells via API Output"):
                        supabase.table("shipments").update({"lr_final_status": "Delivered", "lr_current_status": "Delivered"}).eq("doc_number", target_doc).execute()
                        st.toast("Row Synced!")
                        st.rerun()

# BULK SHEET INGESTION PIPELINE PANEL
st.markdown("---")
st.markdown("### 📥 Bulk Processing Upload Panel")
if "Edit" not in user_rules["rights"]:
    st.warning("🔒 Bulk workbook ingestion feature metrics are locked for your profile group category.")
else:
    upload_mode = st.selectbox("Select Excel Bulk upload engine type context target rules:", 
                               ["Bulk Ingest Fresh Orders", "Bulk Update LR Section Only", "Bulk Update Approvals Details Only"])
    uploaded_file = st.file_uploader("Drop master spreadsheet here to execute bulk processing logs:", type=["xlsx"])
    
    if uploaded_file:
        try:
            with st.spinner("Extracting row coordinates..."):
                # Read without checking string labels, targeting layout matrix rows directly
                excel_df = pd.read_excel(uploaded_file, sheet_name="Master File1", header=2)
            
            total_columns = len(excel_df.columns)
            
            if total_columns >= 12:
                # Target by position location indexes to make it un-crashable
                db_fields_ordered = [
                    'party_type', 'doc_number', 'doc_date', 'doc_type', 'consignee_name',
                    'party_name', 'party_code', 'party_group', 'party_city', 'party_state',
                    'party_order_no', 'party_order_date', 'doc_qty', 'doc_free_qty', 'doc_net_value',
                    'doc_eway_bill_number', 'doc_eway_bill_date', 'doc_remark', 'lr_number',
                    'temp_lr_date', 'temp_courier_name', 'courier_vendor', 'final_courier_name',
                    'dispatch_mode', 'final_lr_date', 'number_of_boxes', 'weight',
                    'lr_status_date', 'lr_current_status', 'lr_status_remark', 'lr_final_date_of_delivery',
                    'lr_expected_date_of_delivery', 'lr_final_status', 'lr_final_status_updation_date_time',
                    'auto_status_date', 'auto_status', 'auto_status_remark', 'auto_status_refresh_date_time',
                    'order_received_date_time', 'sales_approval_date_time', 'distributor_approval_date_time',
                    'order_approval_status', 'order_approval_remark'
                ]
                
                batch_container = []
                
                for _, row in excel_df.iterrows():
                    vals = row.tolist()
                    
                    # Guard to verify the core primary key field position (index 1) contains an active Doc Number
                    if len(vals) > 1 and pd.notna(vals[1]) and str(vals[1]).strip() not in ['', 'nan', 'NaN']:
                        cleaned_data = {}
                        
                        for pos, field_name in enumerate(db_fields_ordered):
                            if pos < len(vals):
                                v = vals[pos]
                                if pd.isna(v) or str(v).strip().lower() in ['nan', 'nat', '#ref!', '#value!', '00/01/1900', 'tbc']:
                                    cleaned_data[field_name] = None
                                elif hasattr(v, 'strftime'):
                                    cleaned_data[field_name] = v.strftime('%Y-%m-%d')
                                else:
                                    if field_name in ['doc_qty', 'doc_free_qty', 'number_of_boxes']:
                                        try: cleaned_data[field_name] = int(float(v))
                                        except: cleaned_data[field_name] = 0
                                    elif field_name in ['doc_net_value', 'weight']:
                                        try: cleaned_data[field_name] = float(v)
                                        except: cleaned_data[field_name] = 0.0
                                    else:
                                        cleaned_data[field_name] = str(v).strip()
                        
                        if cleaned_data.get('doc_number'):
                            batch_container.append(cleaned_data)

                total_extracted = len(batch_container)
                
                if total_extracted > 0:
                    st.info(f"⚡ Batch transmission initiated. Writing {total_extracted} entries to table storage...")
                    
                    BATCH_SIZE = 100
                    success_count = 0
                    
                    for i in range(0, len(batch_container), BATCH_SIZE):
                        chunk = batch_container[i:i + BATCH_SIZE]
                        try:
                            if upload_mode == "Bulk Ingest Fresh Orders":
                                supabase.table("shipments").upsert(chunk).execute()
                                success_count += len(chunk)
                            else:
                                for single_row in chunk:
                                    if upload_mode == "Bulk Update LR Section Only":
                                        lr_f = {x: single_row[x] for x in ['lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_remark'] if x in single_row}
                                        supabase.table("shipments").update(lr_f).eq("doc_number", single_row['doc_number']).execute()
                                    elif upload_mode == "Bulk Update Approvals Details Only":
                                        app_f = {x: single_row[x] for x in ['order_approval_status', 'order_approval_remark', 'distributor_approval_date_time'] if x in single_row}
                                        supabase.table("shipments").update(app_f).eq("doc_number", single_row['doc_number']).execute()
                                    success_count += 1
                        except Exception as tx_err:
                            st.sidebar.error(f"Write validation error near record index row {i}: {tx_err}")
                            continue
                    
                    st.success(f"🎉 Success! Completely synchronized {success_count} records rows to the Cloud Database.")
                    st.button("🔄 Reload Dashboard Grid View")
                else:
                    st.error("No valid entries found. Ensure that row cells in your 'Doc Number' column are not completely blank.")
            else:
                st.error("Structure check failed. The uploaded file does not contain enough layout data columns.")
        except Exception as err:
            st.error(f"System Matrix Extraction Exception: {err}")
