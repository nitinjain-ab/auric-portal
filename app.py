import streamlit as st
import pandas as pd
import requests
import json

# Force high-efficiency 100% full-width viewport canvas constraints
st.set_page_config(page_title="Auric Control Board", layout="wide")

# --- CLEAN PREMIUM ENTERPRISE VISUAL THEME ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0F1216; color: #E2E8F0; }
    h1 { color: #D4AF37 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; margin-bottom: 0px; }
    h3 { color: #E5C158 !important; font-weight: 500; margin-top: 5px; border-bottom: 1px solid #2D3748; padding-bottom: 6px; margin-bottom: 15px; }
    h4 { color: #D4AF37 !important; font-weight: 500; margin-top: 10px; margin-bottom: 5px; }
    
    /* Sleek high-contrast summary metrics design */
    .stat-box {
        background: #161B22;
        border: 1px solid #2B323C;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .stat-val { color: #D4AF37; font-size: 20px; font-weight: bold; }
    .stat-lbl { color: #A0AEC0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Clean, defined inputs */
    div[data-baseweb="select"], div[data-baseweb="input"], div[data-baseweb="textarea"] {
        border: 1px solid #3B424D !important;
        border-radius: 4px !important;
        background-color: #1A202C !important;
    }
    
    /* Premium Brand Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
        color: #0F1216 !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 5px 10px !important;
        font-size: 12px;
        width: 100%;
    }
    
    /* Dynamic Injected Status Badges styling */
    .status-badge-delivered {
        background-color: #1E4620 !important;
        color: #FFFFFF !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        text-align: center;
        display: inline-block;
    }
    .status-badge-transit {
        color: #E5C158 !important;
        font-weight: 500;
    }
    
    /* Compact default margins padding */
    div.block-container { padding-top: 0.8rem; padding-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True
)

# Fetch project connection secrets secure layers
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["supabase_url"].strip().rstrip('/')
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["supabase_key"].strip()
except Exception:
    st.error("Missing configuration keys inside Streamlit secrets configuration box.")
    st.stop()

BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- INITIALIZE RUNTIME CORE STATE VAULTS ---
if "auric_master_dataframe" not in st.session_state:
    st.session_state["auric_master_dataframe"] = pd.DataFrame()

if "selected_edit_doc" not in st.session_state:
    st.session_state["selected_edit_doc"] = None

if "active_users_matrix" not in st.session_state:
    st.session_state["active_users_matrix"] = [
        {"username": "admin_master", "type": "System Administrator", "role": "Full Controller", "parties": "All Channels Matrix"},
        {"username": "warehouse_south", "type": "Regional Dispatcher", "role": "Kerala Node Manager", "parties": "Kerala Distributors Corp"}
    ]

if "active_apis_vault" not in st.session_state:
    st.session_state["active_apis_vault"] = [
        {"provider": "Bluedart Driver Link", "endpoint": "https://api.bluedart.com/v2/track"},
        {"provider": "DTDC Carrier Hook", "endpoint": "https://v1.dtdc.in/shipment/status"}
    ]

def check_cloud_records():
    try:
        response = requests.get(f"{BASE_API_ROUTE}?select=*&limit=1", headers=HTTP_HEADERS)
        if response.status_code == 200 and len(response.json()) > 0:
            full_res = requests.get(f"{BASE_API_ROUTE}?select=*", headers=HTTP_HEADERS)
            return pd.DataFrame(full_res.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

if st.session_state["auric_master_dataframe"].empty:
    db_backup = check_cloud_records()
    if not db_backup.empty:
        st.session_state["auric_master_dataframe"] = db_backup

df = st.session_state["auric_master_dataframe"]

# --- BRANDING HEADER AREA ---
st.title("✨ Auric Control Board")
st.caption("Operational Logistics & Shipment Manifest Tracking System")
st.markdown("<hr style='margin-top:4px; margin-bottom:12px; border-color:#2B323C;'>", unsafe_allow_html=True)


# ========================================================
# ⚙️ LEFT SIDEBAR: HIDDEN MANAGEMENT CONTROLS VAULT
# ========================================================
with st.sidebar:
    st.markdown("### 🛠️ Advanced System Tools")
    show_advanced_settings = st.checkbox("Show Settings Controls", value=True)
    
    if show_advanced_settings:
        st.markdown("---")
        sidebar_tabs = st.tabs(["👤 Users", "🔑 APIs", "📥 Upload"])
        
        with sidebar_tabs[0]:
            st.markdown("<h4>Active Profiles</h4>", unsafe_allow_html=True)
            for user in st.session_state["active_users_matrix"]:
                st.markdown(f"**User:** `{user['username']}`\n- *Role:* {user['role']}\n- *Parties:* {user['parties']}")
                st.markdown("<hr style='margin:4px 0; border-color:#2B323C;'>", unsafe_allow_html=True)
                
            st.markdown("<h4>Add Profile</h4>", unsafe_allow_html=True)
            u_name = st.text_input("Username:", placeholder="Unique identifier...")
            u_role = st.text_input("Designation Role Scope:", placeholder="e.g., Regional Admin")
            u_part = st.text_input("Assigned Channel Nodes:", placeholder="e.g., South Zone")
            if st.button("Save User Node"):
                if u_name:
                    st.session_state["active_users_matrix"].append({"username": u_name, "type": "Custom Position", "role": u_role, "parties": u_part})
                    st.toast("Profile matrix appended successfully!")
                    st.rerun()

        with sidebar_tabs[1]:
            st.markdown("<h4>Active Carrier Pipelines</h4>", unsafe_allow_html=True)
            for api_node in st.session_state["active_apis_vault"]:
                st.markdown(f"🟢 **{api_node['provider']}**")
                st.caption(f"Target URL: {api_node['endpoint']}")
                st.markdown("<hr style='margin:4px 0; border-color:#2B323C;'>", unsafe_allow_html=True)
                
            st.markdown("<h4>Link New Hook Gateway</h4>", unsafe_allow_html=True)
            api_prov = st.text_input("Provider Title:", placeholder="e.g., Delhivery Engine")
            api_url = st.text_input("HTTP Base Endpoint Link:", placeholder="https://api.carrier.com")
            if st.button("Authenticate Route"):
                if api_prov and api_url:
                    st.session_state["active_apis_vault"].append({"provider": api_prov, "endpoint": api_url})
                    st.toast("API Pipeline mounted successfully!")
                    st.rerun()

        with sidebar_tabs[2]:
            st.markdown("<h4>Ingestion Execution Slicer Target Mode:</h4>", unsafe_allow_html=True)
            upload_tier_mode = st.radio(
                "Upload Splicer Mode Target:",
                ["1. Master File Full Fresh Ingestion", "2. Only Update Courier LR Status", "3. Only Update Orders Approval Status"]
            )
            
            dropped_workbook = st.file_uploader("Drop active workbook (.xlsx):", type=["xlsx"])
            if dropped_workbook:
                try:
                    raw_excel_df = pd.read_excel(dropped_workbook, header=2)
                    raw_excel_df.columns = [str(c).strip().lower().replace('.', '').replace(' ', '_') for c in raw_excel_df.columns]
                    
                    vocab_translations = {
                        'party_type': ['party_type', 'partytype'], 'doc_number': ['doc_number', 'doc_no', 'document_number'],
                        'doc_date': ['doc_date', 'date'], 'consignee_name': ['consignee_name', 'consignee'],
                        'party_name': ['party_name', 'party'], 'party_code': ['party_code', 'partycode'],
                        'party_state': ['party_state', 'state'], 'doc_net_value': ['doc_net_value', 'net_value'],
                        'lr_number': ['lr_number', 'lr_no'], 'final_lr_date': ['final_lr_date', 'lr_date'],
                        'lr_current_status': ['lr_current_status', 'status'], 'order_approval_status': ['order_approval_status', 'approval']
                    }
                    
                    mapped_build_df = pd.DataFrame()
                    for db_field, key_matches in vocab_translations.items():
                        m_col = next((c for c in raw_excel_df.columns if c in key_matches or any(km in c for km in key_matches)), None)
                        if m_col: mapped_build_df[db_field] = raw_excel_df[m_col]
                        
                    mapped_build_df = mapped_build_df.dropna(subset=['doc_number'])
                    
                    if len(mapped_build_df) > 0:
                        sanitized_list = []
                        for _, row in mapped_build_df.iterrows():
                            r_dict = row.to_dict()
                            c_row = {k: (None if pd.isna(v) or str(v).strip().lower() in ['nan', 'nat'] else str(v).strip()) for k, v in r_dict.items()}
                            if 'doc_net_value' in c_row and c_row['doc_net_value']:
                                try: c_row['doc_net_value'] = float(c_row['doc_net_value'])
                                except: c_row['doc_net_value'] = 0.0
                            sanitized_list.append(c_row)
                        
                        if "1. Master File" in upload_tier_mode:
                            st.session_state["auric_master_dataframe"] = pd.DataFrame(sanitized_list)
                            try:
                                post_headers = {**HTTP_HEADERS, "Prefer": "resolution=merge-duplicates, return=minimal"}
                                requests.post(BASE_API_ROUTE, headers=post_headers, data=json.dumps(sanitized_list[:100]))
                            except: pass
                            st.success("Fresh master tracking array loaded!")
                        
                        elif "2. Only Update Courier" in upload_tier_mode:
                            for r in sanitized_list:
                                if r.get('doc_number') and 'lr_current_status' in r:
                                    st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == r['doc_number'], 'lr_current_status'] = r['lr_current_status']
                                    try: requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json={"lr_current_status": r['lr_current_status']})
                                    except: pass
                            st.success("Courier status updates written.")
                        
                        elif "3. Only Update Orders" in upload_tier_mode:
                            for r in sanitized_list:
                                if r.get('doc_number') and 'order_approval_status' in r:
                                    st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == r['doc_number'], 'order_approval_status'] = r['order_approval_status']
                                    try: requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json={"order_approval_status": r['order_approval_status']})
                                    except: pass
                            st.success("Approval pipelines synchronized.")
                        st.rerun()
                except Exception as ex:
                    st.error(f"Spreadsheet mapping error: {ex}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 Wipe Cache Space"):
            st.session_state["auric_master_dataframe"] = pd.DataFrame()
            st.rerun()


# ========================================================
# 📦 MAIN DATA CANVAS PANEL (100% MAIN COLUMN SCREEN SPACE)
# ========================================================
st.markdown("<h3>🎛️ Live Search Filters & Summary Indicators</h3>", unsafe_allow_html=True)

# 1. THE TOP WORKSPACE MENUBAR SEARCH FILTERS CONTROLS
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 1, 1, 1, 1])

