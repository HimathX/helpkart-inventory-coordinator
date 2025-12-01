import streamlit as st
from datetime import datetime
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database():
    from app import get_mongo_client
    client = get_mongo_client()
    if client:
        return client["helpkart_db"]
    return None

def show():
    st.title("⚙️ Settings & Profile")
    
    db = get_database()
    if not db:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    centers_col = db["centers"]
    
    center = centers_col.find_one({"_id": ObjectId(center_id)})
    
    if not center:
        st.error("Center not found")
        return
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Security", "Account"])
    
    with tab1:
        st.subheader("📍 Center Profile")
        
        with st.form("profile_form"):
            center_name = st.text_input("Center Name", value=center.get("center_name", ""))
            email = st.text_input("Email Address", value=center.get("email", ""), disabled=True)
            phone = st.text_input("Phone Number", value=center.get("phone", ""))
            address = st.text_area("Address/Location", value=center.get("address", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude", value=center.get("location_coordinates", {}).get("lat", 0.0), format="%.6f")
            with col2:
                lng = st.number_input("Longitude", value=center.get("location_coordinates", {}).get("lng", 0.0), format="%.6f")
            
            status = st.selectbox("Center Status", ["active", "inactive", "maintenance"], 
                                index=["active", "inactive", "maintenance"].index(center.get("status", "active")))
            
            if st.form_submit_button("💾 Save Changes"):
                centers_col.update_one(
                    {"_id": center["_id"]},
                    {"$set": {
                        "center_name": center_name,
                        "phone": phone,
                        "address": address,
                        "location_coordinates": {"lat": lat, "lng": lng},
                        "status": status,
                        "updated_at": datetime.now()
                    }}
                )
                st.success("✅ Profile updated successfully!")
                st.rerun()
        
        st.divider()
        st.subheader("📊 Center Statistics")
        
        inventory_col = db["inventory"]
        requests_col = db["requests"]
        transactions_col = db["transactions"]
        
        total_items = inventory_col.count_documents({"center_id": center_id})
        surplus_items = inventory_col.count_documents({"center_id": center_id, "surplus_or_stock": "surplus"})
        active_requests = requests_col.count_documents({"center_id": center_id, "fulfilled": False})
        completed_trans = transactions_col.count_documents({
            "$or": [
                {"from_center_id": center_id},
                {"to_center_id": center_id}
            ],
            "status": "completed"
        })
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Items", total_items)
        with col2:
            st.metric("Surplus Items", surplus_items)
        with col3:
            st.metric("Active Requests", active_requests)
        with col4:
            st.metric("Completed Trades", completed_trans)
    
    with tab2:
        st.subheader("🔐 Security Settings")
        
        with st.form("security_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔄 Change Password"):
                from app import verify_password, hash_password
                
                if verify_password(current_password, center.get("password", "")):
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            centers_col.update_one(
                                {"_id": center["_id"]},
                                {"$set": {"password": hash_password(new_password)}}
                            )
                            st.success("✅ Password changed successfully!")
                        else:
                            st.error("New password must be at least 6 characters")
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Current password is incorrect")
    
    with tab3:
        st.subheader("🗑️ Danger Zone")
        st.warning("⚠️ These actions cannot be undone!")
        
        if st.button("Delete Account", type="secondary"):
            confirm = st.checkbox("I understand that deleting my account will remove all data")
            
            if confirm:
                if st.button("⚠️ Confirm Delete Account", type="primary"):
                    # Delete all data associated with this center
                    db["inventory"].delete_many({"center_id": center_id})
                    db["requests"].delete_many({"center_id": center_id})
                    db["transactions"].delete_many({
                        "$or": [
                            {"from_center_id": center_id},
                            {"to_center_id": center_id}
                        ]
                    })
                    centers_col.delete_one({"_id": center["_id"]})
                    
                    # Logout
                    st.session_state.logged_in = False
                    st.session_state.center_id = None
                    st.session_state.center_name = None
                    st.success("Account deleted. Redirecting to login...")
                    st.rerun()