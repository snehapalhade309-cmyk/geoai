# GeoAI Outdoor Activity Assistant 🌿🏞️

An intelligent, full-stack, responsive geospatial AI web application that helps users determine:
- Which outdoor activity is best suited for their chosen location.
- Which nearby outdoor places/venues they can visit (OpenStreetMap Overpass API).
- Which time of day offers the most optimal weather conditions.
- How temperature, precipitation, wind, and air quality (AQI) affect plans.
- What essential items to carry and precautions to take.
- Transparent rule-based suitability scoring (0–100) with full data source attribution.

---

## 🎨 Supported Activities (10 Sports & Pastimes)
1. **🏃 Jogging**
2. **🚴 Cycling**
3. **⛳ Golf**
4. **🏏 Cricket**
5. **⚽ Football**
6. **🎾 Tennis**
7. **🥾 Hiking**
8. **🧺 Picnic**
9. **🎪 Outdoor Events**
10. **📸 Photography**

---

## 🚀 Key Features

- **All-in-One Standalone Architecture (`index.html`):** Runs out of the box when double-clicked locally or deployed directly to **GitHub Pages** with live API integration!
- **Flask REST API (`app.py`):** Optional full-stack Python backend providing endpoints:
  - `GET /` - Serves the web interface
  - `GET /api/geocode?q=...` - Open-Meteo Geocoding
  - `GET /api/weather?lat=...&lon=...` - Open-Meteo Forecast
  - `GET /api/air-quality?lat=...&lon=...` - Open-Meteo Air Quality
  - `GET /api/places?lat=...&lon=...&radius=...` - OpenStreetMap Overpass Venues
  - `POST /api/recommend` - Rule-based suitability scoring
  - `GET /api/health` - Backend health monitor
- **Live Interactive Maps:** Powered by Leaflet.js and OpenStreetMap with custom map pins and search radius circles.
- **Dynamic Charts:** Chart.js 24-hour temperature, precipitation probability, and wind trend charts.
- **Transparent Scoring:** Activity-specific rules weighing rain, thermal comfort, wind resistance, and WHO particulate AQI thresholds.

---

## 💻 How to Run Locally

### Option 1: Immediate Browser Execution (No Installation Required)
Simply double-click `index.html` or open it in any modern web browser (Chrome, Edge, Firefox, Safari).

### Option 2: Python / Flask Backend

1. **Clone or navigate to the repository:**
   ```bash
   cd geoai
   ```

2. **Create and activate a virtual environment:**
   - **Windows:**
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask server:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   ```
   http://localhost:5000
   ```

---

## 🌐 How to Deploy Online

### Deployment Option A: GitHub Pages (Instant 1-Click Hosting)
Since `index.html` is completely self-contained with client-side integration of Open-Meteo and Overpass APIs:
1. Initialize Git and commit:
   ```bash
   git init
   git add .
   git commit -m "Initial GeoAI Assistant release"
   ```
2. Create a new GitHub repository and push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/geoai.git
   git branch -M main
   git push -u origin main
   ```
3. In your GitHub repository:
   - Go to **Settings** > **Pages**.
   - Under **Build and deployment** > **Source**, choose **Deploy from a branch**.
   - Select `main` branch and `/ (root)` folder.
   - Click **Save**.
4. Your website will be live in ~1 minute at `https://YOUR_USERNAME.github.io/geoai/`!

### Deployment Option B: Render / Railway / PythonAnywhere (Full Flask Backend)
1. Push to GitHub.
2. Link your repository on [Render](https://render.com) or [Railway](https://railway.app).
3. Set Build Command: `pip install -r requirements.txt`.
4. Set Start Command: `python app.py` (or `gunicorn app:app`).

---

## 📡 Data Sources & Attribution
- **Weather Forecast:** [Open-Meteo Weather API](https://open-meteo.com)
- **Air Quality:** [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
- **Geocoding & Venues:** © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors and Overpass API