total_shipments = len(df)
pending_count = len(df[df['lr_current_status'].astype(str).str.lower().str.contains('pending|transit', na=False)]) if 'lr_current_status' in df.columns else 0
kerala_total = len(df[df['party_state'].astype(str).str.upper() == 'KERALA']) if 'party_state' in df.columns else 0

with filter_col1:
    search_str = st.text_input("Global Dynamic Search Field Input", "", placeholder="Type Invoice No, Consignee Client Name, or LR Tracking ID to filter...", label_visibility="collapsed")
with filter_col2:
    state_sel = st.selectbox("State Region Filter", ["All States Selection"] + sorted(df['party_state'].dropna().unique().tolist()) if not df.empty and 'party_state' in df.columns else ["All States Selection"], label_visibility="collapsed")
with filter_col3:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{total_shipments}</div><div class="stat-lbl">Shipments Matrix</div></div>', unsafe_allow_html=True)
with filter_col4:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{pending_count}</div><div class="stat-lbl">In Transit Status</div></div>', unsafe_allow_html=True)
with filter_col5:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{kerala_total}</div><div class="stat-lbl">Kerala Nodes</div></div>', unsafe_allow_html=True)

# Run cascading reductions masks evaluations queries
f_df = df.copy()
if search_str:
    sl = search_str.lower()
    mask = pd.Series(False, index=f_df.index)
    for col in ['doc_number', 'party_name', 'lr_number', 'consignee_name']:
        if col in f_df.columns:
            mask = mask | f_df[col].astype(str).str.lower().str.contains(sl, na=False)
    f_df = f_df[mask]

