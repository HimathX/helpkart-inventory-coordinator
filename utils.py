import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid
from streamlit_cookies_controller import CookieController

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

COOKIE_PREFIX = "helpkart"

def get_cookie_controller():
    # Use a fixed key so the component is stable across reruns
    return CookieController(key="helpkart_cookies")


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
    if client is not None:
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
