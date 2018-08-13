#!/bin/bash

###
#  BEGIN CUSTOMIZATIONS
###

### Set Docker Image Parts

# (don't need docker image tag, it will be queried at runtime)
DK_USER=andylytical
DK_IMAGE=brewpi-backup


### Set volume mounts

# Associative array; key=src, val=tgt
declare -A MOUNTPOINTS=( ["$HOME"]="$HOME" )


### Set Environment Variable(s) for Container
declare -A ENVIRON

# Google OAuth secret and credentials
ENVIRON['GOOGLE_AUTH_CLIENT_SECRETS_FILE']="$HOME/.googleauth/client_secrets.json"
ENVIRON['GOOGLE_AUTH_CREDENTIALS_FILE']="$HOME/.googleauth/credentials.json"

# Parent folder of the spreadsheets
# Existing spreadsheets must reside in this folder
# New spreadsheets will be created in this folder
ENVIRON['GOOGLE_DRIVE_FOLDER_ID']='1d57i-VAQRbCfLDIb9JCHGI3GPBK8cZ4O'

# If an existing spreadsheet is not found, create one from this template
# This template id is public and can be viewed at:
# https://docs.google.com/spreadsheets/d/1U0B7wu07bCH5X6Yfc3FQWgNEwMpoNCg8eDPtjlH0j6w
ENVIRON['GOOGLE_SHEETS_TEMPLATE_ID']='1U0B7wu07bCH5X6Yfc3FQWgNEwMpoNCg8eDPtjlH0j6w'

# Inside the spreadsheet, which sheet to populate with data
ENVIRON['GOOGLE_SHEETS_SHEET_NAME']='Mash Data'

# Which column (in GOOGLE_SHEETS_SHEET_NAME) has the timestamp
#ENVIRON['GOOGLE_SHEETS_TSDB_PRIMARY_COLUMN']='A'

# Include only cols matching this regex, ignore all others
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
    # Based on code from: https://stackoverflow.com/q/28320134
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


usage() {
    local prg=$(basename $0)
    cat <<ENDHERE

Usage: $prg [options] <path/to/directory>

Options:
    -b BEERNAME - backup up only the beer matching this name prefix
                  Default: search for latest brewlog
    -o          - Run once
                  Default: run continously
    -s SECONDS  - Time between runs (in continuous mode)
                  Default: ${ENVIRON['BREWPI_BACKUP_INTERVAL_SECONDS']}
    -h          - Print this help message
    -d          - Run in debug mode (lots of output)
ENDHERE
}


# Process options
DEBUG=0
TEST=0
VERBOSE=1
ENDWHILE=0
ENVIRON['BREWPI_BACKUP_INTERVAL_SECONDS']=60
while [[ $# -gt 0 ]] && [[ $ENDWHILE -eq 0 ]] ; do
    case $1 in
        -b) ENVIRON['BREWPI_BACKUP_BEERNAME']="$2"; shift;;
        -d) DEBUG=1;;
        -h) usage; exit 0;;
        -o) ENVIRON['BREWPI_BACKUP_RUN_ONCE']='1';;
        -s) ENVIRON['BREWPI_BACKUP_INTERVAL_SECONDS']="$2"; shift;;
        -t) TEST=1;;
        --) ENDWHILE=1;;
        -*) echo "Invalid option '$1'"; exit 1;;
         *) ENDWHILE=1; break;;
    esac
    shift
done

if [[ $DEBUG -eq 1 ]] ; then
    set +x
    for k in "${!ENVIRON[@]}"; do printf '% 31s ... %s\n' "$k" "${ENVIRON[$k]}"; done
    set -x
fi

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

action=
[[ $TEST -eq 1 ]] && action=echo
$action docker run \
    "${envs[@]}" \
    "${mounts[@]}" \
    --rm -it "$IMAGE"
