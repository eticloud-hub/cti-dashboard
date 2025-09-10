from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

app = Flask(__name__)

# Mock historical threat log for chart
THREAT_LOG = [
    {"date": "2025-08-15", "count": 3},
    {"date": "2025-08-16", "count": 5},
    {"date": "2025-08-17", "count": 2},
    {"date": "2025-08-18", "count": 8},
    {"date": "2025-08-19", "count": 6},
]

def lookup_ip(ip):
    """Check IP reputation using AbuseIPDB"""
    url = "https://api.abuseipdb.com/api/v2/check"
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }
    headers = {
        "Accept": "application/json",
        "Key": ABUSEIPDB_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "data" in data:
            score = data["data"]["abuseConfidenceScore"]
            country = data["data"].get("countryCode", "Unknown")
            total_reports = data["data"]["totalReports"]
            return f"IP: {ip} | Confidence Score: {score} | Country: {country} | Reports: {total_reports}"
        else:
            return f"No data found for {ip}."
    except Exception as e:
        return f"Error looking up IP {ip}: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def dashboard():
    ip_result = None

    if request.method == "POST":
        ip = request.form.get("ip")
        ip_result = lookup_ip(ip)

    # Prepare chart data
    dates = [row["date"] for row in THREAT_LOG]
    counts = [row["count"] for row in THREAT_LOG]

    return render_template(
        "dashboard.html",
        dates=dates,
        counts=counts,
        ip_result=ip_result
    )

if __name__ == "__main__":
    app.run(debug=True)
