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
            document[ 'account' ] = tag[ 'account' ]
            document[ 'amount_sign' ] = tag[ 'amount_sign' ]
            db.tags.insert( document )
    
        self.applyTags()
    
    def stripTags( self ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db       

        db.test_transactions.update(
            {},
            {
                '$unset':
                {
                    'tag': ''
                }
            }
        )

    def applyTags( self ):
        print( 'applying tags' )
    
        self.stripTags()

        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db

        tags = db.tags.find()

        for tag in tags:
            tagName = tag[ 'name' ]
            tagPattern = tag[ 'pattern' ]
            tagAccount = tag[ 'account' ]
            tagAmountSign = tag[ 'amount_sign' ]

            findClause = {}
            findClause[ 'description' ] = { '$regex': tagPattern }
            findClause[ 'account' ] = tagAccount

            if( tagAmountSign == '+' ):
                findClause[ 'amount' ] = { '$gte': 0 }
            elif( tagAmountSign == '-' ):
                findClause[ 'amount' ] = { '$lte': 0 }

            results = db.test_transactions.update(
                findClause,
                {
                    "$set":
                    {
                        "tag": tagName
                    }
                },
                multi=True
            )

        self.displayTagStatistics()

    def applyTags_old( self ):
        print( 'applying tags (old)' )
    
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        tags = db.tags.find()
    
        transactions = db.test_transactions.find( {}, { 'description': 1, 'amount': 1 } )
        for transaction in transactions:
            description = transaction[ 'description' ]
            amount = float( transaction[ 'amount' ] )
    
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
                serialNumber = transaction[ '_id' ]
                description = transaction[ 'description' ]
                timestamp = time.localtime( transaction[ 'date' ] )
                date = time.strftime( '%Y-%m-%d', timestamp )
                account = transaction[ 'account' ]
                amount = transaction[ 'amount' ]
                print( serialNumber, account, date, '$' + str( amount ), '[' + description + ']' )
    
    def collectTagStatistics( self ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        statistics = {}
    
        findClause = {
            'tag':
            {
                '$exists': False
            }
        }
        resultFilter = {
            'description': 1,
            'tag': 1,
            'date':1,
            'amount': 1,
            'account': 1
        }
        untaggedTransactionsCursor = db.test_transactions.find( findClause, resultFilter )
        untaggedTransactions = []
        untaggedTransactionCount = 0
        for untaggedTransaction in untaggedTransactionsCursor:
            untaggedTransactions.append( untaggedTransaction )

        totalTransactionCount = db.test_transactions.find().count()
    
        statistics[ 'total_transaction_count' ] = totalTransactionCount
        statistics[ 'tagged_transaction_count' ] = totalTransactionCount - len( untaggedTransactions )
        statistics[ 'untagged_transaction_count' ] = len( untaggedTransactions )
        statistics[ 'untagged_transactions' ] = untaggedTransactions
    
        return statistics


