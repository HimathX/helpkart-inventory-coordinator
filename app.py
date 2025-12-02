import streamlit as st
from utils import get_database, hash_password, verify_password, init_session_state, get_cookie_controller, COOKIE_PREFIX
import uuid
from datetime import datetime
from bson.objectid import ObjectId
import time


# Configure page
st.set_page_config(
    page_title="Helpkart",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
init_session_state()


# Initialize controller with a container to hide it
controller = get_cookie_controller()
with st.container(height=1, border=False):
    st.html("<style>div[style*='height: 1px']{display:none;}</style>")


def try_auto_login_from_cookie():
    """Auto-login from cookies if available"""
    if st.session_state.get("logged_in"):
        return

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

        st.session_state.logged_in = True
        st.session_state.center_id = str(center["_id"])
        st.session_state.center_name = center["center_name"]
        st.session_state.center_email = center["email"]
        
    except Exception as e:
        pass


try_auto_login_from_cookie()


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
    # LOGIN PAGE - ONLY THIS PAGE HAS STYLING
    st.markdown("""
    <style>
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }
        
        .login-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #0066CC;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .login-subheader {
            text-align: center;
            color: #666;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        
        .login-form {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            font-weight: 600;
            color: #1A1A1A;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .smile-labs-footer {
            text-align: center;
            padding: 2rem 0;
            color: #999;
            font-size: 0.9rem;
            margin-top: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Show login/signup page
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">🏥 Helpkart</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subheader">Distribution Center Management</div>', unsafe_allow_html=True)

        
        email = st.text_input("Email Address", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        if st.button("🚀 Login", use_container_width=True, key="login_btn"):
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

                        controller.set(f"{COOKIE_PREFIX}_center_id", str(user["_id"]), max_age=7 * 24 * 60 * 60)
                        controller.set(f"{COOKIE_PREFIX}_email", user["email"], max_age=7 * 24 * 60 * 60)

                        st.success("✅ Login successful! Redirecting...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
            else:
                st.warning("⚠️ Please fill in all fields")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="smile-labs-footer">
            <p>Built with ❤️ by <strong>SMILE LABS</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">📋 Create Account</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subheader">Join Helpkart today</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        center_name = st.text_input("Center Name", placeholder="Enter center name")
        email = st.text_input("Email Address", key="signup_email", placeholder="your@email.com")
        phone = st.text_input("Phone Number", placeholder="+91 XXXXX XXXXX")
        address = st.text_area("Address/Location", placeholder="Enter your center address", height=100)
        
        col_lat, col_lng = st.columns(2)
        with col_lat:
            latitude = st.number_input("Latitude", format="%.6f", value=0.0)
        with col_lng:
            longitude = st.number_input("Longitude", format="%.6f", value=0.0)
        
        password = st.text_input("Password", type="password", key="signup_password", placeholder="At least 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Re-enter password")
        
        if st.button("✨ Create Account", use_container_width=True, key="signup_btn"):
            if all([center_name, email, phone, address, password, confirm_password]):
                if password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    db = get_database()
                    if db is not None:
                        users = db["centers"]
                        
                        if users.find_one({"email": email}):
                            st.error("❌ Email already registered")
                        else:
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
                            st.success("✅ Account created successfully!")
                            st.info("📲 Redirecting to login page...")
            else:
                st.warning("⚠️ Please fill in all fields")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="smile-labs-footer">
            <p>Built with ❤️ by <strong>SMILE LABS</strong></p>
        </div>
        """, unsafe_allow_html=True)

else:
    # LOGGED IN - NO STYLING CHANGES, KEEP ORIGINAL
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
