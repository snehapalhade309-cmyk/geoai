---
title: Geoai Outdoor Assistant
emoji: 🌿
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# GeoAI Outdoor Activity Assistant 🌿🏞️

An intelligent, full-stack geospatial AI web application that recommends outdoor activities based on real-time weather forecasts, air quality index (AQI), and OpenStreetMap outdoor venues.

---

## 🔗 Live Deployments & Endpoints

- **Hugging Face Space:** [https://huggingface.co/spaces/Sneha3008/Geoai-Outdoor-Assistant](https://huggingface.co/spaces/Sneha3008/Geoai-Outdoor-Assistant)
- **Live Deployed API Base URL:** `https://sneha3008-geoai-outdoor-assistant.hf.space`
- **Live API Recommendation Endpoint:** `https://sneha3008-geoai-outdoor-assistant.hf.space/api/recommend`
- **Live Question / Query Endpoint:** `https://sneha3008-geoai-outdoor-assistant.hf.space/api/ask?q=Can+I+jog+in+Pune+today`
- **Frontend Website (GitHub Pages):** [https://snehapalhade309-cmyk.github.io/geoai/](https://snehapalhade309-cmyk.github.io/geoai/)

---

## 📡 API Testing Examples

### 1. Health Status Check
```bash
curl https://sneha3008-geoai-outdoor-assistant.hf.space/api/health
```

### 2. Activity Recommendation (GET Query)
```bash
curl "https://sneha3008-geoai-outdoor-assistant.hf.space/api/recommend?activity=jogging&location=Pune"
```

### 3. Natural Language Question Query (GET Query)
```bash
curl "https://sneha3008-geoai-outdoor-assistant.hf.space/api/ask?q=Can+I+play+cricket+in+Mumbai+tomorrow?"
```

### 4. Activity Recommendation (POST JSON)
```bash
curl -X POST https://sneha3008-geoai-outdoor-assistant.hf.space/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "cycling",
    "location": "Pune, India",
    "time_window": "morning"
  }'
```
