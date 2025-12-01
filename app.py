import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority")

@st.cache_resource
def get_mongo_client():
    """Create and cache MongoDB connection"""
    try:
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'), tls=True, tlsAllowInvalidCertificates=False)
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None

def get_database():
    """Get the helpkart database"""
    client = get_mongo_client()
    if client:
        return client["helpkart_db"]
    return None

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'center_id' not in st.session_state:
        st.session_state.center_id = None
    if 'center_name' not in st.session_state:
        st.session_state.center_name = None
    if 'center_email' not in st.session_state:
        st.session_state.center_email = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

# Configure page
st.set_page_config(
    page_title="Helpkart - Distribution Center Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f5a96;
        margin-bottom: 1rem;
    }
    .status-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .status-critical {
        border-left: 4px solid #ef4444;
    }
    .status-surplus {
        border-left: 4px solid #10b981;
    }
    .status-normal {
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.center_id = None
    st.session_state.center_name = None
    st.session_state.center_email = None
    st.session_state.page = 'login'
    st.rerun()

# Main app
if not st.session_state.logged_in:
    # Show login/signup page
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown('<div class="main-header">Helpkart Login</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, key="login_btn"):
                if email and password:
                    db = get_database()
                    if db:
                        users = db["centers"]
                        user = users.find_one({"email": email})
                        
                        if user and verify_password(password, user["password"]):
                            st.session_state.logged_in = True
                            st.session_state.center_id = str(user["_id"])
                            st.session_state.center_name = user["center_name"]
                            st.session_state.center_email = user["email"]
                            st.session_state.page = 'dashboard'
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                else:
                    st.warning("Please fill in all fields")
    
    with tab2:
        st.markdown('<div class="main-header">Create New Center Account</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            center_name = st.text_input("Center Name")
            email = st.text_input("Email Address", key="signup_email")
            phone = st.text_input("Phone Number")
            address = st.text_area("Address/Location")
            latitude = st.number_input("Latitude", format="%.6f")
            longitude = st.number_input("Longitude", format="%.6f")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", use_container_width=True, key="signup_btn"):
                if all([center_name, email, phone, address, password, confirm_password]):
                    if password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        db = get_database()
                        if db:
                            users = db["centers"]
                            
                            # Check if email already exists
                            if users.find_one({"email": email}):
                                st.error("Email already registered")
                            else:
                                # Create new center
                                center_data = {
                                    "center_id": str(uuid.uuid4()),
                                    "center_name": center_name,
                                    "email": email,
                                    "password": hash_password(password),
                                    "phone": phone,
                                    "address": address,
                                    "location_coordinates": {
                                        "lat": latitude,
                                        "lng": longitude
                                    },
                                    "status": "active",
                                    "created_at": datetime.now(),
                                    "updated_at": datetime.now()
                                }
                                
                                result = users.insert_one(center_data)
                                st.success("Account created successfully! Please login.")
                                st.info("Redirecting to login page...")
                else:
                    st.warning("Please fill in all fields")

else:
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.center_name}!")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "My Inventory", "My Requests", "Browse Items", "Transactions", "Settings"],
            key="sidebar_nav"
        )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Route to pages based on selection
    if page == "Dashboard":
        from pages import dashboard
        dashboard.show()
    elif page == "My Inventory":
        from pages import inventory
        inventory.show()
    elif page == "My Requests":
        from pages import requests
        requests.show()
    elif page == "Browse Items":
        from pages import browse
        browse.show()
    elif page == "Transactions":
        from pages import transactions
        transactions.show()
    elif page == "Settings":
        from pages import settings
        settings.show()