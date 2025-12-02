import streamlit as st
from utils import get_database

def show():
    st.title("🔍 Browse Items")
    
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    inventory = db["inventory"]
    
    # Get all items from all centers except current center
    all_items = list(inventory.find({"center_id": {"$ne": center_id}}))
    
    if all_items:
        st.subheader(f"Available Items ({len(all_items)})")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.multiselect("Category", ["Medical", "Food", "Clothing", "Other"], key="browse_category")
        with col2:
            search_term = st.text_input("Search by name")
        with col3:
            min_qty = st.number_input("Minimum Quantity", min_value=0, value=0)
        
        # Apply filters
        filtered_items = all_items
        
        if category_filter:
            filtered_items = [i for i in filtered_items if i.get("category") in category_filter]
        
        if search_term:
            filtered_items = [i for i in filtered_items if search_term.lower() in i.get("item_name", "").lower()]
        
        filtered_items = [i for i in filtered_items if i.get("quantity", 0) >= min_qty]
        
        # Display items
        if filtered_items:
            for item in filtered_items:
                with st.container(border=True):
                    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1])
                    with col1:
                        st.write(f"**{item.get('item_name', 'N/A')}**")
                    with col2:
                        st.write(f"Category: {item.get('category', 'N/A')}")
                    with col3:
                        st.write(f"Available: {item.get('quantity', 0)} {item.get('unit', '')}")
                    with col4:
                        st.write(f"Description: {item.get('description', 'N/A')[:30]}...")
                    with col5:
                        if st.button("Request", key=f"req_{item['_id']}"):
                            st.success("Request sent!")
        else:
            st.info("No items match your filters")
    else:
        st.info("No items available from other centers")
