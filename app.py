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

# Build the exact, un-crashable direct HTTP endpoint routing paths natively
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
        # Request data rows sorted by primary document key identities
        url = f"{BASE_API_ROUTE}?select=*&order=doc_number"
        response = requests.get(url, headers=HTTP_HEADERS)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Initialize dynamic permission states roles matrices
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
    st.caption("Ver 4.0 Direct API Integration Gateway Engine • Zero Library Bottlenecks")
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

if df.empty:
    st.info("The live database table is currently unpopulated. Seed it via the bulk upload panel below.")
else:
    # DATA SEGMENT FILTERS MATRIX MANAGEMENT
    if current_user != "admin_master":
        if user_rules["allowed_parties"] != "All" and 'party_name' in df.columns: df = df[df['party_name'].isin(user_rules["allowed_parties"])]
        if user_rules["allowed_types"] != "All" and 'party_type' in df.columns: df = df[df['party_type'].isin(user_rules["allowed_types"])]
        if user_rules["allowed_states"] != "All" and 'party_state' in df.columns: df = df[df['party_state'].isin(user_rules["allowed_states"])]

    st.markdown("### 🎛️ Active Dashboard Filters & Slicers")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_q = st.text_input("🔍 Search (Doc Number / Party Name / LR Number)", "")
    with col2:
        ptype = st.selectbox("Party-Type", ["All"] + df['party_type'].dropna().unique().tolist() if 'party_type' in df.columns else ["All"])
    with col3:
        pstate = st.selectbox("State Zone", ["All"] + df['party_state'].dropna().unique().tolist() if 'party_state' in df.columns else ["All"])
    with col4:
        pname = st.selectbox("Party Name", ["All"] + df['party_name'].dropna().unique().tolist() if 'party_name' in df.columns else ["All"])

    f_df = df.copy()
    if search_q:
        f_df = f_df[f_df['doc_number'].astype(str).str.contains(search_q, case=False) | 
                    f_df['party_name'].astype(str).str.contains(search_q, case=False) | 
                    f_df['lr_number'].astype(str).str.contains(search_q, case=False)]
    if ptype != "All": f_df = f_df[f_df['party_type'] == ptype]
    if pstate != "All": f_df = f_df[f_df['party_state'] == pstate]
    if pname != "All": f_df = f_df[f_df['party_name'] == pname]

    # COMPACT DASHBOARD GRID (Clean viewing format)
    st.markdown("### 📦 Active Shipments Log Manifest")
    dashboard_cols = ['consignee_name', 'party_name', 'party_code', 'party_type', 'doc_number', 'doc_date', 'doc_net_value', 'lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_date', 'distributor_approval_date_time']
    available_cols = [c for c in dashboard_cols if c in f_df.columns]
    st.dataframe(f_df[available_cols], use_container_width=True, hide_index=True)

    if "Download" in user_rules["rights"]:
        csv_buffer = f_df[available_cols].to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Selected Entries as Matrix CSV Report", data=csv_buffer, file_name="auric_tracker_report.csv", mime="text/csv")

    # MANUAL EDIT DRAWER PANEL
    st.markdown("---")
    st.markdown("### 📝 Manual Row Level Selection Operations")
    if "Edit" not in user_rules["rights"]:
        st.error("🚫 Access Blocked: Your role does not hold cell modification properties.")
    else:
        target_doc = st.selectbox("Choose a Doc Number to target edits:", ["-- None Selected --"] + f_df['doc_number'].tolist())
        if target_doc != "-- None Selected --":
            target_row = f_df[f_df['doc_number'] == target_doc].iloc[0]
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📝 Form Section: LR Status"): st.session_state.editor = "LR"
            with btn_col2:
                if st.button("📄 Form Section: Order-Approval"): st.session_state.editor = "APP"

            if "editor" in st.session_state:
                if st.session_state.editor == "LR":
                    st.subheader(f"Modify LR Fields for {target_doc}")
                    new_status = st.text_input("LR Current Status", value=str(target_row.get('lr_current_status', '')))
                    new_remark = st.text_input("LR Status Remark", value=str(target_row.get('lr_status_remark', '')))
                    if st.button("Save LR Overwrites"):
                        patch_url = f"{BASE_API_ROUTE}?doc_number=eq.{target_doc}"
                        requests.patch(patch_url, headers=HTTP_HEADERS, json={"lr_current_status": new_status, "lr_status_remark": new_remark})
                        st.success("Logistics modifications saved successfully.")
                        st.rerun()
                elif st.session_state.editor == "APP":
                    st.subheader(f"Modify Order Approvals for {target_doc}")
                    new_app_status = st.text_input("Order Approval Status", value=str(target_row.get('order_approval_status', '')))
                    new_app_rem = st.text_area("Order Approval Remark", value=str(target_row.get('order_approval_remark', '')))
                    if st.button("Save Approval Milestones"):
                        patch_url = f"{BASE_API_ROUTE}?doc_number=eq.{target_doc}"
                        requests.patch(patch_url, headers=HTTP_HEADERS, json={"order_approval_status": new_app_status, "order_approval_remark": new_app_rem})
                        st.success("Milestone indicators logged successfully.")
                        st.rerun()

# BULK BATCH FILE PROCESSING PANEL
st.markdown("---")
st.markdown("### 📥 Bulk Processing Upload Panel")
if "Edit" in user_rules["rights"]:
    upload_mode = st.selectbox("Select Excel Bulk upload engine type context target rules:", ["Bulk Ingest Fresh Orders", "Bulk Update LR Section Only", "Bulk Update Approvals Details Only"])
    uploaded_file = st.file_uploader("Drop master spreadsheet here to execute bulk processing logs:", type=["xlsx"])
    
    if uploaded_file:
        try:
            with st.spinner("Extracting workbook layers..."):
                excel_df = pd.read_excel(uploaded_file, header=2)
            
            excel_df.columns = [str(c).strip().lower().replace('.', '').replace(' ', '_') for c in excel_df.columns]
            
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
                'final_lr_date': ['final_lr_date', 'lrdate(pickupdt)', 'lr_date', 'temp_lr_date'],
                'lr_current_status': ['lr_current_status', 'current_status', 'lr_status'],
                'lr_status_date': ['lr_status_date', 'status_date'],
                'distributor_approval_date_time': ['distributor_approval_date_time', 'distributor_approval_time']
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
                st.info(f"⚡ Processing {total_extracted} entries rows...")
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
                        headers_upsert = {**HTTP_HEADERS, "Prefer": "resolution=merge-duplicates, return=minimal"}
                        res = requests.post(BASE_API_ROUTE, headers=headers_upsert, data=json.dumps(chunk))
                    else:
                        for r in chunk:
                            if upload_mode == "Bulk Update LR Section Only":
                                lr_f = {x: r[x] for x in ['lr_number', 'final_lr_date', 'lr_current_status', 'lr_status_date'] if x in r}
                                requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json=lr_f)
                            elif upload_mode == "Bulk Update Approvals Details Only":
                                app_f = {x: r[x] for x in ['order_approval_status', 'order_approval_remark', 'distributor_approval_date_time'] if x in r}
                                requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json=app_f)
                    success_count += len(chunk)
                    
                st.success(f"🎉 Success! Completely synchronized {success_count} rows across tracker records.")
                st.button("🔄 Click to Refresh Grid Canvas")
            else:
                st.error("Structure mismatch. Check that your spreadsheet rows contain active data entries.")
        except Exception as global_err:
            st.error(f"Ingestion Error: {global_err}")
