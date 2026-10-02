from flask import Flask, Response
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# Dynamically update the directory as per the current date.
def get_base_directory():
    today = datetime.now()
    year = today.strftime("%Y")
    year_month = today.strftime("%Y%m")
    year_month_day = today.strftime("%Y%m%d")
    return os.path.join("/path/to/directory", year, year_month, year_month_day)

# Directory to monitor
directory =  get_base_directory() 

# Persistent storage for today's cumulative data
persistent_file = "./files_today.json"
# File to store the last reset date
last_reset_file = "./last_reset_date.json"

# Function to load persistent data
def load_persistent_data():
    if os.path.exists(persistent_file):
        with open(persistent_file, "r") as f:
            return json.load(f)
    return {}

# Function to save persistent data
def save_persistent_data(data):
    with open(persistent_file, "w") as f:
        json.dump(data, f, indent=4)

# Function to load last reset date
def load_last_reset_date():
    if os.path.exists(last_reset_file):
        with open(last_reset_file, "r") as f:
            return json.load(f)
    return {}

# Function to save last reset date
def save_last_reset_date(date):
    with open(last_reset_file, "w") as f:
        json.dump(date, f)

# Load cumulative data from persistent store
cumulative_data = load_persistent_data()
last_reset_date = load_last_reset_date()

# Function to calculate metrics
def get_metrics():
    global cumulative_data, last_reset_date

    now = datetime.now()
    five_minutes_ago = now - timedelta(minutes=5)
    midnight = datetime(now.year, now.month, now.day)

    # Reset the metrics if a new day has started
    today_str = now.strftime("%d/%m/%y")
    if last_reset_date.get("date") != now.date().isoformat():
        cumulative_data[today_str] = {
            "files_added_today": 0,
            "size_of_files_today": 0
        }
        save_persistent_data(cumulative_data)
        save_last_reset_date({"date": now.date().isoformat()})

    files_last_5_minutes = 0

    # Track current files in the directory
    current_files = {}

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            file_size = os.path.getsize(file_path)

            # Track files added/modified since midnight
            if mtime > midnight:
                current_files[file_path] = {
                    "mtime": mtime.timestamp(),
                    "size": file_size
                }

                # Update cumulative data for today
                if today_str in cumulative_data:
                    cumulative_data[today_str]["files_added_today"] += 1
                    cumulative_data[today_str]["size_of_files_today"] += file_size

            # Count files added in the last 5 minutes
            if mtime > five_minutes_ago:
                files_last_5_minutes += 1

    # Save the updated state to the persistent file
    save_persistent_data(cumulative_data)

    # Return metrics as Prometheus-compatible text
    metrics = f"""
# HELP files_added_last_5_minutes Number of files added in the last 5 minutes.
files_added_last_5_minutes {files_last_5_minutes}

# HELP files_added_today Cumulative number of files added today.
files_added_today {cumulative_data[today_str]["files_added_today"]}

# HELP size_of_files_today Cumulative size of files added today in bytes.
size_of_files_today {cumulative_data[today_str]["size_of_files_today"]}
"""
    return metrics

# Define HTTP endpoint for Prometheus
@app.route("/metrics")
def metrics():
    return Response(get_metrics(), mimetype="text/plain")

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=<<PORT>>)