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
    st.title("📦 My Inventory")
    
    db = get_database()
    if not db:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    inventory_col = db["inventory"]
    
    # Add new item section
    st.subheader("➕ Add New Item to Inventory")
    
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("Item Name", key="item_name_input")
        quantity = st.number_input("Quantity", min_value=1, key="qty_input")
        unit = st.selectbox("Unit", ["kg", "liters", "packs", "pieces", "sets", "boxes"], key="unit_select")
    
    with col2:
        status = st.selectbox("Status", ["surplus", "in_stock"], key="status_select")
        expiry_date = st.date_input("Expiry Date (Optional)", value=None)
        notes = st.text_area("Notes/Description", key="notes_input")
    
    if st.button("✅ Add to Inventory", use_container_width=True):
        if item_name and quantity:
            inventory_data = {
                "inventory_id": str(uuid.uuid4()),
                "center_id": center_id,
                "item": item_name,
                "quantity": quantity,
                "unit": unit,
                "surplus_or_stock": status,
                "notes": notes,
                "added_on": datetime.now(),
                "expiry_date": expiry_date if expiry_date else None
            }
            
            inventory_col.insert_one(inventory_data)
            st.success(f"✅ Added {quantity} {unit} of {item_name} to inventory!")
        else:
            st.warning("Please fill in item name and quantity")
    
    st.divider()
    
    # Display existing inventory
    st.subheader("📋 Current Inventory")
    
    items = list(inventory_col.find({"center_id": center_id}).sort("added_on", -1))
    
    if items:
        # Create a table-like display
        for idx, item in enumerate(items):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{item['item']}**")
                if item.get('notes'):
                    st.caption(item['notes'])
            
            with col2:
                status_badge = "🟢 Surplus" if item['surplus_or_stock'] == "surplus" else "🔵 In Stock"
                st.write(status_badge)
            
            with col3:
                st.write(f"{item['quantity']} {item['unit']}")
            
            with col4:
                st.caption(item['added_on'].strftime("%Y-%m-%d"))
            
            with col5:
                col_e, col_d = st.columns(2)
                with col_e:
                    if st.button("✏️", key=f"edit_{idx}", help="Edit"):
                        st.session_state[f"edit_{idx}"] = True
                
                with col_d:
                    if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
                        inventory_col.delete_one({"_id": item["_id"]})
                        st.success("Item deleted!")
                        st.rerun()
            
            # Edit form if needed
            if st.session_state.get(f"edit_{idx}"):
                with st.expander(f"Edit {item['item']}", expanded=True):
                    new_quantity = st.number_input(f"New Quantity", value=item['quantity'], key=f"new_qty_{idx}")
                    new_status = st.selectbox(f"New Status", ["surplus", "in_stock"], index=0 if item['surplus_or_stock'] == "surplus" else 1, key=f"new_status_{idx}")
                    
                    if st.button("💾 Save Changes", key=f"save_{idx}"):
                        inventory_col.update_one(
                            {"_id": item["_id"]},
                            {"$set": {
                                "quantity": new_quantity,
                                "surplus_or_stock": new_status
                            }}
                        )
                        st.success("Item updated!")
                        st.rerun()
    else:
        st.info("No items in inventory yet. Add your first item above!")