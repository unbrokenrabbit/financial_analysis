#!/bin/python3

import time
import datetime
import tag
from pymongo import MongoClient
from bson.objectid import ObjectId

class TransactionManager:
    
    def __init__( self ):
        self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING = 'transaction_format_csv_chase_checking'
        self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT = 'transaction_format_csv_chase_credit'
        self.formatLines = {}
        self.formatLines[ self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING ] = 'Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #'
        self.formatLines[ self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT ] = 'Type,Trans Date,Post Date,Description,Amount'

        #type (income, expense), date, amount, balance, description
        self.TRANSACTION_ELEMENT_KEY_TYPE = 'type'
        self.TRANSACTION_ELEMENT_KEY_DATE = 'date'
        self.TRANSACTION_ELEMENT_KEY_AMOUNT = 'amount'
        self.TRANSACTION_ELEMENT_KEY_BALANCE = 'balance'
        self.TRANSACTION_ELEMENT_KEY_DESCRIPTION = 'description'

        self.TRANSACTION_ELEMENT_TYPE_INCOME = 'income' 
        self.TRANSACTION_ELEMENT_TYPE_EXPENSE = 'expense' 
        self.CSV_CHASE_DATE_FORMAT = '%m/%d/%Y'

    def importTransactions( self, _file, _account ):
        print( 'importing file', _file, 'into', _account, 'account' )
        inputFile = open( _file, 'r' )
    
        columnsLine = inputFile.readline().strip()
        inputFileFormat = self.determineInputFileFormat( columnsLine )

        rows = []
        for line in inputFile:
            values = self.extractValuesFromInputLine( line.strip(), inputFileFormat )
            row = self.translateValues( values, inputFileFormat )
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

            if( result[ 'updatedExisting' ] ):
                updatedTransactionCount += 1
            else:
                newTransactionCount += 1

        tagManager = tag.TagManager()
        tagManager.applyTags()

    def extractValuesFromInputLine( self, _line, _inputFileFormat ):
        line = _line
        # Correct for any known errors
        if( 'carters, Inc' in _line ):
            line = _line.replace( 'carters, Inc', 'carters Inc' )
        elif( 'GEEKNET, INC' in _line ):
            line = _line.replace( 'GEEKNET, INC', 'GEEKNET INC' )

        values = line.split( ',' )
        if( ( _inputFileFormat == self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING ) and ( len( values ) != 8 ) ):
            print( 'WARNING - problematic split of', self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING, 'line:', _line )
            print( '        - value count:', str( len( values ) ), ' (should be 8)' )
        if( ( _inputFileFormat == self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT ) and ( len( values ) != 5 ) ):
            print( 'WARNING - problematic split of', self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT, 'line:', _line )
            print( '        - value count:', str( len( values ) ), ' (should be 5)' )

        return values

    def translateValues( self, _values, _inputFileFormat ):
        translatedValues = {}
        if( _inputFileFormat == self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING ):
            translatedValues = self.translateCsvChaseCheckingValues( _values )
        elif( _inputFileFormat == self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT ):
            translatedValues = self.translateCsvChaseCreditValues( _values )

        return translatedValues

    # input values should be a list in the following order:
    #     0: Details
    #     1: Posting Date
    #     2: Description
    #     3: Amount
    #     4: Type
    #     5: Balance
    #     6: Check or Slip #
    def translateCsvChaseCheckingValues( self, _values ):
        translatedValues = {}

        # DEBUG
        print( 'values:', _values )

        # Details
        details = _values[ 0 ]
        if( details == 'DEBIT' ):
            translatedValues[ self.TRANSACTION_ELEMENT_KEY_TYPE ] = self.TRANSACTION_ELEMENT_TYPE_INCOME 
        elif( details == 'CREDIT' ):
            translatedValues[ self.TRANSACTION_ELEMENT_KEY_TYPE ] = self.TRANSACTION_ELEMENT_TYPE_EXPENSE 
        else:
            print( 'ERROR - unexpected value in Details column of CSV Chase Checking input line:', details )

        # Posting Date
        postingDate = _values[ 1 ]
        timestamp = datetime.datetime.strptime( postingDate, self.CSV_CHASE_DATE_FORMAT ).timestamp()
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_DATE ] = timestamp

        # Description
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_DESCRIPTION ] = _values[ 2 ]

        # Amount
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_AMOUNT ] = float( _values[ 3 ] )

        # Balance
        balance = _values[ 5 ].strip()
        if( balance != '' ):
            translatedValues[ self.TRANSACTION_ELEMENT_KEY_BALANCE ] = float( balance )

        return translatedValues

    # input values should be a list in the following order:
    #    0: Type
    #    1: Trans Date
    #    2: Post Date
    #    3: Description
    #    4: Amount
    def translateCsvChaseCreditValues( self, _values ):
        translatedValues = {}

        # Type
        transactionType = _values[ 0 ]
        if( transactionType == 'Sale' ):
            translatedValues[ self.TRANSACTION_ELEMENT_KEY_TYPE ] = self.TRANSACTION_ELEMENT_TYPE_EXPENSE 
        elif( transactionType == 'Return' ):
            translatedValues[ self.TRANSACTION_ELEMENT_KEY_TYPE ] = self.TRANSACTION_ELEMENT_TYPE_INCOME 
        else:
            print( 'ERROR - unexpected value in Type column of CSV Chase Credit input line:', transactionType )

        # Trans Date
        transactionDate = _values[ 1 ]
        timestamp = datetime.datetime.strptime( transactionDate, self.CSV_CHASE_DATE_FORMAT ).timestamp()
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_DATE ] = timestamp

        # Post Date


        # Description
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_DESCRIPTION ] = _values[ 3 ]

        # Amount
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_AMOUNT ] = float( _values[ 4 ] )

        # Add an empty balance element
        translatedValues[ self.TRANSACTION_ELEMENT_KEY_BALANCE ] = ''
        
        return translatedValues

    def determineInputFileFormat( self, _columnsLine ):
        inputFileFormat = 'invalid' 
        if( _columnsLine == self.formatLines[ self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING ] ):
            inputFileFormat = self.TRANSACTION_FORMAT_CSV_CHASE_CHECKING
        elif( _columnsLine == self.formatLines[ self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT ] ):
            inputFileFormat = self.TRANSACTION_FORMAT_CSV_CHASE_CREDIT

        return inputFileFormat
    
    def translateColumn( self, _column, _format ):
        translatedColumn = 'invalid'
        if( _format == 'chase_csv_checking_alpha' ):
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
        elif( _format == 'chase_csv_credit_alpha' ):
            if( _column == 'Type' ):
                translatedColumn = ''
            elif( _column == 'Trans Date' ):
                translatedColumn = ''
            elif( _column == 'Post Date' ):
                translatedColumn = ''
            elif( _column == 'Description' ):
                translatedColumn = ''
            elif( _column == 'Amount' ):
                translatedColumn = ''
            else:
                print( 'unknown column in format', _format + ': [' + _column + ']' )
        else:
            print( 'unknown format:', _format )
    
        return translatedColumn

    def translateValue( self, _column, _value, _format ):
    
        value = _value
        if( _column == 'posting_date' ):
            dateFormat = '%m/%d/%Y'
            value = datetime.datetime.strptime( _value, dateFormat ).timestamp()
    
        return value
    
    def deleteAccountTransactions( self, _account ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        result = db.test_transactions.remove( { "account": _account } )

    def deleteTransaction( self, _transactionId ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        result = db.test_transactions.remove( { "_id": ObjectId( _transactionId ) } )

