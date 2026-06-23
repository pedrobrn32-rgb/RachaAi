import logging
import base64
import json
import os
from flask import Flask, request
from google.cloud import run_v2

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.get("/")
def health():
    return "shutdown service alive", 200

@app.post("/")
def kill_service():
    try:
        # Get pubsub message
        envelope = request.get_json()
        if not envelope or "message" not in envelope:
            return "bad request", 400

        # Decode base64 payload
        payload_str = base64.b64decode(envelope["message"]["data"]).decode("utf-8")
        alert_data = json.loads(payload_str)

        # Check if budget is 1 percent or more
        if alert_data.get("alertThresholdExceeded", 0) < 0.55:
            logging.info("BUDGET UNDER 1 PERCENT IGNORING")
            return "ignored", 200

        client = run_v2.ServicesClient()

        service_name = (
            "projects/rachaai-01/"
            "locations/southamerica-east1/"
            "services/rachaai-app"
        )

        # Delete the service completely
        operation = client.delete_service(name=service_name)
        operation.result()

        logging.info("APP DELETED COMPLETELY")

        return {"status": "killed"}, 200

    except Exception as e:
        logging.exception(e)
        return {"error": str(e)}, 500

# Start server on 0.0.0.0 and dynamically assign the PORT variable
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)