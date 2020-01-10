#!/bin/bash

# Copy files to destination with SFTP

# Default path at destnation (can be set with positional argument 2)
DST_PATH="/tmp/"

# Current location compared to script location if symbolic link
SYM_DIR=$(dirname "$(readlink -f "$0")")

# Current location compared to script location
NO_SYM_DIR="$(dirname $0)"

# SFTP batch file with commands
SFTP_BATCH_FILE="sftp_deploy_files"

# Check for destination host
if [ "${1}" == "" ]; then
    echo "Error: user@host missing!"
    exit 1
fi
USER_HOST=${1}

# Check for destination path
if [ "${2}" != "" ]; then
    DST_PATH=${2}
fi

echo "sftp -b ${SFTP_BATCH_FILE} ${USER_HOST}:${DST_PATH}"
cd "${SYM_DIR}" || return
sftp -b ${SFTP_BATCH_FILE} "${USER_HOST}:${DST_PATH}"
cd "${NO_SYM_DIR}" || return
