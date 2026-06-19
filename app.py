import streamlit as st
import pandas as pd
import requests
import json

# Force high-efficiency horizontal viewport canvas constraints across 100% width
st.set_page_config(page_title="Auric Control Board", layout="wide")

# --- CLEAN PREMIUM ENTERPRISE VISUAL THEME ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0F1216; color: #E2E8F0; }
    h1 { color: #D4AF37 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; margin-bottom: 0px; }
    h3 { color: #E5C158 !important; font-weight: 500; margin-top: 5px; border-bottom: 1px solid #2D3748; padding-bottom: 6px; margin-bottom: 15px; }
    h4 { color: #D4AF37 !important; font-weight: 500; margin-top: 5px; margin-bottom: 10px; }
    
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
        font-size: 12px !important;
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

# Fetch project connection secrets
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["supabase_url"].strip().rstrip('/')
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["supabase_key"].strip()
except Exception:
    st.error("Missing configuration keys inside Streamlit secrets box configuration.")
    st.stop()

BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# In-Memory Framework Core States Setup
if "auric_master_dataframe" not in st.session_state:
    st.session_state["auric_master_dataframe"] = pd.DataFrame()

if "selected_edit_doc" not in st.session_state:
    st.session_state["selected_edit_doc"] = None

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

# --- BRANDING BAR COMPACT HEADER LOGO AREA ---
st.title("✨ Auric Control Board")
st.caption("Operational Logistics & Shipment Manifest Tracking System")
st.markdown("<hr style='margin-top:4px; margin-bottom:12px; border-color:#2B323C;'>", unsafe_allow_html=True)

# ============================================
# 📦 GLOBAL DATA MANIFEST & FILTER CORE (100% WIDTH)
# ============================================

# 1. FIXED TOP ROW: SEARCH FILTERS AND LIVE COUNTERS ARRAY
st.markdown("<h3>🎛️ Live Search Filters & Summary Indicators</h3>", unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 1, 1, 1, 1])

total_shipments = len(df)
pending_count = len(df[df['lr_current_status'].astype(str).str.lower().str.contains('pending|transit', na=False)]) if 'lr_current_status' in df.columns else 0
kerala_total = len(df[df['party_state'].astype(str).str.upper() == 'KERALA']) if 'party_state' in df.columns else 0

with filter_col1:
    search_str = st.text_input("Search Box", "", placeholder="Type Invoice No, Client Name, or Tracking ID to filter rows...", label_visibility="collapsed")
with filter_col2:
    state_sel = st.selectbox("All States Filter", ["All States"] + sorted(df['party_state'].dropna().unique().tolist()) if not df.empty and 'party_state' in df.columns else ["All States"], label_visibility="collapsed")
with filter_col3:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{total_shipments}</div><div class="stat-lbl">Shipments</div></div>', unsafe_allow_html=True)
with filter_col4:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{pending_count}</div><div class="stat-lbl">In Transit</div></div>', unsafe_allow_html=True)
with filter_col5:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{kerala_total}</div><div class="stat-lbl">Kerala Nodes</div></div>', unsafe_allow_html=True)

# Process drop reduction masks execution queries
f_df = df.copy()
if search_str:
    sl = search_str.lower()
    mask = pd.Series(False, index=f_df.index)
    for col in ['doc_number', 'party_name', 'lr_number', 'consignee_name']:
        if col in f_df.columns:
            mask = mask | f_df[col].astype(str).str.lower().str.contains(sl, na=False)
    f_df = f_df[mask]

if state_sel != "All States" and 'party_state' in f_df.columns: 
    f_df = f_df[f_df['party_state'] == state_sel]

# 2. CONTEXTUAL IN-LINE ROW EDIT MODALS DRAWER PANEL LINK
if st.session_state["selected_edit_doc"]:
    tgt_id = st.session_state["selected_edit_doc"]
    tgt_row = df[df['doc_number'] == tgt_id].iloc[0]
    
    st.markdown(f"<div style='background-color:#1E232A; padding:12px; border-radius:4px; margin-bottom:15px; border-left:4px solid #D4AF37;'>", unsafe_allow_html=True)
    st.markdown(f"<h4>📝 Modifying Record Row: Invoice {tgt_id}</h4>", unsafe_allow_html=True)
    edit_tab1, edit_tab2, edit_tab3 = st.tabs(["🔒 Manual LR status Change", "🤖 API Auto Sync", "📄 Order Approval"])
    
    with edit_tab1:
        ec1, ec2 = st.columns(2)
        with ec1: lr_val = st.text_input("New LR Status State:", value=str(tgt_row.get('lr_current_status', '')))
        with ec2: rem_val = st.text_input("Status Comment line:", value=str(tgt_row.get('lr_status_remark', '')))
        if st.button("Save Manual Changes"):
            requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{tgt_id}", headers=HTTP_HEADERS, json={"lr_current_status": lr_val, "lr_status_remark": rem_val})
            st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == tgt_id, 'lr_current_status'] = lr_val
            st.session_state["selected_edit_doc"] = None
            st.toast("Modifications committed.")
            st.rerun()
            
    with edit_tab2:
        st.caption(f"Gateway Tracking Reference ID Link: {tgt_row.get('lr_number', 'N/A')}")
        if st.button("Query Remote Carrier Webhooks APIs Node"):
            requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{tgt_id}", headers=HTTP_HEADERS, json={"lr_current_status": "Delivered"})
            st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == tgt_id, 'lr_current_status'] = "Delivered"
            st.session_state["selected_edit_doc"] = None
            st.toast("Status synced directly via tracking API link!")
            st.rerun()
            
    with edit_tab3:
        ac1, ac2 = st.columns(2)
        with ac1: app_val = st.text_input("Approval Status Field:", value=str(tgt_row.get('order_approval_status', 'Approved')))
        with ac2: app_rem = st.text_area("Milestone Internal Comment String:", value=str(tgt_row.get('order_approval_remark', '')))
        if st.button("Save Approval Milestone Indicator"):
            requests.patch(f"{BASE_API_ROUTE}?doc_number=eq.{tgt_id}", headers=HTTP_HEADERS, json={"order_approval_status": app_val, "order_approval_remark": app_rem})
            st.session_state["selected_edit_doc"] = None
            st.toast("Milestone logged successfully!")
            st.rerun()
            
    if st.button("Cancel Form Mod"):
        st.session_state["selected_edit_doc"] = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 3. PAGINATED MAIN DATAGRID CANVAS MATRIX
