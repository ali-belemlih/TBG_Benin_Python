#!/bin/bash

# File exporter services
EXPORTER_SERVICES=(file_exporter2 file_exporter)
LOG_FILE="/home/mapr/monitoring/scripts/logs/data-reset.log"
DATA_DIR="/home/mapr/monitoring"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "===== Data Reset Script Started at $TIMESTAMP =====" >> "$LOG_FILE"

# Stop all running file exporter services
systemctl --user stop "${EXPORTER_SERVICES[@]}" && \
echo "Stopped file exporter services: ${EXPORTER_SERVICES[*]}" >> "$LOG_FILE" || \
echo "Failed to stop some file exporter services" >> "$LOG_FILE"


# Remove older data files
echo "Removing old data files..." >> "$LOG_FILE"
if rm -rf /home/mapr/monitoring/file_*/*.json; then
    echo "Old data files removed successfully" >> "$LOG_FILE"
else
    echo "Failed to remove old data files" >> "$LOG_FILE"
fi

sleep 5

# Restart all stopped file exporter services
systemctl --user start "${EXPORTER_SERVICES[@]}" && \
echo "Restarted file exporter services: ${EXPORTER_SERVICES[*]}" >> "$LOG_FILE" || \
echo "Failed to restart some file exporter services" >> "$LOG_FILE"

echo "===== Data Reset Script Ended at $(date "+%Y-%m-%d %H:%M:%S") =====" >> "$LOG_FILE"
