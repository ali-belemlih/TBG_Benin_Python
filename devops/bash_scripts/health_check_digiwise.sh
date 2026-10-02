#!/bin/bash

# Initialize success flags
disk_ok=true
memory_ok=true

# Check disk usage
echo "Checking disk usage..."
df -h | awk 'NR==1 || $5+0 > 75 {print $0}' | while read line; do
  if [[ $line == Filesystem* ]]; then
    continue
  fi
  mount_point=$(echo "$line" | awk '{print $NF}')
  echo "WARNING: High disk usage on mount point: $mount_point"
  disk_ok=false
done

# Check memory usage
echo "Checking memory usage..."
memory_info=$(free -h)
echo "$memory_info"

available_mem=$(free -g | awk '/^Mem:/ {print $7}')

# Convert the threshold to MB (10 GB = 10240 MB)
threshold_mb=15

if [[ $available_mem -lt $threshold_mb ]]; then
  echo "ALERT: Low available memory! Only $available_mem GB available."
  memory_ok=false
else
  echo "Available memory is sufficient ($available_mem GB)."
fi
