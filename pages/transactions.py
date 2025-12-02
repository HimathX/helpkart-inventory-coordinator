import streamlit as st
from utils import get_database

def show():
    st.title("💰 Transactions")
    
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return
    
    center_id = st.session_state.center_id
    transactions = db["transactions"]
    
    tab1, tab2 = st.tabs(["Transaction History", "Statistics"])
    
    with tab1:
        st.subheader("Your Transactions")
        user_transactions = list(transactions.find({"center_id": center_id}).sort("_id", -1))
        
        if user_transactions:
            for trans in user_transactions:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**Item**: {trans.get('item_name', 'N/A')}")
                    with col2:
                        st.write(f"**Quantity**: {trans.get('quantity', 0)}")
                    with col3:
                        st.write(f"**Type**: {trans.get('type', 'N/A')}")
                    with col4:
                        st.write(f"**Date**: {trans.get('date', 'N/A')}")
        else:
            st.info("No transactions yet")
    
    with tab2:
        st.subheader("Transaction Statistics")
        
        if user_transactions:
            total_trans = len(user_transactions)
            total_quantity = sum([trans.get("quantity", 0) for trans in user_transactions])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Transactions", total_trans)
            with col2:
                st.metric("Total Quantity Transferred", total_quantity)
        else:
            st.info("No data to display")
