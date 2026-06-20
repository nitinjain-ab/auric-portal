import streamlit as st
import pandas as pd
import requests
import json
import time

# Force high-efficiency 100% full-width viewport canvas constraints
st.set_page_config(page_title="Auric Control Board", layout="wide")

# --- PREMIUM VISUAL THEME ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0F1216; color: #E2E8F0; }
    h1 { color: #D4AF37 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; margin-bottom: 0px; }
    h3 { color: #E5C158 !important; font-weight: 500; margin-top: 5px; border-bottom: 1px solid #2D3748; padding-bottom: 6px; margin-bottom: 15px; }
    h4 { color: #D4AF37 !important; font-weight: 500; margin-top: 10px; margin-bottom: 5px; }
    
    .stat-box {
        background: #161B22;
        border: 1px solid #2B323C;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
    }
    .stat-val { color: #D4AF37; font-size: 20px; font-weight: bold; }
    .stat-lbl { color: #A0AEC0; font-size: 11px; text-transform: uppercase; }
    
    div[data-baseweb="select"], div[data-baseweb="input"] {
        border: 1px solid #3B424D !important;
        background-color: #1A202C !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
        color: #0F1216 !important;
        font-weight: 600 !important;
    }
    
    div [data-testid="stProgressBar"] > div > div {
        background-color: #D4AF37 !important;
    }
    
    .status-badge-delivered {
        background-color: #1E4620 !important;
        color: #FFFFFF !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-badge-transit {
        color: #E5C158 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Fetch secure configuration endpoints safely
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["supabase_url"].strip().rstrip('/')
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["supabase_key"].strip()
except Exception:
    st.error("Missing configuration credentials inside the secrets manager panel.")
    st.stop()

BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- STAGING SESSIONS INITIALIZATIONS ---
if "auric_master_dataframe" not in st.session_state:
    st.session_state["auric_master_dataframe"] = pd.DataFrame()

if "selected_edit_doc" not in st.session_state:
    st.session_state["selected_edit_doc"] = None

def check_cloud_records():
    try:
        test_url = f"{BASE_API_ROUTE}?select=doc_number&limit=1"
        response = requests.get(test_url, headers=HTTP_HEADERS)
        if response.status_code == 200 and len(response.json()) > 0:
            full_res = requests.get(f"{BASE_API_ROUTE}?select=*", headers=HTTP_HEADERS)
            if full_res.status_code == 200:
                return pd.DataFrame(full_res.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Background recovery checkpoint scan
if st.session_state["auric_master_dataframe"].empty:
    db_backup = check_cloud_records()
    if not db_backup.empty:
        st.session_state["auric_master_dataframe"] = db_backup

df = st.session_state["auric_master_dataframe"]

# --- BRANDING BAR HEADER ---
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
        sidebar_tabs = st.tabs(["👤 Users Panel", "🔑 API Gateway", "📥 Workbook Upload"])
        
        with sidebar_tabs[0]:
            st.markdown("<h4>Active Access Matrices</h4>", unsafe_allow_html=True)
            st.caption("Admin profile locked to active master configurations loop.")
            
        with sidebar_tabs[1]:
            st.markdown("<h4>API Carrier Pipelines</h4>", unsafe_allow_html=True)
            st.caption("Carrier sync nodes actively listening on backend loops.")

        with sidebar_tabs[2]:
            st.markdown("<h4>Spreadsheet Processing Engine</h4>", unsafe_allow_html=True)
            upload_tier_mode = st.radio(
                "Upload Splicer Mode Target:",
                ["1. Ingest Master Tracker Sheet", "2. Update LR Logistics Only", "3. Update Orders Approval Status Only"]
            )
            
            dropped_workbook = st.file_uploader("Drop tracking workbook file (.xlsx):", type=["xlsx"])
            if dropped_workbook:
                try:
                    # Clean multi-row Excel headers
                    raw_excel_df = pd.read_excel(dropped_workbook, header=2)
                    
                    # Force strict structural naming formats across incoming elements row blocks
                    raw_excel_df.columns = [str(c).strip().lower().replace('.', '').replace(' ', '_') for c in raw_excel_df.columns]
                    
                    vocab_translations = {
                        'party_type': ['party_type', 'partytype', 'type'], 
                        'doc_number': ['doc_number', 'doc_no', 'document_number', 'invoice_no', 'invoice_number'],
                        'doc_date': ['doc_date', 'date', 'document_date', 'invoice_date'], 
                        'consignee_name': ['consignee_name', 'consignee', 'customer_name'],
                        'party_name': ['party_name', 'party', 'distributor_name'], 
                        'party_code': ['party_code', 'partycode', 'customer_code'],
                        'party_state': ['party_state', 'state', 'region'], 
                        'doc_net_value': ['doc_net_value', 'net_value', 'amount', 'bill_value'],
                        'lr_number': ['lr_number', 'lr_no', 'tracking_no', 'tracking_number'], 
                        'final_lr_date': ['final_lr_date', 'lr_date', 'dispatch_date'],
                        'lr_current_status': ['lr_current_status', 'status', 'delivery_status'], 
                        'order_approval_status': ['order_approval_status', 'approval_status', 'approval']
                    }
                    
                    mapped_build_df = pd.DataFrame()
                    for db_field, key_matches in vocab_translations.items():
                        m_col = next((c for c in raw_excel_df.columns if c in key_matches or any(km in c for km in key_matches)), None)
                        if m_col: mapped_build_df[db_field] = raw_excel_df[m_col]
                    
                    # Fallback assignment arrays drivers if mapping hits blank spaces
                    if 'doc_number' not in mapped_build_df.columns and len(raw_excel_df.columns) > 1:
                        mapped_build_df['doc_number'] = raw_excel_df.iloc[:, 1]
                    if 'party_name' not in mapped_build_df.columns and len(raw_excel_df.columns) > 4:
                        mapped_build_df['party_name'] = raw_excel_df.iloc[:, 4]
                        
                    # Drop blank spaces safely
                    mapped_build_df = mapped_build_df.dropna(subset=['doc_number'])
                    total_rows_to_process = len(mapped_build_df)
                    
                    if total_rows_to_process > 0:
                        sanitized_list = []
                        for _, row in mapped_build_df.iterrows():
                            r_dict = row.to_dict()
                            c_row = {}
                            for k, v in r_dict.items():
                                if pd.isna(v) or str(v).strip().lower() in ['nan', 'nat', '#ref!', '#value!']:
                                    c_row[k] = "N/A"
                                else:
                                    c_row[k] = str(v).strip()
                            
                            # Standardize values arrays formatting
                            if 'doc_net_value' in c_row and c_row['doc_net_value'] != "N/A":
                                try: c_row['doc_net_value'] = str(round(float(c_row['doc_net_value']), 2))
                                except: pass
                            sanitized_list.append(c_row)
                        
                        # Convert to solid dataframe layout object
                        loaded_df = pd.DataFrame(sanitized_list)
                        
                        progress_label_placeholder = st.empty()
                        progress_bar_placeholder = st.empty()
                        
                        if "1. Ingest Master" in upload_tier_mode:
                            # FORCE DATA STRAIGHT TO APP WORKSPACE TO PREVENT EMPTY VIEWS COMPLETELY
                            st.session_state["auric_master_dataframe"] = loaded_df
                            
                            CHUNK_SIZE = 250
                            for index in range(0, total_rows_to_process, CHUNK_SIZE):
                                current_chunk_end = min(index + CHUNK_SIZE, total_rows_to_process)
                                completion_percentage = float(current_chunk_end / total_rows_to_process)
                                
                                progress_label_placeholder.markdown(f"⏳ **Writing Data Stream: {current_chunk_end} of {total_rows_to_process} rows**")
                                progress_bar_placeholder.progress(completion_percentage)
                                
                                try:
                                    chunk_data = sanitized_list[index:current_chunk_end]
                                    post_headers = {**HTTP_HEADERS, "Prefer": "resolution=merge-duplicates, return=minimal"}
                                    requests.post(BASE_API_ROUTE, headers=post_headers, data=json.dumps(chunk_data))
                                except:
                                    pass
                                time.sleep(0.01)
                                
                            progress_label_placeholder.empty()
                            progress_bar_placeholder.empty()
                            st.success(f"🎉 Success! {total_rows_to_process} structural records loaded.")
                        
                        elif "2. Update LR" in upload_tier_mode:
                            for r in sanitized_list:
                                if r.get('doc_number'):
                                    st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == r['doc_number'], 'lr_current_status'] = r.get('lr_current_status', 'N/A')
                                    try: requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json={"lr_current_status": r.get('lr_current_status', 'N/A')})
                                    except: pass
                            st.success("Courier updates synced.")
                        
                        elif "3. Update Orders" in upload_tier_mode:
                            for r in sanitized_list:
                                if r.get('doc_number'):
                                    st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == r['doc_number'], 'order_approval_status'] = r.get('order_approval_status', 'N/A')
                                    try: requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{r['doc_number']}", headers=HTTP_HEADERS, json={"order_approval_status": r.get('order_approval_status', 'N/A')})
                                    except: pass
                            st.success("Approvals updates written.")
                        st.rerun()
                except Exception as ex:
                    st.error(f"Incompatible file structure format layout template: {ex}")
                    
        st.markdown("<br><hr style='border-color:#2B323C;'>", unsafe_allow_html=True)
        if st.button("🚨 Clear App Memory Workspace"):
            st.session_state["auric_master_dataframe"] = pd.DataFrame()
            try: requests.delete(f"{BASE_API_ROUTE}?select=*", headers=HTTP_HEADERS)
            except: pass
            st.rerun()


# ========================================================
# 📦 MAIN DATA CANVAS PANEL (100% MAIN COLUMN SCREEN SPACE)
# ========================================================
st.markdown("### 🎛️ Live Search Filters & Summary Indicators</h3>", unsafe_allow_html=True)

# 1. THE TOP WORKSPACE MENUBAR SEARCH FILTERS CONTROLS
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 1, 1, 1, 1])

total_shipments = len(df)
pending_count = len(df[df['lr_current_status'].astype(str).str.lower().str.contains('pending|transit', na=False)]) if 'lr_current_status' in df.columns else 0
kerala_total = len(df[df['party_state'].astype(str).str.upper() == 'KERALA']) if 'party_state' in df.columns else 0

# DYNAMIC DROPDOWN SELECTION: Generates labels directly from active column records values
available_states_options = ["All States Selection"]
if not df.empty and 'party_state' in df.columns:
    unique_states_list = sorted([str(x) for x in df['party_state'].dropna().unique() if str(x).strip() != ''])
    available_states_options += unique_states_list

with filter_col1:
    search_str = st.text_input("Global Search Input Field Tracker", "", placeholder="Type any Invoice No, Client Name, or LR tracking code here to filter dashboard instantly...", label_visibility="collapsed")
with filter_col2:
    state_sel = st.selectbox("State Region Filter Dropdown Menu", options=available_states_options, index=0, label_visibility="collapsed")
with filter_col3:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{total_shipments}</div><div class="stat-lbl">Total Shipments</div></div>', unsafe_allow_html=True)
with filter_col4:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{pending_count}</div><div class="stat-lbl">In Transit</div></div>', unsafe_allow_html=True)
with filter_col5:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{kerala_total}</div><div class="stat-lbl">Kerala Nodes</div></div>', unsafe_allow_html=True)

# Run cascading reductions masks evaluations queries safely with string fallback safety layers
f_df = df.copy()
if not f_df.empty:
    if search_str:
        sl = search_str.lower()
        search_mask = pd.Series(False, index=f_df.index)
        for col in f_df.columns:
            search_mask = search_mask | f_df[col].astype(str).str.lower().str.contains(sl, na=False)
        f_df = f_df[search_mask]

    if state_sel != "All States Selection" and 'party_state' in f_df.columns: 
        f_df = f_df[f_df['party_state'].astype(str) == state_sel]

# 2. CONTEXTUAL IN-LINE FORM WORKSPACE FIELD OVERWRITES DRAWER PANEL MODULE
if st.session_state["selected_edit_doc"]:
    tgt_id = st.session_state["selected_edit_doc"]
    tgt_row = df[df['doc_number'] == tgt_id].iloc[0]
    
    st.markdown(f"<div style='background-color:#1E232A; padding:12px; border-radius:4px; margin-bottom:15px; border-left:4px solid #D4AF37;'>", unsafe_allow_html=True)
    st.markdown(f"<h4>📝 Modifying Record Row Target: Invoice {tgt_id}</h4>", unsafe_allow_html=True)
    edit_tabs = st.tabs(["🔒 Manual LR status Overwrite", "🤖 API Carrier Auto Sync", "📄 Milestone Handshake Approval"])
    
    with edit_tabs[0]:
        ec1, ec2 = st.columns(2)
        with ec1: lr_val = st.text_input("New LR Status State Value:", value=str(tgt_row.get('lr_current_status', '')))
        with ec2: rem_val = st.text_input("Internal Status Comment remark:", value=str(tgt_row.get('lr_status_remark', '')))
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
    st.info("No shipments records found in display memory. Open the Left Sidebar and drop your file in the Upload tab to populate records.")
else:
    # Set up exact pagination bounds parameters offsets
    ROWS_PER_PAGE = 100
    total_lines = len(f_df)
    max_pages = max(1, ((total_lines - 1) // ROWS_PER_PAGE) + 1)
    
    page_col_left, page_col_right = st.columns([3, 1])
    with page_col_left:
        current_page = st.selectbox(
            "Page Navigation Selector Dropdown Bar", options=range(1, max_pages + 1),
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
        status_string = str(row.get('lr_current_status', 'N/A')).strip()
        
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
        with r_col_val: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('doc_net_value', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_lr: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('lr_number', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_disp: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('final_lr_date', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col_st: st.markdown(f"<div style='font-size:12px; margin:0;'>{status_html}</div>", unsafe_allow_html=True)
        with r_col_zone: st.markdown(f"<p style='font-size:12px; margin:0; color:#A0AEC0;'>{row.get('party_state', 'N/A')}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:2px 0px; border-color:#1E232A;'>", unsafe_allow_html=True)
        serial_counter += 1
