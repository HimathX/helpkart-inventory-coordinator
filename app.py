import streamlit as st
from utils import get_database, hash_password, verify_password, init_session_state, get_cookie_controller, COOKIE_PREFIX
import uuid
from datetime import datetime
from bson.objectid import ObjectId
import time


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


# Initialize controller with a container to hide it
controller = get_cookie_controller()
with st.container(height=1, border=False):
    st.html("<style>div[style*='height: 1px']{display:none;}</style>")


def try_auto_login_from_cookie():
    """Auto-login from cookies if available"""
    # If already logged in, nothing to do
    if st.session_state.get("logged_in"):
        return

    # Small delay to let cookie component initialize
    time.sleep(0.5)
    
    try:
        cookies = controller.getAll()
        center_id_cookie = cookies.get(f"{COOKIE_PREFIX}_center_id")
        email_cookie = cookies.get(f"{COOKIE_PREFIX}_email")

        if not center_id_cookie or not email_cookie:
            return

        db = get_database()
        if db is None:
            return

        centers = db["centers"]
        try:
            center = centers.find_one({"_id": ObjectId(center_id_cookie)})
        except Exception:
            return

        if not center:
            return

        # Rehydrate session_state
        st.session_state.logged_in = True
        st.session_state.center_id = str(center["_id"])
        st.session_state.center_name = center["center_name"]
        st.session_state.center_email = center["email"]
        
    except Exception as e:
        # Silently fail - cookies might not be ready yet
        pass


# Call auto-login
try_auto_login_from_cookie()


# Logout function
def logout():
    controller = get_cookie_controller()
    controller.remove(f"{COOKIE_PREFIX}_center_id")
    controller.remove(f"{COOKIE_PREFIX}_email")

    st.session_state.logged_in = False
    st.session_state.center_id = None
    st.session_state.center_name = None
    st.session_state.center_email = None
    st.session_state.page = "login"
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
                    if db is not None:
                        users = db["centers"]
                        user = users.find_one({"email": email})
                        
                        if user and verify_password(password, user["password"]):
                            st.session_state.logged_in = True
                            st.session_state.center_id = str(user["_id"])
                            st.session_state.center_name = user["center_name"]
                            st.session_state.center_email = user["email"]
                            st.session_state.page = 'dashboard'

                            # Set cookies with 7-day expiry
                            controller.set(f"{COOKIE_PREFIX}_center_id", str(user["_id"]), max_age=7 * 24 * 60 * 60)
                            controller.set(f"{COOKIE_PREFIX}_email", user["email"], max_age=7 * 24 * 60 * 60)

                            st.success("Login successful! Redirecting...")
                            time.sleep(0.5)  # Wait for cookies to sync
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
                        if db is not None:
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
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.center_name}!")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "My Inventory", "My Requests", "Browse Items", "Settings"],
            key="sidebar_nav"
        )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Route to pages based on selection
    if page == "Dashboard":
        from components import dashboard
        dashboard.show()
    elif page == "My Inventory":
        from components import inventory
        inventory.show()
    elif page == "My Requests":
        from components import requests
        requests.show()
    elif page == "Browse Items":
        from components import browse
        browse.show()
    elif page == "Settings":
        from components import settings
        settings.show()
