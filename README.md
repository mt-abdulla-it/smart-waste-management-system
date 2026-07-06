# EcoSync: Smart Waste Management System

EcoSync is a modern, AI-powered smart waste management application designed to optimize municipal waste collection. It features real-time live bin tracking, AI-powered predictive fill levels, dynamic route optimization, and localized budget calculations.

This version is specifically localized for the **Colombo Municipal Council (CMC)** (the "Sri Lanka Way"), featuring LKR currencies, traffic simulation for narrow roads like Pettah, and CMC-styled alert dispatching.

## Features

- 📍 **Smart Heatmap & Live Tracking**: Real-time Leaflet maps centered on Colombo, Sri Lanka.
- 🧠 **AI Prediction Engine**: Predicts when bins will become fully loaded based on their current fill levels.
- 🚚 **Dynamic Route Optimization**: 
  - Uses NetworkX TSP approximation to find the most efficient collection route.
  - Detects traffic-heavy locations (e.g., Pettah Market) and automatically switches vehicle types (Small Compactor vs Large Truck).
  - Adjusts fuel mileage and speeds dynamically to calculate true operational costs.
- 💰 **Localized Budgeting**: Formats all costs in LKR with appropriate commas. Simulates a 5,000,000 LKR municipal budget.
- 📱 **Automated Alerting**: Dispatches CMC-formatted alerts to terminal when bins hit critical mass or when budget thresholds are exceeded.
- 📄 **PDF Reporting**: Instantly generates comprehensive monthly financial and operational reports using ReportLab.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Algorithms**: NetworkX (TSP), Math
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism + Dark Mode), JavaScript (Vanilla)
- **Map & Charts**: Leaflet.js, Chart.js

## Installation

1. **Clone the repository** (if not already downloaded) and navigate to the directory:
   ```bash
   cd smart-waste-management-system
   ```

2. **Install Python Dependencies**:
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database**:
   This will seed the database with mock bins for Colombo (Galle Face Green, Viharamahadevi Park, etc.).
   ```bash
   python database/init_db.py
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the App**:
   Open your browser and navigate to `http://127.0.0.1:5000/`.

## Usage

- **Live Dashboard**: View all bin statuses. Use the "Add Waste" button to simulate trash being added to the bin in real-time.
- **Route Optimization**: Go to the Routes tab or trigger a route calculation from the dashboard to see how EcoSync optimizes the pickup route based on Colombo's traffic.
- **Reports**: Click the "Download Monthly Report" button to generate and view a PDF summary of your budget limits and collection logs.