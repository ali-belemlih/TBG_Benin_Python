#!/bin/bash

LOCKFILE="/tmp/move_Ericsson_to_maprfs.lock"

if [ -f "$LOCKFILE" ]; then
    echo "Script is already running"
    exit 1
fi

# Create Lock File
touch "$LOCKFILE"

LOCAL_DIR="/root/Ericsson"
MAPR_FS_DIR="/user/root/Ericsson"
LOG_DIR="/var/log"
DATE_TIME=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${LOG_DIR}/transfer_$(basename $LOCAL_DIR)_${DATE_TIME}.log"

command -v hadoop &>/dev/null || {
    echo "Error: Hadoop command not found."
    exit 1
}
command -v logger &>/dev/null && SYSLOG=1 || SYSLOG=0

log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >>"$LOG_FILE"
    [ "$SYSLOG" -eq 1 ] && logger "$message"
}

error_exit() {
    log_message "Error: $1. Exiting."
    exit 1
}

[ ! -d "$LOCAL_DIR" ] && error_exit "Local directory $LOCAL_DIR does not exist"
hadoop fs -test -d "$MAPR_FS_DIR" || error_exit "Target MapR-FS directory $MAPR_FS_DIR does not exist"

log_message "Starting data transfer from $LOCAL_DIR to $MAPR_FS_DIR..."

for file in "$LOCAL_DIR"/*; do
    [ -e "$file" ] || continue # will skip if no files found

    # log_message "Transferring file: $file"
    hadoop fs -put "$file" "$MAPR_FS_DIR"
    if [ $? -eq 0 ]; then
        log_message "File $file successfully transferred. Deleting local file..."
        rm -f "$file"
        if [ $? -eq 0 ]; then
            log_message "File $file successfully deleted from local filesystem."
        else
            log_message "Warning: Unable to delete file $file from local filesystem."
        fi
    else
        log_message "Error: Failed to transfer file $file to MapR-FS."
    fi
done

log_message "Data transfer completed."

# Remove the lock file
rm -rf "$LOCKFILE"

exit 0
