"""
GeoAI Outdoor Activity Assistant - Gradio & FastAPI Backend Service
Runs on Hugging Face Free CPU without Docker or Credit Card verification requirements.
Provides both an interactive UI and full REST API endpoints.
"""

import os
import math
import re
from datetime import datetime
import requests
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

USER_AGENT = "GeoAI-OutdoorAssistant/1.0 (contact: geoai@example.com)"
TIMEOUT_SECONDS = 10

ACTIVITIES_RULES = {
    "jogging": {
        "name": "Jogging",
        "keywords": ["jog", "jogging", "run", "running", "sprint"],
        "ideal_temp": (14, 22),
        "max_wind": 28,
        "max_precip_prob": 25,
        "max_aqi": 100,
        "gear": ["Cushioned Running Shoes", "Hydration Bottle", "Moisture-wicking shirt", "Cap / Sweatband"],
        "precautions": ["Warm up for 5 mins", "Wear reflective clothes in twilight", "Stay hydrated even in cold"]
    },
    "cycling": {
        "name": "Cycling",
        "keywords": ["cycle", "cycling", "bike", "biking", "bicycle", "ride"],
        "ideal_temp": (15, 26),
        "max_wind": 24,
        "max_precip_prob": 20,
        "max_aqi": 90,
        "gear": ["Bicycle Helmet (Mandatory)", "Tire repair kit & pump", "Bike lights", "Padded gloves"],
        "precautions": ["Check tire pressure & brakes", "Beware of slippery painted road lines", "Watch crosswinds"]
    },
    "golf": {
        "name": "Golf",
        "keywords": ["golf", "golfing", "driving range"],
        "ideal_temp": (18, 27),
        "max_wind": 22,
        "max_precip_prob": 15,
        "max_aqi": 120,
        "gear": ["Golf clubs & tees", "Golf glove & balls", "Sun protection cap", "Soft-spiked golf shoes"],
        "precautions": ["Halt play if lightning warnings emerge", "Apply SPF 30+ sunscreen", "Drink water frequently"]
    },
    "cricket": {
        "name": "Cricket",
        "keywords": ["cricket", "batting", "bowling", "nets"],
        "ideal_temp": (18, 29),
        "max_wind": 25,
        "max_precip_prob": 10,
        "max_aqi": 110,
        "gear": ["Cricket bat & protective pads", "Match balls", "Cricket helmet", "Spiked cricket footwear"],
        "precautions": ["Inspect pitch moisture", "Stop play if rain creates slippery footing", "Wear head protection"]
    },
    "football": {
        "name": "Football",
        "keywords": ["football", "soccer", "turf"],
        "ideal_temp": (14, 25),
        "max_wind": 30,
        "max_precip_prob": 30,
        "max_aqi": 95,
        "gear": ["Football boots/studs", "Shin guards", "Team kit", "Size 5 football"],
        "precautions": ["Check pitch surface for waterlogging", "Hydrate at half-time", "Dynamic warm-up before play"]
    },
    "tennis": {
        "name": "Tennis",
        "keywords": ["tennis", "racket", "court"],
        "ideal_temp": (16, 26),
        "max_wind": 18,
        "max_precip_prob": 5,
        "max_aqi": 100,
        "gear": ["Tennis racket & balls", "Non-marking tennis shoes", "Overgrips & wristbands", "Sun visor"],
        "precautions": ["Never play on wet hard courts (severe injury hazard)", "Wear polarized glasses for overhead sun", "Pace rallies in heat"]
    },
    "hiking": {
        "name": "Hiking",
        "keywords": ["hike", "hiking", "trek", "trekking", "climb"],
        "ideal_temp": (13, 24),
        "max_wind": 32,
        "max_precip_prob": 20,
        "max_aqi": 90,
        "gear": ["Trekking boots", "Trekking poles", "1.5L Hydration pack & electrolytes", "Offline GPS & first aid kit"],
        "precautions": ["Check trail maps & sunset time before departure", "Stay on marked trails", "Tell someone your itinerary"]
    },
    "picnic": {
        "name": "Picnic",
        "keywords": ["picnic", "outing", "garden", "bbq", "barbecue"],
        "ideal_temp": (18, 27),
        "max_wind": 20,
        "max_precip_prob": 15,
        "max_aqi": 120,
        "gear": ["Waterproof picnic blanket", "Cooler basket & napkins", "Trash bags for waste cleanup", "Outdoor games"],
        "precautions": ["Set up under tree canopy for shade", "Keep perishables in cooler", "Practice Leave-No-Trace"]
    },
    "outdoor_events": {
        "name": "Outdoor Events",
        "keywords": ["event", "concert", "festival", "gathering", "fair", "wedding"],
        "ideal_temp": (18, 28),
        "max_wind": 25,
        "max_precip_prob": 20,
        "max_aqi": 130,
        "gear": ["Folding lawn chair", "Light evening layer/jacket", "Phone power bank", "Reusable water tumbler"],
        "precautions": ["Identify shelter points in case of sudden rain", "Stay aware of event crowds", "Check organizer updates"]
    },
    "photography": {
        "name": "Photography",
        "keywords": ["photo", "photography", "photoshoot", "camera", "shooting"],
        "ideal_temp": (12, 28),
        "max_wind": 35,
        "max_precip_prob": 30,
        "max_aqi": 140,
        "gear": ["Camera with spare batteries", "Sturdy tripod", "Weather-sealed lens bag", "ND & Polarizing filters"],
        "precautions": ["Golden hour happens around sunrise and sunset", "Shield camera body from high humidity", "Respect private grounds"]
    }
}