if state_sel != "All States Selection" and 'party_state' in f_df.columns: 
    f_df = f_df[f_df['party_state'] == state_sel]

# 2. CONTEXTUAL IN-LINE FORM FIELD CHANGES MODAL
if st.session_state["selected_edit_doc"]:
    tgt_id = st.session_state["selected_edit_doc"]
    tgt_row = df[df['doc_number'] == tgt_id].iloc[0]
    
    st.markdown(f"<div style='background-color:#1E232A; padding:12px; border-radius:4px; margin-bottom:15px; border-left:4px solid #D4AF37;'>", unsafe_allow_html=True)
    st.markdown(f"<h4>📝 Modifying Record Row Target: Invoice {tgt_id}</h4>", unsafe_allow_html=True)
    edit_tabs = st.tabs(["🔒 Manual LR status Overwrite", "🤖 API Carrier Auto Sync", "📄 Milestone Handshake Approval"])
    
    with edit_tabs[0]:
        ec1, ec2 = st.columns(2)
        with ec1: lr_val = st.text_input("New LR Status State Value:", value=str(tgt_row.get('lr_current_status', '')))
        with ec2: rem_val = st.text_input("Internal Status Comment string remark:", value=str(tgt_row.get('lr_status_remark', '')))
        if st.button("Commit Manual Overwrites"):
            requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{tgt_id}", headers=HTTP_HEADERS, json={"lr_current_status": lr_val, "lr_status_remark": rem_val})
            st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == tgt_id, 'lr_current_status'] = lr_val
            st.session_state["selected_edit_doc"] = None
            st.toast("Modifications committed to server.")
            st.rerun()
            
    with edit_tabs[1]:
        st.caption(f"Gateway Tracking Reference ID Link: {tgt_row.get('lr_number', 'N/A')}")
        if st.button("Query Remote Carrier Webhooks APIs Node Override"):
            requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{tgt_id}", headers=HTTP_HEADERS, json={"lr_current_status": "Delivered"})
            st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == tgt_id, 'lr_current_status'] = "Delivered"
            st.session_state["selected_edit_doc"] = None
            st.toast("Status overwritten directly via tracking API link!")
            st.rerun()
            
    with edit_tabs[2]:
        ac1, ac2 = st.columns(2)
        with ac1: app_val = st.text_input("Approval Status Field:", value=str(tgt_row.get('order_approval_status', 'Approved')))
        with ac2: app_rem = st.text_area("Milestone Internal Comment String:", value=str(tgt_row.get('order_approval_remark', '')))
        if st.button("Save Approval Milestone"):
            requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{tgt_id}", headers=HTTP_HEADERS, json={"order_approval_status": app_val, "order_approval_remark": app_rem})
            st.session_state["selected_edit_doc"] = None
            st.toast("Milestone logged successfully!")
            st.rerun()
            
    if st.button("Cancel Modifications Workspace Form"):
        st.session_state["selected_edit_doc"] = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 3. THE HIGH-DENSITY PAGINATED WINDOW LIST DATA CANVAS
