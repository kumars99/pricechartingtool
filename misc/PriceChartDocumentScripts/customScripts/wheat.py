#!/usr/bin/env python3
##############################################################################
# Description:
#
#   Module for adding various PriceBarChartArtifacts to a
#   PriceChartDocumentData object that are relevant to a Wheat
#   chart.
#
##############################################################################

# For logging.
import logging

# For timestamps and timezone information.
import datetime
import pytz

# For PyQt UI classes.
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Include some PriceChartingTool modules.
from ephemeris import Ephemeris
from data_objects import *
from pricebarchart import PriceBarChartGraphicsScene

# Holds functions for adding artifacts for various aspects.
from planetaryCombinationsLibrary import PlanetaryCombinationsLibrary

##############################################################################
# Global variables
##############################################################################

# For logging.
#logLevel = logging.DEBUG
logLevel = logging.INFO
logging.basicConfig(format='%(levelname)s: %(message)s')
moduleName = globals()['__name__']
log = logging.getLogger(moduleName)
log.setLevel(logLevel)

# Start and ending timestamps for drawing.
#startDt = datetime.datetime(year=1508, month=1, day=1,n
#                            hour=0, minute=0, second=0,
#                            tzinfo=pytz.utc)
startDt = datetime.datetime(year=1968, month=1, day=1,
                            hour=0, minute=0, second=0,
                            tzinfo=pytz.utc)
#startDt = datetime.datetime(year=2001, month=1, day=1,
#                            hour=0, minute=0, second=0,
#                            tzinfo=pytz.utc)
#startDt = datetime.datetime(year=2011, month=12, day=18,
#                            hour=0, minute=0, second=0,
#                            tzinfo=pytz.utc)

#endDt   = datetime.datetime(year=2013, month=1, day=1,
#                            hour=0, minute=0, second=0,
#                            tzinfo=pytz.utc)
endDt   = datetime.datetime(year=2012, month=1, day=1,
                            hour=0, minute=0, second=0,
                            tzinfo=pytz.utc)
#endDt   = datetime.datetime(year=2020, month=1, day=1,
#                            hour=0, minute=0, second=0,
#                            tzinfo=pytz.utc)

# High and low price limits for drawing the vertical lines.
highPrice = 1200.0
lowPrice = 100.0

##############################################################################

