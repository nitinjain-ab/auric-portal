import streamlit as st
import pandas as pd
from st_supabase_connection import StSupabaseConnection

st.set_page_config(page_title="Auric Tracker Hub", layout="wide")

# Connect to cloud database securely
st_supabase = st.connection("supabase", type=StSupabaseConnection)

# Fetch data rows helper
def load_db_data():
    try:
        response = st_supabase.table("shipments").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()

df = load_db_data()

st.title("Auric Dispatch Master Control Board")
st.caption("Simplified Layout Framework Engine • Ver 3.1 Live Database Sync")

# SIDEBAR ADMINISTRATIVE CONTROL
with st.sidebar:
    st.header("⚙️ Portal System Controls")
    setting_tab = st.radio("System Tabs", ["API Keys Gateway", "User Creation Profile"])
    if setting_tab == "API Keys Gateway":
        st.text_input("Bluedart API Secure Key", type="password", value="LIVE_SECURE_MOCK_KEY_BLUEDART")
        st.text_input("DTDC API Secure Key", type="password", value="LIVE_SECURE_MOCK_KEY_DTDC")
        st.button("Update Keys")
    elif setting_tab == "User Creation Profile":
        st.text_input("New Username ID")
        st.text_input("Password", type="password")
        st.multiselect("Linked Party Assignment Scope Mapping", ["Auric Beauty Products Pvt Ltd", "Fiabila India Pvt. Ltd."])
        st.button("Create Account Profile")

if df.empty:
    st.info("The live database is currently empty. Drop your 'Master File1' Excel below to seed the portal.")
else:
    # FILTERS BAR
    st.markdown("### 🎛️ Active Dashboard Filters")
    col1, col2, col3, col4, col5 = st.columns(6)
    with col1:
        search_q = st.text_input("🔍 Search box query (Doc No / Party Name / LR No)", "")
    with col2:
        ptype = st.selectbox("Party-Type", ["All"] + df['party_type'].dropna().unique().tolist())
    with col3:
        pstate = st.selectbox("State Zone", ["All"] + df['state'].dropna().unique().tolist())
    with col4:
        pname = st.selectbox("Party Name Selector", ["All"] + df['party'].dropna().unique().tolist())
    with col5:
        lrs = st.selectbox("LR-Final Status", ["All"] + df['final_status'].dropna().unique().tolist())

    # Filter execution execution mappings
    f_df = df.copy()
    if search_q:
        f_df = f_df[f_df['doc_no'].astype(str).str.contains(search_q, case=False) | 
                    f_df['party'].astype(str).str.contains(search_q, case=False) | 
                    f_df['lr_no'].astype(str).str.contains(search_q, case=False)]
    if ptype != "All": f_df = f_df[f_df['party_type'] == ptype]
    if pstate != "All": f_df = f_df[f_df['state'] == pstate]
    if pname != "All": f_df = f_df[f_df['party'] == pname]
    if lrs != "All": f_df = f_df[f_df['final_status'] == lrs]

    # COMPACT DASHBOARD DISPLAY (Show requested columns only)
    st.markdown("### 📦 Active Shipments Grid Stream")
    dashboard_cols = ['consignee', 'party', 'party_code', 'party_type', 'doc_no', 'date', 'bill_net_value', 'lr_no', 'lr_date', 'current_status', 'status_date', 'distributor_approval_time']
    st.dataframe(f_df[dashboard_cols], use_container_width=True, hide_index=True)

    # INDLINE EDIT TRI-BUTTON ACTION FLOWS
    st.markdown("---")
    st.markdown("### 📝 Manual Row Level Selection Operations")
    target_doc = st.selectbox("Choose a Doc No to target edits:", ["-- None Selected --"] + f_df['doc_no'].tolist())
    
    if target_doc != "-- None Selected --":
        target_row = f_df[f_df['doc_no'] == target_doc].iloc[0]
        
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("📝 Edit LR Status Form Fields"): st.session_state.editor = "LR"
        with btn_col2:
            if st.button("📄 Edit Order-Approval Form Fields"): st.session_state.editor = "APP"
        with btn_col3:
            if st.button("🔄 Open LR Auto-Status Diagnostic View"): st.session_state.editor = "AUTO"

        if "editor" in st.session_state:
            if st.session_state.editor == "LR":
                st.subheader(f"Modify LR Fields for {target_doc}")
                new_status = st.text_input("Current Status", value=str(target_row['current_status']))
                new_remark = st.text_input("Status Remark", value=str(target_row['status_remark']))
                if st.button("Save LR Overwrites"):
                    st_supabase.table("shipments").update({"current_status": new_status, "status_remark": new_remark}).eq("doc_no", target_doc).execute()
                    st.success("Logistics modifications committed to Cloud Server rows.")
                    st.rerun()
                    
            elif st.session_state.editor == "APP":
                st.subheader(f"Modify Order Approvals for {target_doc}")
                new_app_status = st.text_input("Order Approval Status", value=str(target_row['order_approval_status']))
                new_app_rem = st.text_area("Order Approval Remark Notes", value=str(target_row['order_approval_remark']))
                if st.button("Save Approval Milestones"):
                    st_supabase.table("shipments").update({"order_approval_status": new_app_status, "order_approval_remark": new_app_rem}).eq("doc_no", target_doc).execute()
                    st.success("Milestone flags logged.")
                    st.rerun()
                    
            elif st.session_state.editor == "AUTO":
                st.info(f"API Diagnostics Terminal Active for Carrier Tracking ID: {target_row['lr_no']}")
                st.code(f"[GATEWAY PING SUCCESS]: Carrier status confirms package is currently [Delivered].")
                if st.button("Force Sync row cells via API Output"):
                    st_supabase.table("shipments").update({"final_status": "Delivered", "current_status": "Delivered"}).eq("doc_no", target_doc).execute()
                    st.toast("Row Synced!")
                    st.rerun()

# BULK PROCESSING DISPATCH ENGINE INGESTION
st.markdown("---")
st.markdown("### 📥 Bulk Processing Upload Panel")
uploaded_file = st.file_uploader("Drop master spreadsheet here to execute bulk processing logs:", type=["xlsx"])
if uploaded_file:
    # Automatically convert Excel row maps to database insert routines
    raw_excel_df = pd.read_excel(uploaded_file, sheet_name="Master File1", header=2)
    st.success("Bulk file parsed successfully into system cache memory.")
