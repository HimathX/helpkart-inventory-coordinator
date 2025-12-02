# 🏥 Helpkart - Inventory Coordinator

> A collaborative relief distribution network connecting centers to efficiently share resources and coordinate aid delivery.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.40.2-red.svg)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/mongodb-atlas-green.svg)](https://www.mongodb.com/atlas)
[![License](https://img.shields.io/badge/license-open--source-orange.svg)](LICENSE)

## 🌟 Overview

Helpkart is a web-based platform designed for disaster relief and humanitarian operations. It enables distribution centers to manage their inventory, post requests for needed supplies, and coordinate resource transfers with other centers in real-time.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Secure signup/login with bcrypt password hashing |
| 📦 **Inventory** | Track surplus and in-stock items with expiry dates |
| 🆘 **Requests** | Post urgent needs and browse network-wide requests |
| 🌐 **Network** | Search and offer supplies across all connected centers |
| 💼 **Transactions** | Approve transfers with built-in messaging |
| ⚙️ **Settings** | Manage center profile and account preferences |



## ⚙️ CI / Workflows

This repository includes CI workflows under the `.github/workflows/` directory.

- `compile_data.yml` — compiles or prepares dataset(s) used by the app.
- `compile_&_save_data.yml` — runs compilation and saves a snapshot/export into the `exports/` folder (example: `helpkart_export_20251202_091905.json`).


Generated exports are saved to the `exports/` folder. These JSON exports can be used to seed local development, inspect sample data, or archive snapshots of compiled data.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **MongoDB Atlas** account ([Create free account](https://www.mongodb.com/cloud/atlas/register))
- Git for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HimathX/helpkart-inventory-coordinator.git
   cd helpkart-inventory-coordinator
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Create .env file from template
   copy env.example .env  # Windows
   # cp env.example .env  # macOS/Linux
   ```
   
   Edit `.env` and add your MongoDB connection string:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

5. **Launch the application**
   ```bash
   streamlit run app.py
   ```
   
   🎉 Open your browser to **http://localhost:8501**


---

## 📁 Project Architecture

```
helpkart-inventory-coordinator/
│
├── 📄 app.py                 # Application entry point (auth & routing)
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env                   # Environment configuration (create locally)
├── 📄 env.example            # Template for environment variables
├── 📄 README.md              # Project documentation
│
└── 📂 pages/                 # Streamlit multi-page app
    ├── dashboard.py          # Overview with stats & notifications
    ├── inventory.py          # Manage center's items
    ├── requests.py           # Post & track supply requests
    ├── browse.py             # Network-wide item search
    ├── transactions.py       # Transfer history & approvals
    └── settings.py           # Profile & account management
```

### Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **Database**: MongoDB Atlas (NoSQL cloud database)
- **Auth**: bcrypt (password hashing)
- **Config**: python-dotenv (environment management)


---

## 🚢 Deployment

### Deploy to Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click **"New app"**
   - Connect your GitHub repository
   - Select `main` branch and `app.py` as entry point

3. **Configure Secrets**
   - Go to **Settings** → **Secrets**
   - Add your MongoDB connection:
     ```toml
     MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
     ```

4. **Launch** 🚀
   - Click **Deploy**
   - Your app will be live at `https://your-app.streamlit.app`


---

## 🤝 Contributing

Contributions are welcome! This project is built to serve humanitarian efforts.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📄 License

This project is **open-source** and available for humanitarian and disaster relief purposes.

---

## 🙏 Acknowledgments

Built with ❤️ to support disaster relief operations and community aid coordination.


---

<div align="center">

**[Report Bug](https://github.com/HimathX/helpkart-inventory-coordinator/issues)** • 
**[Request Feature](https://github.com/HimathX/helpkart-inventory-coordinator/issues)** • 
**[View Demo](https://appkart-inventory-coordinator.streamlit.app/)**

Made for communities in need 🌍

</div>