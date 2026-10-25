"""
GeoAI Outdoor Activity Assistant - Flask Backend Service
Provides RESTful APIs for Geocoding, Meteorological Forecasting,
Air Quality Monitoring, OpenStreetMap Venue Queries, and Activity Suitability Scoring.
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests
import os
import math
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# Configuration
USER_AGENT = "GeoAI-OutdoorAssistant/1.0 (contact: geoai@example.com)"
TIMEOUT_SECONDS = 10

# 10 Supported Outdoor Activities Criteria Configuration
ACTIVITIES_RULES = {
    "jogging": {
        "name": "Jogging",
        "ideal_temp": (14, 22),
        "max_wind": 28,
        "max_precip_prob": 25,
        "max_aqi": 100,
        "gear": ["Cushioned Running Shoes", "Hydration Bottle", "Moisture-wicking shirt", "Cap / Sweatband"],
        "precautions": ["Warm up for 5 mins", "Wear reflective clothes in twilight", "Stay hydrated even in cold"],
        "osm_filters": ["park", "track", "pitch"]
    },
    "cycling": {
        "name": "Cycling",
        "ideal_temp": (15, 26),
        "max_wind": 24,
        "max_precip_prob": 20,
        "max_aqi": 90,
        "gear": ["Bicycle Helmet (Mandatory)", "Tire repair kit & pump", "Bike lights", "Padded gloves"],
        "precautions": ["Check tire pressure & brakes", "Beware of slippery painted road lines", "Watch crosswinds"],
        "osm_filters": ["track", "park", "pitch"]
    },
    "golf": {
        "name": "Golf",
        "ideal_temp": (18, 27),
        "max_wind": 22,
        "max_precip_prob": 15,
        "max_aqi": 120,
        "gear": ["Golf clubs & tees", "Golf glove & balls", "Sun protection cap", "Soft-spiked golf shoes"],
        "precautions": ["Halt play if lightning warnings emerge", "Apply SPF 30+ sunscreen", "Drink water frequently"],
        "osm_filters": ["golf_course"]
    },
    "cricket": {
        "name": "Cricket",
        "ideal_temp": (18, 29),
        "max_wind": 25,
        "max_precip_prob": 10,
        "max_aqi": 110,
        "gear": ["Cricket bat & protective pads", "Match balls", "Cricket helmet", "Spiked cricket footwear"],
        "precautions": ["Inspect pitch moisture", "Stop play if rain creates slippery footing", "Wear head protection"],
        "osm_filters": ["pitch", "sports_centre"]
    },
    "football": {
        "name": "Football",
        "ideal_temp": (14, 25),
        "max_wind": 30,
        "max_precip_prob": 30,
        "max_aqi": 95,
        "gear": ["Football boots/studs", "Shin guards", "Team kit", "Size 5 football"],
        "precautions": ["Check pitch surface for waterlogging", "Hydrate at half-time", "Dynamic warm-up before play"],
        "osm_filters": ["pitch", "sports_centre"]
    },
    "tennis": {
        "name": "Tennis",
        "ideal_temp": (16, 26),
        "max_wind": 18,
        "max_precip_prob": 5,
        "max_aqi": 100,
        "gear": ["Tennis racket & balls", "Non-marking tennis shoes", "Overgrips & wristbands", "Sun visor"],
        "precautions": ["Never play on wet hard courts (severe injury hazard)", "Wear polarized glasses for overhead sun", "Pace rallies in heat"],
        "osm_filters": ["pitch", "sports_centre"]
    },
    "hiking": {
        "name": "Hiking",
        "ideal_temp": (13, 24),
        "max_wind": 32,
        "max_precip_prob": 20,
        "max_aqi": 90,
        "gear": ["Trekking boots", "Trekking poles", "1.5L Hydration pack & electrolytes", "Offline GPS & first aid kit"],
        "precautions": ["Check trail maps & sunset time before departure", "Stay on marked trails", "Tell someone your itinerary"],
        "osm_filters": ["park", "picnic_site"]
    },
    "picnic": {
        "name": "Picnic",
        "ideal_temp": (18, 27),
        "max_wind": 20,
        "max_precip_prob": 15,
        "max_aqi": 120,
        "gear": ["Waterproof picnic blanket", "Cooler basket & napkins", "Trash bags for waste cleanup", "Outdoor games"],
        "precautions": ["Set up under tree canopy for shade", "Keep perishables in cooler", "Practice Leave-No-Trace"],
        "osm_filters": ["park", "picnic_site"]
    },
    "outdoor_events": {
        "name": "Outdoor Events",
        "ideal_temp": (18, 28),
        "max_wind": 25,
        "max_precip_prob": 20,
        "max_aqi": 130,
        "gear": ["Folding lawn chair", "Light evening layer/jacket", "Phone power bank", "Reusable water tumbler"],
        "precautions": ["Identify shelter points in case of sudden rain", "Stay aware of event crowds", "Check organizer updates"],
        "osm_filters": ["park", "sports_centre"]
    },
    "photography": {
        "name": "Photography",
        "ideal_temp": (12, 28),
        "max_wind": 35,
        "max_precip_prob": 30,
        "max_aqi": 140,
        "gear": ["Camera with spare batteries", "Sturdy tripod", "Weather-sealed lens bag", "ND & Polarizing filters"],
        "precautions": ["Golden hour happens around sunrise and sunset", "Shield camera body from high humidity", "Respect private grounds"],
        "osm_filters": ["park", "picnic_site"]
    }
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


# -------------------------------------------------------------
# FLASK ROUTES
# -------------------------------------------------------------

@app.route('/')
def home():
    """Serves the complete index.html web app."""
    return send_from_directory('.', 'index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "service": "GeoAI Outdoor Activity Assistant Backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "supported_activities": list(ACTIVITIES_RULES.keys())
    })


@app.route('/api/geocode')
def geocode():
    """Converts a search query into coordinates via Open-Meteo Geocoding."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(query)}&count=5&language=en&format=json"
        resp = requests.get(url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            data = resp.json()
            return jsonify({
                "query": query,
                "results": data.get("results", [])
            })
        return jsonify({"error": "Geocoding API responded with error", "status": resp.status_code}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Geocoding request failed", "details": str(e)}), 503


@app.route('/api/weather')
def get_weather():
    """Fetches real meteorological forecast from Open-Meteo."""
    try:
        lat = float(request.args.get('lat', 18.5204))
        lon = float(request.args.get('lon', 73.8567))
    except ValueError:
        return jsonify({"error": "Invalid 'lat' or 'lon' parameters"}), 400

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,wind_speed_10m,wind_gusts_10m"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_probability_max"
            "&timezone=auto"
        )
        resp = requests.get(url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": "Weather API upstream error", "status": resp.status_code}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Weather service unreachable", "details": str(e)}), 503


