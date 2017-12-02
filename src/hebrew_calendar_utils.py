

# For logging.
import logging

import datetime
import pytz
import convertdate

class HebrewCalendarUtils:
    """Contains some methods to help with working with the Hebrew calendar."""

    @staticmethod
    def datetimeToHebrewDateStr(dt):
        """Converts the given datetime.datetime to a Hebrew date str.
        """

        hebrewDateTuple = \
            convertdate.hebrew.from_gregorian(dt.year, dt.month, dt.day)

        hebrewYear = hebrewDateTuple[0]
        hebrewMonth = hebrewDateTuple[1]
        hebrewDay = hebrewDateTuple[2]

        rv = "{: >4}, {: >2}, {: >2}".\
            format(hebrewYear,
                   hebrewMonth,
                   hebrewDay)

        return rv

    @staticmethod
    def datetimeToHebrewMonthDayStr(dt):
        """Converts the given datetime.datetime to a Hebrew month and date str.
        """

        hebrewDateTuple = \
            convertdate.hebrew.from_gregorian(dt.year, dt.month, dt.day)

        hebrewYear = hebrewDateTuple[0]
        hebrewMonth = hebrewDateTuple[1]
        hebrewDay = hebrewDateTuple[2]

        rv = "{}: {}".\
            format(HebrewCalendarUtils.monthNumberToMonthName(hebrewMonth),
                   hebrewDay)

        return rv

    @staticmethod
    def monthNumberToMonthName(monthNumber):
        """Converts the given hebrew month number to the month name"

        Arguments:
        monthNumber - int for the month number, where 1 represents .

        Returns:
        str value holding the month name.  If the input is
        invalid, then None is returned.
        """

        rv = None

        if monthNumber == 1:
            rv = "Nisan"
        elif monthNumber == 2:
            rv = "Iyar"
        elif monthNumber == 3:
            rv = "Sivan"
        elif monthNumber == 4:
            rv = "Tammuz"
        elif monthNumber == 5:
            rv = "Av"
        elif monthNumber == 6:
            rv = "Elul"
        elif monthNumber == 7:
            rv = "Tishri"
        elif monthNumber == 8:
            rv = "Marheshvan"
        elif monthNumber == 9:
            rv = "Kislev"
        elif monthNumber == 10:
            rv = "Tevet"
        elif monthNumber == 11:
            rv = "Shevat"
        elif monthNumber == 12:
            rv = "Adar I"
        elif monthNumber == 13:
            rv = "Adar II"
        else:
            rv = None

        return rv


class HebrewLunarCalendar:
    """Class for calculating Hebrew calendar dates and holidays.
    These dates are the holidays reckoned from the astronomical lunar
    phases (30 phases in total).
    Many of the methods of this class take in a gregorianYear,
    which is the year for which the date of the Nisan 1 occurs.
    """

    @staticmethod
    def getPesachForYear(gregorianYear):
        """Also known as Passover."""
        pass

    @staticmethod
    def getFeastOfUnleavenBreadForYear(gregorianYear):
        pass

    @staticmethod
    def getFeastOfFirstFruitsForYear(gregorianYear):
        pass

    @staticmethod
    def getRoshHashanahForYear(gregorianYear):
        pass

    @staticmethod
    def getKomKippurForYear(gregorianYear):
        pass

    @staticmethod
    def getSukkotForYear(gregorianYear):
        pass

    @staticmethod
    def getHanukkahForYear(gregorianYear):
        pass

    @staticmethod
    def yearHas13Months(gregorianYear):
        """Returns a boolean for whether or not the given gregorian
        calendar year has 13 months."""

        pass
