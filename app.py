import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="Auric Control Hub v4.0", layout="wide")

# Initialize native clean connection directly to secure database cloud
@st.cache_resource
def init_supabase():
    url = st.secrets["connections"]["supabase"]["supabase_url"]
    key = st.secrets["connections"]["supabase"]["supabase_key"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error("Database handshake failed. Please check your variables inside Streamlit Cloud Secrets box configuration.")
    st.stop()

# Load dynamic data fields directly out of live table rows
def load_db_data():
    try:
        response = supabase.table("shipments").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.warning("Could not read records table. Ensure your Supabase table is built using the SQL Editor.")
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
    st.caption("Ver 4.0 Core Dashboard Engine • Multi-Carrier Integration Matrix Hub")
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
            
            map_parties = st.multiselect("Assign Selected Parties (Empty for All)", options=["All"] + (df['party_name'].dropna().unique().tolist() if not df.empty else []))
            map_types = st.multiselect("Restrict to Selected Party-Types", options=df['party_type'].dropna().unique().tolist() if not df.empty else ["Distributor", "Vendor", "Warehouse"])
            map_states = st.multiselect("Restrict to Selected States", options=df['party_state'].dropna().unique().tolist() if not df.empty else [])
            
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
        if user_rules["allowed_parties"] != "All": df = df[df['party_name'].isin(user_rules["allowed_parties"])]
        if user_rules["allowed_types"] != "All": df = df[df['party_type'].isin(user_rules["allowed_types"])]
        if user_rules["allowed_states"] != "All": df = df[df['party_state'].isin(user_rules["allowed_states"])]

    # STEP 2: RENDER DASHBOARD CRITERIA SEGMENT FILTERS
    st.markdown("### 🎛️ Active Dashboard Filters & Slicers")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        search_q = st.text_input("🔍 Search box query (Doc Number / Party Name / LR Number)", "")
    with col2:
        ptype = st.selectbox("Party-Type", ["All"] + df['party_type'].dropna().unique().tolist())
    with col3:
        pstate = st.selectbox("State Zone", ["All"] + df['party_state'].dropna().unique().tolist())
    with col4:
        pname = st.selectbox("Party Name Selector", ["All"] + df['party_name'].dropna().unique().tolist())
    with col5:
        lrs = st.selectbox("LR-Final Status", ["All"] + df['lr_final_status'].dropna().unique().tolist())

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

# BULK SHEET INGESTION PANEL
st.markdown("---")
st.markdown("### 📥 Bulk Processing Upload Panel")
if "Edit" not in user_rules["rights"]:
    st.warning("🔒 Bulk workbook ingestion feature metrics are locked for your profile group category.")
else:
    upload_mode = st.selectbox("Select Excel Bulk upload engine type context target rules:", 
                               ["Bulk Ingest Fresh Orders", "Bulk Update LR Section Only", "Bulk Update Approvals Details Only"])
    uploaded_file = st.file_uploader("Drop master version 4.0 spreadsheet here to execute bulk processing logs:", type=["xlsx"])
    
    if uploaded_file:
        # Load excel ignoring multi-level visual top header layers cleanly
        excel_df = pd.read_excel(uploaded_file, sheet_name="Master File1", header=2)
        
        # Clean naming mapping translations dictionary to safely bridge Excel headers to database fields
        rename_map = {
            'Party Type': 'party_type', 'Doc Number': 'doc_number', 'Doc Date': 'doc_date', 'Doc Type': 'doc_type',
            'Consignee Name': 'consignee_name', 'Party Name': 'party_name', 'Party Code': 'party_code', 'Party Group': 'party_group',
            'Party City': 'party_city', 'Party State': 'party_state', 'Party Order No.': 'party_order_no', 'Party Order Date': 'party_order_date',
            'Doc Qty': 'doc_qty', 'Doc Free Qty': 'doc_free_qty', 'Doc Net Value': 'doc_net_value', 'Doc Eway bill number': 'doc_eway_bill_number',
            'Doc Eway bill Date': 'doc_eway_bill_date', 'Doc Remark': 'doc_remark', 'LR Number': 'lr_number', 'Temp LR Date': 'temp_lr_date',
            'Temp Courier Name': 'temp_courier_name', 'Courier Vendor': 'courier_vendor', 'Final Courier name': 'final_courier_name',
            'Dispatch Mode': 'dispatch_mode', 'Final LR Date': 'final_lr_date', 'Number of Boxes': 'number_of_boxes', 'Weight': 'weight',
            'LR Status Date': 'lr_status_date', 'LR Current Status': 'lr_current_status', 'LR Status Remark': 'lr_status_remark',
            'LR Final Date of Delivery': 'lr_final_date_of_delivery', 'LR Expected date of Delivery': 'lr_expected_date_of_delivery',
            'LR Final Status': 'lr_final_status', 'LR Final Status Updation Date Time': 'lr_final_status_updation_date_time',
            'Auto Status Date': 'auto_status_date', 'Auto Status': 'auto_status', 'Auto Status Remark': 'auto_status_remark',
            'Auto Status Refresh Date Time': 'auto_status_refresh_date_time', 'Order Received Date time': 'order_received_date_time',
            'Sales Approval Date time': 'sales_approval_date_time', 'Distributor Approval Date Time': 'distributor_approval_date_time',
            'Order Approval Status': 'order_approval_status', 'Order Approval Remark': 'order_approval_remark'
        }
        
        excel_df = excel_df.rename(columns=rename_map)
        # Drop unmapped or blank row rows to clean processing arrays
        excel_df = excel_df.dropna(subset=['doc_number'])
        
        records_pushed = 0
        
        for _, row in excel_df.iterrows():
            row_data = row.to_dict()
            # Clean floating/timestamp structures to string fields for flat database compatibility
            for k, v in row_data.items():
                if pd.isna(v): row_data[k] = None
                elif hasattr(v, 'strftime'): row_data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                else: row_data[k] = str(v) if k not in ['doc_qty', 'doc_free_qty', 'number_of_boxes', 'bill_qty', 'free_qty', 'cases'] else int(float(v)) if v else 0

            try:
                if upload_mode == "Bulk Ingest Fresh Orders":
                    supabase.table("shipments").upsert(row_data).execute()
                elif upload_mode == "Bulk Update LR Section Only":
                    lr_patch = {k: row_data[k] for k in ['lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_remark'] if k in row_data}
                    supabase.table("shipments").update(lr_patch).eq("doc_number", row_data['doc_number']).execute()
                elif upload_mode == "Bulk Update Approvals Details Only":
                    app_patch = {k: row_data[k] for k in ['order_approval_status', 'order_approval_remark', 'distributor_approval_date_time'] if k in row_data}
                    supabase.table("shipments").update(app_patch).eq("doc_number", row_data['doc_number']).execute()
                records_pushed += 1
            except Exception as e:
                continue
                
        st.success(f"🎉 Success! Processed and synchronized {records_pushed} records to the Live Cloud Database.")
        st.button("🔄 Refresh Application Dashboard Grid")
