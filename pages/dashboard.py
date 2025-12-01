import streamlit as st
from datetime import datetime
from bson import ObjectId
import sys
import os

# Add parent directory to path to import from app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database():
    """Get the helpkart database"""
    from app import get_mongo_client
    client = get_mongo_client()
    if client:
        return client["helpkart_db"]
    return None

def show():
    st.title("📊 Dashboard")
    
    db = get_database()
    if not db:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    
    # Get center info
    centers = db["centers"]
    center = centers.find_one({"_id": ObjectId(center_id)})
    
    if not center:
        st.error("Center not found")
        return
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    # Count surplus items
    inventory = db["inventory"]
    surplus_count = inventory.count_documents({"center_id": center_id, "surplus_or_stock": "surplus"})
    total_items = inventory.count_documents({"center_id": center_id})
    
    # Count requests
    requests_col = db["requests"]
    active_requests = requests_col.count_documents({"center_id": center_id, "fulfilled": False})
    
    # Count pending transactions
    transactions = db["transactions"]
    pending_trans = transactions.count_documents(
        {"$or": [{"from_center_id": center_id}, {"to_center_id": center_id}], "status": "pending"}
    )
    
    with col1:
        st.metric("📦 Items in Surplus", surplus_count)
    
    with col2:
        st.metric("🛒 Total Inventory Items", total_items)
    
    with col3:
        st.metric("🆘 Active Requests", active_requests)
    
    with col4:
        st.metric("⏳ Pending Transactions", pending_trans)
    
    st.divider()
    
    # Recent inventory additions
    st.subheader("🆕 Recently Added Items")
    recent_items = list(inventory.find({"center_id": center_id}).sort("added_on", -1).limit(5))
    
    if recent_items:
        for item in recent_items:
            status_color = "🟢" if item["surplus_or_stock"] == "surplus" else "🔵"
            st.write(f"{status_color} **{item['item']}** - {item['quantity']} {item['unit']} ({item['surplus_or_stock']})")
            st.caption(f"Added on: {item['added_on'].strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No items added yet. Start by adding items to your inventory!")
    
    st.divider()
    
    # Recent requests from network
    st.subheader("🌐 Recent Network Requests (From Other Centers)")
    all_requests = list(requests_col.find({"center_id": {"$ne": center_id}, "fulfilled": False}).sort("requested_on", -1).limit(5))
    
    if all_requests:
        for req in all_requests:
            req_center = centers.find_one({"_id": ObjectId(req["center_id"])})
            urgency_emoji = "🔴" if req["urgency"] == "critical" else ("🟡" if req["urgency"] == "normal" else "🟢")
            st.write(f"{urgency_emoji} **{req['item']}** - {req['quantity_needed']} {req['unit']} needed")
            st.caption(f"From: {req_center['center_name']} | Posted: {req['requested_on'].strftime('%Y-%m-%d %H:%M')}")
            
            if st.button(f"I can help with this", key=f"help_{req['_id']}"):
                st.info(f"You selected to provide {req['item']} to {req_center['center_name']}. Please navigate to 'Browse Items' to formalize this offer.")
    else:
        st.info("No active requests from other centers right now.")
    
    st.divider()
    
    # Center info card
    st.subheader("📍 Your Center Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Center Name:** {center['center_name']}")
        st.write(f"**Email:** {center['email']}")
        st.write(f"**Phone:** {center['phone']}")
    
    with col2:
        st.write(f"**Address:** {center['address']}")
        st.write(f"**Member Since:** {center['created_at'].strftime('%Y-%m-%d')}")
        st.write(f"**Status:** {center['status']}")
