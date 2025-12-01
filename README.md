# 🏥 Helpkart - Distribution Center Management System

A Streamlit application for managing relief distribution centers with MongoDB backend. Features inventory management, request tracking, and transaction coordination between centers.

## Features

- Secure authentication with bcrypt password hashing
- Real-time inventory and request management
- Network browsing to find/offer supplies across centers
- Transaction tracking and approval system
- Center profile and settings management


## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account

### Installation

```bash
# Clone repository
git clone <repo> helpkart-app
cd helpkart-app

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your MongoDB URI to .env

# Run
streamlit run app.py
```

App opens at `http://localhost:8501`


## Project Structure

```
helpkart-app/
├── app.py                # Main application
├── requirements.txt      # Dependencies
├── .env                  # Environment variables
└── pages/                # Application pages
    ├── dashboard.py      
    ├── inventory.py      
    ├── requests.py       
    ├── browse.py         
    ├── transactions.py   
    └── settings.py       
```


## Database Schema

MongoDB collections:

**centers** - Distribution centers/users
- center_id, center_name, email, password (hashed), phone, address, location_coordinates

**inventory** - Items centers have
- inventory_id, center_id, item, quantity, unit, surplus_or_stock, notes, expiry_date

**requests** - Items centers need  
- request_id, center_id, item, quantity_needed, unit, urgency, description, fulfilled, status

**transactions** - Transfer records
- transaction_id, from_center_id, to_center_id, item, quantity, unit, status, message


## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Create new app from repository
4. Add `MONGODB_URI` in Settings → Secrets
5. Deploy

### Recommended MongoDB Indexes
```javascript
db.centers.createIndex({ "email": 1 }, { unique: true })
db.inventory.createIndex({ "center_id": 1 })
db.requests.createIndex({ "center_id": 1, "fulfilled": 1 })
db.transactions.createIndex({ "from_center_id": 1, "to_center_id": 1 })
```

## License

Open-source for humanitarian use.

---

**Version**: 1.0.0 | Built for disaster relief and community support