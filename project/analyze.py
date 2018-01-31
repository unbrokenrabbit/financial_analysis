#!/bin/python3

"""Usage:
    analyze import <input-file> <account> [--format=FORMAT | --account-type=ACCOUNT-TYPE]
    analyze report <report-config-file> <output-file>
    analyze import-tags <tags-file>
    analyze reset-tags
    analyze list-formats
    analyze list-tag-stats
    analyze delete-account <account>
    analyze delete-transaction <transaction-id>
"""

#analyze import <input-file> <account> [--format=FORMAT | --account-type=ACCOUNT-TYPE]

from docopt import docopt
import numpy
import report
import tag
import transaction

def parseArguments( _usageString ):
    arguments = docopt( _usageString, version = '1.0.0' )

    print( '' )

    # DEBUG
    #print( 'arguments:' )
    #print( arguments )

    if( arguments[ 'import' ] ):
        transactionManager = transaction.TransactionManager()
        #inputFileFormat = 'chase_csv_alpha' if ( arguments[ '--format' ] == None ) else arguments[ '--format' ]
        #accountType = 'checking' if ( arguments[ '--account-type' ] == None ) else arguments[ '--account-type' ]
        #transactionManager.importTransactions( arguments[ '<input-file>' ], inputFileFormat, arguments[ '<account>' ], accountType )
        transactionManager.importTransactions( arguments[ '<input-file>' ], arguments[ '<account>' ] )
    elif( arguments[ 'report' ] ):
        reporter = report.Reporter()
        reporter.report( arguments[ '<report-config-file>' ], arguments[ '<output-file>' ] )
    elif( arguments[ 'import-tags' ] ):
        tagger = tag.Tagger()
        tagger.importTags( arguments[ '<tags-file>' ] )
    elif( arguments[ 'list-formats' ] ):
        listFormats()
    elif( arguments[ 'list-tag-stats' ] ):
        tagger = tag.Tagger()
        tagger.displayTagStatistics()
    elif( arguments[ 'delete-account' ] ):
        transactionManager = transaction.TransactionManager()
        transactionManager.deleteAccountTransactions( arguments[ '<account>' ] )
    elif( arguments[ 'delete-transaction' ] ):
        transactionManager = transaction.TransactionManager()
        transactionManager.deleteTransaction( arguments[ '<transaction-id>' ] )

def listFormats():
    formatsMessage = ''
    formatsMessage += "input file formats:\n"
    formatsMessage += "    chase-csv-alpha\n"
    formatsMessage += "output file formats:\n"
    formatsMessage += "    pdf\n"

    print( formatsMessage )
   
parseArguments( __doc__ )

print( 'done' )


