#!/bin/python3

"""Usage:
    analyze import <input-file> <format> <account>
    analyze report <report-config-file> <output-file>
    analyze list-formats
    analyze delete <account>
"""

from docopt import docopt
from pymongo import MongoClient
from subprocess import call
#import plotly
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot
import numpy
import json

uniqueId = 0

def parseArguments( _usageString ):
    arguments = docopt( _usageString, version = '1.0.0' )

    # DEBUG
    #print( 'arguments:', arguments )

    if( arguments[ 'import' ] ):
        importTransactions( arguments[ '<input-file>' ], arguments[ '<format>' ], arguments[ '<account>' ] )
    elif( arguments[ 'report' ] ):
        report( arguments[ '<report-config-file>' ], arguments[ '<output-file>' ] )
    elif( arguments[ 'list-formats' ] ):
        listFormats()
    elif( arguments[ 'delete' ] ):
        deleteAccountTransactions( arguments[ '<account>' ] )

def translateColumn( _column, _format ):
    translatedColumn = 'invalid'
    if( _format == 'chase_csv_alpha' ):
        if( _column == 'Details' ):
            translatedColumn = 'details'
        elif( _column == 'account' ):
            translatedColumn = 'account'
        elif( _column == 'Amount' ):
            translatedColumn = 'amount'
        elif( _column == 'Description' ):
            translatedColumn = 'description'
        elif( _column == 'Posting Date' ):
            translatedColumn = 'posting_date'
        elif( _column == 'Type' ):
            translatedColumn = 'type'
        elif( _column == 'Balance' ):
            translatedColumn = 'balance'
        elif( _column == 'Check or Slip #' ):
            translatedColumn = 'check_number'
        else:
            print( 'unknown column in format', _format + ': [' + _column + ']' )
    else:
        print( 'unknown format:', _format )

    return translatedColumn

def translateValue( _column, _value ):
    import time
    import datetime

    value = _value
    if( _column == 'posting_date' ):
        print( 'posting date from CSV:', _value )
        dateFormat = '%m/%d/%Y'
        value = datetime.datetime.strptime( _value, dateFormat ).timestamp()

    return value

def deleteAccountTransactions( _account ):
    mongoClient = MongoClient( 'financial-analysis-mongodb' )
    db = mongoClient.financial_analysis_db

    db.test_transactions.remove( { "account": _account } )

    # DEBUG
    cursor = db.test_transactions.find()
    print( 'documents:' )
    for document in cursor:
        print( document )

def importTransactions( _file, _format, _account ):
    print( 'importing', _format, 'file', _file, 'into', _account, 'account' )
    inputFile = open( _file, 'r' )

    # DEBUG
    print( inputFile )

    columnsString = inputFile.readline().strip()
    columns = columnsString.split( ',' )

    for column in columns:
        print( 'column:', column )

    rows = []
    for line in inputFile:
        print( line )

        values = line.split( ',' )

        row = dict()
        for index in range( 0, len( columns ) ):
            translatedColumn = translateColumn( columns[ index ], _format )
            translatedValue = translateValue( translatedColumn, values[ index ] )
            row[ translatedColumn ] = translatedValue

        row[ "account" ] = _account

        rows.append( row )

    print( rows )

    mongoClient = MongoClient( 'financial-analysis-mongodb' )

    # DEBUG
    print( 'connected to mongo server' )

    db = mongoClient.financial_analysis_db

    for row in rows:
        result = db.test_transactions.update(
            row,
            {
                "$set": row,
            },
            upsert = True
        )

    cursor = db.test_transactions.find()

    # DEBUG
    #print( cursor )

    # DEBUG
    print( 'documents:' )
    for document in cursor:
        print( document )
    

