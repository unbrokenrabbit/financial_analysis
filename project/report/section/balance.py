#!/bin/python3

from pymongo import MongoClient
import dates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot

class Manager:

    def __init__( self ):
        self.uniqueId = 0

    def createSectionModel( self, _sectionParameters ):
        dateManager = dates.DateManager()
    
        findClause = {}
        findClause[ 'account' ] = _sectionParameters[ 'account' ]
    
        startDate = _sectionParameters[ 'start_date' ]
        if( startDate != 'none' ):
            startDate = dateManager.stringToDate( startDate )
            findClause[ 'date' ] = { "$gt": dateManager.dateToTimestamp( startDate ) }
    
        endDate = _sectionParameters[ 'end_date' ]
        if( endDate != 'none' ):
            endDate = dateManager.stringToDate( endDate )
            findClause[ 'date' ] = { "$lt": dateManager.dateToTimestamp( endDate ) }
    
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        cursor = db.test_transactions.find( findClause ).sort( 'date' )
    
        x = []
        y = []
        for document in cursor:
            timestamp = dateManager.timestampToDate( document[ 'date' ] )
            x.append( timestamp )
            y.append( document[ 'balance' ] )
    
        pyplot.gca().xaxis.set_major_formatter( matplotlib.dates.DateFormatter( dateManager.getDateFormat() ) )
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
        #print( 'created plot:', plotFilename )
    
        return result

    def writeSectionToFile( self, _outputFile, _sectionModel ):
        pathToImage = _sectionModel[ 'plot_filename' ]
        _outputFile.write( "\n" )
        _outputFile.write( "\\includegraphics[width=\linewidth]{" + pathToImage + "}\n" )
        _outputFile.write( "\n" )

    def getUniqueId( self ):
        self.uniqueId = self.uniqueId + 1
    
        return self.uniqueId

