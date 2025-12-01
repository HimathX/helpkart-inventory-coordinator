import streamlit as st
from datetime import datetime
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database():
    from app import get_mongo_client
    client = get_mongo_client()
    if client:
        return client["helpkart_db"]
    return None

def show():
    st.title("🆘 My Requests")
    
    db = get_database()
    if not db:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    requests_col = db["requests"]
    
    # Create new request section
    st.subheader("➕ Post New Request")
    
    col1, col2 = st.columns(2)
    
    with col1:
        item_needed = st.text_input("What do you need?", key="req_item")
        quantity_needed = st.number_input("Quantity Needed", min_value=1, key="req_qty")
        unit = st.selectbox("Unit", ["kg", "liters", "packs", "pieces", "sets", "boxes"], key="req_unit")
    
    with col2:
        urgency = st.selectbox("Urgency Level", ["critical", "normal", "low"], key="req_urgency")
        description = st.text_area("Why do you need this? (Description)", key="req_desc")
    
    if st.button("📤 Post Request", use_container_width=True):
        if item_needed and quantity_needed:
            request_data = {
                "request_id": str(uuid.uuid4()),
                "center_id": center_id,
                "item": item_needed,
                "quantity_needed": quantity_needed,
                "unit": unit,
                "urgency": urgency,
                "description": description,
                "requested_on": datetime.now(),
                "fulfilled": False,
                "fulfilled_by": None,
                "status": "open"
            }
            
            requests_col.insert_one(request_data)
            st.success(f"✅ Request posted for {quantity_needed} {unit} of {item_needed}!")
        else:
            st.warning("Please fill in item name and quantity")
    
    st.divider()
    
    # Display existing requests
    st.subheader("📋 Your Current Requests")
    
    my_requests = list(requests_col.find({"center_id": center_id}).sort("requested_on", -1))
    
    if my_requests:
        tab1, tab2 = st.tabs(["Open", "Fulfilled"])
        
        with tab1:
            open_reqs = [r for r in my_requests if not r["fulfilled"]]
            if open_reqs:
                for idx, req in enumerate(open_reqs):
                    urgency_emoji = "🔴" if req["urgency"] == "critical" else ("🟡" if req["urgency"] == "normal" else "🟢")
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"{urgency_emoji} **{req['item']}** - {req['quantity_needed']} {req['unit']}")
                        st.caption(req.get('description', 'No description'))
                        st.caption(f"Posted: {req['requested_on'].strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        st.metric("Status", req.get('status', 'open').capitalize())
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_req_{idx}"):
                            requests_col.delete_one({"_id": req["_id"]})
                            st.success("Request deleted!")
                            st.rerun()
            else:
                st.info("No open requests. Great job!")
        
        with tab2:
            fulfilled_reqs = [r for r in my_requests if r["fulfilled"]]
            if fulfilled_reqs:
                for req in fulfilled_reqs:
                    centers = db["centers"]
                    provider = centers.find_one({"_id": req.get("fulfilled_by")}) if req.get("fulfilled_by") else None
                    
                    st.write(f"✅ **{req['item']}** - {req['quantity_needed']} {req['unit']}")
                    if provider:
                        st.caption(f"Provided by: {provider['center_name']}")
                    st.caption(f"Fulfilled on: {req.get('fulfilled_on', 'N/A')}")
            else:
                st.info("No fulfilled requests yet.")
    else:
        st.info("No requests posted yet. Start posting what you need!")