#!/bin/bash

###
#  BEGIN CUSTOMIZATIONS
###

# Uncomment to turn on debugging
DEBUG=1

# Uncomment to enable test mode (show what would be run)
#TEST=1


###
# Set Docker Image Parts

# (don't need docker image tag, it will be queried at runtime)
DK_USER=andylytical
DK_IMAGE=brewpi-backup


###
# Set volume mounts

# Associative array; key=src, val=tgt
declare -A MOUNTPOINTS=( ["$HOME"]="$HOME" )


###
# Set Environment Variable(s) for Container
declare -A ENVIRON

# Google OAuth secret and credentials
ENVIRON['GOOGLE_AUTH_CLIENT_SECRETS_FILE']="$HOME/.googleauth/client_secrets.json"
ENVIRON['GOOGLE_AUTH_CREDENTIALS_FILE']="$HOME/.googleauth/credentials.json"

# Parent folder of the spreadsheets
# Existing spreadsheets must reside in this folder
# New spreadsheets will be created in this folder
ENVIRON['GOOGLE_DRIVE_FOLDER_ID']='1d57i-VAQRbCfLDIb9JCHGI3GPBK8cZ4O'

# If an existing spreadsheet is not found, create a copy of one using this template
ENVIRON['GOOGLE_SHEETS_TEMPLATE_ID']='1U0B7wu07bCH5X6Yfc3FQWgNEwMpoNCg8eDPtjlH0j6w'

# Name of the google spreadsheet to load data into
# Can be just a prefix, must be enough to uniquely identify the spreadsheet
# TODO - pass this on cmdline
ENVIRON['GOOGLE_SHEETS_NAME_PREFIX']='20180714'

# Inside the spreadsheet, which sheet to populate with data
ENVIRON['GOOGLE_SHEETS_SHEET_NAME']='RIMS Data'

# Which column (in the goole sheet) has the timestamp
#ENVIRON['GOOGLE_SHEETS_TSDB_PRIMARY_COLUMN']='A'

# Keep matching cols, ignore all others
#ENVIRON['BREWLOG_COLS_REGEX']='.'

# 1=keep empty cols, 0=filter empty cols
#ENVIRON['BREWLOG_KEEP_EMPTY_COLS']=1


###
#  END OF CUSTOMIZATIONS
###

die() {
    echo "ERR: $*"
    exit 99
}

latest_docker_tag() {
    # Based on code from:
    # https://stackoverflow.com/questions/28320134/how-to-list-all-tags-for-a-docker-image-on-a-remote-registry
    [[ $DEBUG -eq 1 ]] && set -x
    [[ $# -ne 1 ]] && die "latest_docker_tag: must have exactly 1 parameter, got '$#'"
    image="$1"
    wget -q https://registry.hub.docker.com/v1/repositories/${image}/tags -O - \
    | sed -e 's/[][]//g' \
          -e 's/"//g' \
          -e 's/ //g' \
    | tr '}' '\n' \
    | awk -F: '{print $3}' \
    | sort -r \
    | head -1
}

[[ $DEBUG -eq 1 ]] && set -x

action=
[[ $TEST -eq 1 ]] && action=echo

DK_TAG=$( latest_docker_tag "$DK_USER/$DK_IMAGE" )
[[ -z "$DK_TAG" ]] && die "No tags found for docker image: '$DK_USER/$DK_IMAGE'"
IMAGE="$DK_USER/$DK_IMAGE:$DK_TAG"

envs=()
for k in "${!ENVIRON[@]}"; do
    envs+=( '-e' "$k=${ENVIRON[$k]}" )
done

mounts=()
for src in "${!MOUNTPOINTS[@]}"; do
    dst="${MOUNTPOINTS[$src]}"
    mounts+=( '--mount' "type=bind,src=$src,dst=$dst" )
done

$action docker run \
    "${envs[@]}" \
    "${mounts[@]}" \
    --rm -it "$IMAGE"
