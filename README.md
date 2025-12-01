# 🏥 Helpkart - Distribution Center Management System

A **production-ready Streamlit application** for managing relief distribution centers. Built with MongoDB, featuring real-time inventory management, request tracking, and transaction coordination.

## ✨ Key Features

### 🔐 Authentication
- Secure signup/login with email & password
- Password hashing using bcrypt
- Session-based authentication
- Account deletion with data cleanup

### 📊 Dashboard
- Real-time statistics (inventory, requests, transactions)
- Recently added items feed
- Network request notifications
- Center information display

### 📦 Inventory Management
- Add/edit/delete items
- Track surplus and in-stock items
- Optional expiry date tracking
- Notes for each item

### 🆘 Request Management
- Post requests for needed items
- Set urgency levels (Critical/Normal/Low)
- Track request status
- View who fulfilled your requests

### 🌐 Network Browsing
- Search across all centers' surplus items
- View other centers' requests
- Request items from other centers
- Offer to fulfill requests

### 💼 Transaction Management
- Track sent and received items
- Pending transaction approval system
- Message communication between centers
- Complete transaction history

### ⚙️ Settings & Profile
- Edit center information
- Change password
- View center statistics
- Delete account option

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account (free at [mongodb.com](https://mongodb.com))

### Installation

```bash
# 1. Clone/Create project
git clone <repo> helpkart-app
cd helpkart-app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and add your MongoDB URI

# 5. Run the app
streamlit run app.py
```

**App will open at**: `http://localhost:8501`

---

## 📁 Project Structure

```
helpkart-app/
├── app.py                    # Main application (login/signup)
├── requirements.txt          # Dependencies
├── .env                      # Environment variables (create locally)
├── .env.example              # Example configuration
├── README.md                 # This file
│
└── pages/                    # Application pages
    ├── __init__.py
    ├── dashboard.py          # Overview & statistics
    ├── inventory.py          # Manage items
    ├── requests.py           # Post & track requests
    ├── browse.py             # Network browsing
    ├── transactions.py       # Transaction history
    └── settings.py           # User settings
```

---

## 🗄️ Database Schema

### MongoDB Collections

#### 1. **centers** - Distribution Centers/Users
```json
{
  "center_id": "uuid",
  "center_name": "Colombo Relief Center",
  "email": "center@email.com",
  "password": "bcrypt_hash",
  "phone": "0112345678",
  "address": "Colombo, Sri Lanka",
  "location_coordinates": { "lat": 6.9271, "lng": 79.8612 },
  "status": "active",
  "created_at": "2025-12-01T09:00:00",
  "updated_at": "2025-12-01T09:00:00"
}
```

#### 2. **inventory** - Items Centers Have
```json
{
  "inventory_id": "uuid",
  "center_id": "parent_center_uuid",
  "item": "Rice",
  "quantity": 50,
  "unit": "kg",
  "surplus_or_stock": "surplus",
  "notes": "High quality",
  "added_on": "2025-12-01T09:00:00",
  "expiry_date": "2025-12-15"
}
```

#### 3. **requests** - Items Centers Need
```json
{
  "request_id": "uuid",
  "center_id": "parent_center_uuid",
  "item": "Water",
  "quantity_needed": 100,
  "unit": "liters",
  "urgency": "critical",
  "description": "For flood victims",
  "requested_on": "2025-12-01T09:00:00",
  "fulfilled": false,
  "status": "open",
  "fulfilled_by": null
}
```

#### 4. **transactions** - Who Gave to Whom
```json
{
  "transaction_id": "uuid",
  "from_center_id": "uuid",
  "to_center_id": "uuid",
  "item": "Rice",
  "quantity": 20,
  "unit": "kg",
  "transaction_date": "2025-12-01T10:00:00",
  "status": "pending|completed|cancelled",
  "message": "Optional message"
}
```

---

## 🎯 User Workflows

### Workflow 1: Adding Inventory
1. Log in to center account
2. Navigate to "My Inventory"
3. Fill in item details (name, quantity, unit, status)
4. Click "Add to Inventory"
5. Item appears in list and network browsing

### Workflow 2: Posting a Request
1. Go to "My Requests"
2. Fill in what you need (item, quantity, urgency, reason)
3. Click "Post Request"
4. Other centers can see and respond to your request

### Workflow 3: Helping Another Center
1. Browse "Browse Items" page
2. Switch to "Network Requests" tab
3. Find a critical request you can fulfill
4. Click "I Can Help"
5. Specify quantity and send offer
6. Recipient approves/rejects in "Transactions"
7. Once approved, transaction marked as "Completed"

---

## 🔐 Security Features

### Authentication
- Passwords hashed with bcrypt (10 salt rounds)
- Email validation on signup
- Prevents duplicate email registration
- Secure password reset via settings

### Authorization
- Centers can only edit their own data
- Cannot modify other centers' requests/inventory
- Transactions require both parties
- Destructive actions require confirmation

### Data Privacy
- Phone numbers shared only after transaction initiation
- Private messaging between centers
- Transaction history isolated per user
- No data exposed in URLs (uses session state)

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit==1.40.2` | Web framework |
| `pymongo==4.8.0` | MongoDB driver |
| `bcrypt==4.1.3` | Password hashing |
| `python-dotenv==1.0.1` | Environment variables |
| `certifi==2024.12.14` | SSL certificates |
| `pytz==2024.1` | Timezone handling |

---

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Click "New app" → Select repository
4. Go to Settings → Secrets
5. Add `MONGODB_URI` with your connection string
6. Deploy!

### Self-Hosted
```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn -w 1 -b 0.0.0.0:8000 'streamlit run app.py'

# Configure with nginx or Apache as reverse proxy
```

---

## 🧪 Testing Guide

### Create Test Centers
```
Center 1:
- Email: center1@test.com
- Password: Test@123
- Name: "Central Relief Hub"

Center 2:
- Email: center2@test.com
- Password: Test@123
- Name: "District Medical Center"
```

### Test Workflow
1. **Sign up** both centers
2. **Add Items**: Center 1 adds Rice (100kg, surplus)
3. **Post Requests**: Center 2 posts Water request (critical)
4. **Browse**: Center 1 checks "Browse Items" → sees Water request
5. **Offer**: Center 1 offers Water to Center 2
6. **Approve**: Center 2 approves transaction
7. **Verify**: Both see completed transaction in history

---

## 🐛 Troubleshooting

### "Failed to connect to MongoDB"
- Check `MONGODB_URI` in `.env`
- Whitelist your IP in MongoDB Atlas (Network Access)
- Ensure URL-encoded credentials

### "Module not found" errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python virtual environment is activated

### Session state not persisting
- Clear browser cache
- Use Incognito mode to test
- Restart Streamlit server

### Slow queries
- Add MongoDB indexes on frequently queried fields
- Use `.limit()` in browse queries
- Consider caching with `@st.cache_data`

---

## 🗺️ API Reference

### Main Functions (in `app.py`)

#### `get_mongo_client()`
Returns cached MongoDB client connection.

#### `get_database()`
Returns the `helpkart_db` database instance.

#### `hash_password(password)`
Hashes password using bcrypt. Returns hashed string.

#### `verify_password(password, hashed)`
Verifies plain password against bcrypt hash. Returns boolean.

### Page Modules
Each page module has a `show()` function:
```python
# pages/dashboard.py
def show():
    # Page logic
    pass
```

---

## 📊 MongoDB Indexes Recommendation

For better performance, create these indexes:

```javascript
// Centers collection
db.centers.createIndex({ "email": 1 }, { unique: true })
db.centers.createIndex({ "center_id": 1 })

// Inventory collection
db.inventory.createIndex({ "center_id": 1 })
db.inventory.createIndex({ "surplus_or_stock": 1 })

// Requests collection
db.requests.createIndex({ "center_id": 1 })
db.requests.createIndex({ "fulfilled": 1 })
db.requests.createIndex({ "urgency": 1 })

// Transactions collection
db.transactions.createIndex({ "from_center_id": 1 })
db.transactions.createIndex({ "to_center_id": 1 })
db.transactions.createIndex({ "status": 1 })
```

---

## 🚀 Future Roadmap

### Phase 2 (Planned)
- [ ] Email notifications on request/transaction changes
- [ ] Reputation/rating system for centers
- [ ] AI-powered item matching
- [ ] Maps integration (Leaflet)
- [ ] Analytics dashboard

### Phase 3 (Considered)
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Sinhala, Tamil)
- [ ] Offline sync capability
- [ ] Advanced reporting
- [ ] Integration with government systems

---

## 📄 License

This project is open-source and available for humanitarian use.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: support@helpkart.org
- Documentation: [HELPKART_SETUP_GUIDE.pdf](./HELPKART_SETUP_GUIDE.pdf)

---

## ⭐ Acknowledgments

- Built for disaster relief and community support
- Inspired by original Helpkart project
- Built with ❤️ for Sri Lanka

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: December 2025