def processPCDD(pcdd, tag):
    """Module for adding various PriceBarChartArtifacts that are
    relevant to the Wheat chart.  The tag str used for the created
    artifacts is based the name of the function that is being called,
    without the 'add' string at the beginning.
    
    Arguments:
    pcdd - PriceChartDocumentData object that will be modified.
    tag  - str containing the tag.
           This implementation does not use this value.

    Returns:
    0 if the changes are to be saved to file.
    1 if the changes are NOT to be saved to file.
    """

    global highPrice
    global lowPrice
    
    # Return value.
    rv = 0

    #success = PlanetaryCombinationsLibrary.\
    #    addHelioSaturnUranus15xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoSaturnUranus15xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoVenusMars15xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioVenusMars15xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioVenusMars90xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioVenus265DegVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    
    
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioVenusJupiter120xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioMars150NeptuneVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioNeptune150MarsVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioVenus150NeptuneVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addHelioNeptune150VenusVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoVenusSaturn120xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoMarsJupiter30xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoMarsSaturn120xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoMercuryJupiter90xVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice)

    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetCrossingLongitudeDegVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "geocentric", "sidereal", "Venus", 358)
    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetCrossingLongitudeDegVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "geocentric", "sidereal", "Mars", 297)

    degreeValue = 180
    success = PlanetaryCombinationsLibrary.\
        addLongitudeAspectVerticalLines(\
        pcdd, startDt, endDt, highPrice, lowPrice,
        "Mars", "Uranus",
        "geocentric", "sidereal", degreeValue)

    #divisor = 13
    #incrementSize = 14.4 # 360 / divisor
    #for i in range(divisor):
    #    if i == 0:
    #        continue
    #    degreeValue = i * incrementSize
    #    success = PlanetaryCombinationsLibrary.\
    #        addLongitudeAspectVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "Venus", "Mars",
    #        "geocentric", "sidereal", degreeValue)
    
    #divisor = 5
    #incrementSize = 72 # 360 / divisor
    #for i in range(divisor):
    #    if i == 0:
    #        continue
    #    degreeValue = i * incrementSize
    #    success = PlanetaryCombinationsLibrary.\
    #        addLongitudeAspectVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "Venus", "Mars",
    #        "geocentric", "sidereal", degreeValue)
    
    #divisor = 5
    #incrementSize = 72 # 360 / divisor
    #for i in range(divisor):
    #    degreeValue = i * incrementSize
    #    success = PlanetaryCombinationsLibrary.\
    #        addPlanetCrossingLongitudeDegVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "geocentric", "tropical",
    #        "Venus", degreeValue)

    #divisor = 9
    #incrementSize = 40 # 360 / divisor
    #for i in range(divisor):
    #    degreeValue = (3.3333333333 / 2.0) + (i * incrementSize)
    #    success = PlanetaryCombinationsLibrary.\
    #        addPlanetCrossingLongitudeDegVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "heliocentric", "sidereal",
    #        "Venus", degreeValue)

    #divisor = 12
    #incrementSize = 30 # 360 / divisor
    #for i in range(divisor):
    #    degreeValue = 15 + (i * incrementSize)
    #    success = PlanetaryCombinationsLibrary.\
    #        addPlanetCrossingLongitudeDegVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "geocentric", "sidereal",
    #        "Venus", degreeValue)

    #divisor = 24
    #incrementSize = 360 / divisor # 15
    #for i in range(divisor):
    #    degreeValue = i * incrementSize
    #    success = PlanetaryCombinationsLibrary.\
    #        addPlanetCrossingLongitudeDegVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "geocentric", "tropical",
    #        "Sun", degreeValue)
    
    #divisor = 25
    #incrementSize = 360 / divisor # 15
    #for i in range(divisor):
    #    degreeValue = i * incrementSize
    #    success = PlanetaryCombinationsLibrary.\
    #        addPlanetCrossingLongitudeDegVerticalLines(\
    #        pcdd, startDt, endDt, highPrice, lowPrice,
    #        "geocentric", "tropical",
    #        "Venus", degreeValue)
    
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Mars",
    #    "geocentric", "sidereal", 54)
    
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 0)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 15)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 30)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 45)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 60)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 75)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 90)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 105)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 120)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 135)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 150)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 165)
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 180)
    
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Earth",
    #    "heliocentric", "sidereal", 10)
    
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Mars",
    #    "geocentric", "sidereal", 17.5)
    
    #success = PlanetaryCombinationsLibrary.\
    #    addLongitudeAspectVerticalLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "Mars",
    #    "geocentric", "sidereal", 45)
    
    
    stepSizeTd = datetime.timedelta(days=3)
    #highPrice = 800.0
    #highPrice = 600.0
    #lowPrice = 600.0
    #lowPrice = 300.0

    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mercury", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mars", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Uranus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="MeanOfFive", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoLongitudeVelocityLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="CycleOfEight", 
    #    color=None, stepSizeTd=stepSizeTd)


    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice=700, lowPrice=660,
    #    planetName="Moon", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mercury", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Mars", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Jupiter", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Saturn", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Uranus", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Neptune", 
    #    color=None, stepSizeTd=stepSizeTd)
    #success = PlanetaryCombinationsLibrary.addGeoDeclinationLines(\
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Pluto", 
    #    color=None, stepSizeTd=stepSizeTd)

    
    p = 1000
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H1")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H2")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H3")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H4")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H5")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H6")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H7")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H8")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H9")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H10")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H11")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="H12")
    #p += 20
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Sun")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Moon")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Mercury")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Venus")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Mars")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Jupiter")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Saturn")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Uranus")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Neptune")
    #p += 200
    #success = PlanetaryCombinationsLibrary.\
    #    addTimeMeasurementAndTiltedTextForNakshatraTransits(
    #    pcdd, startDt, endDt, price=p, planetName="Pluto")
    #p += 200



    #success = PlanetaryCombinationsLibrary.\
    #    addZeroDeclinationVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addDeclinationVelocityPolarityChangeVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addGeoLongitudeElongationVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
     
    success = PlanetaryCombinationsLibrary.\
        addGeoLongitudeElongationVerticalLines(
        pcdd, startDt, endDt, highPrice, lowPrice, planetName="Mercury")
     
    #success = PlanetaryCombinationsLibrary.\
    #    addContraparallelDeclinationAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addParallelDeclinationAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetOOBVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus")
    
    #success =  PlanetaryCombinationsLibrary.\
    #    addGeoLatitudeLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus")
    
    #success =  PlanetaryCombinationsLibrary.\
    #    addZeroLatitudeVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planetName="Venus")

    #success = PlanetaryCombinationsLibrary.\
    #    addLatitudeVelocityPolarityChangeVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice, planetName="Venus")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addContraparallelLatitudeAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addParallelLatitudeAspectVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    planet1Name="Venus", planet2Name="Mars")
    
    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetLongitudeTraversalIncrementsVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "geocentric", "sidereal", 
    #    planetEpocDt=datetime.datetime(year=1976, month=4, day=1,
    #                                   hour=13, minute=0, second=0,
    #                                   tzinfo=pytz.utc),
    #    degreeIncrement=18)

    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetLongitudeTraversalIncrementsVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Venus", "heliocentric", "sidereal", 
    #    planetEpocDt=datetime.datetime(year=1970, month=3, day=21,
    #                                   hour=0, minute=0, second=0,
    #                                   tzinfo=pytz.utc),
    #    degreeIncrement=30)

    #success = PlanetaryCombinationsLibrary.\
    #    addPlanetLongitudeTraversalIncrementsVerticalLines(
    #    pcdd, startDt, endDt, highPrice, lowPrice,
    #    "Sun", "geocentric", "tropical", 
    #    planetEpocDt=datetime.datetime(year=1970, month=3, day=21,
    #                                   hour=6, minute=0, second=0,
    #                                   tzinfo=pytz.utc),
    #    degreeIncrement=15)

    if success == True:
        log.debug("Success!")
        rv = 0
    else:
        log.debug("Failure!")
        rv = 1

    return rv

