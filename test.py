from simplegoogledrive import SimpleGoogleDrive
from timeseriesdb import TimeSeriesDB
import os
import simpledir
import brewlog

import pprint

###
# LOAD BREWPI DATA
###
d = simpledir.SimpleDir( '/home/pi/brewpi-data/data' )
#print('DIRS')
#pprint.pprint( d.dirs )
#print('FILES')
#pprint.pprint( d.files )


# Get latest brewlog (directory that was modified most recently)
dirs_sorted = d.sorted_dirs( sortby='st_mtime', reverse=True )
#print( 'DIRS SORTED BY mtime' )
#pprint.pprint( dirs_sorted )

# Is there any need to perform any checks?
# If nothing is active, then there will be no new data, so no action will occur

# Get brewpi data from latest brewlog
beer = brewlog.BrewLog( dirs_sorted[0] )
#print( 'DATA' )
#pprint.pprint( beer.data )

###
# APPEND TO TSDB IN GOOGLE SHEETS
###
# Get or create TSDB sheet in google
g = SimpleGoogleDrive()
sheets_parms = {
    'parent': os.environ['GOOGLE_DRIVE_FOLDER_ID'],
    'pfx': beer.name,
}
file_list = g.get_sheet_by_name_prefix( **sheets_parms )
if len(file_list) > 1:
    msg = "Found more than one file with name '' in google drive".format( beer.name )
    raise UserWarning( msg )
elif len( file_list ) < 1:
    # Create new file from template
    template_id = os.environ['GOOGLE_SHEETS_TEMPLATE_ID']
    file_id = g.create_from_template( template_id, beer.name )
    print( "Created new sheet: '{}' with fileID: '{}'".format( beer.name, file_id ) )
else:
    file_id = file_list[0]['id']
tsdb_parms = {
    'sheets_service': g.sheets,
    'file_id': file_id,
    'sheet_name': os.environ['GOOGLE_SHEETS_SHEET_NAME'],
}
tsdb = TimeSeriesDB( **tsdb_parms )

# Find local timestamps that are newer than cloud data
