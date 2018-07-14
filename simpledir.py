import csv
import json
import os
import pathlib
import operator

import pprint

class SimpleDir( object ):
    ''' Simple interface to interact with filesystem directories.
    '''

    def __init__( self, path ):
        self.path = pathlib.Path( path ).resolve( strict=True )
        self.contents = {}
        self._load_contents()


    def _load_contents( self ):
        contents = { 'dirs': {}, 'files': {} }
        for child in self.path.iterdir():
            if child.is_dir():
                d = contents['dirs']
            elif child.is_file():
                d = contents['files']
            else:
                msg = "Unknown file type for '{}'".format( child )
                raise UserWarning( msg )
            d[ child.name ] = {
                'path': child,
                'st_info': child.stat()
            }
        self.contents = contents


    def __str__( self ):
        return '<SimpleDir ({})>'.format( self.path )

    __repr__ = __str__


    @property
    def name( self ):
        return self.path.name


    def refresh( self ):
        self.contents = {}
        self._load_contents()


    def sorted_dirs( self, sortby=None, reverse=False ):
        ''' Get list of dirs in sorted order by "sortby"
            where "sortby" is a valid attribute of os.stat_result
            or where "sortby" is None, the default, in which case sort by name
        '''
        data = self.contents['dirs'].values()
        return self._file_sorter( data, sortby, reverse )


    def files_matching_glob( self, glob, sortby=None, reverse=False ):
        ''' Get list of files that match "glob" pattern.
            List is sorted by "sortby",
            where "sortby" is either: an os.stat_result attr name
            or where "sortby" is None, the default, in which case sort by name
        '''
        matches = []
        for name,dict_ in self.contents['files'].items():
            if dict_['path'].match( glob ):
                matches.append( dict_ )
#        print( 'FILE MATCHES' )
#        pprint.pprint( matches )
        return self._file_sorter( matches, sortby, reverse )


    def _file_sorter( self, data, sortby, reverse ):
        '''
            List is sorted by "sortby",
            where "sortby" is either: an os.stat_result attr name
            or where "sortby" is None, the default, in which case sort by name
        '''
        if sortby is None:
            f = operator.itemgetter('path')
        else:
            f = lambda x: getattr( x['st_info'], sortby )
        sorted_ = sorted( data, key=f, reverse=reverse )
        return [ x['path'] for x in sorted_ ]
