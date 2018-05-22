#!/bin/python3

import dates
from pymongo import MongoClient

class IncomeVsExpensesSectionModelBuilder:
    def buildSectionModel( self, _sectionParameters ):
        sectionModel = IncomeVsExpensesSectionModel()

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

            monthlyEvaluationModel = MonthlyEvaluationModel()

            NONE = 'none'
            if( startDateString == NONE ):
                startDate = dateManager.getMinDate()
            else:
                startDate = dateManager.yearMonthStringToDate( startDateString )

            if( endDateString == NONE ):
                endDate = dateManager.getMaxDate()
            else:
                endDate = dateManager.yearMonthStringToDate( endDateString )

            minDateFindClause = {
                'date': {
                    '$gte': startDate.timestamp()
                }
            }
            results = db.test_transactions.find( minDateFindClause ).sort( 'date', pymongo.ASCENDING ).limit( 1 )
            minDateTransaction = results.next()
            minDate = dateManager.timestampToDate( minDateTransaction[ 'date' ] )
            monthlyEvaluationModel.startDate = minDate

            maxDateFindClause = {
                'date': {
                    '$lte': endDate.timestamp()
                }
            }
            results = db.test_transactions.find( maxDateFindClause ).sort( 'date', pymongo.DESCENDING ).limit( 1 )
            maxDateTransaction = results.next()
            maxDate = dateManager.timestampToDate( maxDateTransaction[ 'date' ] )
            monthlyEvaluationModel.endDate = maxDate

            monthStart = dateManager.getDate( minDate.year, minDate.month, 1 )
            monthEnd = dateManager.advanceToEndOfMonth( monthStart )

            monthStartTimestamp = dateManager.dateToTimestamp( monthStart )
            endDateTimestamp = dateManager.dateToTimestamp( maxDate )
            while( monthStartTimestamp < endDateTimestamp ):
                # Update date range to the next month
                monthEnd = dateManager.advanceToEndOfMonth( monthStart )

                try:
                    totalIncome = self.getTotalAmount( monthStart, monthEnd, 'income_' )
                    totalExpenses = self.getTotalAmount( monthStart, monthEnd, 'expense_' )
                    distinctExpenses = self.getDistinctExpenses( monthStart, monthEnd )
                    distinctIncomeSources = self.getDistinctIncomeSources( monthStart, monthEnd )
                    pieChartFilename = 'monthly-pie-' + str( monthStart.year ) + '-' + str( monthStart.month )
                    pathToPieChartFile = self.createDistinctExpensesPieChart( distinctExpenses, totalExpenses, pieChartFilename )
                    barChartFilename = 'monthly-bar-' + str( monthStart.year ) + '-' + str( monthStart.month )
                    pathToBarChartFile = self.createDistinctExpensesBarChart( distinctExpenses, barChartFilename )

                    monthModel = MonthModel()
                    monthModel.start = monthStart
                    monthModel.end = monthEnd
                    monthModel.totalIncome = totalIncome
                    monthModel.totalExpenses = totalExpenses
                    monthModel.distinctExpenses = distinctExpenses
                    monthModel.distinctIncomeSources = distinctIncomeSources
                    monthModel.pathToPieChartFile = pathToPieChartFile
                    monthModel.pathToBarChartFile = pathToBarChartFile

                    monthlyEvaluationModel.months.append( monthModel )

                except InvalidResultException as errorMessage:
                    print( 'ERROR calculating totals:', errorMessage )

                monthStart = dateManager.advanceToNextMonth( monthStart )
                monthStartTimestamp = dateManager.dateToTimestamp( monthStart )

            monthlyEvaluationModel.monthlyIncomeVsExpensesBarChartFilename = self.createMonthlyIncomeVsExpensesBarChart( monthlyEvaluationModel.months )
            monthlyEvaluationModel.monthlyNetBalanceLineChartFilename = self.createNetBalanceLineChart( monthlyEvaluationModel.months )

            sectionModel.monthlyEvaluations.append( monthlyEvaluationModel )

        return sectionModel

class IncomeVsExpensesSectionModel:
    def __init__( self ):
        self.monthlyEvaluations = []

class MonthlyEvaluationModel:
    def __init__( self ):
        self.startDate = ''
        self.endDate = ''
        self.months = []
        self.monthlyIncomeVsExpensesBarChartFilename = ''
        self.monthlyNetBalanceLineChartFilename = ''
        
class MonthModel:
    def __init__( self ):
        self.start = ''
        self.end = ''
        self.totalIncome = 0
        self.totalExpenses = 0
        self.distinctExpenses = {}
        self.distinctIncomeSources = {}
        self.pathToPieChartFile = ''
        self.pathToBarChartFile = ''

class InvalidResultException( Exception ):
    pass
