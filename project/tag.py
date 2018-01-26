#!/bin/python3

import json
import re
from pymongo import MongoClient

class Tagger:
    
    def importTags( self, _tagsFile ):
        print( 'importing tags' )
    
        tags = {}
        with open( _tagsFile ) as jsonConfig:
            tags = json.load( jsonConfig )[ 'tags' ]
    
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        # Remove all documents from the tags collection
        db.tags.remove( {} )
    
        for tag in tags:
            document = {}
            document[ 'name' ] = tag[ 'name' ]
            document[ 'pattern' ] = tag[ 'pattern' ]
            db.tags.insert( document )
    
        self.applyTags()
    
    def applyTags( self ):
        print( 'applying tags' )
    
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        tags = db.tags.find()
    
        transactions = db.test_transactions.find( {}, { 'description': 1 } )
        for transaction in transactions:
            print( 'transaction:', transaction )
            description = transaction[ 'description' ]
    
            tags.rewind()
            isMatch = False
            tagValue = ''
            for tag in tags:
                pattern = tag[ 'pattern' ]
                if( re.match( pattern, description ) ):
                    isMatch = True
                    tagValue = tag[ 'name' ]
    
            db.test_transactions.update_one(
                { '_id': transaction[ '_id' ] },
                {
                    "$set":
                    {
                        "tag": tagValue
                    }
                }
            )
    
        self.displayTagStatistics()
    
    def displayTagStatistics( self ):
        import time
    
        statistics = self.collectTagStatistics()
    
        print( 'total transaction count:   ', str( statistics[ 'total_transaction_count' ] ) )
        print( 'tagged transaction count:  ', str( statistics[ 'tagged_transaction_count' ] ) )
        print( 'untagged transaction count:', str( statistics[ 'untagged_transaction_count' ] ) )
    
        if( len( statistics[ 'untagged_transactions' ] ) > 0 ):
            print( 'untagged transactions' )
            print( '-----------------------------------' )
            for transaction in statistics[ 'untagged_transactions' ]:
                description = transaction[ 'description' ]
                timestamp = time.localtime( transaction[ 'posting_date' ] )
                date = time.strftime( '%Y-%m-%d', timestamp )
                account = transaction[ 'account' ]
                amount = transaction[ 'amount' ]
                print( account, '$' + amount, date, '[' + description + ']' )
    
    def collectTagStatistics( self ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        statistics = {}
    
        untaggedTransactions = []
        transactions = db.test_transactions.find(
            {},
            {
                'description': 1,
                'tag': 1,
                'posting_date':1,
                'amount': 1,
                'account': 1,
                '_id': 0
            }
        )
        for transaction in transactions:
            if( transaction[ 'tag' ] == '' ):
                untaggedTransactions.append( transaction )
    
        totalTransactionCount = db.test_transactions.find().count()
    
        statistics[ 'total_transaction_count' ] = totalTransactionCount
        statistics[ 'tagged_transaction_count' ] = totalTransactionCount - len( untaggedTransactions )
        statistics[ 'untagged_transaction_count' ] = len( untaggedTransactions )
        statistics[ 'untagged_transactions' ] = untaggedTransactions
    
        return statistics


