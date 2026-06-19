import streamlit as st
import pandas as pd
import requests
import json

# Force high-efficiency horizontal viewport canvas constraints
st.set_page_config(page_title="Auric Control Board", layout="wide")

# --- PREMIUM LUXURY ENTERPRISE BRAND COLOR ENGINE ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0F1216; color: #E2E8F0; }
    h1 { color: #D4AF37 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; margin-bottom: 0px; }
    h4 { color: #E5C158 !important; font-weight: 500; margin-top: 5px; margin-bottom: 10px; border-bottom: 1px solid #2D3748; padding-bottom: 4px; }
    
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
    
    /* Clean, defined borders for inputs across different browser windows */
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
        width: 100% !important;
        padding: 6px !important;
        font-size: 13px !important;
    }
    
    /* Compact the default multi-row spacing padding grids */
    div.block-container { padding-top: 0.8rem; padding-bottom: 0.5rem; }
    div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
    </style>
    """, unsafe_allow_html=True
)

# Fetch project variables securely
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["supabase_url"].strip().rstrip('/')
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["supabase_key"].strip()
except Exception:
    st.error("Configuration variables mismatch inside Streamlit secrets panel.")
    st.stop()

BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# In-Memory Matrix Core Frame Initializations
if "auric_master_dataframe" not in st.session_state:
    st.session_state["auric_master_dataframe"] = pd.DataFrame()

# Silent recovery routine checks if historical records exist in database
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

# --- BRANDING BAR COMPACT HEADER LAYER ---
top_col1, top_col2, top_col3, top_col4, top_col5 = st.columns([3, 1, 1, 1, 1])
with top_col1:
    st.title("✨ Auric Control Board")
    st.caption("Ver 4.5 Production Suite • Single-Screen Command Layout")

# Generate live runtime metrics
total_shipments = len(df)
pending_count = len(df[df['lr_current_status'].astype(str).str.lower().str.contains('pending|transit', na=False)]) if 'lr_current_status' in df.columns else 0
kerala_count = len(df[df['party_state'].astype(str).str.upper() == 'KERALA']) if 'party_state' in df.columns else 0

with top_col2:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{total_shipments}</div><div class="stat-lbl">Shipments</div></div>', unsafe_allow_html=True)
with top_col3:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{pending_count}</div><div class="stat-lbl">In Transit</div></div>', unsafe_allow_html=True)
with top_col4:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{kerala_count}</div><div class="stat-lbl">Kerala Nodes</div></div>', unsafe_allow_html=True)
with top_col5:
    view_tier = st.selectbox("", ["Admin (All Zones)", "Kerala Restricted"], label_visibility="collapsed")

if view_tier == "Kerala Restricted" and 'party_state' in df.columns:
    df = df[df['party_state'].astype(str).str.upper() == 'KERALA']

st.markdown("<hr style='margin-top:8px; margin-bottom:12px; border-color:#2B323C;'>", unsafe_allow_html=True)

# --- SPLIT SCREEN HOOK: LEFT HAND CANVAS (80%) vs RIGHT HAND TOOLBOX (20%) ---
left_canvas, right_toolbox = st.columns([4, 1])

with left_canvas:
    if df.empty:
        st.markdown("<br><br><div style='background-color:#161B22; padding:30px; border-left:4px solid #D4AF37; border-radius:4px;'><h4>👋 Dashboard Database Canvas is Active</h4><p style='color:#A0AEC0;'>The tracking manifest matrix is currently unseeded. Please use the <b>Spreadsheet Ingestion Tab</b> inside the right-hand toolbox console to drop your master file and populate the live grid tracking arrays instantly.</p></div>", unsafe_allow_html=True)
    else:
        # High speed global row search layout box
        search_str = st.text_input("🔍 Rapid Manifest Search Box:", "", placeholder="Type any Invoice No, Client Name, or Tracking ID to filter matching elements lines...")
        
        f_df = df.copy()
        
        # Handle search matches across the canvas frame
        if search_str:
            sl = search_str.lower()
            mask = pd.Series(False, index=f_df.index)
            for col in ['doc_number', 'party_name', 'lr_number', 'consignee_name']:
                if col in f_df.columns:
                    mask = mask | f_df[col].astype(str).str.lower().str.contains(sl, na=False)
            f_df = f_df[mask]
            
        # Slice pagination matrices rows allocation groups of 100 entries per table index drawer
        ROWS_PER_PAGE = 100
        total_matching_lines = len(f_df)
        max_pages_calc = max(1, ((total_matching_lines - 1) // ROWS_PER_PAGE) + 1)
        
        page_col_1, page_col_2 = st.columns([3, 1])
        with page_col_1:
            active_page_idx = st.selectbox(
                "📖 Select View Page Block Matrix:",
                options=range(1, max_pages_calc + 1),
                format_func=lambda x: f"Displaying rows {(x-1)*ROWS_PER_PAGE + 1} to {min(x*ROWS_PER_PAGE, total_matching_lines)} (Page {x} of {max_pages_calc})"
            )
        with page_col_2:
            st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
            csv_buffer = f_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Data CSV", data=csv_buffer, file_name="auric_manifest_report.csv", mime="text/csv")

        start_offset = (active_page_idx - 1) * ROWS_PER_PAGE
        paginated_slice_view = f_df.iloc[start_offset:start_offset + ROWS_PER_PAGE]
        
        # User Friendly Business Display Header Maps Translation Table Arrays
        headers_labels_dict = {
            'consignee_name': 'Consignee Name', 'party_name': 'Registered Party',
            'party_code': 'Party Code', 'party_type': 'Category',
            'doc_number': 'Invoice No', 'doc_date': 'Billing Date',
            'doc_net_value': 'Net Amount (INR)', 'lr_number': 'Courier LR Tracking',
            'final_lr_date': 'Dispatch Date', 'lr_current_status': 'Live Delivery Status'
        }
        
        render_df = paginated_slice_view.rename(columns=headers_labels_dict)
        target_viewable_cols = [headers_labels_dict[c] for c in headers_labels_dict.keys() if headers_labels_dict[c] in render_df.columns]
        
        if not target_viewable_cols: target_viewable_cols = render_df.columns.tolist()
        
        # Output clean grid manifest
        st.dataframe(render_df[target_viewable_cols], use_container_width=True, hide_index=True, height=450)

# --- THE RIGHT HAND RIGHT-SIDEBAR UTILITY CONTROL TOOLBOX (20%) ---
with right_toolbox:
    st.markdown("<div style='background-color:#161B22; padding:12px; border:1px solid #2B323C; border-radius:6px; min-height:550px;'>", unsafe_allow_html=True)
    
    # Establish direct functional tabs within the right-side operational panel container
    tool_tab1, tool_tab2, tool_tab3 = st.tabs(["🎛️ Slicers", "📝 Overwrite", "📥 Upload"])
    
    with tool_tab1:
        st.markdown("<h4>Global Data Slicers</h4>", unsafe_allow_html=True)
        state_sel = st.selectbox("Target State Zone:", ["All States"] + sorted(df['party_state'].dropna().unique().tolist()) if not df.empty and 'party_state' in df.columns else ["All States"])
        type_sel = st.selectbox("Target Channel Node:", ["All Categories"] + sorted(df['party_type'].dropna().unique().tolist()) if not df.empty and 'party_type' in df.columns else ["All Categories"])
        
        # Dynamically trigger cascading reductions from sidebar state models
        if not df.empty:
            if state_sel != "All States" and 'party_state' in df.columns:
                st.session_state["auric_master_dataframe"] = st.session_state["auric_master_dataframe"][st.session_state["auric_master_dataframe"]['party_state'] == state_sel]
            if type_sel != "All Categories" and 'party_type' in df.columns:
                st.session_state["auric_master_dataframe"] = st.session_state["auric_master_dataframe"][st.session_state["auric_master_dataframe"]['party_type'] == type_sel]

    with tool_tab2:
        st.markdown("<h4>Cell Overwrite Form</h4>", unsafe_allow_html=True)
        if df.empty or 'doc_number' not in df.columns:
            st.caption("No rows available to target edits.")
        else:
            target_invoice_id = st.selectbox("Invoice Target ID:", ["-- Select ID --"] + paginated_slice_view['doc_number'].tolist() if 'doc_number' in paginated_slice_view.columns else ["-- Select ID --"])
            
            if target_invoice_id != "-- Select ID --":
                active_target_row = df[df['doc_number'] == target_invoice_id].iloc[0]
                new_courier_state = st.text_input("New Courier Status:", value=str(active_target_row.get('lr_current_status', 'Delivered')))
                new_remarks_line = st.text_input("Add Audit Remark:", value=str(active_target_row.get('lr_status_remark', '')))
                
                if st.button("Sync Row Edits"):
                    endpoint_patch = f"{BASE_API_ROUTE}?doc_number=eq.{target_invoice_id}"
                    requests.patch(endpoint_patch, headers=HTTP_HEADERS, json={"lr_current_status": new_courier_state, "lr_status_remark": new_remarks_line})
                    
                    st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == target_invoice_id, 'lr_current_status'] = new_courier_state
                    st.toast("Row variables committed successfully!")
                    st.rerun()

    with tool_tab3:
        st.markdown("<h4>Spreadsheet Ingestion</h4>", unsafe_allow_html=True)
        dropped_workbook = st.file_uploader("Drop master tracker sheet:", type=["xlsx"], label_visibility="collapsed")
        
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
                    
                    st.session_state["auric_master_dataframe"] = pd.DataFrame(sanitized_list)
                    
                    try:
                        post_headers = {**HTTP_HEADERS, "Prefer": "resolution=merge-duplicates, return=minimal"}
                        requests.post(BASE_API_ROUTE, headers=post_headers, data=json.dumps(sanitized_list[:150]))
                    except: pass
                    
                    st.success("Ingestion finalized.")
                    st.rerun()
            except Exception as ex:
                st.error(f"Ingestion failed: {ex}")
                
        st.markdown("<br><hr style='border-color:#2B323C; margin-top:10px; margin-bottom:10px;'>", unsafe_allow_html=True)
        if st.button("🚨 Clear Global Canvas"):
            st.session_state["auric_master_dataframe"] = pd.DataFrame()
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
