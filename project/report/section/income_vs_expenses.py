#!/bin/python3

from pymongo import MongoClient
import dates
import pymongo

class Manager:
    
    #def __init__( self ):
        
    def createSectionModel( self, _sectionParameters ):
        result = {}

        mongoClient = MongoClient( 'financial-analysis-mongodb' )
        db = mongoClient.financial_analysis_db
    
        dateManager = dates.DateManager()

        # retrieve the sum of all expenses in the given time period
        resultMonthlyEvaluations = []
        for monthlyEvaluation in _sectionParameters[ 'monthly_evaluations' ]:
            startDate = dateManager.getToday()
            endDate = dateManager.getToday()

            startDateString = monthlyEvaluation[ 'start_date' ]
            endDateString = monthlyEvaluation[ 'end_date' ]

            resultMonthlyEvaluation = {}

            NONE = 'none'
            if( startDateString == NONE ):
                startDate = dateManager.getMinDate()
                resultMonthlyEvaluation[ 'start_date' ] = '-'
            else:
                startDate = dateManager.yearMonthStringToDate( startDateString )
                resultMonthlyEvaluation[ 'start_date' ] = startDateString

            if( endDateString == NONE ):
                endDate = dateManager.getMaxDate()
                resultMonthlyEvaluation[ 'end_date' ] = 'present'
            else:
                endDate = dateManager.yearMonthStringToDate( endDateString )
                resultMonthlyEvaluation[ 'end_date' ] = endDateString

            minDateFindClause = {
                'date': {
                    '$gte': startDate.timestamp()
                }
            }
            results = db.test_transactions.find( minDateFindClause ).sort( 'date', pymongo.ASCENDING ).limit( 1 )
            minDateTransaction = results.next()
            minDate = dateManager.timestampToDate( minDateTransaction[ 'date' ] )

            maxDateFindClause = {
                'date': {
                    '$lte': endDate.timestamp()
                }
            }
            results = db.test_transactions.find( maxDateFindClause ).sort( 'date', pymongo.DESCENDING ).limit( 1 )
            maxDateTransaction = results.next()
            maxDate = dateManager.timestampToDate( maxDateTransaction[ 'date' ] )

            monthStart = dateManager.getDate( minDate.year, minDate.month, 1 )
            monthEnd = dateManager.advanceToEndOfMonth( monthStart )

            months = []
            monthStartTimestamp = dateManager.dateToTimestamp( monthStart )
            endDateTimestamp = dateManager.dateToTimestamp( maxDate )
            while( monthStartTimestamp < endDateTimestamp ):
                # Update date range to the next month
                monthStart = dateManager.advanceToNextMonth( monthStart )
                monthEnd = dateManager.advanceToEndOfMonth( monthStart )

                monthStartTimestamp = dateManager.dateToTimestamp( monthStart )

                try:
                    totalIncome = self.getTotalAmount( monthStart, monthEnd, 'income_' )
                    totalExpenses = self.getTotalAmount( monthStart, monthEnd, 'expense_' )

                    month = {}
                    month[ 'start' ] = monthStart
                    month[ 'end' ] = monthEnd
                    month[ 'total_income' ] = totalIncome
                    month[ 'total_expenses' ] = totalExpenses

                    months.append( month )

                except InvalidResultException as errorMessage:
                    print( 'ERROR calculating totals:', errorMessage )

            resultMonthlyEvaluation[ 'months' ] = months

            resultMonthlyEvaluations.append( resultMonthlyEvaluation )

        result[ 'monthly_evaluations' ] = resultMonthlyEvaluations

        return result

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

    def writeSectionToFile( self, _outputFile, _sectionModel ):
        _outputFile.write( '\\section{Income vs Expenses}' )

        for monthlyEvaluation in _sectionModel[ 'monthly_evaluations' ]:
            startDate = monthlyEvaluation[ 'start_date' ]
            endDate = monthlyEvaluation[ 'end_date' ]

            dateLine = "\\subsection{Monthly Evaluation: " + startDate + " to " + endDate + "}"
            _outputFile.write( dateLine  )

            for month in monthlyEvaluation[ 'months' ]:
                monthStart = month[ 'start' ]
                totalIncome = month[ 'total_income' ]
                totalExpenses = month[ 'total_expenses' ]
                delta = totalIncome + totalExpenses
                _outputFile.write( "\n" + str( monthStart.year ) + " " + self.monthAsString( monthStart.month ) + "\\\\" )
                _outputFile.write( "\nincome: \\hfill " + '{0:.2f}'.format( totalIncome ) + "\\\\" )
                _outputFile.write( "\nexpenses: \\hfill " + '{0:.2f}'.format( totalExpenses ) + "\\\\" )
                _outputFile.write( "\n\\noindent\\rule{\\textwidth}{1pt}" )

                if( delta > 0 ):
                    _outputFile.write( "\ndelta:\\hfill {\\color{ForestGreen} " + '{0:.2f}'.format( delta ) + "}\\\\" )
                else:
                    _outputFile.write( "\ndelta:\\hfill {\\color{BrickRed} " + '{0:.2f}'.format( delta ) + "}\\\\" )

                _outputFile.write( "\n\\linebreak" )
     
    def monthAsString( self, _monthIndex ):
        month = 'ERROR'
        if( _monthIndex == 1 ):
            month = 'JAN'
        elif( _monthIndex == 2 ):
            month = 'FEB'
        elif( _monthIndex == 3 ):
            month = 'MAR'
        elif( _monthIndex == 4 ):
            month = 'APR'
        elif( _monthIndex == 5 ):
            month = 'MAY'
        elif( _monthIndex == 6 ):
            month = 'JUN'
        elif( _monthIndex == 7 ):
            month = 'JUL'
        elif( _monthIndex == 8 ):
            month = 'AUG'
        elif( _monthIndex == 9 ):
            month = 'SEP'
        elif( _monthIndex == 10 ):
            month = 'OCT'
        elif( _monthIndex == 11 ):
            month = 'NOV'
        elif( _monthIndex == 12 ):
            month = 'DEC'
        else:
            raise IndexError( 'Invalid month:', _monthIndex )

        return month


