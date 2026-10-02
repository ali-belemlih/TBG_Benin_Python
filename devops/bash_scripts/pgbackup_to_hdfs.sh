#!/bin/bash

# Configuration variables
PG_HOST="localhost"
PG_PORT="5432"
PG_USER="postgres"
PG_PASSWORD="your_password" # Set this securely, e.g., use a .pgpass file
HDFS_BACKUP_DIR="/path/to/hdfs/backup/directory"
LOG_DIR="/var/log/postgres_backup"
LOG_FILE="$LOG_DIR/backup_$(date +%Y%m%d%H%M%S).log"

# Export PostgreSQL password to avoid interactive prompts
export PGPASSWORD=$PG_PASSWORD

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
}

# Error handling function
handle_error() {
    log "ERROR: $1"
    exit 1
}

# List all databases except template0 and template1
log "Listing databases..."
DATABASES=$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;")
if [[ $? -ne 0 ]]; then
    handle_error "Failed to list databases."
fi

log "Databases found: $DATABASES"

# Loop through each database and back it up directly to HDFS
for DB in $DATABASES; do
    HDFS_FILE="$HDFS_BACKUP_DIR/${DB}_$(date +%Y%m%d%H%M%S).sql.gz"
    log "Backing up database: $DB to HDFS file: $HDFS_FILE..."

    # Run pg_dump and pipe output directly to gzip and HDFS
    pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB" | gzip | hdfs dfs -put - "$HDFS_FILE"
    if [[ $? -ne 0 ]]; then
        handle_error "Failed to backup database: $DB to HDFS."
    fi

    log "Backup for database $DB completed successfully."
done

log "All database backups completed successfully!"