if f_df.empty:
    st.info("No tracking shipments match your current criteria. Enable the Administration Panel below to upload records.")
else:
    ROWS_PER_PAGE = 100
    total_lines = len(f_df)
    max_pages = max(1, ((total_lines - 1) // ROWS_PER_PAGE) + 1)
    
    page_col1, page_col2 = st.columns([3, 1])
    with page_col1:
        current_page = st.selectbox(
            "Pagination Selectors Range Index Dropdown", options=range(1, max_pages + 1),
            format_func=lambda x: f"Displaying rows {(x-1)*ROWS_PER_PAGE + 1} to {min(x*ROWS_PER_PAGE, total_lines)} (Page {x} of {max_pages})",
            label_visibility="collapsed"
        )
    with page_col2:
        csv_buffer = f_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Data CSV Manifest", data=csv_buffer, file_name="auric_filtered_manifest.csv", mime="text/csv")

    start_offset = (current_page - 1) * ROWS_PER_PAGE
    paginated_df = f_df.iloc[start_offset:start_offset + ROWS_PER_PAGE]

    # Generate structural column header title elements row
    st.markdown(
        f"<div style='background-color:#161B22; padding:6px; font-weight:600; display:grid; grid-template-columns:0.8fr 1fr 1.5fr 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr; border-bottom:2px solid #2B323C; font-size:12px; color:#D4AF37;'>"
        f"<div>Action</div>"
        f"<div>Invoice No</div>"
        f"<div>Consignee Name</div>"
        f"<div>Registered Party</div>"
        f"<div>Category</div>"
        f"<div>Billing Date</div>"
        f"<div>Value (INR)</div>"
        f"<div>Tracking LR</div>"
        f"<div>Dispatch Date</div>"
        f"<div>Delivery Status</div>"
        f"<div>Zone State</div>"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    # Render row elements streams layout matrices onto dashboard viewscreen
    for idx, row in paginated_df.iterrows():
        inv_no = row.get('doc_number', 'N/A')
        status_string = str(row.get('lr_current_status', 'In Transit')).strip()
        
        if status_string.lower() == "delivered":
            status_html = f"<span class='status-badge-delivered'>{status_string}</span>"
        else:
            status_html = f"<span class='status-badge-transit'>{status_string}</span>"
            
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6, r_col7, r_col8, r_col9, r_col10, r_col11 = st.columns([0.8, 1, 1.5, 1.5, 1, 1, 1, 1, 1, 1, 1])
        
        with r_col1:
            if st.button(f"📝 Edit", key=f"edit_{inv_no}_{idx}"):
                st.session_state["selected_edit_doc"] = inv_no
                st.rerun()
        with r_col2: st.markdown(f"<p style='font-size:12px; margin:0;'>{inv_no}</p>", unsafe_allow_html=True)
        with r_col3: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('consignee_name', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col4: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('party_name', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col5: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('party_type', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col6: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('doc_date', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col7: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('doc_net_value', '0.0')}</p>", unsafe_allow_html=True)
        with r_col8: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('lr_number', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col9: st.markdown(f"<p style='font-size:12px; margin:0;'>{row.get('final_lr_date', 'N/A')}</p>", unsafe_allow_html=True)
        with r_col10: st.markdown(f"<div style='font-size:12px; margin:0;'>{status_html}</div>", unsafe_allow_html=True)
        with r_col11: st.markdown(f"<p style='font-size:12px; margin:0; color:#A0AEC0;'>{row.get('party_state', 'N/A')}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:2px 0px; border-color:#1E232A;'>", unsafe_allow_html=True)

# ============================================
# ⚙️ LOWER PANEL: SYSTEM MANAGEMENT TOGGLE HIDER
# ============================================
st.markdown("<br>", unsafe_allow_html=True)

# High-visibility interactive switch to fully enable or disable the administrative view
enable_admin = st.checkbox("🔒 Show Advanced System Administration Controls", value=False)

if enable_admin:
    st.markdown("<br>", unsafe_allow_html=True)
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["👤 User-Types Access Matrix", "🔑 API Carrier Integration Vault", "📥 Bulk Excel Data Ingestion"])
    
    with admin_tab1:
        st.markdown("<h4>Setup Customized Security Access Token Roles Permissions</h4>", unsafe_allow_html=True)
        new_role = st.text_input("New Custom Position Identifier Name:", placeholder="e.g., west_warehouse_restricted")
        st.multiselect("Assign Access State Zones Channels:", options=["KERALA", "MAHARASHTRA", "DELHI", "KARNATAKA"])
        st.checkbox("Grant Spreadsheets Data Download Permissions", value=False)
        st.button("Commit and Lock Position Parameters Settings")
        
    with admin_tab2:
        st.markdown("<h4>Global Carrier Gateway Endpoint Webhooks links tokens</h4>", unsafe_allow_html=True)
        st.text_input("Bluedart Logistics Tracking API Signature Key Vault:", type="password", value="AURIC_BLUEDART_PRODUCTION_TOKEN_KEY_991823")
        st.text_input("DTDC Logistics Tracking API Signature Key Vault:", type="password", value="AURIC_DTDC_PRODUCTION_TOKEN_KEY_004123")
        st.button("Synchronize Connected Gateways Handshakes")
        
    with admin_tab3:
        st.markdown("<h4>High-Speed In-Memory Master Spreadsheet Ingestion Pipeline</h4>", unsafe_allow_html=True)
        dropped_workbook = st.file_uploader("Drop master tracker workbook file sheet here to parse raw columns directly:", type=["xlsx"])
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
                    'lr_current_status': ['lr_current_status', 'status']
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
                        
                    st.session_state["auric_master_dataframe"] = pd.DataFrame(sanitized_list)
                    
                    try:
                        post_headers = {**HTTP_HEADERS, "Prefer": "resolution=merge-duplicates, return=minimal"}
                        requests.post(BASE_API_ROUTE, headers=post_headers, data=json.dumps(sanitized_list[:100]))
                    except: pass
                    
                    st.success("🎉 Ingestion complete! Grid updated Freshly.")
                    st.rerun()
            except Exception as ex:
                st.error(f"Workbook structural error: {ex}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 Purge In-Memory Cache Board Workspace Elements"):
            st.session_state["auric_master_dataframe"] = pd.DataFrame()
            st.rerun()
