#!/bin/bash

# Get the hostname of the system
hostname=$(hostname)

# Define the output file
output_file="${hostname}_mapr_conf.txt"

# Redirect both stdout and stderr to the output file
exec > "$output_file" 2>&1

# Write initial information to the output file
echo "System Configuration for: $hostname"
echo "=========================="
echo "=========================="
echo "Generated on: $(date)"
echo ""

# Get MapR version
echo "MapR Build Version:"
cat /opt/mapr/MapRBuildVersion
echo ""
echo "=========================="

# Get MapR FS list
echo "MapR FS info:"
hadoop fs -ls
echo ""
echo "=========================="

# Get MapR FS root list
echo "MapR root FS:"
hadoop fs -ls /
echo ""
echo "=========================="

# Get MapR FS space
echo "MapR FS space:"
hadoop fs -df -h
echo ""
echo "=========================="

# Get MapR disk usage
echo "MapR disk usage:"
hadoop fs -du -h /
echo ""
echo "=========================="

# Get List of MapR packages
echo "List of MapR installed packages:"
yum list installed | grep mapr
echo ""
echo "=========================="

# Get user ID
echo "MapR user details:"
id
echo ""
echo "=========================="

# Get MapR cluster service layout
echo "MapR node service layout:"
maprcli node list -columns svc
echo ""
echo "=========================="

exec > /dev/tty 2>&1
# Confirm completion
echo "MapR configuration details have been saved to $output_file."
