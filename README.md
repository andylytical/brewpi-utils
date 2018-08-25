Utilities for added functionality with BrewPi.

# Brewpi-Backup
Backup brewpi csv data to a google spreadsheet.
## Usage
Start docker container on Raspberry Pi:
1. _One Time Setup_ (below)
1. `curl -o /home/pi/brewpi-backup.sh https://github.com/andylytical/brewpi-utils/blob/master/brewpi-backup/dkrun.sh`
1. Edit `/home/pi/brewpi-backup.sh`
   1. Change environment variables as needed
1. `/home/pi/brewpi-backup.sh`

# One Time Setup
Enable Google API access
1. Go to [Google Cloud Platform Credentials Management](https://console.cloud.google.com/apis/credentials)
1. Create a client ID
   1. Click *Credentials* (on the left hand pane)
      1. Create credentials (dropdown) → OAuth client ID
      1. Other
      1. Enter a name: (something like _BrewPi Backups_)
         1. Client ID and Client Secret are displayed, close that pop-up window.
      1.  In the client IDs list, find the client ID row you just created and click the *Download JSON* image. Save the file to your computer.
      1. Transfer the JSON file to raspberry pi as `/home/pi/.googleauth/client_secret.json`.
1. Enable API access for your google account
   1.  Click *Library* (on the left hand pane)
      1. Find *Google Drive API* (part of G Suite category) and click on it
      1. Click the *Enable* button
      1. Find the *Google Sheets API* (part of the G Suite category) and click on it
      1. Click the *Enable* button
      
# Docker Help
#### View docker containers
1. `docker ps`
#### Stop a docker container
1. `docker stop CONTAINER-ID`
