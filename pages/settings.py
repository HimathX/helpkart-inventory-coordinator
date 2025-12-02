import streamlit as st
from utils import get_database, hash_password

def show():
    st.title("⚙️ Settings")
    
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    centers = db["centers"]
    
    tab1, tab2 = st.tabs(["Profile Settings", "Change Password"])
    
    with tab1:
        st.subheader("Update Profile")
        
        center = centers.find_one({"_id": center_id})
        
        if center:
            col1, col2 = st.columns(2)
            with col1:
                new_center_name = st.text_input("Center Name", value=center.get("center_name", ""))
                new_phone = st.text_input("Phone Number", value=center.get("phone", ""))
            
            with col2:
                new_address = st.text_area("Address", value=center.get("address", ""))
                new_email = st.text_input("Email", value=center.get("email", ""))
            
            if st.button("Update Profile", use_container_width=True):
                centers.update_one(
                    {"_id": center_id},
                    {"$set": {
                        "center_name": new_center_name,
                        "phone": new_phone,
                        "address": new_address,
                        "email": new_email
                    }}
                )
                st.success("Profile updated successfully!")
                st.session_state.center_name = new_center_name
                st.session_state.center_email = new_email
                st.rerun()
    
    with tab2:
        st.subheader("Change Password")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("Change Password", use_container_width=True):
            center = centers.find_one({"_id": center_id})
            
            if new_password != confirm_password:
                st.error("Passwords don't match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                st.success("Password changed successfully!")
                # Hash and update password
                hashed_pwd = hash_password(new_password)
                centers.update_one(
                    {"_id": center_id},
                    {"$set": {"password": hashed_pwd}}
                )
