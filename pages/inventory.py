import streamlit as st
from utils import get_database
from datetime import datetime
import uuid
from bson.objectid import ObjectId


def show():
    st.title("📦 My Inventory")
    
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    inventory = db["inventory"]
    
    # Dialog function for editing
    @st.dialog("✏️ Edit Item")
    def edit_item_dialog(item_id):
        try:
            selected_item = inventory.find_one({"_id": ObjectId(item_id)})
            
            if selected_item:
                col1, col2 = st.columns(2)
                with col1:
                    new_quantity = st.number_input("New Quantity", value=selected_item.get("quantity", 0), min_value=0)
                    new_category = st.selectbox("Category", ["Medical", "Food", "Clothing", "Other"], 
                                               index=["Medical", "Food", "Clothing", "Other"].index(selected_item.get("category", "Other")))
                
                with col2:
                    new_unit = st.selectbox(
                        "Unit",
                        ["kg", "liters", "pieces", "grams", "meters", "boxes", "bottles", "packets", "cartons", "bags", "Other"],
                        index=["kg", "liters", "pieces", "grams", "meters", "boxes", "bottles", "packets", "cartons", "bags", "Other"].index(selected_item.get("unit", "kg"))
                    )
                    new_description = st.text_area("Description", value=selected_item.get("description", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Changes", use_container_width=True):
                        inventory.update_one(
                            {"_id": selected_item["_id"]},
                            {"$set": {
                                "quantity": new_quantity,
                                "category": new_category,
                                "unit": new_unit,
                                "description": new_description,
                                "updated_at": datetime.now()
                            }}
                        )
                        st.success("Item updated successfully! ✅")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Tabs for different actions
    tab1, tab2 = st.tabs(["View Items", "Add Item"])
    
    with tab1:
        st.subheader("View All Items")
        items = list(inventory.find({"center_id": center_id}))
        
        if items:
            for item in items:
                with st.container(border=True):
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1:
                        st.write(f"**{item.get('item_name', 'N/A')}**")
                    with col2:
                        st.write(f"Category: {item.get('category', 'N/A')}")
                    with col3:
                        st.write(f"Qty: {item.get('quantity', 0)}")
                    with col4:
                        st.write(f"Unit: {item.get('unit', 'N/A')}")
                    with col5:
                        if st.button("✏️ Edit", key=f"edit_{item['_id']}"):
                            edit_item_dialog(str(item["_id"]))
                    with col6:
                        if st.button("🗑️ Delete", key=f"del_{item['_id']}"):
                            inventory.delete_one({"_id": item["_id"]})
                            st.success("Item deleted!")
                            st.rerun()
        else:
            st.info("No items in inventory")
    
    with tab2:
        st.subheader("Add New Item")
        
        with st.form("add_item_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("Item Name")
                category = st.selectbox("Category", ["Medical", "Food", "Clothing", "Other"])
            
            with col2:
                quantity = st.number_input("Quantity", min_value=0)
                unit = st.selectbox(
                    "Unit",
                    ["kg", "liters", "pieces", "grams", "meters", "boxes", "bottles", "packets", "cartons", "bags", "Other"]
                )
            
            description = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Item", use_container_width=True)
        
        if submitted:
            if item_name and quantity >= 0:
                item_data = {
                    "item_id": str(uuid.uuid4()),
                    "center_id": center_id,
                    "item_name": item_name,
                    "category": category,
                    "quantity": quantity,
                    "unit": unit,
                    "description": description,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                inventory.insert_one(item_data)
                st.success("Item added successfully! ✅")
                st.rerun()
            else:
                st.error("Please fill in all required fields")
