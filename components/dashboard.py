import streamlit as st
from utils import get_database
from datetime import datetime
from bson.objectid import ObjectId

def show():
    st.title("📊 Dashboard")
    
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    
    # Convert string back to ObjectId
    try:
        center_oid = ObjectId(center_id)
    except:
        st.error("Invalid center ID")
        return
    
    # Get center data
    centers = db["centers"]
    center = centers.find_one({"_id": center_oid})
    
    if center:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Center Name", center["center_name"])
        
        with col2:
            st.metric("Email", center["email"])
        
        with col3:
            st.metric("Phone", center["phone"])
        
        with col4:
            st.metric("Status", center["status"])
        
        st.divider()
        
        # Inventory Summary
        st.subheader("📦 Inventory Summary")
        inventory = db["inventory"]
        items = list(inventory.find({"center_id": center_id}))
        
        if items:
            total_items = len(items)
            low_stock = len([i for i in items if i.get("quantity", 0) < 10])
            total_quantity = sum([i.get("quantity", 0) for i in items])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Item Types", total_items)
            with col2:
                st.metric("Total Quantity", total_quantity)
            with col3:
                st.metric("Low Stock Items", low_stock)
        else:
            st.info("No inventory items yet")
        
        st.divider()
        
