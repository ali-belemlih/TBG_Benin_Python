#!/bin/bash

# Get the hostname of the system
hostname=$(hostname)

# Define the output file
output_file="${hostname}_system_config.txt"

# Write initial information to the output file
echo "System Configuration for: $hostname" > "$output_file"
echo "==========================" >> "$output_file"
echo "==========================" >> "$output_file"
echo "Generated on: $(date)" >> "$output_file"
echo "" >> "$output_file"

# Get OS type and version
echo "Operating System:" >> "$output_file"
cat /etc/os-release >> "$output_file" 2>/dev/null || uname -a >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# Get Memory Information
echo "Memory Information:" >> "$output_file"
# Total and available memory
total_mem=$(awk '/MemTotal/ {print $2/1024/1024 " GB"}' /proc/meminfo)
available_mem=$(awk '/MemAvailable/ {print $2/1024/1024 " GB"}' /proc/meminfo)
echo "Total Memory: $total_mem" >> "$output_file"
echo "Available Memory: $available_mem" >> "$output_file"

# Buffer/Cache memory in GB
buffer_cache_mem=$(awk '/^Buffers/ {buffers=$2} /^Cached/ {cached=$2} END {print (buffers+cached)/1024/1024 " GB"}' /proc/meminfo)
echo "Buffer/Cache Memory: $buffer_cache_mem" >> "$output_file"

# Swap memory in GB
total_swap=$(awk '/SwapTotal/ {print $2/1024/1024 " GB"}' /proc/meminfo)
free_swap=$(awk '/SwapFree/ {print $2/1024/1024 " GB"}' /proc/meminfo)
echo "Total Swap: $total_swap" >> "$output_file"
echo "Free Swap: $free_swap" >> "$output_file"

echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# Get CPU Information
echo "CPU Information:" >> "$output_file"
lscpu >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# Get Storage Information
echo "Storage Information:" >> "$output_file"
echo "Attached Disks:" >> "$output_file"
lsblk >> "$output_file"
echo "" >> "$output_file"
echo "Mounted Filesystems and Usage:" >> "$output_file"
df -h >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# Get Network Information
echo "Network Configuration:" >> "$output_file"
echo "IP Address:" >> "$output_file"
ip -br addr show >> "$output_file"
echo "" >> "$output_file"
echo "NICs Available:" >> "$output_file"
nmcli device status >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# Get Port Information
echo "Port Information:" >> "$output_file"
netstat -tulnp >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# List Running Services
echo "Running Services:" >> "$output_file"
systemctl list-units --type=service --state=running >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# ID of the user
echo "ID of MapR User:" >> "$output_file"
id >> "$output_file"
echo "" >> "$output_file"
echo "Users available:" >> "$output_file"
cat /etc/passwd >> "$output_file"
echo "" >> "$output_file"
echo "==========================" >> "$output_file"

# Confirm completion
echo "System configuration details have been saved to $output_file."
