#!/bin/python3

"""Usage:
    analyze import <file> <format> <account>
    analyze report <file> <format>
"""

from docopt import docopt

def parseArguments( _usageString ):
    arguments = docopt( _usageString, version = '1.0.0' )

    print( 'arguments:', arguments )

    if( arguments[ 'import' ] ):
        importTransactions( arguments[ '<file>' ], arguments[ '<format>' ], arguments[ '<account>' ] )
    elif( arguments[ 'report' ] ):
        report( arguments[ '<file>' ], arguments[ '<format>' ] )

print( 'hey there' )

def importTransactions( _file, _format, _account ):
    print( 'importing', _format, 'file', _file, 'into', _account, 'account' )
    inputFile = open( _file, 'r' )

    # DEBUG
    print( inputFile )

    columnsString = inputFile.readline()
    columns = columnsString.split( ',' )

    for column in columns:
        print( 'column:', column )

    rows = []
    for line in inputFile:
        print( line )

        values = line.split( ',' )

        row = dict()
        for index in range( 0, len( columns ) ):
            row[ columns[ index ] ] = values[ index ]

        rows.append( row )

    print( rows )

def report( _file, _format ):
    print( 'publishing report to', _file, 'as', _format )

parseArguments( __doc__ )

print( 'done' )


