#!/bin/python3

from pymongo import MongoClient
import dates
import pymongo
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot
import numpy as np
from .. import utilities

class Manager:
    
    def createSectionModel( self, _sectionParameters ):
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

    def createDistinctExpensesBarChart( self, _distinctExpenses, _filename ):
        print( "creating distinct expenses bar chart" )

        yAxis = []
        for index in range( len( _distinctExpenses ) ):
            yAxis.append( index )
        amounts = []
        labels = []
        for distinctExpense in _distinctExpenses:
            prettyExpense = distinctExpense[ 'tag' ].replace( 'expense_', '' ).replace( '_', ' ' )
            labels.append( prettyExpense )
            amounts.append( distinctExpense[ 'total' ] * ( -1 ) )
         
        pyplot.bar( yAxis, amounts, align='center', alpha=0.5 )
        pyplot.xticks( yAxis, labels, rotation=90 )
        pyplot.ylabel( 'Amount' )
        pyplot.tight_layout()

        utils = utilities.Utilities()
        pathToFile = utils.getWorkspaceDirectory() + "/" + _filename
        pyplot.savefig( pathToFile )
        pyplot.clf()

        return pathToFile

    def createMonthlyIncomeVsExpensesBarChart( self, _months ):
        print( "creating monthly income vs expenses bar chart" )

        incomeTotals = []
        expensesTotals = []
        labels = []
        for month in _months:
            incomeTotals.append( month.totalIncome )
            expensesTotals.append( month.totalExpenses * ( -1 ) )

            monthStart = month.start
            dateManager = dates.DateManager()
            
            label = dateManager.monthAsString( monthStart.month ) + ' ' + str( monthStart.year )
            labels.append( label )
         
        fig, ax = pyplot.subplots()
        index = np.arange( len( incomeTotals ) )
        bar_width = 0.35
        opacity = 0.8
         
        rects1 = pyplot.bar(
            index,
            incomeTotals,
            bar_width,
            alpha=opacity,
            color='#339966',
            label='income' )
         
        rects2 = pyplot.bar(
            index + bar_width,
            expensesTotals,
            bar_width,
            alpha=opacity,
            color='#993333',
            label='expenses' )
         
        pyplot.xlabel( 'Month' )
        pyplot.ylabel( 'Amount' )
        pyplot.title( 'Income vs Expenses' )
        pyplot.xticks( index + bar_width, labels )
        pyplot.legend()
         
        pyplot.tight_layout()

        utils = utilities.Utilities()
        pathToFile = utils.getWorkspaceDirectory() + "/monthly_income_vs_expenses_bar_graph.png"
        pyplot.savefig( pathToFile )
        pyplot.clf()

        return pathToFile

    def createNetBalanceLineChart( self, _months ):
        print( "creating monthly net balance line chart" )

        x = []
        y = []
        labels = []
        index = 0
        for month in _months:
            print( "month:", month )
            x.append( index )
            index += 1
            netSpending = month.totalIncome + month.totalExpenses
            y.append( netSpending )

            dateManager = dates.DateManager()

            label = dateManager.monthAsString( month.start.month ) + '-' + str( month.start.year )
            labels.append( label )
    
        pyplot.plot( x, y )
        pyplot.xticks( x, labels )
        pyplot.ylabel( 'net balance' )
        
        utils = utilities.Utilities()
        pathToFile = utils.getWorkspaceDirectory() + "/net_balance.png"
        pyplot.savefig( pathToFile )
        pyplot.clf()

        return pathToFile

    def createDistinctExpensesPieChart( self, _distinctExpenses, _totalExpenses, _filename ):
        print( "creating distinct expenses pie chart" )

        labels = []
        sizes = []
        for distinctExpense in _distinctExpenses:
            labels.append( distinctExpense[ 'tag' ] )
            sizes.append( distinctExpense[ 'total' ] / _totalExpenses )
         
            pyplot.pie( sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
             
            pyplot.axis('equal')

            utils = utilities.Utilities()
            pyplot.savefig( utils.getWorkspaceDirectory() + "/" + _filename )
            pyplot.clf()

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

    def writeSectionToFile( self, _outputFile, _sectionModel ):
        print( "creating LaTeX report output file:", _outputFile.name )

        _outputFile.write( '\\section{Income vs Expenses}' )

        self.writeMonthlyEvaluationsToFile( _outputFile, _sectionModel.monthlyEvaluations )

    def writeMonthlyEvaluationsToFile( self, _outputFile, _monthlyEvaluations ):
        for monthlyEvaluation in _monthlyEvaluations:
            self.writeMonthlyEvaluationToFile( _outputFile, monthlyEvaluation )

    def writeMonthlyEvaluationToFile( self, _outputFile, _monthlyEvaluation ):
        dateManager = dates.DateManager()

        startDate = _monthlyEvaluation.startDate
        startDateString = dateManager.monthAsString( startDate.month ) + '-' + str( startDate.year )
        endDate = _monthlyEvaluation.endDate
        endDateString = dateManager.monthAsString( endDate.month ) + '-' + str( endDate.year )

        dateLine = "\n\\subsection{Monthly Evaluation: " + startDateString + " to " + endDateString + "}"
        _outputFile.write( dateLine  )

        incomeVsExpensesBarChartFile = _monthlyEvaluation.monthlyIncomeVsExpensesBarChartFilename
        _outputFile.write( "\n\\includegraphics[width=\linewidth]{" + incomeVsExpensesBarChartFile + "}" )

        netBalanceLineChartFilename = _monthlyEvaluation.monthlyNetBalanceLineChartFilename
        _outputFile.write( "\n\\includegraphics[width=\linewidth]{" + netBalanceLineChartFilename + "}" )

        _outputFile.write( "\n\\newpage" )

        self.writeMonthsToFile( _outputFile, _monthlyEvaluation.months )

    def writeMonthsToFile( self, _outputFile, _months ):
        for month in _months:
            self.writeMonthToFile( _outputFile, month )

    def writeMonthToFile( self, _outputFile, _month ):
        monthStart = _month.start

        dateManager = dates.DateManager()
        title = str( monthStart.year ) + " " + dateManager.monthAsString( monthStart.month )
        _outputFile.write( "\n\\subsubsection{" + title + "}" )

        self.writeDistinctIncomeVsExpensesListToFile( _outputFile, _month )

        _outputFile.write( "\n\\newpage" )
        _outputFile.write( "\n\\includegraphics[width=\linewidth]{" + _month.pathToBarChartFile + "}" )
        _outputFile.write( "\n\\newpage" )

    def writeDistinctIncomeVsExpensesListToFile( self, _outputFile, _month ):
        delta = _month.totalIncome + _month.totalExpenses

        _outputFile.write( "\n\\textbf{income}\\\\" )

        for distinctIncomeSource in _month.distinctIncomeSources:
            prettyIncomeSource = distinctIncomeSource[ 'tag' ].replace( 'income_', '' ).replace( '_', ' ' )
            incomeAmount = '{0:.2f}'.format( distinctIncomeSource[ 'total' ] )
            _outputFile.write( "\n" + prettyIncomeSource + "\\hfill " + incomeAmount + "\\\\" )

        _outputFile.write( "\n\\noindent\\rule{\\textwidth}{1pt}" )
        _outputFile.write( "\n\\textbf{total income:} \\hfill " + '{0:.2f}'.format( _month.totalIncome ) + "\\\\" )
        _outputFile.write( "\n\\noindent\\rule{\\textwidth}{1pt}" )
        _outputFile.write( "\n\\textbf{expenses}\\\\" )

        for distinctExpense in _month.distinctExpenses:
            prettyExpense = distinctExpense[ 'tag' ].replace( 'expense_', '' ).replace( '_', ' ' )
            expenseAmount = '{0:.2f}'.format( distinctExpense[ 'total' ] )
            _outputFile.write( "\n" + prettyExpense + "\\hfill " + expenseAmount + "\\\\" )

        _outputFile.write( "\n\\noindent\\rule{\\textwidth}{1pt}" )
        _outputFile.write( "\n\\textbf{total expenses} \\hfill " + '{0:.2f}'.format( _month.totalExpenses ) + "\\\\" )
        _outputFile.write( "\n\\noindent\\rule{\\textwidth}{1pt}" )

        if( delta > 0 ):
            _outputFile.write( "\n\\textbf{net}:\\hfill {\\color{ForestGreen} " + '{0:.2f}'.format( delta ) + "}\\\\" )
        else:
            _outputFile.write( "\n\\textbf{net}:\\hfill {\\color{BrickRed} " + '{0:.2f}'.format( delta ) + "}\\\\" )

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