def report( _configFile, _outputFile ):
    print( 'reading report config from', _configFile )
    print( 'publishing report to', _outputFile )

    reportConfig = {}
    with open( _configFile ) as jsonConfig:
        reportConfig = json.load( jsonConfig )
        print( reportConfig )

    report = reportConfig[ 'report' ]

    # Create a workspace for temporary files
    workspaceDirectory = 'temp'
    call( [ 'mkdir', workspaceDirectory ] )

    latexFilenamePrefix = 'report'
    latexFilenameExtension = 'tex'
    latexFilename = workspaceDirectory + '/' + latexFilenamePrefix + '.' + latexFilenameExtension
    latexOutputFile = open( latexFilename, 'w' )

    writeDocumentHeader( latexOutputFile )

    for section in report[ 'sections' ]:
        sectionType = section[ 'type' ]
        if( sectionType == 'balance' ):
            balanceSectionModel = createBalanceSectionModel( section )
            writeBalanceSection( latexOutputFile, balanceSectionModel )
        else:
            print( 'Unknown section type:', sectionType )

    writeDocumentFooter( latexOutputFile )
    latexOutputFile.close()

    call( [ 'pdflatex', '-output-format=pdf', ( '-output-directory=' + workspaceDirectory ), latexFilename ] )
    call( [ 'mv', ( workspaceDirectory + '/' + latexFilenamePrefix + '.pdf' ), _outputFile ] )
    call( [ 'rm', '-r', workspaceDirectory ] )

def writeDocumentHeader( _outputFile ):
    _outputFile.write( '\\documentclass{article}\n' )
    _outputFile.write( '\\usepackage{graphicx}\n' )
    _outputFile.write( '\\begin{document}\n' )

def writeDocumentFooter( _outputFile ):
    _outputFile.write( '\\end{document}\n' )

def writeBalanceSection( _outputFile, _sectionModel ):
    pathToImage = _sectionModel[ 'plot_filename' ]
    _outputFile.write( "\n" )
    _outputFile.write( "\\includegraphics[width=\linewidth]{" + pathToImage + "}\n" )
    _outputFile.write( "\n" )

def createBalanceSectionModel( _sectionParameters ):
    import time
    import datetime

    findClause = {}
    findClause[ 'account' ] = _sectionParameters[ 'account' ]

    reportDateFormat = '%Y-%m-%d'

    startDate = _sectionParameters[ 'start_date' ]
    if( startDate != 'none' ):
        startDate = datetime.datetime.strptime( startDate, reportDateFormat )
        findClause[ 'posting_date' ] = { "$gt": startDate.timestamp() }

    endDate = _sectionParameters[ 'end_date' ]
    if( endDate != 'none' ):
        endDate = datetime.datetime.strptime( endDate, reportDateFormat )
        findClause[ 'posting_date' ] = { "$lt": endDate.timestamp() }

    # DEBUG
    #print( 'find clause:', findClause )

    mongoClient = MongoClient( 'financial-analysis-mongodb' )
    db = mongoClient.financial_analysis_db

    cursor = db.test_transactions.find( findClause ).sort( 'posting_date' )

    # DEBUG
    #print( cursor )

    x = []
    y = []
    for document in cursor:
        #print( document )
        timestamp = datetime.datetime.fromtimestamp( document[ 'posting_date' ] ).date()
        x.append( timestamp )
        y.append( document[ 'balance' ] )

        # DEBUG
        #print( 'timestamp:', timestamp )

    # DEBUG
    #print( 'x:', x )
    #print( 'y:', y )

    pyplot.gca().xaxis.set_major_formatter( matplotlib.dates.DateFormatter( '%m/%d/%Y' ) )
    pyplot.gca().xaxis.set_major_locator( matplotlib.dates.DayLocator() )

    pyplot.plot( x, y )
    pyplot.gcf().autofmt_xdate()

    pyplot.gca().set_xlim( [ startDate, endDate ] )
    pyplot.gca().set_xticks( [ startDate, endDate ] )

    pyplot.gca().set_ylim( [ 0, 12000 ] )
    pyplot.gca().set_yticks( [ 0, 3000, 6000, 9000, 12000 ] )

    pyplot.ylabel( 'balance' )
    
    plotFilename = 'balance_' + str( getUniqueId() ) + '.png'
    pyplot.savefig( plotFilename )
    pyplot.clf()

    result = {}
    result[ 'plot_filename' ] = plotFilename

    # DEBUG
    print( 'created plot:', plotFilename )

    return result

def listFormats():
    formatsMessage = ''
    formatsMessage += "input file formats:\n"
    formatsMessage += "    chase-csv-alpha\n"
    formatsMessage += "output file formats:\n"
    formatsMessage += "    pdf\n"

    print( formatsMessage )

def getUniqueId():
    global uniqueId
    uniqueId = uniqueId + 1
    return uniqueId
    
parseArguments( __doc__ )

print( 'done' )


