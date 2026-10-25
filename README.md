---
title: GeoAI Outdoor Activity Assistant
emoji: 🌿
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# GeoAI Outdoor Activity Assistant 🌿🏞️

An intelligent, full-stack geospatial AI web application that recommends outdoor activities based on real-time weather forecasts, air quality index (AQI), and OpenStreetMap outdoor venues.

---

## 🔗 Live Deployments & Endpoints

- **Frontend Website (GitHub Pages):** [https://snehapalhade309-cmyk.github.io/geoai/](https://snehapalhade309-cmyk.github.io/geoai/)
- **Hugging Face Space:** `https://huggingface.co/spaces/<YOUR_HF_USERNAME>/geoai`
- **Live Deployed API Base URL:** `https://<YOUR_HF_USERNAME>-geoai.hf.space`
- **Live API Recommendation Endpoint:** `https://<YOUR_HF_USERNAME>-geoai.hf.space/api/recommend`
- **Live Question / Query Endpoint:** `https://<YOUR_HF_USERNAME>-geoai.hf.space/api/ask?q=Can+I+jog+in+Pune+today`

---

## 📡 API Testing Examples

### 1. Health Status
```bash
curl https://<YOUR_HF_USERNAME>-geoai.hf.space/api/health
```

### 2. Activity Recommendation (GET Query)
```bash
curl "https://<YOUR_HF_USERNAME>-geoai.hf.space/api/recommend?activity=jogging&location=Pune"
```

### 3. Natural Language Question Query (GET Query)
```bash
curl "https://<YOUR_HF_USERNAME>-geoai.hf.space/api/ask?q=Can+I+play+cricket+in+Mumbai+tomorrow?"
```

### 4. Activity Recommendation (POST JSON)
```bash
curl -X POST https://<YOUR_HF_USERNAME>-geoai.hf.space/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "cycling",
    "location": "Pune, India",
    "radius_km": 5,
    "time_window": "morning"
  }'
```

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

## 🚀 Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   python app.py
   ```
   Server runs at `http://localhost:7860` (or `http://localhost:5000`).
