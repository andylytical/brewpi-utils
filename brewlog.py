import datetime
import json
import os
import re
import simpledir

import pprint

class BrewLog( object ):
    ''' Interface to the logs for a single beer.
        See BrewLog.env_map for possible environment variables.
        See BrewLog.env_defaults for default values.
    '''
    env_map = {
        'BREWLOG_COLS_REGEX': 'cols_regex',
        'BREWLOG_KEEP_EMPTY_COLS': 'keep_empty_cols',
    }
    env_defaults = {
        'cols_regex': '.',
        'keep_empty_cols': 1,
    }

    def __init__( self, dirpath ):
        self.dir = simpledir.SimpleDir( dirpath )
        # Load any environment variables
        for e,k in self.env_map.items():
            setattr( self, k, os.getenv( e, self.env_defaults[k] ) )
        self.cols_regex = re.compile( self.cols_regex )
        self.data = None
        self._load_data()

    def __str__( self ):
        return '<BrewLog ({})>'.format( self.dir )

    __repr__ = __str__


    @property
    def name( self ):
        return self.dir.name


    def refresh( self ):
        self.data = None
        self._load_data()


    def timestamps( self ):
        return [ r[0] for r in self.data['values'] ]


    def headers( self ):
        return self.data['labels']


    def _load_data( self ):
        # get list of json files from simpledir
        jsonfiles = self.dir.files_matching_glob( '*.json', sortby='st_mtime' )
#        pprint.pprint( jsonfiles )
        # parse json data (as in mk_brewlog_graphs)
        self._parse_jsondata( jsonfiles )


    def _parse_jsondata( self, jsonlist ):
        ''' jsonlist is a list of json filepaths
            Returns a dict with format:
                { 'labels': [ ... ],
                  'values': [ [...], [...], ... ],
                }
            INPUT:
                jsonlist - list of pathlib.Path's to json files
        '''
        thisdata = { 'values': [] }
        for jsonfile in sorted( jsonlist ):
            hdrs, rows = self._parse_jsonfile( jsonfile )
            if 'labels' not in thisdata:
                thisdata[ 'labels' ] = hdrs
            if len( hdrs ) != len( thisdata[ 'labels' ] ):
                raise UserWarning( "mismatched labels in file: '{}'".format( jsonfile ) )
            thisdata[ 'values' ].extend( rows )
        if self.keep_empty_cols:
            cleandata = thisdata
        else:
            cleandata = filter_empty_cols( thisdata )
        self.data = cleandata


    def _parse_jsonfile( self, jpath ):
        ''' jpath is a pathlib.Path object
            Returns a tuple with format (labels, values)
            where labels is a list of strings
            and where values is a list of lists of values (ie: rows of data)
        '''
        # read in raw json
        with jpath.open() as fp:
            data = json.load( fp )
        # filter column headers, keep only those matching cols_regex
        col_nums = []
        for i,v in enumerate( data['cols'] ):
            if self.cols_regex.search( v['id'] ):
                col_nums.append( i )
        # get labels, respecting col_nums
        labels = [ data[ 'cols' ][ i ][ 'id' ] for i in col_nums ]
        # get rows
        rows = []
        for row in data[ 'rows' ]:
            values = []
            # for each row, get only the values from columns given in col_nums
            for i in col_nums:
                elem = row['c'][i]
                typ = data[ 'cols' ][ i ][ 'type' ]
                values.append( self.j2py( elem, typ ) )
            rows.append( values )
        return ( labels, rows )

    @staticmethod
    def j2py( elem, typ ):
        ''' Convert a json value into a native python datatype
        '''
        val = None
        if elem:
            rawval = elem[ 'v' ]
            if typ == 'datetime':
                # JS Date looks like "Date(2018,5,28,20,51,36)"
                parts = map( int, rawval[5:-1].split(',') )
                val = datetime.datetime( *parts )
            elif typ == 'number':
                val = float( rawval )
            elif typ == 'string':
                val = rawval
            else:
                raise UserWarning( "Unknown type '{}' from json".format( typ ) )
        return val


    @staticmethod
    def filter_empty_cols( data ):
        ''' Remove columns of data in which there is no value present in any row.
            PARAMS:
                data - dict - of the form { 'labels': list,
                                            'values': list of lists 
                                          }
            RETURN:
                cleandata - dict with same format as above but with empty cols removed
            Note: labels are excluded from checking for empty values,
                  but will be filtered based on data from the remaining values (rows)
        '''
        cols_with_data = []
        for ary in data[ 'values' ]:
            for i, elem in enumerate( ary ):
                if elem is not None:
                    cols_with_data.append( i )
        valid_cols = set( sorted( cols_with_data ) )
        cleanhdrs = [ data[ 'labels' ][ i ] for i in valid_cols ]
        cleanrows = []
        for ary in data[ 'values' ]:
            cleanrows.append( [ ary[i] for i in valid_cols ] )
        return { 'labels': cleanhdrs, 'values': cleanrows }
