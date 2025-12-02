import streamlit as st
from utils import get_database
from datetime import datetime
import uuid

def show():
    st.title("📬 My Requests")
    
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    requests_col = db["requests"]
    
    tab1, tab2 = st.tabs(["View Requests", "Create Request"])
    
    with tab1:
        st.subheader("Your Requests")
        user_requests = list(requests_col.find({"center_id": center_id}))
        
        if user_requests:
            for req in user_requests:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**Item**: {req.get('item_name', 'N/A')}")
                    with col2:
                        st.write(f"**Quantity**: {req.get('quantity', 0)}")
                    with col3:
                        st.write(f"**Status**: {req.get('status', 'Pending')}")
        else:
            st.info("No requests yet")
    
    with tab2:
        st.subheader("Create New Request")
        
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=1)
        reason = st.text_area("Reason for Request")
        
        if st.button("Submit Request", use_container_width=True):
            if item_name and quantity > 0:
                request_data = {
                    "request_id": str(uuid.uuid4()),
                    "center_id": center_id,
                    "item_name": item_name,
                    "quantity": quantity,
                    "reason": reason,
                    "status": "Pending",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                requests_col.insert_one(request_data)
                st.success("Request submitted successfully!")
                st.rerun()
            else:
                st.error("Please fill in all fields")
