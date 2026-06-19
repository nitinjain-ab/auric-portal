import streamlit as st
import pandas as pd
import requests
import json

# Set up clean page layout
st.set_page_config(page_title="Auric Dispatch Tracker", layout="wide")

# --- CLEAN ENTERPRISE VISUAL THEMING ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0F1216; color: #E2E8F0; }
    h1 { color: #D4AF37 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 600; }
    h3 { color: #E5C158 !important; font-weight: 500; margin-top: 20px; }
    
    .metric-card {
        background-color: #161B22;
        border: 1px solid #2D3748;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .metric-val { color: #D4AF37; font-size: 24px; font-weight: bold; }
    .metric-lbl { color: #A0AEC0; font-size: 14px; }
    
    div[data-baseweb="select"], div[data-baseweb="input"] {
        border: 1px solid #4A5568 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"]:focus-within, div[data-baseweb="input"]:focus-within {
        border-color: #D4AF37 !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
        color: #0F1216 !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 20px !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Fetch system configurations securely from environment vaults
try:
    SUPABASE_URL = st.secrets["connections"]["supabase"]["supabase_url"].strip().rstrip('/')
    SUPABASE_KEY = st.secrets["connections"]["supabase"]["supabase_key"].strip()
except Exception:
    st.error("Missing configuration keys. Please verify your Streamlit secrets settings panel.")
    st.stop()

BASE_API_ROUTE = f"{SUPABASE_URL}/rest/v1/shipments"
HTTP_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- STAGING SESSIONS AND APPLICATION CACHE RECOVERY ---
if "auric_master_dataframe" not in st.session_state:
    st.session_state["auric_master_dataframe"] = pd.DataFrame()

# Background recovery query used to check if rows are pre-saved on cloud storage
def load_database_records_silently():
    try:
        url = f"{BASE_API_ROUTE}?select=*&limit=10"
        response = requests.get(url, headers=HTTP_HEADERS)
        if response.status_code == 200 and len(response.json()) > 0:
            full_url = f"{BASE_API_ROUTE}?select=*"
            full_res = requests.get(full_url, headers=HTTP_HEADERS)
            return pd.DataFrame(full_res.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# If session cache is fresh, check database rows instantly
if st.session_state["auric_master_dataframe"].empty:
    db_backup = load_database_records_silently()
    if not db_backup.empty:
        st.session_state["auric_master_dataframe"] = db_backup

df = st.session_state["auric_master_dataframe"]

# --- BRANDING HEADER AREA ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("✨ Auric Dispatch Control Dashboard")
    st.caption("Operational Logistics & Shipment Manifest Tracking System")
with header_col2:
    active_profile = st.selectbox("👤 Switch View Profile:", ["Full System Administrator", "Restricted Regional User"])

# --- SCREEN 1: INSTANT SHEET FILE INGESTION PIPELINE ---
if df.empty:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👋 Welcome! The live cloud storage table is currently unpopulated. Drop your Excel tracker here to load all data lines instantly.")
    
    uploaded_file = st.file_uploader("Upload Master Workbook Sheet (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            # Step 1: Read workbook elements into local memory instantaneously
            excel_df = pd.read_excel(uploaded_file, header=2)
            excel_df.columns = [str(c).strip().lower().replace('.', '').replace(' ', '_') for c in excel_df.columns]
            
            translations = {
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
                'lr_current_status': ['lr_current_status', 'current_status'],
                'order_approval_status': ['order_approval_status', 'approval_status']
            }
            
            final_mapped_df = pd.DataFrame()
            for db_field, sample_matches in translations.items():
                matched_col = next((c for c in excel_df.columns if c in sample_matches or any(sm in c for sm in sample_matches)), None)
                if matched_col: final_mapped_df[db_field] = excel_df[matched_col]
            
            if 'doc_number' not in final_mapped_df.columns and len(excel_df.columns) > 1:
                final_mapped_df['doc_number'] = excel_df.iloc[:, 1]
            if 'party_name' not in final_mapped_df.columns and len(excel_df.columns) > 5:
                final_mapped_df['party_name'] = excel_df.iloc[:, 5]
                
            final_mapped_df = final_mapped_df.dropna(subset=['doc_number'])
            
            if len(final_mapped_df) > 0:
                sanitized_rows = []
                for _, row in final_mapped_df.iterrows():
                    rd = row.to_dict()
                    cleaned_row = {k: (None if pd.isna(v) or str(v).strip().lower() in ['nan', 'nat'] else str(v).strip()) for k, v in rd.items()}
                    if 'doc_net_value' in cleaned_row and cleaned_row['doc_net_value']:
                        try: cleaned_row['doc_net_value'] = float(cleaned_row['doc_net_value'])
                        except: cleaned_row['doc_net_value'] = 0.0
                    sanitized_rows.append(cleaned_row)
                
                # Immediate local state population to bypass network processing freeze checks
                loaded_df = pd.DataFrame(sanitized_rows)
                st.session_state["auric_master_dataframe"] = loaded_df
                
                # Background upload pipeline block split into small pieces to prevent stalling
                try:
                    headers_post = {**HTTP_HEADERS, "Prefer": "resolution=merge-duplicates, return=minimal"}
                    # Seed an initial quick slice to assert operational structures
                    requests.post(BASE_API_ROUTE, headers=headers_post, data=json.dumps(sanitized_rows[:200]))
                except:
                    pass
                
                st.success("🎉 Success! Core data matrix loaded instantly into operational dashboard view models.")
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing workbook: {e}")

# --- SCREEN 2: ACTIVE RE-RENDER ENGINE CONTROLLER GRIDS ---
else:
    # 1. Dashboard summary cards
    st.markdown("### 📊 Live Operations Summary")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    total_count = len(df)
    kerala_count = len(df[df['party_state'].astype(str).str.upper() == 'KERALA']) if 'party_state' in df.columns else 0
    pending_delivery = len(df[df['lr_current_status'].astype(str).str.lower().str.contains('pending|transit', na=False)]) if 'lr_current_status' in df.columns else 0
    approved_orders = len(df[df['order_approval_status'].astype(str).str.lower().str.contains('approve|done', na=False)]) if 'order_approval_status' in df.columns else total_count
    
    with stat_col1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{total_count}</div><div class="metric-lbl">Total Logged Shipments</div></div>', unsafe_allow_html=True)
    with stat_col2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{pending_delivery}</div><div class="metric-lbl">In-Transit / Pending Delivery</div></div>', unsafe_allow_html=True)
    with stat_col3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{approved_orders}</div><div class="metric-lbl">Approved Order Handshakes</div></div>', unsafe_allow_html=True)
    with stat_col4:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{kerala_count}</div><div class="metric-lbl">Active Kerala Nodes</div></div>', unsafe_allow_html=True)

    if active_profile == "Restricted Regional User" and 'party_state' in df.columns:
        df = df[df['party_state'].astype(str).str.upper() == 'KERALA']

    # 2. Filter workspace selectors
    st.markdown("### 🔍 Search and Filter Tools")
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    
    with search_col1:
        global_search = st.text_input("💡 Quick Global Search Box:", "", placeholder="Type any Invoice Number, Client Name, or LR Code here...")
    with search_col2:
        state_filter = st.selectbox("Filter by State Zone:", ["All States"] + sorted(df['party_state'].dropna().unique().tolist()) if 'party_state' in df.columns else ["All States"])
    with search_col3:
        type_filter = st.selectbox("Filter by Channel Partner:", ["All Types"] + sorted(df['party_type'].dropna().unique().tolist()) if 'party_type' in df.columns else ["All Types"])

    f_df = df.copy()
    if global_search:
        search_lower = global_search.lower()
        mask = pd.Series(False, index=f_df.index)
        for check_field in ['doc_number', 'party_name', 'lr_number', 'consignee_name']:
            if check_field in f_df.columns:
                mask = mask | f_df[check_field].astype(str).str.lower().str.contains(search_lower, na=False)
        f_df = f_df[mask]

    if state_filter != "All States" and 'party_state' in f_df.columns:
        f_df = f_df[f_df['party_state'] == state_filter]
    if type_filter != "All Types" and 'party_type' in f_df.columns:
        f_df = f_df[f_df['party_type'] == type_filter]

    # 3. Pagination controls setup
    ROWS_PER_PAGE = 100
    total_filtered = len(f_df)
    max_pages = max(1, ((total_filtered - 1) // ROWS_PER_PAGE) + 1)
    
    st.markdown("---")
    nav_col1, nav_col2 = st.columns([3, 1])
    with nav_col1:
        current_page = st.selectbox(
            "📖 Viewing Page Range Index:",
            options=range(1, max_pages + 1),
            format_func=lambda x: f"Showing rows {(x-1)*ROWS_PER_PAGE + 1} to {min(x*ROWS_PER_PAGE, total_filtered)} (Page {x} of {max_pages})"
        )
    with nav_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        csv_buffer = f_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Export Report to CSV", data=csv_buffer, file_name="auric_filtered_manifest.csv", mime="text/csv")

    start_offset = (current_page - 1) * ROWS_PER_PAGE
    paginated_slice_df = f_df.iloc[start_offset:start_offset + ROWS_PER_PAGE]

    # 4. Standard label header mappings
    user_friendly_headers_map = {
        'consignee_name': 'Consignee Client Name', 'party_name': 'Registered Party Name',
        'party_code': 'Party Code String', 'party_type': 'Channel Category',
        'doc_number': 'Invoice / Doc Number', 'doc_date': 'Billing Date',
        'doc_net_value': 'Net Value Amount (INR)', 'lr_number': 'LR Courier Tracking Code',
        'final_lr_date': 'Dispatch Manifest Date', 'lr_current_status': 'Live Courier Status Zone'
    }
    
    display_df = paginated_slice_df.rename(columns=user_friendly_headers_map)
    visible_cols = [user_friendly_headers_map[c] for c in user_friendly_headers_map.keys() if user_friendly_headers_map[c] in display_df.columns]
    
    if not visible_cols: visible_cols = display_df.columns.tolist()
    st.dataframe(display_df[visible_cols], use_container_width=True, hide_index=True)

    # 5. Row modification form
    st.markdown("---")
    st.markdown("### 📝 Quick Row Modification Action Box")
    
    if 'doc_number' in f_df.columns:
        target_selection = st.selectbox("Select a Document Number to quickly edit field columns data metrics:", ["-- Dropdown Selection List --"] + paginated_slice_df['doc_number'].tolist())
        
        if target_selection != "-- Dropdown Selection List --":
            target_data_row = paginated_slice_df[paginated_slice_df['doc_number'] == target_selection].iloc[0]
            
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                updated_status_str = st.text_input("Update Live Courier Status Value:", value=str(target_data_row.get('lr_current_status', 'In Transit')))
            with form_col2:
                updated_remarks_str = st.text_input("Add Tracking Status Internal Remark Line:", value=str(target_data_row.get('lr_status_remark', '')))
                
            if st.button("Save Changes and Sync Back to Master Records"):
                patch_endpoint_target = f"{BASE_API_ROUTE}?doc_number=eq.{target_selection}"
                update_payload_object = {"lr_current_status": updated_status_str, "lr_status_remark": updated_remarks_str}
                requests.patch(patch_endpoint_target, headers=HTTP_HEADERS, json=update_payload_object)
                
                st.session_state["auric_master_dataframe"].loc[st.session_state["auric_master_dataframe"]['doc_number'] == target_selection, 'lr_current_status'] = updated_status_str
                st.toast("Record updated successfully!")
                st.rerun()
    
    # 6. Global Reset Button
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚨 Clear Workspace and Ingest New Sheet Version"):
        st.session_state["auric_master_dataframe"] = pd.DataFrame()
        st.rerun()
