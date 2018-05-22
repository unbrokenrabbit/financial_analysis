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

class InvalidResultException( Exception ):
    pass

