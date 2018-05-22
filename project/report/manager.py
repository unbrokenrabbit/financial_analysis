#!/bin/python3

from subprocess import call
import json
from .section.incomevsexpenses import model
from .section import balance
from . import utilities

class ReportManager:

    def report( self, _configFile, _outputFile ):
        print( 'reading report config from', _configFile )
        print( 'publishing report to', _outputFile )
    
        reportConfig = {}
        with open( _configFile ) as jsonConfig:
            reportConfig = json.load( jsonConfig )
    
        report = reportConfig[ 'report' ]
    
        # Create a workspace for temporary files
        utils = utilities.Utilities()
        workspaceDirectory = utils.getWorkspaceDirectory()
        call( [ 'mkdir', workspaceDirectory ] )
    
        latexFilenamePrefix = 'report'
        latexFilenameExtension = 'tex'
        latexFilename = workspaceDirectory + '/' + latexFilenamePrefix + '.' + latexFilenameExtension
        latexOutputFile = open( latexFilename, 'w' )
    
        self.writeDocumentHeader( latexOutputFile )
    
        for section in report[ 'sections' ]:
            sectionType = section[ 'type' ]
            if( sectionType == 'balance' ):
                sectionManager = balance.Manager()
                sectionModel = sectionManager.createSectionModel( section )
                sectionManager.writeSectionToFile( latexOutputFile, sectionModel )
            elif( sectionType == 'income_vs_expenses' ):
                builder = model.IncomeVsExpensesSectionModelBuilder()
                sectionModel = builder.buildSectionModel( section )
                latexWriter = latex.LatexFileBuilder()
                latexWriter.writeIncomeVsExpensesSectionToFile( latexOutputFile, sectionModel )
            else:
                print( 'Unknown section type:', sectionType )
    
        self.writeDocumentFooter( latexOutputFile )
        latexOutputFile.close()
    
        call( [ 'pdflatex', '-output-format=pdf', ( '-output-directory=' + workspaceDirectory ), latexFilename ] )
        call( [ 'mv', ( workspaceDirectory + '/' + latexFilenamePrefix + '.pdf' ), _outputFile ] )
        #call( [ 'rm', '-r', workspaceDirectory ] )

    def writeDocumentHeader( self, _outputFile ):
        _outputFile.write( '\\documentclass{article}\n' )
        _outputFile.write( '\\usepackage{graphicx}\n' )
        _outputFile.write( '\\usepackage[usenames, dvipsnames]{color}\n' )
        _outputFile.write( '\\begin{document}\n' )

    def writeDocumentFooter( self, _outputFile ):
        _outputFile.write( '\\end{document}\n' )

