#!/bin/python3

class MongoDataManager:

    def getTotalAmount( self, _startDate, _endDate, _tagPrefix ):
    
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db

        matchesClause = {
            '$and':
            [
                { 'date': { '$gte': _startDate.timestamp() } },
                { 'date': { '$lte': _endDate.timestamp() } },
                { 'tag': { '$regex': _tagPrefix + '.*' } }
            ]
        }
        groupClause = {
            '_id': '',
            'total': { '$sum': '$amount' }
        }
        aggregationResults = db.test_transactions.aggregate(
            [
                { '$match': matchesClause },
                { '$group': groupClause }
            ]
        )
        aggregationResultCount = 0
        amountTotal = 0.0
        for result in aggregationResults:
            aggregationResultCount += 1
            amountTotal = float( result[ 'total' ] )

        if( aggregationResultCount > 1 ):
            raise InvalidResultException( 'Aggregation result for', _tagPrefix, 'count:', aggregationResultCount, ' (should be <= 1)' )

        return amountTotal

    def getDistinctIncomeSources( self, _startDate, _endDate ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db

        matchesClause = {
            '$and':
            [
                { 'date': { '$gte': _startDate.timestamp() } },
                { 'date': { '$lte': _endDate.timestamp() } },
                { 'tag': { '$regex': 'income_.*' } }
            ]
        }
        groupClause = {
            '_id': '$tag',
            'total': { '$sum': '$amount' }
        }
        aggregationResults = db.test_transactions.aggregate(
            [
                { '$match': matchesClause },
                { '$group': groupClause },
                { '$sort': { 'total': -1 } }
            ]
        )
        aggregationResultCount = 0
        amountTotal = 0.0
        distinctIncomeSources = []
        for result in aggregationResults:
            aggregationResultCount += 1
            distinctIncomeSource = {}
            distinctIncomeSource[ 'tag' ] = result[ '_id' ]
            distinctIncomeSource[ 'total' ] = result[ 'total' ]

            distinctIncomeSources.append( distinctIncomeSource )

        return distinctIncomeSources

    def getDistinctExpenses( self, _startDate, _endDate ):
        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db

        matchesClause = {
            '$and':
            [
                { 'date': { '$gte': _startDate.timestamp() } },
                { 'date': { '$lte': _endDate.timestamp() } },
                { 'tag': { '$regex': 'expense_.*' } }
            ]
        }
        groupClause = {
            '_id': '$tag',
            'total': { '$sum': '$amount' }
        }
        aggregationResults = db.test_transactions.aggregate(
            [
                { '$match': matchesClause },
                { '$group': groupClause },
                { '$sort': { 'total': 1 } }
            ]
        )
        aggregationResultCount = 0
        amountTotal = 0.0
        distinctExpenses = []
        for result in aggregationResults:
            aggregationResultCount += 1
            distinctExpense = {}
            distinctExpense[ 'tag' ] = result[ '_id' ]
            distinctExpense[ 'total' ] = result[ 'total' ]

            distinctExpenses.append( distinctExpense )

        return distinctExpenses


