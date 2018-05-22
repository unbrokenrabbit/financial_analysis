#!/bin/python3

class IncomeVsExpenseChartBuilder:
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



