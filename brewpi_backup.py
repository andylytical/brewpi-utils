from simplegoogledrive import SimpleGoogleDrive
from timeseriesdb import TimeSeriesDB
import os
import simpledir
import brewlog
import bisect
import time


def get_latest_beerlog():
    brew_logdir.refresh()
    # Get latest brewlog (directory that was modified most recently)
    dirs_sorted = brew_logdir.sorted_dirs( sortby='st_mtime', reverse=True )
    beername = os.getenv( 'BREWPI_BACKUP_BEERNAME' )
    if beername is None:
        beer = brewlog.BrewLog( dirs_sorted[0] )
    else:
        # Find matching dir name
        matches = [ x for x in dirs_sorted if x.name == beername ]
        if len( matches ) < 1:
            raise UserWarning( 'No matches for beername: {}'.format( beername ) )
        elif len( matches ) > 1:
            raise UserWarning( 'Multiple matches for beername: {}'.format( beername ) )
        else:
            beer = brewlog.BrewLog( matches[0] )
    return beer


def get_or_create_tsdb( name ):
    sheets_parms = {
        'parent': os.environ['GOOGLE_DRIVE_FOLDER_ID'],
        'pfx': name,
    }
    file_list = googl.get_sheet_by_name_prefix( **sheets_parms )
    if len(file_list) > 1:
        msg = "Found more than one file with name '{}' in google drive".format( name )
        raise UserWarning( msg )
    elif len( file_list ) < 1:
        # Create new file from template
        template_id = os.environ['GOOGLE_SHEETS_TEMPLATE_ID']
        file_id = googl.create_from_template( template_id, name )
    else:
        file_id = file_list[0]['id']
    tsdb_parms = {
        'sheets_service': googl.sheets,
        'file_id': file_id,
        'sheet_name': os.environ['GOOGLE_SHEETS_SHEET_NAME'],
    }
    return TimeSeriesDB( **tsdb_parms )


def assert_headers_equal( tsdb, beer ):
    tsdb_headers = tsdb.headers()
    local_headers = beer.headers()
    if len(local_headers) != len(tsdb_headers) :
        msg = "Header length mismatch: local data header count='{}' cloud data header count='{}'".format(
            len(local_headers),
            len(tsdb_headers)
        )
        raise UserWarning(msg)


def update_cloud( local, cloud ):
    # Find local timestamps that are newer than cloud data
    timestamps = sorted( cloud.timestamps() )
    start = 0
    if len(timestamps) > 0:
        start = bisect.bisect( local.timestamps(), timestamps[-1] )
    if start < len(local.data['values']) :
        #APPEND
        print( "Start index into local data is '{}'".format( start ) )
        num_rows_added = cloud.append( local.data['values'][start:] )
        print( 'Added {} new rows'.format( num_rows_added ) )
    else :
        print( "Start='{}' , local beer data row count='{}' , nothing to do".format(
            start, len(local.data['values'])
        ) )


def run_loop( continuous=True ):
    pause = os.environ['BREWPI_BACKUP_INTERVAL_SECONDS']
    while True:
        beer = get_latest_beerlog()
        tsdb = get_or_create_tsdb( beer.name )
        assert_headers_equal( tsdb, beer )
        update_cloud( beer, tsdb )
        if not continuous:
            break
        time.sleep( pause )


if __name__ == '__main__':
    brew_logdir = simpledir.SimpleDir( '/home/pi/brewpi-data/data' )
    googl = SimpleGoogleDrive()
    val = True
    if 'BREWPI_BACKUP_RUNONCE' in os.environ:
        val = bool( os.environ['BREWPI_BACKUP_RUNONCE'] )
    run_loop( continuous=val )
