#!/bin/bash

# Get the hostname of the system
hostname=$(hostname)

# Define the output file
output_file="${hostname}_system_config.txt"

# Redirect both stdout and stderr to the output file
exec > "$output_file" 2>&1

# Write initial information to the output file
echo "System Configuration for: $hostname"
echo "=========================="
echo "=========================="
echo "Generated on: $(date)"
echo ""

# Get OS type and version
echo "Operating System:"
cat /etc/os-release 2>/dev/null || uname -a
echo ""
echo "=========================="

# Get Memory Information
echo "Memory Information:"
# Total and available memory
total_mem=$(awk '/MemTotal/ {print $2/1024/1024 " GB"}' /proc/meminfo)
available_mem=$(awk '/MemAvailable/ {print $2/1024/1024 " GB"}' /proc/meminfo)
echo "Total Memory: $total_mem"
echo "Available Memory: $available_mem"

# Buffer/Cache memory in GB
buffer_cache_mem=$(awk '/^Buffers/ {buffers=$2} /^Cached/ {cached=$2} END {print (buffers+cached)/1024/1024 " GB"}' /proc/meminfo)
echo "Buffer/Cache Memory: $buffer_cache_mem"

# Swap memory in GB
total_swap=$(awk '/SwapTotal/ {print $2/1024/1024 " GB"}' /proc/meminfo)
free_swap=$(awk '/SwapFree/ {print $2/1024/1024 " GB"}' /proc/meminfo)
echo "Total Swap: $total_swap"
echo "Free Swap: $free_swap"

echo ""
echo "=========================="

# Get CPU Information
echo "CPU Information:"
lscpu
echo ""
echo "=========================="

# Get Storage Information
echo "Storage Information:"
echo "Attached Disks:"
lsblk
echo ""
echo "Mounted Filesystems and Usage:"
df -h
echo ""
echo "=========================="

# Get Network Information
echo "Network Configuration:"
echo "IP Address:"
ip -br addr show
echo ""
echo "NICs Available:"
nmcli device status
echo ""
echo "=========================="

# Get Port Information
echo "Port Information:"
netstat -tulnp
echo ""
echo "=========================="

# List Running Services
echo "Running Services:"
systemctl list-units --type=service --state=running
echo ""
echo "=========================="

# ID of the user
echo "ID of User:"
id
echo ""
echo "Users available:"
cat /etc/passwd
echo ""
echo "=========================="

# Installed MapR packages
echo "MapR Installed packages and version:"
yum list installed | grep mapr
echo ""
echo "=========================="

# Crontab
echo "Crontab:"
crontab -l
echo ""

exec > /dev/tty 2>&1
# Confirm completion
echo "System configuration details have been saved to $output_file."
