import unittest

import os
import sys

# Include some PriceChartingTool modules.
# This assumes that the relative directory from this script is: ../src
thisScriptDir = os.path.dirname(os.path.abspath(__file__))
srcDir = os.path.dirname(thisScriptDir) + os.sep + "src"
if srcDir not in sys.path:
    sys.path.insert(0, srcDir)

from util import Util
from ephemeris import Ephemeris
from lunar_calendar_utils import LunarDate
from lunar_calendar_utils import LunarTimeDelta
from lunar_calendar_utils import LunarCalendarUtils

##############################################################################

class LunarDateTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize Ephemeris (required).
        Ephemeris.initialize()

        # Set the Location (required).

        # Chicago:
        #lon = -87.627777777777
        #lat = 41.8819444444444444

        # Chantilly/Arlington:
        #lon = -77.084444
        #lat = 38.890277

        # New York City:
        lon = -74.0064
        lat = 40.7142

        #Ephemeris.setGeographicPosition(lon, lat, -68)
        Ephemeris.setGeographicPosition(lon, lat)

    def tearDown(self):
        # Close the Ephemeris so it can do necessary cleanups.
        Ephemeris.closeEphemeris()

    def testCreationAllInts(self):
        lunarDate = LunarDate(2016, 3, 0)
        self.assertEqual(lunarDate.year, 2016)
        self.assertEqual(lunarDate.month, 3)
        self.assertEqual(lunarDate.day, 0)

    def testCreationFloatYear(self):
        with self.assertRaises(ValueError):
            lunarDate = LunarDate(2016.2, 3, 0)

    def testCreationFloatMonth(self):
        with self.assertRaises(ValueError):
            lunarDate = LunarDate(2016, 3.5, 0)

    def testCreationFullMoon(self):
        lunarDate = LunarDate(2016, 1, 15)
        self.assertEqual(lunarDate.year, 2016)
        self.assertEqual(lunarDate.month, 1)
        self.assertEqual(lunarDate.day, 15)
        #print("lunarDate == {}".format(lunarDate))
        dt = LunarCalendarUtils.lunarDateToDatetime(lunarDate)
        #print("dt == {}".format(Ephemeris.datetimeToDayStr(dt)))
        pi = Ephemeris.getPlanetaryInfo("MoSu", dt)
        longitude = pi.geocentric['tropical']['longitude']
        #print("longitude == {}".format(longitude))
        self.assertTrue(Util.fuzzyIsEqual(longitude, 180.0, maxDiff=0.0002))

    def testCreationFloatDay(self):
        lunarDate = LunarDate(2016, 3, 0.5)
        self.assertEqual(lunarDate.year, 2016)
        self.assertEqual(lunarDate.month, 3)
        self.assertEqual(lunarDate.day, 0.5)
        #print("lunarDate == {}".format(lunarDate))
        dt = LunarCalendarUtils.lunarDateToDatetime(lunarDate)
        #print("dt == {}".format(Ephemeris.datetimeToDayStr(dt)))
        pi = Ephemeris.getPlanetaryInfo("MoSu", dt)
        longitude = pi.geocentric['tropical']['longitude']
        #print("longitude == {}".format(longitude))
        self.assertTrue(Util.fuzzyIsEqual(longitude, 6.0, maxDiff=0.0002))

    def testCreationInvalidMonth(self):
        with self.assertRaises(ValueError):
            lunarDate = LunarDate(2016, 13, 5)

    def testAdditionWithWrongType(self):
        lunarDateA = LunarDate(2016, 3, 0.5)
        lunarDateB = LunarDate(2016, 5, 23)
        with self.assertRaises(ValueError):
            lunarDateC = lunarDateA + lunarDateB

    def testAdditionWithLunarTimeDeltaYearAdditionNotLeapYear(self):
        lunarDate = LunarDate(2016, 12, 5)
        lunarTimeDelta = LunarTimeDelta(years=1)
        result = lunarDate + lunarTimeDelta
        self.assertEqual(result, LunarDate(2017, 12, 5))

        # Normal wrapping (non-leap year).
        lunarDate = LunarDate(2016, 7, 15)
        lunarTimeDelta = LunarTimeDelta(months=10)
        result = lunarDate + lunarTimeDelta
        self.assertEqual(result, LunarDate(2017, 5, 15))

    def testAdditionWithLunarTimeDeltaYearAdditionLeapYear(self):
        lunarDate = LunarDate(2017, 7, 15)
        lunarTimeDelta = LunarTimeDelta(years=1)
        result = lunarDate + lunarTimeDelta
        self.assertEqual(result, LunarDate(2018, 7, 15))

        # Normal wrapping (leap year).
        lunarDate = LunarDate(2017, 7, 15)
        lunarTimeDelta = LunarTimeDelta(months=10)
        result = lunarDate + lunarTimeDelta
        self.assertEqual(result, LunarDate(2018, 4, 15))

        # This is showing that adding can result in wrapping 
        # of an extra lunar year.
        lunarDate = LunarDate(2017, 13, 5)
        lunarTimeDelta = LunarTimeDelta(years=1)
        result = lunarDate + lunarTimeDelta
        self.assertEqual(result, LunarDate(2019, 1, 5))

        # Adding negative LunarTimeDelta values.
        lunarDate = LunarDate(2017, 13, 5)
        lunarTimeDelta = LunarTimeDelta(years=0, months=-13, days=2)
        result = lunarDate + lunarTimeDelta
        self.assertEqual(result, LunarDate(2016, 12, 7))

    def testSubtraction(self):
        lunarDate = LunarDate(2017, 13, 5)
        lunarTimeDelta = LunarTimeDelta(months=5, days=3)
        result = lunarDate - lunarTimeDelta
        self.assertEqual(result, LunarDate(2017, 8, 2))

        # Test wraping months.
        lunarDate = LunarDate(2017, 13, 5)
        lunarTimeDelta = LunarTimeDelta(months=5, days=9)
        result = lunarDate - lunarTimeDelta
        self.assertEqual(result, LunarDate(2017, 7, 26))

        # Test wraping years.
        lunarDate = LunarDate(2017, 13, 5)
        lunarTimeDelta = LunarTimeDelta(months=13)
        result = lunarDate - lunarTimeDelta
        self.assertEqual(result, LunarDate(2016, 12, 5))

        # Subtracting negative LunarTimeDelta values.
        lunarDate = LunarDate(2017, 13, 5)
        lunarTimeDelta = LunarTimeDelta(years=0, months=-13, days=2)
        result = lunarDate - lunarTimeDelta
        self.assertEqual(result, LunarDate(2019, 1, 3))

    def testEquals(self):
        lunarDateA = LunarDate(2017, 13, 5.0)
        lunarDateB = LunarDate(2017, 13, 5.0)
        self.assertTrue(lunarDateA == lunarDateB)
        lunarDateA = LunarDate(2017, 13, 5.0)
        lunarDateB = LunarDate(2016, 12, 1.0)
        self.assertFalse(lunarDateA == lunarDateB)

    def testNotEquals(self):
        lunarDateA = LunarDate(2017, 13, 5.0)
        lunarDateB = LunarDate(2017, 13, 6.0)
        self.assertTrue(lunarDateA != lunarDateB)
        lunarDateA = LunarDate(2017, 13, 6.0)
        lunarDateB = LunarDate(2017, 13, 6.0)
        self.assertFalse(lunarDateA != lunarDateB)

    def testGreaterThan(self):
        lunarDateA = LunarDate(2017, 13, 8.0)
        lunarDateB = LunarDate(2017, 13, 5.0)
        self.assertTrue(lunarDateA > lunarDateB)

    def testLessThan(self):
        lunarDateA = LunarDate(2017, 13, 1.0)
        lunarDateB = LunarDate(2017, 13, 5.0)
        self.assertTrue(lunarDateA < lunarDateB)

    def testIsLunarLeapYear(self):
        year = 2000
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2001
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2002
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2003
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2004
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2005
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2006
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2007
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2008
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2009
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2010
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2011
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2012
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2013
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2014
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2015
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2016
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2017
        self.assertTrue(LunarDate.isLunarLeapYear(year))
        year = 2018
        self.assertFalse(LunarDate.isLunarLeapYear(year))
        year = 2019
        self.assertFalse(LunarDate.isLunarLeapYear(year))

class LunarTimeDeltaTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize Ephemeris (required).
        Ephemeris.initialize()

        # Set the Location (required).

        # Chicago:
        #lon = -87.627777777777
        #lat = 41.8819444444444444

        # Chantilly/Arlington:
        #lon = -77.084444
        #lat = 38.890277

        # New York City:
        lon = -74.0064
        lat = 40.7142

        #Ephemeris.setGeographicPosition(lon, lat, -68)
        Ephemeris.setGeographicPosition(lon, lat)

    def tearDown(self):
        # Close the Ephemeris so it can do necessary cleanups.
        Ephemeris.closeEphemeris()

    def testAdditionWithLunarTimeDelta(self):
        # Test wrapping months.
        lunarTimeDeltaA = LunarTimeDelta(years=1, months=2, days=3)
        lunarTimeDeltaB = LunarTimeDelta(years=1, months=3, days=29)
        resultTimeDelta = lunarTimeDeltaA + lunarTimeDeltaB
        self.assertTrue(resultTimeDelta == LunarTimeDelta(years=2, months=6, days=2))

        # Test many months, not wrapping years.
        lunarTimeDeltaA = LunarTimeDelta(years=1, months=11, days=3)
        lunarTimeDeltaB = LunarTimeDelta(years=1, months=5, days=29)
        resultTimeDelta = lunarTimeDeltaA + lunarTimeDeltaB
        self.assertTrue(resultTimeDelta == LunarTimeDelta(years=2, months=17, days=2))

    def testSubtractionWithLunarTimeDelta(self):
        # Test wrapping months.
        lunarTimeDeltaA = LunarTimeDelta(years=1, months=2, days=3)
        lunarTimeDeltaB = LunarTimeDelta(years=1, months=3, days=29)
        resultTimeDelta = lunarTimeDeltaA - lunarTimeDeltaB
        self.assertTrue(resultTimeDelta == LunarTimeDelta(years=0, months=-2, days=4))

        lunarTimeDeltaA = LunarTimeDelta(years=1, months=2, days=3)
        lunarTimeDeltaB = LunarTimeDelta(years=0, months=3, days=4)
        resultTimeDelta = lunarTimeDeltaA - lunarTimeDeltaB
        self.assertTrue(resultTimeDelta == LunarTimeDelta(years=1, months=-2, days=29))

        lunarTimeDeltaA = LunarTimeDelta(years=5, months=5, days=3)
        lunarTimeDeltaB = LunarTimeDelta(years=0, months=4, days=4)
        resultTimeDelta = lunarTimeDeltaA - lunarTimeDeltaB
        self.assertTrue(resultTimeDelta == LunarTimeDelta(years=5, months=0, days=29))

        # Test many months, not wrapping years.
        lunarTimeDeltaA = LunarTimeDelta(years=1, months=11, days=3)
        lunarTimeDeltaB = LunarTimeDelta(years=0, months=50, days=1)
        resultTimeDelta = lunarTimeDeltaA - lunarTimeDeltaB
        self.assertTrue(resultTimeDelta == LunarTimeDelta(years=1, months=-39, days=2))

class LunarCalendarUtilsTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize Ephemeris (required).
        Ephemeris.initialize()

        # Set the Location (required).

        # Chicago:
        #lon = -87.627777777777
        #lat = 41.8819444444444444

        # Chantilly/Arlington:
        #lon = -77.084444
        #lat = 38.890277

        # New York City:
        lon = -74.0064
        lat = 40.7142

        #Ephemeris.setGeographicPosition(lon, lat, -68)
        Ephemeris.setGeographicPosition(lon, lat)

    def tearDown(self):
        # Close the Ephemeris so it can do necessary cleanups.
        Ephemeris.closeEphemeris()

    def testDatetimeToLunarDate(self):
        # TODO_rluu: Write this method.
        pass

    def testGetNisan1DatetimeForYear(self):
        # TODO_rluu: Write this method.
        pass

    def testLunarDateToDatetime(self):
        # TODO_rluu: Write this method.
        pass

    def testIsSolarEclipse(self):
        # TODO_rluu: Write this method.
        pass

    def testIsLunarEclipse(self):
        # TODO_rluu: Write this method.
        pass

##############################################################################

if __name__ == "__main__":
    unittest.main()

##############################################################################