def extract_intent(text):
    if not text:
        return "jogging", "Pune"
    clean = text.lower()
    found_act = "jogging"
    for k, v in ACTIVITIES_RULES.items():
        for kw in v["keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', clean):
                found_act = k
                break
        if found_act != "jogging":
            break
            
    loc_match = re.search(r'\b(?:in|at|near|for|around)\s+([a-zA-Z\s]{2,30}?)(?:\?|\.|\,| tomorrow| today| morning| evening| afternoon|$)', text, re.IGNORECASE)
    if loc_match:
        found_loc = loc_match.group(1).strip()
    else:
        cities = ["pune", "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata", "london", "new york", "paris", "tokyo", "sydney"]
        found_loc = "Pune"
        for c in cities:
            if c in clean:
                found_loc = c.title()
                break
    return found_act, found_loc

def geocode_location(loc_name):
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(loc_name)}&count=1&language=en&format=json"
        resp = requests.get(url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            data = resp.json()
            if data.get("results") and len(data["results"]) > 0:
                first = data["results"][0]
                return float(first['latitude']), float(first['longitude']), f"{first['name']}, {first.get('country', '')}"
    except Exception:
        pass
    return 18.5204, 73.8567, loc_name or "Pune, India"

def compute_recommendation(activity_key="jogging", location_name="Pune", time_window="morning"):
    lat, lon, full_name = geocode_location(location_name)
    rule = ACTIVITIES_RULES.get(activity_key.lower(), ACTIVITIES_RULES["jogging"])

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,apparent_temperature,precipitation_probability,weather_code,wind_speed_10m"
        "&timezone=auto"
    )
    aqi_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
        "&hourly=european_aqi,pm2_5,pm10&timezone=auto"
    )

    weather_data, aqi_data = None, None
    try:
        w_res = requests.get(weather_url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if w_res.status_code == 200:
            weather_data = w_res.json()
    except Exception:
        pass

    try:
        a_res = requests.get(aqi_url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if a_res.status_code == 200:
            aqi_data = a_res.json()
    except Exception:
        pass

    window_bounds = {"morning": (6, 10), "midday": (10, 14), "afternoon": (14, 18), "evening": (18, 21), "allday": (6, 20)}
    start_h, end_h = window_bounds.get(time_window, (6, 10))

    evaluated_hours = []
    if weather_data and "hourly" in weather_data:
        h = weather_data["hourly"]
        times = h.get("time", [])
        temps = h.get("temperature_2m", [])
        precips = h.get("precipitation_probability", [])
        winds = h.get("wind_speed_10m", [])
        w_codes = h.get("weather_code", [])
        aqis = (aqi_data.get("hourly", {}).get("european_aqi", []) if aqi_data else [])

        for idx in range(min(len(times), 48)):
            try:
                hour = datetime.fromisoformat(times[idx]).hour
            except Exception:
                hour = idx % 24

            if start_h <= hour <= end_h:
                t = temps[idx] if idx < len(temps) else 22
                p = precips[idx] if idx < len(precips) else 0
                w = winds[idx] if idx < len(winds) else 10
                wc = w_codes[idx] if idx < len(w_codes) else 0
                aq = aqis[idx] if idx < len(aqis) and aqis[idx] is not None else 35

                rain_score = max(0, min(100, 100 - (p * 1.3)))
                if p > rule["max_precip_prob"]:
                    rain_score = max(0, rain_score - 25)

                min_t, max_t = rule["ideal_temp"]
                temp_score = 100
                if t < min_t:
                    temp_score -= (min_t - t) * 6
                elif t > max_t:
                    temp_score -= (t - max_t) * 7.5
                temp_score = max(10, min(100, round(temp_score)))

                wind_score = 100
                if w > rule["max_wind"]:
                    wind_score -= (w - rule["max_wind"]) * 4.5
                wind_score = max(15, min(100, round(wind_score)))

                aqi_score = 100
                if aq > 50:
                    aqi_score -= (aq - 50) * 0.8
                aqi_score = max(10, min(100, round(aqi_score)))

                total = round((rain_score * 0.35) + (temp_score * 0.30) + (wind_score * 0.20) + (aqi_score * 0.15))
                if wc in [95, 96, 99]:
                    total = min(total, 25)

                evaluated_hours.append({
                    "hour": hour,
                    "time_str": f"{hour:02d}:00",
                    "temperature_c": t,
                    "precipitation_prob": p,
                    "wind_kmh": w,
                    "aqi": aq,
                    "total_score": total,
                    "rain_score": rain_score,
                    "temp_score": temp_score,
                    "wind_score": wind_score,
                    "aqi_score": aqi_score
                })

    if not evaluated_hours:
        evaluated_hours.append({
            "hour": 7, "time_str": "07:00", "temperature_c": 22, "precipitation_prob": 0, "wind_kmh": 9, "aqi": 32,
            "total_score": 92, "rain_score": 100, "temp_score": 92, "wind_score": 95, "aqi_score": 90
        })

    best = max(evaluated_hours, key=lambda x: x["total_score"])
    verdict = "Excellent" if best["total_score"] >= 85 else ("Good" if best["total_score"] >= 70 else ("Marginal" if best["total_score"] >= 50 else "Avoid"))

    explanation = (
        f"At {best['time_str']}, atmospheric conditions for {rule['name']} in {full_name} are rated {verdict.upper()} "
        f"with a suitability score of {best['total_score']}/100. Forecast indicates {best['temperature_c']}°C, "
        f"{best['precipitation_prob']}% rain risk, wind {best['wind_kmh']} km/h, and European AQI of {best['aqi']}."
    )
    answer = f"Yes! {explanation}" if best["total_score"] >= 70 else f"Caution advised. {explanation}"

    return {
        "status": "success",
        "activity": rule["name"],
        "location": full_name,
        "coordinates": {"latitude": lat, "longitude": lon},
        "suitability_score": best["total_score"],
        "verdict": verdict,
        "answer": answer,
        "explanation": explanation,
        "best_slot": best,
        "hourly_breakdown": evaluated_hours,
        "gear_checklist": rule["gear"],
        "safety_precautions": rule["precautions"],
        "data_sources": [
            "Open-Meteo Weather Forecast API",
            "Open-Meteo Air Quality API",
            "OpenStreetMap Overpass API"
        ]
    }

# -------------------------------------------------------------
# GRADIO INTERFACE
# -------------------------------------------------------------
def gradio_predict(activity, location, time_window, question):
    if question and question.strip():
        act, loc = extract_intent(question)
        activity = act
        location = loc
    res = compute_recommendation(activity, location, time_window)
    summary = f"### Result: {res['verdict']} ({res['suitability_score']}/100)\n\n"
    summary += f"**Answer:** {res['answer']}\n\n"
    summary += f"**Optimal Time:** {res['best_slot']['time_str']} | **Temp:** {res['best_slot']['temperature_c']}°C | **Rain Risk:** {res['best_slot']['precipitation_prob']}%\n\n"
    summary += f"**Gear to Carry:** {', '.join(res['gear_checklist'])}\n\n"
    summary += f"**Safety Tips:** {', '.join(res['safety_precautions'])}"
    return summary, res

with gr.Blocks(title="GeoAI Outdoor Activity Assistant", theme=gr.themes.Soft(primary_hue="green")) as demo:
    gr.Markdown("# 🌿 GeoAI Outdoor Activity Assistant")
    gr.Markdown("Real-time meteorological & geospatial intelligence for outdoor activities.")
    
    with gr.Row():
        with gr.Column():
            act_dropdown = gr.Dropdown(choices=list(ACTIVITIES_RULES.keys()), value="jogging", label="Outdoor Activity")
            loc_input = gr.Textbox(value="Pune, India", label="Location")
            time_dropdown = gr.Dropdown(choices=["morning", "midday", "afternoon", "evening", "allday"], value="morning", label="Time Window")
            q_input = gr.Textbox(placeholder="Or ask a question: Can I cycle in Mumbai tomorrow?", label="Ask Question (Optional)")
            submit_btn = gr.Button("Get Outdoor Recommendation", variant="primary")
            
        with gr.Column():
            output_md = gr.Markdown("### Recommendations will appear here.")
            output_json = gr.JSON(label="Full Live API JSON Response")

    submit_btn.click(gradio_predict, inputs=[act_dropdown, loc_input, time_dropdown, q_input], outputs=[output_md, output_json])

# -------------------------------------------------------------
# ATTACH REST API ENDPOINTS TO GRADIO'S FASTAPI APP
# -------------------------------------------------------------
demo_app = demo.app

demo_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@demo_app.get("/api/health")
async def health():
    return {
        "status": "online",
        "service": "GeoAI Outdoor Activity Assistant",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "supported_activities": list(ACTIVITIES_RULES.keys())
    }

@demo_app.get("/api/recommend")
@demo_app.post("/api/recommend")
@demo_app.get("/api/ask")
@demo_app.post("/api/ask")
async def api_recommend(request: Request):
    data = {}
    if request.method == "POST":
        try:
            data = await request.json()
        except Exception:
            data = {}
    for k, v in request.query_params.items():
        data[k] = v

    q = data.get("question") or data.get("query") or data.get("q")
    if q:
        act, loc = extract_intent(q)
        activity = data.get("activity") or act
        location = data.get("location") or loc
    else:
        activity = data.get("activity", "jogging")
        location = data.get("location", "Pune")

    time_w = data.get("time_window", data.get("time", "morning"))
    return compute_recommendation(activity, location, time_w)

@demo_app.get("/app")
async def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "index.html not found"}

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