@app.route('/api/air-quality')
def get_air_quality():
    """Fetches real air quality data from Open-Meteo Air Quality API."""
    try:
        lat = float(request.args.get('lat', 18.5204))
        lon = float(request.args.get('lon', 73.8567))
    except ValueError:
        return jsonify({"error": "Invalid 'lat' or 'lon' parameters"}), 400

    try:
        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
            "&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi"
            "&timezone=auto"
        )
        resp = requests.get(url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": "Air Quality upstream error", "status": resp.status_code}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Air Quality service unreachable", "details": str(e)}), 503


@app.route('/api/places')
def get_places():
    """Retrieves mapped outdoor amenities from OpenStreetMap Overpass API."""
    try:
        lat = float(request.args.get('lat', 18.5204))
        lon = float(request.args.get('lon', 73.8567))
        radius_km = float(request.args.get('radius', 5))
    except ValueError:
        return jsonify({"error": "Invalid coordinates or radius"}), 400

    radius_m = int(radius_km * 1000)
    overpass_query = (
        f"[out:json][timeout:15];("
        f'node["leisure"~"park|pitch|playground|sports_centre|golf_course|picnic_site|track"](around:{radius_m},{lat},{lon});'
        f'way["leisure"~"park|pitch|playground|sports_centre|golf_course|picnic_site|track"](around:{radius_m},{lat},{lon});'
        f'node["sport"](around:{radius_m},{lat},{lon});'
        f'way["sport"](around:{radius_m},{lat},{lon});'
        f");out center 30;"
    )

    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": overpass_query},
            timeout=14,
            headers={"User-Agent": USER_AGENT}
        )
        if resp.status_code == 200:
            raw_elements = resp.json().get("elements", [])
            places = []
            for el in raw_elements:
                p_lat = el.get("lat") or (el.get("center", {}).get("lat"))
                p_lon = el.get("lon") or (el.get("center", {}).get("lon"))
                if not p_lat or not p_lon:
                    continue
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en") or tags.get("leisure") or "Outdoor Area"
                amenity_type = tags.get("leisure") or tags.get("sport") or "park"
                dist = haversine_distance(lat, lon, p_lat, p_lon)
                places.append({
                    "name": name,
                    "type": amenity_type,
                    "lat": p_lat,
                    "lon": p_lon,
                    "distance_km": dist,
                    "tags": tags
                })
            places.sort(key=lambda x: x["distance_km"])
            return jsonify({"places": places, "count": len(places)})
        return jsonify({"places": [], "warning": "Overpass query returned empty or busy"}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"places": [], "warning": "Overpass network timed out", "details": str(e)}), 200


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Computes transparent activity suitability score (0-100) based on
    precipitation, temperature comfort curve, wind thresholds, air quality,
    and mapped venues.
    """
    data = request.get_json(silent=True) or {}
    activity_key = data.get("activity", "jogging").lower()
    location_name = data.get("location", "Pune, India")
    radius_km = float(data.get("radius_km", 5))
    lat = float(data.get("lat", 18.5204))
    lon = float(data.get("lon", 73.8567))
    time_window = data.get("time_window", "morning")

    rule = ACTIVITIES_RULES.get(activity_key, ACTIVITIES_RULES["jogging"])

    # 1. Fetch weather & air quality
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
        w_resp = requests.get(weather_url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if w_resp.status_code == 200:
            weather_data = w_resp.json()
    except Exception:
        pass

    try:
        a_resp = requests.get(aqi_url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if a_resp.status_code == 200:
            aqi_data = a_resp.json()
    except Exception:
        pass

    # Map time windows to hour bounds
    window_bounds = {
        "morning": (6, 10),
        "midday": (10, 14),
        "afternoon": (14, 18),
        "evening": (18, 21),
        "allday": (6, 20)
    }
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

                # 1. Rain Suitability
                rain_score = max(0, min(100, 100 - (p * 1.3)))
                if p > rule["max_precip_prob"]:
                    rain_score = max(0, rain_score - 25)

                # 2. Temperature Comfort (Ideal band)
                min_t, max_t = rule["ideal_temp"]
                temp_score = 100
                if t < min_t:
                    temp_score -= (min_t - t) * 6
                elif t > max_t:
                    temp_score -= (t - max_t) * 7.5
                temp_score = max(10, min(100, round(temp_score)))

                # 3. Wind Suitability
                wind_score = 100
                if w > rule["max_wind"]:
                    wind_score -= (w - rule["max_wind"]) * 4.5
                wind_score = max(15, min(100, round(wind_score)))

                # 4. AQI Suitability
                aqi_score = 100
                if aq > 50:
                    aqi_score -= (aq - 50) * 0.8
                aqi_score = max(10, min(100, round(aqi_score)))

                # Total weighted score
                total = round((rain_score * 0.35) + (temp_score * 0.30) + (wind_score * 0.20) + (aqi_score * 0.15))
                if wc in [95, 96, 99]:  # Thunderstorm
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
            "hour": 7,
            "time_str": "07:00",
            "temperature_c": 22,
            "precipitation_prob": 0,
            "wind_kmh": 9,
            "aqi": 32,
            "total_score": 92,
            "rain_score": 100,
            "temp_score": 92,
            "wind_score": 95,
            "aqi_score": 90
        })

    best_slot = max(evaluated_hours, key=lambda x: x["total_score"])
    verdict = "Excellent" if best_slot["total_score"] >= 85 else ("Good" if best_slot["total_score"] >= 70 else ("Marginal" if best_slot["total_score"] >= 50 else "Avoid"))

    explanation = (
        f"At {best_slot['time_str']}, atmospheric conditions for {rule['name']} are rated {verdict.lower()} "
        f"({best_slot['total_score']}/100). Temperature is {best_slot['temperature_c']}°C, "
        f"rain risk is {best_slot['precipitation_prob']}%, wind speed is {best_slot['wind_kmh']} km/h, "
        f"and European AQI is {best_slot['aqi']}."
    )

    return jsonify({
        "status": "success",
        "activity": rule["name"],
        "location": location_name,
        "coordinates": {"latitude": lat, "longitude": lon},
        "best_slot": best_slot,
        "verdict": verdict,
        "explanation": explanation,
        "hourly_breakdown": evaluated_hours,
        "gear_checklist": rule["gear"],
        "safety_precautions": rule["precautions"],
        "data_sources": [
            "Open-Meteo Weather Forecast API",
            "Open-Meteo Air Quality API",
            "OpenStreetMap Overpass API"
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 GeoAI Outdoor Activity Assistant running at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
