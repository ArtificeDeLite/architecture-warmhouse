from flask import Flask, request, jsonify, Response
from datetime import datetime, timezone
import random

app = Flask(__name__)

SENSORS = {
    "1": {"location": "Living Room", "base_temp": 22.0},
    "2": {"location": "Bedroom",     "base_temp": 20.0},
    "3": {"location": "Kitchen",     "base_temp": 24.0},
}

LOCATIONS = {info["location"]: sid for sid, info in SENSORS.items()}

DEFAULT_BASE_TEMP = 18.0
DEFAULT_SENSOR_ID = "0"

def _build_model(sensor_id: str, location: str, base_temp: float) -> dict:
    return {
        "location": location,
        "value": round(random.uniform(base_temp - 3, base_temp + 3), 1),
        "unit": "celsius",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "sensor_id": sensor_id,
        "sensor_type": "temperature",
    }

def model_by_sensor_id(sensor_id: str) -> dict:
    sensor = SENSORS.get(sensor_id)
    if sensor is not None:
        return _build_model(sensor_id, sensor["location"], sensor["base_temp"])
    return _build_model(sensor_id, "Unknown", DEFAULT_BASE_TEMP)


def model_by_location(location: str) -> dict:
    sensor_id = LOCATIONS.get(location)
    if sensor_id is not None:
        return _build_model(sensor_id, location, SENSORS[sensor_id]["base_temp"])
    return _build_model(DEFAULT_SENSOR_ID, location, DEFAULT_BASE_TEMP)

@app.route("/temperature")
def get_temperature() -> tuple[Response, int]:
    location = request.args.get("location", type=str, default="")

    if not location:
        return jsonify({"error": "Parameter 'location' is required"}), 400

    model = model_by_location(location)
    return jsonify(model), 200


@app.get("/temperature/<int:sensor_id>")
def get_temperature_by_id(sensor_id: str) -> tuple[Response, int]:
    model = model_by_sensor_id(str(sensor_id))
    return jsonify(model), 200


@app.route("/health")
def health() -> tuple[Response, int]:
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)