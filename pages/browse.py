import streamlit as st
from datetime import datetime
from bson import ObjectId
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
    st.title("🌐 Browse Available Items")
    
    db = get_database()
    if not db:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    centers_col = db["centers"]
    inventory_col = db["inventory"]
    requests_col = db["requests"]
    
    # Filter section
    st.subheader("🔍 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_item = st.text_input("Search Item", placeholder="e.g., Rice, Water...", key="search_item")
    
    with col2:
        filter_type = st.selectbox("Show", ["All Items", "Surplus Available", "Network Requests"], key="filter_type")
    
    with col3:
        sort_by = st.selectbox("Sort By", ["Recently Added", "Name", "Quantity"], key="sort_by")
    
    st.divider()
    
    # Display based on filter type
    if filter_type == "All Items":
        st.subheader("📦 All Surplus Items from Network")
        
        # Get all surplus items from other centers
        all_items = list(inventory_col.find({
            "center_id": {"$ne": center_id},
            "surplus_or_stock": "surplus"
        }).sort("added_on", -1))
        
        if search_item:
            all_items = [item for item in all_items if search_item.lower() in item['item'].lower()]
        
        if all_items:
            for item in all_items:
                provider_center = centers_col.find_one({"_id": ObjectId(item["center_id"])})
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{item['item']}**")
                    st.caption(f"From: {provider_center['center_name']}")
                
                with col2:
                    st.write(f"{item['quantity']} {item['unit']}")
                
                with col3:
                    st.write(f"📞 {provider_center['phone']}")
                
                with col4:
                    if st.button("📩 Request This", key=f"req_{item['_id']}"):
                        st.session_state[f"show_request_form_{item['_id']}"] = True
                
                # Request form
                if st.session_state.get(f"show_request_form_{item['_id']}"):
                    with st.expander("Create Request for this Item", expanded=True):
                        qty_request = st.number_input(f"Quantity to Request", 1, item['quantity'], key=f"qty_req_{item['_id']}")
                        notes = st.text_area(f"Message to {provider_center['center_name']}", key=f"msg_{item['_id']}")
                        
                        if st.button("✅ Send Request", key=f"send_req_{item['_id']}"):
                            transaction = {
                                "transaction_id": str(uuid.uuid4()),
                                "from_center_id": item["center_id"],
                                "to_center_id": center_id,
                                "item": item['item'],
                                "quantity": qty_request,
                                "unit": item['unit'],
                                "transaction_date": datetime.now(),
                                "status": "pending",
                                "message": notes,
                                "created_at": datetime.now()
                            }
                            
                            db["transactions"].insert_one(transaction)
                            st.success(f"✅ Request sent to {provider_center['center_name']}!")
        else:
            st.info("No surplus items available in the network right now.")
    
    elif filter_type == "Surplus Available":
        st.subheader("🟢 Available Surplus by Center")
        
        # Group by center
        other_centers = centers_col.find({"_id": {"$ne": ObjectId(center_id)}})
        
        for center in other_centers:
            center_surplus = list(inventory_col.find({
                "center_id": center["_id"],
                "surplus_or_stock": "surplus"
            }))
            
            if center_surplus:
                with st.expander(f"📍 {center['center_name']} - {len(center_surplus)} items", expanded=False):
                    st.write(f"**Contact:** {center['phone']}")
                    st.write(f"**Address:** {center['address']}")
                    
                    for item in center_surplus:
                        st.write(f"  • {item['item']} - {item['quantity']} {item['unit']}")
    
    else:  # Network Requests
        st.subheader("🆘 Requests from Other Centers")
        
        # Get all open requests from other centers
        all_requests = list(requests_col.find({
            "center_id": {"$ne": center_id},
            "fulfilled": False
        }).sort("requested_on", -1))
        
        if search_item:
            all_requests = [r for r in all_requests if search_item.lower() in r['item'].lower()]
        
        if all_requests:
            for req in all_requests:
                req_center = centers_col.find_one({"_id": ObjectId(req["center_id"])})
                urgency_emoji = "🔴" if req["urgency"] == "critical" else ("🟡" if req["urgency"] == "normal" else "🟢")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"{urgency_emoji} **{req['item']}** - {req['quantity_needed']} {req['unit']}")
                    st.caption(f"From: {req_center['center_name']}")
                    st.caption(f"Reason: {req.get('description', 'N/A')}")
                
                with col2:
                    st.write(f"📞 {req_center['phone']}")
                
                with col3:
                    if st.button("✋ I Can Help", key=f"help_{req['_id']}"):
                        st.session_state[f"show_help_form_{req['_id']}"] = True
                
                # Help offer form
                if st.session_state.get(f"show_help_form_{req['_id']}"):
                    with st.expander("Offer to Provide", expanded=True):
                        qty_offer = st.number_input(f"Quantity You Can Provide", 1, req['quantity_needed'], key=f"qty_off_{req['_id']}")
                        notes = st.text_area(f"Message", key=f"offer_msg_{req['_id']}")
                        
                        if st.button("✅ Send Offer", key=f"send_offer_{req['_id']}"):
                            transaction = {
                                "transaction_id": str(uuid.uuid4()),
                                "from_center_id": center_id,
                                "to_center_id": req["center_id"],
                                "item": req['item'],
                                "quantity": qty_offer,
                                "unit": req['unit'],
                                "transaction_date": datetime.now(),
                                "status": "pending",
                                "message": notes,
                                "created_at": datetime.now()
                            }
                            
                            db["transactions"].insert_one(transaction)
                            st.success(f"✅ Offer sent to {req_center['center_name']}!")
        else:
            st.info("No active requests from other centers.")