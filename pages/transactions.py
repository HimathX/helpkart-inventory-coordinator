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
    st.title("💼 Transaction History")
    
    db = get_database()
    if not db:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    transactions_col = db["transactions"]
    centers_col = db["centers"]
    
    # Get all transactions involving this center
    all_transactions = list(transactions_col.find({
        "$or": [
            {"from_center_id": center_id},
            {"to_center_id": center_id}
        ]
    }).sort("transaction_date", -1))
    
    # Create tabs for different transaction types
    tab1, tab2, tab3 = st.tabs(["Received", "Sent", "Pending"])
    
    with tab1:
        st.subheader("📥 Items Received")
        
        received = [t for t in all_transactions if t["to_center_id"] == center_id and t["status"] == "completed"]
        
        if received:
            for trans in received:
                from_center = centers_col.find_one({"_id": ObjectId(trans["from_center_id"])})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"📦 **{trans['item']}**")
                    st.caption(f"From: {from_center['center_name']}")
                
                with col2:
                    st.write(f"{trans['quantity']} {trans['unit']}")
                
                with col3:
                    st.write(f"✅ Completed")
                
                with col4:
                    st.caption(trans['transaction_date'].strftime("%Y-%m-%d"))
                
                if trans.get('message'):
                    st.info(f"Message: {trans['message']}")
        else:
            st.info("No received items yet.")
    
    with tab2:
        st.subheader("📤 Items Sent")
        
        sent = [t for t in all_transactions if t["from_center_id"] == center_id and t["status"] == "completed"]
        
        if sent:
            for trans in sent:
                to_center = centers_col.find_one({"_id": ObjectId(trans["to_center_id"])})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"📦 **{trans['item']}**")
                    st.caption(f"To: {to_center['center_name']}")
                
                with col2:
                    st.write(f"{trans['quantity']} {trans['unit']}")
                
                with col3:
                    st.write(f"✅ Completed")
                
                with col4:
                    st.caption(trans['transaction_date'].strftime("%Y-%m-%d"))
                
                if trans.get('message'):
                    st.info(f"Message: {trans['message']}")
        else:
            st.info("No sent items yet.")
    
    with tab3:
        st.subheader("⏳ Pending Transactions")
        
        pending = [t for t in all_transactions if t["status"] == "pending"]
        
        if pending:
            for idx, trans in enumerate(pending):
                if trans["from_center_id"] == center_id:
                    other_center = centers_col.find_one({"_id": ObjectId(trans["to_center_id"])})
                    direction = "→"
                else:
                    other_center = centers_col.find_one({"_id": ObjectId(trans["from_center_id"])})
                    direction = "←"
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"⏳ **{trans['item']}** {direction} {other_center['center_name']}")
                    st.write(f"Quantity: {trans['quantity']} {trans['unit']}")
                
                with col2:
                    if trans['from_center_id'] == center_id:
                        st.write("Status: Awaiting Response")
                    else:
                        st.write("Status: Review Offer")
                
                with col3:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if trans['to_center_id'] == center_id:
                            if st.button("✅", key=f"approve_{idx}", help="Approve"):
                                transactions_col.update_one(
                                    {"_id": trans["_id"]},
                                    {"$set": {"status": "completed"}}
                                )
                                st.success("Transaction approved!")
                                st.rerun()
                    
                    with col_b:
                        if st.button("❌", key=f"reject_{idx}", help="Reject"):
                            transactions_col.delete_one({"_id": trans["_id"]})
                            st.info("Transaction cancelled")
                            st.rerun()
                
                if trans.get('message'):
                    st.info(f"Message: {trans['message']}")
                
                st.divider()
        else:
            st.info("No pending transactions.")