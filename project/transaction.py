#!/bin/python3

import tag
from pymongo import MongoClient

class TransactionManager:
    
    def importTransactions( self, _file, _format, _account ):
        print( 'importing', _format, 'file', _file, 'into', _account, 'account' )
        inputFile = open( _file, 'r' )
    
        columnsString = inputFile.readline().strip()
        columns = columnsString.split( ',' )

        rows = []
        for line in inputFile:
            values = line.split( ',' )
    
            row = dict()
            for index in range( 0, len( columns ) ):
                translatedColumn = self.translateColumn( columns[ index ], _format )
                translatedValue = self.translateValue( translatedColumn, values[ index ] )
                row[ translatedColumn ] = translatedValue
    
            row[ "account" ] = _account
    
            rows.append( row )
    
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        newTransactionCount = 0
        updatedTransactionCount = 0
        for row in rows:
            result = db.test_transactions.update(
                row,
                {
                    "$set": row,
                },
                upsert = True
            )

            print( 'row:   ', row )
            print( 'result:', result )

            if( result[ 'updatedExisting' ] ):
                updatedTransactionCount += 1
            else:
                newTransactionCount += 1

        print( 'new transactions:    ', newTransactionCount )
        print( 'updated transactions:', updatedTransactionCount )

        tagger = tag.Tagger()
        tagger.applyTags()

    def translateColumn( self, _column, _format ):
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

    def translateValue( self, _column, _value ):
        import time
        import datetime
    
        value = _value
        if( _column == 'posting_date' ):
            dateFormat = '%m/%d/%Y'
            value = datetime.datetime.strptime( _value, dateFormat ).timestamp()
    
        return value
    
    def deleteAccountTransactions( self, _account ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        db.test_transactions.remove( { "account": _account } )

