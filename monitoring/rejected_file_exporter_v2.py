from prometheus_client import start_http_server, Gauge, CollectorRegistry
import os
import time

# Define the directories and port to monitor
DIRECTORIES_TO_MONITOR = ['/RAW/mapr/Ericsson','/RAW/mapr/Huawei','/RAW/mapr/Nokia']
PORT = 9201

custom_registry = CollectorRegistry()

# Define a Prometheus Gauge metric using the custom registry
file_count_metric = Gauge('rejected_file_count', 'Number of files in the directory', ['directory'], registry=custom_registry)

def count_files(directory):
    """Counts the number of files in the given directory."""
    try:
        return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])
    except Exception as e:
        print(f"Error counting files in directory {directory}: {e}")
        return 0

def update_metrics():
    """Updates the Prometheus metrics for all directories."""
    for directory in DIRECTORIES_TO_MONITOR:
        file_count = count_files(directory)
        file_count_metric.labels(directory=directory).set(int(file_count))

if __name__ == "__main__":
    start_http_server(PORT, registry=custom_registry)
    print("Node exporter is running on port", PORT, "...")

    while True:
        update_metrics()
        time.sleep(15)  # Scrape interval
