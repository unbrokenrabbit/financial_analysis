#!/bin/python3

from subprocess import call
from pymongo import MongoClient
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot

class Reporter:

    def __init__( self ):
        self.uniqueId = 0

    def report( self, _configFile, _outputFile ):
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
    
        self.writeDocumentHeader( latexOutputFile )
    
        for section in report[ 'sections' ]:
            sectionType = section[ 'type' ]
            if( sectionType == 'balance' ):
                balanceSectionModel = self.createBalanceSectionModel( section )
                self.writeBalanceSection( latexOutputFile, balanceSectionModel )
            else:
                print( 'Unknown section type:', sectionType )
    
        self.writeDocumentFooter( latexOutputFile )
        latexOutputFile.close()
    
        call( [ 'pdflatex', '-output-format=pdf', ( '-output-directory=' + workspaceDirectory ), latexFilename ] )
        call( [ 'mv', ( workspaceDirectory + '/' + latexFilenamePrefix + '.pdf' ), _outputFile ] )
        call( [ 'rm', '-r', workspaceDirectory ] )

    def writeDocumentHeader( self, _outputFile ):
        _outputFile.write( '\\documentclass{article}\n' )
        _outputFile.write( '\\usepackage{graphicx}\n' )
        _outputFile.write( '\\begin{document}\n' )

    def createBalanceSectionModel( self, _sectionParameters ):
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
        
        plotFilename = 'balance_' + str( self.getUniqueId() ) + '.png'
        pyplot.savefig( plotFilename )
        pyplot.clf()
    
        result = {}
        result[ 'plot_filename' ] = plotFilename
    
        # DEBUG
        print( 'created plot:', plotFilename )
    
        return result

    def getUniqueId( self ):
        self.uniqueId = self.uniqueId + 1
    
        return self.uniqueId

    def writeDocumentFooter( self, _outputFile ):
        _outputFile.write( '\\end{document}\n' )
    
    def writeBalanceSection( self, _outputFile, _sectionModel ):
        pathToImage = _sectionModel[ 'plot_filename' ]
        _outputFile.write( "\n" )
        _outputFile.write( "\\includegraphics[width=\linewidth]{" + pathToImage + "}\n" )
        _outputFile.write( "\n" )