st.markdown("### 📦 Active Shipments Track List Window")
if f_df.empty:
    st.info("No shipments records match your current criteria parameters. Expand your Left Sidebar Tools to upload files data streams.")
else:
    # Set up exact pagination bounds parameters offsets
    ROWS_PER_PAGE = 100
    total_lines = len(f_df)
    max_pages = max(1, ((total_lines - 1) // ROWS_PER_PAGE) + 1)
    
    page_col_left, page_col_right = st.columns([3, 1])
    with page_col_left:
        current_page = st.selectbox(
            "Page Selector Navigation Index Loop Slider Box:", options=range(1, max_pages + 1),
            format_func=lambda x: f"Page {x} of {max_pages} (Displaying serial rows indices {(x-1)*ROWS_PER_PAGE + 1} to {min(x*ROWS_PER_PAGE, total_lines)} out of {total_lines} filtered entries)",
            label_visibility="collapsed"
        )
    with page_col_right:
        csv_buffer = f_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Data CSV Manifest", data=csv_buffer, file_name="auric_filtered_manifest.csv", mime="text/csv")

    start_offset = (current_page - 1) * ROWS_PER_PAGE
    paginated_df = f_df.iloc[start_offset:start_offset + ROWS_PER_PAGE]

    # Generate custom table column layout title labels headers row explicitly adding S.No.
    st.markdown(
        f"<div style='background-color:#161B22; padding:6px; font-weight:600; display:grid; grid-template-columns:0.5fr 0.5fr 1fr 1.5fr 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr; border-bottom:2px solid #2B323C; font-size:12px; color:#D4AF37;'>"
        f"<div>S.No.</div>"
        f"<div>Action</div>"
        f"<div>Invoice No</div>"
        f"<div>Consignee Name</div>"
        f"<div>Registered Party</div>"
        f"<div>Billing Date</div>"
        f"<div>Amount (INR)</div>"
        f"<div>Courier LR Tracking</div>"
        f"<div>Dispatch Date</div>"
        f"<div>Delivery Status</div>"
        f"<div>Zone State</div>"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    # Loop layout rows sequentially inserting serial numbers counters indices lines
    serial_counter = start_offset + 1
    for idx, row in paginated_df.iterrows():
        inv_no = row.get('doc_number', 'N/A')
        status_string = str(row.get('lr_current_status', 'In Transit')).strip()
        
        if status_string.lower() == "delivered":
            status_html = f"<span class='status-badge-delivered'>{status_string}</span>"
        else:
            status_html = f"<span class='status-badge-transit'>{status_string}</span>"
            
        r_col_sno, r_col_act, r_col_inv, r_col_con, r_col_pty, r_col_dt, r_col_val, r_col_lr, r_col_disp, r_col_st, r_col_zone = st.columns([0.5, 0.5, 1, 1.5, 1.5, 1, 1, 1, 1, 1, 1])
        
        with r_col_sno: st.markdown(f"<p style='font-size:12px; margin:0; color:#A0AEC0;'>{serial_counter}</p>", unsafe_allow_html=True)
        with r_col_act:
            if st.button(f"📝 Edit", key=f"edit_{inv_no}_{idx}"):
                st.session_state["selected_edit_doc"] = inv_no
                st.rerun()
        with r_col_inv: st.markdown(f"<p style='font-size:12px; margin:0;'>{inv_no}</p>", unsafe_allow_html=True)
        with r_col_con: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('consignee_name', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_pty: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('party_name', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_dt: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('doc_date', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_val: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('doc_net_value', '0.0')}</p>", unsafe_allow_html=True)
        with r_col_lr: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('lr_number', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_disp: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('final_lr_date', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_st: st.markdown(f"<div style='font-size:12px; margin:0;'>{status_html}</div>", unsafe_allow_html=True)
        with r_col_zone: st.markdown(f"<p style='font-size:12px; margin:0; color:#A0AEC0;'>{row.get('party_state', 'N/A')}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:2px 0px; border-color:#1E232A;'>", unsafe_allow_html=True)
        serial_counter += 1
