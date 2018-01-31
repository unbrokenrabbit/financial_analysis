#!/bin/python3

import time
import datetime

class DateManager:

    def __init__( self ):
        self.dateFormat = '%Y-%m-%d'
        self.yearMonthDateFormat = '%Y-%m'
        
    def getDateFormat( self ):
        return self.dateFormat

    def stringToDate( self, _dateString ):
        return datetime.datetime.strptime( _dateString, self.dateFormat )

    def stringToTimestamp( self, _dateString ):
        return self.stringToDate( _dateString ).timestamp()
        
    def dateToTimestamp( self, _date ):
        return _date.timestamp()

    def timestampToDate( self, _timestamp ):
        #return datetime.datetime.fromtimestamp( _timestamp ).date()
        return datetime.datetime.fromtimestamp( _timestamp )

    def yearMonthStringToDate( self, _yearMonthString ):
        return datetime.datetime.strptime( _yearMonthString, self.yearMonthDateFormat )

    def yearMonthStringToTimestamp( self, _yearMonthString ):
        return self.yearMonthStringToDate( _yearMonthString ).timestamp()
        
    def getMinDate( self ):
        #return datetime.date.min
        return datetime.datetime.min
        
    def getMaxDate( self ):
        #return datetime.date.max
        return datetime.datetime.max

    def getToday( self ):
        #return datetime.date.today()
        return datetime.datetime.today()

    def getDate( self, _year, _month, _day ):
        #return datetime.date( _year, _month, _day )
        return datetime.datetime( _year, _month, _day )

    def advanceToEndOfMonth( self, _date ):
        month = _date.month
        year = _date.year
        if( month == 12 ):
            month = 1
            year += 1
        else:
            month = month + 1
            
        return ( datetime.datetime( year, month, 1 ) - datetime.timedelta( days=1 ) )

    def advanceToNextMonth( self, _date ):
        month = _date.month
        year = _date.year
        day = _date.day
        if( month == 12 ):
            month = 1
            year += 1
        else:
            month = month + 1

        return datetime.datetime( year, month, day )
