#!/bin/python3

"""Usage:
    analyze import <input-file> <account> [--format=FORMAT]
    analyze report <report-config-file> <output-file>
    analyze import-tags <tags-file>
    analyze reset-tags
    analyze list-formats
    analyze delete <account>
"""

from docopt import docopt
import numpy
import report
import tag
import transaction

def parseArguments( _usageString ):
    arguments = docopt( _usageString, version = '1.0.0' )

    if( arguments[ 'import' ] ):
        transactionManager = transaction.TransactionManager()
        inputFileFormat = 'chase_csv_alpha' if ( arguments[ '--format' ] == None ) else arguments[ '--format' ]
        transactionManager.importTransactions( arguments[ '<input-file>' ], inputFileFormat, arguments[ '<account>' ] )
    elif( arguments[ 'report' ] ):
        reporter = report.Reporter()
        reporter.report( arguments[ '<report-config-file>' ], arguments[ '<output-file>' ] )
    elif( arguments[ 'import-tags' ] ):
        tagger = tag.Tagger()
        tagger.importTags( arguments[ '<tags-file>' ] )
    elif( arguments[ 'list-formats' ] ):
        listFormats()
    elif( arguments[ 'delete' ] ):
        transactionManager = transaction.TransactionManager()
        transactionManager.deleteAccountTransactions( arguments[ '<account>' ] )

def listFormats():
    formatsMessage = ''
    formatsMessage += "input file formats:\n"
    formatsMessage += "    chase-csv-alpha\n"
    formatsMessage += "output file formats:\n"
    formatsMessage += "    pdf\n"

    print( formatsMessage )
   
parseArguments( __doc__ )

print( 'done' )


