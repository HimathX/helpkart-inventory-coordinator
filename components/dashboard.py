import streamlit as st
from utils import get_database
from datetime import datetime
from bson.objectid import ObjectId
from datetime import timedelta


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
    
    if not center:
        st.error("Center not found")
        return
    
    # Get inventory data
    inventory = db["inventory"]
    items = list(inventory.find({"center_id": center_id}))
    
    # ===== HEADER SECTION =====
    st.write(f"### Welcome back, {center['center_name']}! 👋")
    st.write(f"📍 {center['address']}")
    st.divider()
    
    # ===== KEY METRICS =====
    st.write("## 📈 Quick Metrics")
    
    total_items = len(items)
    total_quantity = sum([i.get("quantity", 0) for i in items])
    low_stock = len([i for i in items if 0 < i.get("quantity", 0) < 10])
    out_of_stock = len([i for i in items if i.get("quantity", 0) == 0])
    
    # Calculate items added this month
    today = datetime.now()
    month_start = datetime(today.year, today.month, 1)
    items_this_month = len([i for i in items if i.get("created_at", datetime.now()) >= month_start])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Item Types", total_items)
    
    with col2:
        st.metric("Total Quantity", total_quantity)
    
    with col3:
        st.metric("Low Stock", low_stock)
    
    with col4:
        st.metric("Out of Stock", out_of_stock)
    
    with col5:
        st.metric("Added This Month", items_this_month)
    
    st.divider()
    
    # ===== INVENTORY HEALTH =====
    if items:
        st.write("## 🏥 Inventory Health")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📦 Category Breakdown")
            
            # Count items by category
            categories = {}
            for item in items:
                cat = item.get("category", "Other")
                categories[cat] = categories.get(cat, 0) + 1
            
            # Display as text-based summary
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{cat}:** {count} item{'s' if count != 1 else ''}")
        
        with col2:
            st.subheader("⚠️ Stock Status")
            
            if out_of_stock > 0:
                st.error(f"🔴 {out_of_stock} item{'s' if out_of_stock != 1 else ''} out of stock")
            
            if low_stock > 0:
                st.warning(f"🟡 {low_stock} item{'s' if low_stock != 1 else ''} running low")
            
            if low_stock == 0 and out_of_stock == 0:
                st.success("🟢 All items well stocked!")
        
        st.divider()
        
        # ===== ITEMS NEEDING ATTENTION =====
        st.write("## 🚨 Items Needing Attention")
        
        # Out of stock items
        out_of_stock_items = [i for i in items if i.get("quantity", 0) == 0]
        
        if out_of_stock_items:
            st.subheader("🔴 Out of Stock")
            for item in out_of_stock_items[:5]:
                st.write(f"• **{item['item_name']}** ({item['category']})")
        
        # Low stock items
        low_stock_items = [i for i in items if 0 < i.get("quantity", 0) < 10]
        
        if low_stock_items:
            st.subheader("🟡 Low Stock (< 10 units)")
            for item in low_stock_items[:5]:
                qty = item.get("quantity", 0)
                st.write(f"• **{item['item_name']}** ({item['category']}) - {qty} {item.get('unit', 'units')}")
        
        if not out_of_stock_items and not low_stock_items:
            st.success("✅ All items are well stocked!")
        
        st.divider()
        
        # ===== RECENT ITEMS =====
        st.write("## 📋 Recently Added Items")
        
        # Sort by created_at
        sorted_items = sorted(items, key=lambda x: x.get("created_at", datetime.now()), reverse=True)
        recent_items = sorted_items[:5]
        
        if recent_items:
            for item in recent_items:
                created = item.get("created_at", datetime.now())
                days_ago = (datetime.now() - created).days
                time_str = f"{days_ago} days ago" if days_ago > 0 else "Today"
                
                st.write(f"• **{item['item_name']}** ({item['category']}) - {item.get('quantity', 0)} {item.get('unit', 'units')} - {time_str}")
        else:
            st.info("No items added yet")
        
        st.divider()
        
        # ===== CENTER INFO =====
        st.write("## 🏢 Center Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Center Name:** {center['center_name']}")
            st.write(f"**Email:** {center['email']}")
            st.write(f"**Phone:** {center['phone']}")
        
        with col2:
            st.write(f"**Address:** {center['address']}")
            st.write(f"**Status:** {center['status']}")
            st.write(f"**Member Since:** {center['created_at'].strftime('%d %b %Y')}")
    
    else:
        st.info("📦 No inventory items yet. Start by adding items to your inventory!")
