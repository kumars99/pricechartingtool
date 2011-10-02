
# For line separator.
import os

# For copy.deepcopy().
import copy

# For logging.
import logging
import logging.config

# For timestamps and timezone information.
import datetime
import pytz

# For PyQt UI classes.
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# For QSettings keys.
from settings import SettingsKeys

# For PriceBars and artifacts in the chart.
from data_objects import BirthInfo
from data_objects import PriceBar
from data_objects import MusicalRatio
from data_objects import PriceBarChartBarCountArtifact
from data_objects import PriceBarChartTimeMeasurementArtifact
from data_objects import PriceBarChartTimeModalScaleArtifact
from data_objects import PriceBarChartPriceModalScaleArtifact
from data_objects import PriceBarChartTextArtifact
from data_objects import PriceBarChartPriceTimeInfoArtifact
from data_objects import PriceBarChartPriceMeasurementArtifact
from data_objects import PriceBarChartTimeRetracementArtifact
from data_objects import PriceBarChartPriceRetracementArtifact
from data_objects import PriceBarChartPriceTimeVectorArtifact
from data_objects import PriceBarChartLineSegmentArtifact
from data_objects import PriceBarChartOctaveFanArtifact
from data_objects import PriceBarChartFibFanArtifact
from data_objects import PriceBarChartGannFanArtifact
from data_objects import PriceBarChartVimsottariDasaArtifact
from data_objects import PriceBarChartAshtottariDasaArtifact

from data_objects import PriceBarChartScaling

from dialogs import TimestampEditWidget

from widgets import ColorEditPushButton

# For formatting datetime.datetime to string.
from ephemeris import Ephemeris

# This file contains the edit widgets and dialogs for editing the
# fields in various PriceBarChartArtifact objects within the context
# of a PriceBarChart.


class PriceBarChartBarCountArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartBarCountArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartBarCountArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartBarCountArtifact object.

        Arguments:
        artifact - PriceBarChartBarCountArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartBarCountArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartBarCountArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.priceLocationValueLabel = QLabel("Artifact location (in price):")
        self.priceLocationValueSpinBox = QDoubleSpinBox()
        self.priceLocationValueSpinBox.setDecimals(4)
        self.priceLocationValueSpinBox.setMinimum(0.0)
        self.priceLocationValueSpinBox.setMaximum(999999999.0)

        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("BarCount Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("BarCount End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.priceLocationValueLabel, r, 0, al)
        self.gridLayout.addWidget(self.priceLocationValueSpinBox, r, 1, al)
        r += 1

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addWidget(self.startPointDatetimeLocationWidget)
        self.layout.addWidget(self.endPointDatetimeLocationWidget)
        
        self.groupBox.setLayout(self.layout)

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.priceLocationValueSpinBox.setReadOnly(self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartBarCountArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartBarCountArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))

        locationPointY = self.artifact.startPointF.y()
        locationPointPrice = self.convertObj.sceneYPosToPrice(locationPointY)
        self.priceLocationValueSpinBox.setValue(locationPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)
        
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartBarCountArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.

        price = self.priceLocationValueSpinBox.value()
        y = self.convertObj.priceToSceneYPos(price)

        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()
                          
        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        posF = QPointF(startPointX, y)
        startPointF = QPointF(startPointX, y)
        endPointF = QPointF(endPointX, y)

        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)

        self.log.debug("Exiting saveValues()")


    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartBarCountArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartBarCountArtifact.
    """

    def __init__(self,
                 priceBarChartBarCountArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartBarCountArtifact.
        
        Note: The 'priceBarChartBarCountArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartBarCountArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartBarCountArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartBarCountArtifact Data")

        # Check input.
        if not isinstance(priceBarChartBarCountArtifact,
                          PriceBarChartBarCountArtifact):
            self.log.error("Input type invalid to " + 
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartBarCountArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartBarCountArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartBarCountArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartBarCountArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact



class PriceBarChartTimeMeasurementArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartTimeMeasurementArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartTimeMeasurementArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartTimeMeasurementArtifact object.

        Arguments:
        artifact - PriceBarChartTimeMeasurementArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartTimeMeasurementArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag

        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()
        self.groupBoxPage3 = self._createGroupBoxPage3()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")
        self.tabWidget.addTab(self.groupBoxPage3, "Page 3")
        
        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        
        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(\
            self._handleFontEditButtonClicked)
        
        self.groupBoxPage2CheckAllButton.clicked.connect(\
            self._handleGroupBoxPage2CheckAllButtonClicked)
        self.groupBoxPage2UncheckAllButton.clicked.connect(\
            self._handleGroupBoxPage2UncheckAllButtonClicked)
        
        self.groupBoxPage3CheckAllButton.clicked.connect(\
            self._handleGroupBoxPage3CheckAllButtonClicked)
        self.groupBoxPage3UncheckAllButton.clicked.connect(\
            self._handleGroupBoxPage3UncheckAllButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)


    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """


        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartTimeMeasurementArtifact Data (page 1):")
        
        lineEditWidth = 420

        # Create the edit widgets that will go on this page.
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.priceLocationValueLabel = QLabel("Artifact location (in price):")
        self.priceLocationValueSpinBox = QDoubleSpinBox()
        self.priceLocationValueSpinBox.setDecimals(4)
        self.priceLocationValueSpinBox.setMinimum(0.0)
        self.priceLocationValueSpinBox.setMaximum(999999999.0)

        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("TimeMeasurement Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("TimeMeasurement End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.fontLabel, r, 0, al)
        gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.priceLocationValueLabel, r, 0, al)
        gridLayout.addWidget(self.priceLocationValueSpinBox, r, 1, al)
        r += 1

        # Put all the layouts together.
        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addWidget(self.startPointDatetimeLocationWidget)
        layout.addWidget(self.endPointDatetimeLocationWidget)
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1


    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartTimeMeasurementArtifact Data (page 2):")

        # Create the QCheckBox widgets going on this page.
        self.showBarsTextFlagCheckBox = \
            QCheckBox("Show Bars Text")
        self.showSqrtBarsTextFlagCheckBox = \
            QCheckBox("Show Sqrt Bars Text")
        self.showSqrdBarsTextFlagCheckBox = \
            QCheckBox("Show Sqrd Bars Text")
        self.showHoursTextFlagCheckBox = \
            QCheckBox("Show Hours Text")
        self.showSqrtHoursTextFlagCheckBox = \
            QCheckBox("Show Sqrt Hours Text")
        self.showSqrdHoursTextFlagCheckBox = \
            QCheckBox("Show Sqrd Hours Text")
        self.showDaysTextFlagCheckBox = \
            QCheckBox("Show Days Text")
        self.showSqrtDaysTextFlagCheckBox = \
            QCheckBox("Show Sqrt Days Text")
        self.showSqrdDaysTextFlagCheckBox = \
            QCheckBox("Show Sqrd Days Text")
        self.showWeeksTextFlagCheckBox = \
            QCheckBox("Show Weeks Text")
        self.showSqrtWeeksTextFlagCheckBox = \
            QCheckBox("Show Sqrt Weeks Text")
        self.showSqrdWeeksTextFlagCheckBox = \
            QCheckBox("Show Sqrd Weeks Text")
        self.showMonthsTextFlagCheckBox = \
            QCheckBox("Show Months Text")
        self.showSqrtMonthsTextFlagCheckBox = \
            QCheckBox("Show Sqrt Months Text")
        self.showSqrdMonthsTextFlagCheckBox = \
            QCheckBox("Show Sqrd Months Text")
        self.showTimeRangeTextFlagCheckBox = \
            QCheckBox("Show Time Range Text")
        self.showSqrtTimeRangeTextFlagCheckBox = \
            QCheckBox("Show Sqrt Time Range Text")
        self.showSqrdTimeRangeTextFlagCheckBox = \
            QCheckBox("Show Sqrd Time Range Text")
        self.showScaledValueRangeTextFlagCheckBox = \
            QCheckBox("Show scaled value range text")
        self.showSqrtScaledValueRangeTextFlagCheckBox = \
            QCheckBox("Show sqrt scaled value range text")
        self.showSqrdScaledValueRangeTextFlagCheckBox = \
            QCheckBox("Show sqrd scaled value range text")

        # Button for checkmarking all of the checkboxes on this page.
        self.groupBoxPage2CheckAllButton = QPushButton("Check all below")
        self.groupBoxPage2UncheckAllButton = QPushButton("Uncheck all below")

        # Layout holding just the buttons for checking all the
        # checkboxes or unchecking them all.
        checkUncheckButtonsLayout = QHBoxLayout()
        checkUncheckButtonsLayout.addWidget(\
            self.groupBoxPage2CheckAllButton)
        checkUncheckButtonsLayout.addWidget(\
            self.groupBoxPage2UncheckAllButton)
        checkUncheckButtonsLayout.addStretch()

        # Layout on the left side holding about half of the checkboxes
        # for this page.
        showTextCheckBoxesLeftLayout = QVBoxLayout()
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showBarsTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtBarsTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdBarsTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showHoursTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtHoursTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdHoursTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showDaysTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtDaysTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdDaysTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addStretch()

        # Layout on the right side holding about half of the checkboxes
        # for this page.
        showTextCheckBoxesRightLayout = QVBoxLayout()
        showTextCheckBoxesRightLayout.addWidget(\
            self.showWeeksTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtWeeksTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdWeeksTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showMonthsTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtMonthsTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdMonthsTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showTimeRangeTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtTimeRangeTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdTimeRangeTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showScaledValueRangeTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtScaledValueRangeTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdScaledValueRangeTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addStretch()

        # Layout for all the checkboxes.
        checkBoxesLayout = QHBoxLayout()
        checkBoxesLayout.addLayout(showTextCheckBoxesLeftLayout)
        checkBoxesLayout.addLayout(showTextCheckBoxesRightLayout)

        # Layout for this groupbox page.
        layout = QVBoxLayout()
        layout.addLayout(checkUncheckButtonsLayout)
        layout.addSpacing(10)
        layout.addLayout(checkBoxesLayout)

        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2

    
    def _createGroupBoxPage3(self):
        """Creates a QGroupBox (and the widgets within it) for page3
        of the edit widget, and then returns it.
        """

        self.groupBoxPage3 = \
            QGroupBox("PriceBarChartTimeMeasurementArtifact Data (page 3):")

        # Create the QCheckBox widgets going on this page.
        self.showAyanaTextFlagCheckBox = \
            QCheckBox("Show ayana (6 months/Sun) text")
        self.showSqrtAyanaTextFlagCheckBox = \
            QCheckBox("Show sqrt ayana (6 months/Sun) text")
        self.showSqrdAyanaTextFlagCheckBox = \
            QCheckBox("Show sqrd ayana (6 months/Sun) text")
        self.showMuhurtaTextFlagCheckBox = \
            QCheckBox("Show muhurta (48 minutes/Moon) text")
        self.showSqrtMuhurtaTextFlagCheckBox = \
            QCheckBox("Show sqrt muhurta (48 minutes/Moon) text")
        self.showSqrdMuhurtaTextFlagCheckBox = \
            QCheckBox("Show sqrd muhurta (48 minutes/Moon) text")
        self.showVaraTextFlagCheckBox = \
            QCheckBox("Show vara (24-hour day/Mars) text")
        self.showSqrtVaraTextFlagCheckBox = \
            QCheckBox("Show sqrt vara (24-hour day/Mars) text")
        self.showSqrdVaraTextFlagCheckBox = \
            QCheckBox("Show sqrd vara (24-hour day/Mars) text")
        self.showRtuTextFlagCheckBox = \
            QCheckBox("Show rtu (season of 2 months/Mercury) text")
        self.showSqrtRtuTextFlagCheckBox = \
            QCheckBox("Show sqrt rtu (season of 2 months/Mercury) text")
        self.showSqrdRtuTextFlagCheckBox = \
            QCheckBox("Show sqrd rtu (season of 2 months/Mercury) text")
        self.showMasaTextFlagCheckBox = \
            QCheckBox("Show masa (lunar synodic month/Jupiter) text")
        self.showSqrtMasaTextFlagCheckBox = \
            QCheckBox("Show sqrt masa (lunar synodic month/Jupiter) text")
        self.showSqrdMasaTextFlagCheckBox = \
            QCheckBox("Show sqrd masa (lunar syndoci month/Jupiter) text")
        self.showPaksaTextFlagCheckBox = \
            QCheckBox("Show paksa (fortnight/Venus) text")
        self.showSqrtPaksaTextFlagCheckBox = \
            QCheckBox("Show sqrt paksa (fortnight/Venus) text")
        self.showSqrdPaksaTextFlagCheckBox = \
            QCheckBox("Show sqrd paksa (fortnight/Venus) text")
        self.showSamaTextFlagCheckBox = \
            QCheckBox("Show sama (year/Saturn) text")
        self.showSqrtSamaTextFlagCheckBox = \
            QCheckBox("Show sqrt sama (year/Saturn) text")
        self.showSqrdSamaTextFlagCheckBox = \
            QCheckBox("Show sqrd sama (year/Saturn) text")
        
        # Button for checkmarking all of the checkboxes on this page.
        self.groupBoxPage3CheckAllButton = QPushButton("Check all below")
        self.groupBoxPage3UncheckAllButton = QPushButton("Uncheck all below")

        # Layout holding just the buttons for checking all the
        # checkboxes or unchecking them all.
        checkUncheckButtonsLayout = QHBoxLayout()
        checkUncheckButtonsLayout.addWidget(\
            self.groupBoxPage3CheckAllButton)
        checkUncheckButtonsLayout.addWidget(\
            self.groupBoxPage3UncheckAllButton)
        checkUncheckButtonsLayout.addStretch()

        # Layout on the left side holding about half of the checkboxes
        # for this page.
        showTextCheckBoxesLeftLayout = QVBoxLayout()
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showAyanaTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtAyanaTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdAyanaTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showMuhurtaTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtMuhurtaTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdMuhurtaTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showVaraTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtVaraTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdVaraTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showRtuTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrtRtuTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addWidget(\
            self.showSqrdRtuTextFlagCheckBox)
        showTextCheckBoxesLeftLayout.addStretch()
        
        # Layout on the right side holding about half of the checkboxes
        # for this page.
        showTextCheckBoxesRightLayout = QVBoxLayout()
        showTextCheckBoxesRightLayout.addWidget(\
            self.showMasaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtMasaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdMasaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showPaksaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtPaksaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdPaksaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSamaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrtSamaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addWidget(\
            self.showSqrdSamaTextFlagCheckBox)
        showTextCheckBoxesRightLayout.addStretch()

        # Layout for all the checkboxes.
        checkBoxesLayout = QHBoxLayout()
        checkBoxesLayout.addLayout(showTextCheckBoxesLeftLayout)
        checkBoxesLayout.addLayout(showTextCheckBoxesRightLayout)

        # Layout for this groupbox page.
        layout = QVBoxLayout()
        layout.addLayout(checkUncheckButtonsLayout)
        layout.addSpacing(10)
        layout.addLayout(checkBoxesLayout)

        self.groupBoxPage3.setLayout(layout)

        return self.groupBoxPage3
        
        
    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.priceLocationValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        self.showBarsTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtBarsTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrdBarsTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showHoursTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtHoursTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrdHoursTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showDaysTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtDaysTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrdDaysTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showWeeksTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtWeeksTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrdWeeksTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showMonthsTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtMonthsTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrdMonthsTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showTimeRangeTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtTimeRangeTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrdTimeRangeTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showScaledValueRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtScaledValueRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdScaledValueRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showAyanaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtAyanaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdAyanaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showMuhurtaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtMuhurtaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdMuhurtaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showVaraTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtVaraTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdVaraTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showRtuTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtRtuTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdRtuTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showMasaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtMasaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdMasaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showPaksaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtPaksaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdPaksaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSamaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtSamaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrdSamaTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)

        # Buttons for mass checking or unchecking.
        self.groupBoxPage2CheckAllButton.\
            setEnabled(not self.readOnlyFlag)
        self.groupBoxPage2UncheckAllButton.\
            setEnabled(not self.readOnlyFlag)
        self.groupBoxPage3CheckAllButton.\
            setEnabled(not self.readOnlyFlag)
        self.groupBoxPage3UncheckAllButton.\
            setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartTimeMeasurementArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartTimeMeasurementArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        
        locationPointY = self.artifact.startPointF.y()
        locationPointPrice = self.convertObj.sceneYPosToPrice(locationPointY)
        self.priceLocationValueSpinBox.setValue(locationPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        if self.artifact.getShowBarsTextFlag() == True:
            self.showBarsTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showBarsTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtBarsTextFlag() == True:
            self.showSqrtBarsTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtBarsTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrdBarsTextFlag() == True:
            self.showSqrdBarsTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdBarsTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowHoursTextFlag() == True:
            self.showHoursTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showHoursTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtHoursTextFlag() == True:
            self.showSqrtHoursTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtHoursTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrdHoursTextFlag() == True:
            self.showSqrdHoursTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdHoursTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowDaysTextFlag() == True:
            self.showDaysTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showDaysTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtDaysTextFlag() == True:
            self.showSqrtDaysTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtDaysTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrdDaysTextFlag() == True:
            self.showSqrdDaysTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdDaysTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowWeeksTextFlag() == True:
            self.showWeeksTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showWeeksTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtWeeksTextFlag() == True:
            self.showSqrtWeeksTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtWeeksTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrdWeeksTextFlag() == True:
            self.showSqrdWeeksTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdWeeksTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowMonthsTextFlag() == True:
            self.showMonthsTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showMonthsTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtMonthsTextFlag() == True:
            self.showSqrtMonthsTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtMonthsTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrdMonthsTextFlag() == True:
            self.showSqrdMonthsTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdMonthsTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowTimeRangeTextFlag() == True:
            self.showTimeRangeTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showTimeRangeTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtTimeRangeTextFlag() == True:
            self.showSqrtTimeRangeTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtTimeRangeTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdTimeRangeTextFlag() == True:
            self.showSqrdTimeRangeTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdTimeRangeTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowScaledValueRangeTextFlag() == True:
            self.showScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtScaledValueRangeTextFlag() == True:
            self.showSqrtScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrtScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrdScaledValueRangeTextFlag() == True:
            self.showSqrdScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrdScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowAyanaTextFlag() == True:
            self.showAyanaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showAyanaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtAyanaTextFlag() == True:
            self.showSqrtAyanaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtAyanaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdAyanaTextFlag() == True:
            self.showSqrdAyanaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdAyanaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowMuhurtaTextFlag() == True:
            self.showMuhurtaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showMuhurtaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtMuhurtaTextFlag() == True:
            self.showSqrtMuhurtaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtMuhurtaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdMuhurtaTextFlag() == True:
            self.showSqrdMuhurtaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdMuhurtaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowVaraTextFlag() == True:
            self.showVaraTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showVaraTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtVaraTextFlag() == True:
            self.showSqrtVaraTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtVaraTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdVaraTextFlag() == True:
            self.showSqrdVaraTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdVaraTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowRtuTextFlag() == True:
            self.showRtuTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showRtuTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtRtuTextFlag() == True:
            self.showSqrtRtuTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtRtuTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdRtuTextFlag() == True:
            self.showSqrdRtuTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdRtuTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowMasaTextFlag() == True:
            self.showMasaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showMasaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtMasaTextFlag() == True:
            self.showSqrtMasaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtMasaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdMasaTextFlag() == True:
            self.showSqrdMasaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdMasaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowPaksaTextFlag() == True:
            self.showPaksaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showPaksaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtPaksaTextFlag() == True:
            self.showSqrtPaksaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtPaksaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdPaksaTextFlag() == True:
            self.showSqrdPaksaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdPaksaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSamaTextFlag() == True:
            self.showSamaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSamaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtSamaTextFlag() == True:
            self.showSqrtSamaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtSamaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrdSamaTextFlag() == True:
            self.showSqrdSamaTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrdSamaTextFlagCheckBox.setCheckState(Qt.Unchecked)

        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartTimeMeasurementArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.

        price = self.priceLocationValueSpinBox.value()
        y = self.convertObj.priceToSceneYPos(price)

        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        posF = QPointF(startPointX, y)
        startPointF = QPointF(startPointX, y)
        endPointF = QPointF(endPointX, y)

        showBarsTextFlag = \
            (self.showBarsTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtBarsTextFlag = \
            (self.showSqrtBarsTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdBarsTextFlag = \
            (self.showSqrdBarsTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showHoursTextFlag = \
            (self.showHoursTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtHoursTextFlag = \
            (self.showSqrtHoursTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdHoursTextFlag = \
            (self.showSqrdHoursTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showDaysTextFlag = \
            (self.showDaysTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtDaysTextFlag = \
            (self.showSqrtDaysTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdDaysTextFlag = \
            (self.showSqrdDaysTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showWeeksTextFlag = \
            (self.showWeeksTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtWeeksTextFlag = \
            (self.showSqrtWeeksTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdWeeksTextFlag = \
            (self.showSqrdWeeksTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showMonthsTextFlag = \
            (self.showMonthsTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtMonthsTextFlag = \
            (self.showSqrtMonthsTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdMonthsTextFlag = \
            (self.showSqrdMonthsTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showTimeRangeTextFlag = \
            (self.showTimeRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtTimeRangeTextFlag = \
            (self.showSqrtTimeRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdTimeRangeTextFlag = \
            (self.showSqrdTimeRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showScaledValueRangeTextFlag = \
            (self.showScaledValueRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtScaledValueRangeTextFlag = \
            (self.showSqrtScaledValueRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdScaledValueRangeTextFlag = \
            (self.showSqrdScaledValueRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showAyanaTextFlag = \
            (self.showAyanaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtAyanaTextFlag = \
            (self.showSqrtAyanaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdAyanaTextFlag = \
            (self.showSqrdAyanaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showMuhurtaTextFlag = \
            (self.showMuhurtaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtMuhurtaTextFlag = \
            (self.showSqrtMuhurtaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdMuhurtaTextFlag = \
            (self.showSqrdMuhurtaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showVaraTextFlag = \
            (self.showVaraTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtVaraTextFlag = \
            (self.showSqrtVaraTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdVaraTextFlag = \
            (self.showSqrdVaraTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showRtuTextFlag = \
            (self.showRtuTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtRtuTextFlag = \
            (self.showSqrtRtuTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdRtuTextFlag = \
            (self.showSqrdRtuTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showMasaTextFlag = \
            (self.showMasaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtMasaTextFlag = \
            (self.showSqrtMasaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdMasaTextFlag = \
            (self.showSqrdMasaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showPaksaTextFlag = \
            (self.showPaksaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtPaksaTextFlag = \
            (self.showSqrtPaksaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdPaksaTextFlag = \
            (self.showSqrdPaksaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSamaTextFlag = \
            (self.showSamaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtSamaTextFlag = \
            (self.showSqrtSamaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrdSamaTextFlag = \
            (self.showSqrdSamaTextFlagCheckBox.checkState() == \
             Qt.Checked)
        
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)
        self.artifact.setShowBarsTextFlag(showBarsTextFlag)
        self.artifact.setShowSqrtBarsTextFlag(showSqrtBarsTextFlag)
        self.artifact.setShowSqrdBarsTextFlag(showSqrdBarsTextFlag)
        self.artifact.setShowHoursTextFlag(showHoursTextFlag)
        self.artifact.setShowSqrtHoursTextFlag(showSqrtHoursTextFlag)
        self.artifact.setShowSqrdHoursTextFlag(showSqrdHoursTextFlag)
        self.artifact.setShowDaysTextFlag(showDaysTextFlag)
        self.artifact.setShowSqrtDaysTextFlag(showSqrtDaysTextFlag)
        self.artifact.setShowSqrdDaysTextFlag(showSqrdDaysTextFlag)
        self.artifact.setShowWeeksTextFlag(showWeeksTextFlag)
        self.artifact.setShowSqrtWeeksTextFlag(showSqrtWeeksTextFlag)
        self.artifact.setShowSqrdWeeksTextFlag(showSqrdWeeksTextFlag)
        self.artifact.setShowMonthsTextFlag(showMonthsTextFlag)
        self.artifact.setShowSqrtMonthsTextFlag(showSqrtMonthsTextFlag)
        self.artifact.setShowSqrdMonthsTextFlag(showSqrdMonthsTextFlag)
        self.artifact.setShowTimeRangeTextFlag(showTimeRangeTextFlag)
        self.artifact.setShowSqrtTimeRangeTextFlag(showSqrtTimeRangeTextFlag)
        self.artifact.setShowSqrdTimeRangeTextFlag(showSqrdTimeRangeTextFlag)
        self.artifact.setShowScaledValueRangeTextFlag(\
            showScaledValueRangeTextFlag)
        self.artifact.setShowSqrtScaledValueRangeTextFlag(\
            showSqrtScaledValueRangeTextFlag)
        self.artifact.setShowSqrdScaledValueRangeTextFlag(\
            showSqrdScaledValueRangeTextFlag)
        self.artifact.setShowAyanaTextFlag(showAyanaTextFlag)
        self.artifact.setShowSqrtAyanaTextFlag(showSqrtAyanaTextFlag)
        self.artifact.setShowSqrdAyanaTextFlag(showSqrdAyanaTextFlag)
        self.artifact.setShowMuhurtaTextFlag(showMuhurtaTextFlag)
        self.artifact.setShowSqrtMuhurtaTextFlag(showSqrtMuhurtaTextFlag)
        self.artifact.setShowSqrdMuhurtaTextFlag(showSqrdMuhurtaTextFlag)
        self.artifact.setShowVaraTextFlag(showVaraTextFlag)
        self.artifact.setShowSqrtVaraTextFlag(showSqrtVaraTextFlag)
        self.artifact.setShowSqrdVaraTextFlag(showSqrdVaraTextFlag)
        self.artifact.setShowRtuTextFlag(showRtuTextFlag)
        self.artifact.setShowSqrtRtuTextFlag(showSqrtRtuTextFlag)
        self.artifact.setShowSqrdRtuTextFlag(showSqrdRtuTextFlag)
        self.artifact.setShowMasaTextFlag(showMasaTextFlag)
        self.artifact.setShowSqrtMasaTextFlag(showSqrtMasaTextFlag)
        self.artifact.setShowSqrdMasaTextFlag(showSqrdMasaTextFlag)
        self.artifact.setShowPaksaTextFlag(showPaksaTextFlag)
        self.artifact.setShowSqrtPaksaTextFlag(showSqrtPaksaTextFlag)
        self.artifact.setShowSqrdPaksaTextFlag(showSqrdPaksaTextFlag)
        self.artifact.setShowSamaTextFlag(showSamaTextFlag)
        self.artifact.setShowSqrtSamaTextFlag(showSqrtSamaTextFlag)
        self.artifact.setShowSqrdSamaTextFlag(showSqrdSamaTextFlag)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))

    def _handleGroupBoxPage2CheckAllButtonClicked(self):
        """Called when the groupBoxPage2CheckAllButton is clicked.
        This function will checkmark all the QCheckBox widgets in
        page 2.
        """

        checkState = Qt.Checked
        
        self.showBarsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtBarsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdBarsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showHoursTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtHoursTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdHoursTextFlagCheckBox.\
            setCheckState(checkState)
        self.showDaysTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtDaysTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdDaysTextFlagCheckBox.\
            setCheckState(checkState)
        self.showWeeksTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtWeeksTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdWeeksTextFlagCheckBox.\
            setCheckState(checkState)
        self.showMonthsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtMonthsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdMonthsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showTimeRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtTimeRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdTimeRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showScaledValueRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtScaledValueRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdScaledValueRangeTextFlagCheckBox.\
            setCheckState(checkState)
        
    def _handleGroupBoxPage2UncheckAllButtonClicked(self):
        """Called when the groupBoxPage2CheckAllButton is clicked.
        This function will uncheckmark all the QCheckBox widgets in
        page 2.
        """

        checkState = Qt.Unchecked
        
        self.showBarsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtBarsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdBarsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showHoursTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtHoursTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdHoursTextFlagCheckBox.\
            setCheckState(checkState)
        self.showDaysTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtDaysTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdDaysTextFlagCheckBox.\
            setCheckState(checkState)
        self.showWeeksTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtWeeksTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdWeeksTextFlagCheckBox.\
            setCheckState(checkState)
        self.showMonthsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtMonthsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdMonthsTextFlagCheckBox.\
            setCheckState(checkState)
        self.showTimeRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtTimeRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdTimeRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showScaledValueRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtScaledValueRangeTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdScaledValueRangeTextFlagCheckBox.\
            setCheckState(checkState)
        
    def _handleGroupBoxPage3CheckAllButtonClicked(self):
        """Called when the groupBoxPage3CheckAllButton is clicked.
        This function will checkmark all the QCheckBox widgets in
        page 3.
        """

        checkState = Qt.Checked
        
        self.showAyanaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtAyanaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdAyanaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showMuhurtaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtMuhurtaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdMuhurtaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showVaraTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtVaraTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdVaraTextFlagCheckBox.\
            setCheckState(checkState)
        self.showRtuTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtRtuTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdRtuTextFlagCheckBox.\
            setCheckState(checkState)
        self.showMasaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtMasaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdMasaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showPaksaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtPaksaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdPaksaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSamaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtSamaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdSamaTextFlagCheckBox.\
            setCheckState(checkState)
        
    def _handleGroupBoxPage3UncheckAllButtonClicked(self):
        """Called when the groupBoxPage3CheckAllButton is clicked.
        This function will uncheckmark all the QCheckBox widgets in
        page 3.
        """

        checkState = Qt.Unchecked
        
        self.showAyanaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtAyanaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdAyanaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showMuhurtaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtMuhurtaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdMuhurtaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showVaraTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtVaraTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdVaraTextFlagCheckBox.\
            setCheckState(checkState)
        self.showRtuTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtRtuTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdRtuTextFlagCheckBox.\
            setCheckState(checkState)
        self.showMasaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtMasaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdMasaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showPaksaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtPaksaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdPaksaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSamaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrtSamaTextFlagCheckBox.\
            setCheckState(checkState)
        self.showSqrdSamaTextFlagCheckBox.\
            setCheckState(checkState)
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartTimeMeasurementArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartTimeMeasurementArtifact.
    """

    def __init__(self,
                 priceBarChartTimeMeasurementArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartTimeMeasurementArtifact.
        
        Note: The 'priceBarChartTimeMeasurementArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartTimeMeasurementArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartTimeMeasurementArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartTimeMeasurementArtifact Data")

        # Check input.
        if not isinstance(priceBarChartTimeMeasurementArtifact,
                          PriceBarChartTimeMeasurementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartTimeMeasurementArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartTimeMeasurementArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartTimeMeasurementArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartTimeMeasurementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartTimeModalScaleArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartTimeModalScaleArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartTimeModalScaleArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartTimeModalScaleArtifact object.

        Arguments:
        artifact - PriceBarChartTimeModalScaleArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartTimeModalScaleArtifactEditWidget")

        # This variable holds a copy of the artifact passed in.  We
        # set this value via self.loadValues(), which is called later
        # in this funtion on parameter 'artifact'.
        self.artifact = None

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.barHeightValueSpinBox.valueChanged.\
            connect(self._handleBarHeightValueSpinBoxChanged)
        self.textFontSizeValueSpinBox.valueChanged.\
            connect(self._handleTextFontSizeValueSpinBoxChanged)
        self.textEnabledCheckBox.stateChanged.\
            connect(self._handleTextEnabledCheckBoxToggled)
        
        # Connect rotateUp and rotateDown buttons.
        self.rotateUpButton.clicked.\
            connect(self._handleRotateUpButtonClicked)
        self.rotateDownButton.clicked.\
            connect(self._handleRotateDownButtonClicked)
        self.reverseButton.clicked.\
            connect(self._handleReverseButtonClicked)
        self.checkMarkAllButton.clicked.\
            connect(self._handleCheckMarkAllButtonClicked)
        self.checkMarkNoneButton.clicked.\
            connect(self._handleCheckMarkNoneButtonClicked)

        # Connect the signals for the price and time values changing,
        # so that we can update the start and end points in the
        # artifact and update all the prices and datetimes in
        # between.
        self.startPointPriceValueSpinBox.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        #self.endPointPriceValueSpinBox.valueChanged.\
        #    connect(self. _saveAndReloadMusicalRatios)
        self.startPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.endPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartTimeModalScaleArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.colorLabel = QLabel("Bar color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.barHeightValueLabel = \
            QLabel("TimeModalScale bar height:")
        self.barHeightValueSpinBox = QDoubleSpinBox()
        self.barHeightValueSpinBox.setMinimum(0.0)
        self.barHeightValueSpinBox.setMaximum(999999999.0)

        self.textFontSizeValueLabel = \
            QLabel("Text font size:")
        self.textFontSizeValueSpinBox = QDoubleSpinBox()
        self.textFontSizeValueSpinBox.setMinimum(0.0)
        self.textFontSizeValueSpinBox.setMaximum(999999999.0)

        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        self.startPointPriceValueLabel = \
            QLabel("TimeModalScale Start Point (in price):")
        self.startPointPriceValueSpinBox = QDoubleSpinBox()
        self.startPointPriceValueSpinBox.setDecimals(4)
        self.startPointPriceValueSpinBox.setMinimum(0.0)
        self.startPointPriceValueSpinBox.setMaximum(999999999.0)
        startPointPriceValueLayout = QHBoxLayout()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueLabel)
        startPointPriceValueLayout.addStretch()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueSpinBox)
        
        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("TimeModalScale Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        #self.endPointPriceValueLabel = \
        #    QLabel("TimeModalScale End Point (in price):")
        #self.endPointPriceValueSpinBox = QDoubleSpinBox()
        #self.endPointPriceValueSpinBox.setDecimals(4)
        #self.endPointPriceValueSpinBox.setMinimum(0.0)
        #self.endPointPriceValueSpinBox.setMaximum(999999999.0)
        #endPointPriceValueLayout = QHBoxLayout()
        #endPointPriceValueLayout.addWidget(self.endPointPriceValueLabel)
        #endPointPriceValueLayout.addStretch()
        #endPointPriceValueLayout.addWidget(self.endPointPriceValueSpinBox)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("TimeModalScale End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.barHeightValueLabel, r, 0, al)
        gridLayout.addWidget(self.barHeightValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textFontSizeValueLabel, r, 0, al)
        gridLayout.addWidget(self.textFontSizeValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(startPointPriceValueLayout, r, 0, al)
        #gridLayout.addLayout(endPointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        gridLayout.addWidget(self.endPointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1
    
    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartTimeModalScaleArtifact Data (page 2):")
        
        self.rotateDownButton = QPushButton("Rotate Down")
        self.rotateUpButton = QPushButton("Rotate Up")
        self.reverseButton = QPushButton("Reverse")
        self.checkMarkAllButton = QPushButton("Check All")
        self.checkMarkNoneButton = QPushButton("Check None")
        
        rotateButtonsLayout = QHBoxLayout()
        rotateButtonsLayout.addWidget(self.rotateDownButton)
        rotateButtonsLayout.addWidget(self.rotateUpButton)
        rotateButtonsLayout.addWidget(self.reverseButton)
        rotateButtonsLayout.addWidget(self.checkMarkAllButton)
        rotateButtonsLayout.addWidget(self.checkMarkNoneButton)
        rotateButtonsLayout.addStretch()
        
        # Layout for the musical ratio intervals.
        self.musicalRatiosGridLayout = QGridLayout()
        self.numMusicalRatios = 0

        # Holds the list of QCheckBox objects corresponding to the
        # MusicalRatios (ordered) in the artifact. 
        self.checkBoxes = []
        
        layout = QVBoxLayout()
        layout.addLayout(rotateButtonsLayout)
        layout.addLayout(self.musicalRatiosGridLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2
        
    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.barHeightValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textFontSizeValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        self.rotateDownButton.setEnabled(not self.readOnlyFlag)
        self.rotateUpButton.setEnabled(not self.readOnlyFlag)
        self.reverseButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkAllButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkNoneButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        #self.endPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.checkBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartTimeModalScaleArtifact.

        Arguments:
        
        artifact - PriceBarChartTimeModalScaleArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        elif self.artifact is artifact:
            # They are the same, so no need to do a deep copy.
            # Just continue on, creating and loading the widgets.
            self.log.debug("Same artifact, no need for deep copy.")
        else:
            # Store a deep copy of the artifact because we manipulate
            # the musicalRatios list and its ordering.
            self.log.debug("Deep copying artifact...")
            self.artifact = copy.deepcopy(artifact)

        self.log.debug("Setting the widgets...")
        
        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        self.colorEditButton.setColor(self.artifact.getColor())
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        self.barHeightValueSpinBox.setValue(self.artifact.getBarHeight())
        self.textFontSizeValueSpinBox.setValue(self.artifact.getFontSize())
                                        
        if self.artifact.isTextEnabled():
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        #self.endPointPriceValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        self._reloadMusicalRatiosGrid()
        
        self.log.debug("Exiting loadValues()")

    def _reloadMusicalRatiosGrid(self):
        """Clears and recreates the self.musicalRatiosGridLayout
        according to teh values in self.artifact.
        """
        
        # Remove any old widgets that were in the grid layout from
        # the grid layout..
        for r in range(self.musicalRatiosGridLayout.rowCount()):
            for c in range(self.musicalRatiosGridLayout.columnCount()):
                # Get the QLayoutItem.
                item = self.musicalRatiosGridLayout.itemAtPosition(r, c)
                if item != None:
                    # Get the widget in the layout item.
                    widget = item.widget()
                    if widget != None:
                        widget.setEnabled(False)
                        widget.setVisible(False)
                        widget.setParent(None)

                        # Actually remove the widget from the
                        # QGridLayout.  
                        self.musicalRatiosGridLayout.removeWidget(widget)
                                
        # Row.
        r = 0
        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        # Create the musical ratio items in the
        # self.musicalRatiosGridLayout QGridLayout.
        musicalRatios = self.artifact.getMusicalRatios()
        self.numMusicalRatios = len(musicalRatios)

        # Clear the checkboxes list.
        self.checkBoxes = []

        rangeUsed = None
        if self.artifact.isReversed() == False:
            rangeUsed = range(self.numMusicalRatios)
        else:
            rangeUsed = reversed(range(self.numMusicalRatios))
            
        for i in rangeUsed:
            musicalRatio = musicalRatios[i]

            checkBox = QCheckBox("{}".format(musicalRatio.getRatio()))

            # Set the check state based on whether or not the musical
            # ratio is enabled.
            if musicalRatio.isEnabled():
                checkBox.setCheckState(Qt.Checked)
            else:
                checkBox.setCheckState(Qt.Unchecked)

            # Connect the signal to the slot function
            # _handleCheckMarkToggled().  That function will update
            # the self.artifact's musicalRatios with new check state.
            checkBox.stateChanged.connect(self._handleCheckMarkToggled)
            
            # Append to our list of checkboxes so that we can
            # reference them later and see what values are used in
            # them.  Remember, if we are reversed, then we will need
            # to reverse this list later.
            self.checkBoxes.append(checkBox)
            
            descriptionLabel = QLabel(musicalRatio.getDescription())

            # Use QLabels to
            # display the price and timestamp information.
            (x, y) = self.artifact.getXYForMusicalRatio(i)
                
            price = self.convertObj.sceneYPosToPrice(y)
            priceStr = "{}".format(price)
            priceWidget = QLabel(priceStr)

            timestamp = self.convertObj.sceneXPosToDatetime(x)
            timestampStr = Ephemeris.datetimeToDayStr(timestamp)
            timestampWidget = QLabel(timestampStr)

            # Actually add the widgets to the grid layout.
            self.musicalRatiosGridLayout.addWidget(checkBox, r, 0, al)
            self.musicalRatiosGridLayout.addWidget(descriptionLabel, r, 1, al)
            self.musicalRatiosGridLayout.addWidget(priceWidget, r, 2, al)
            self.musicalRatiosGridLayout.addWidget(timestampWidget, r, 3, al)

            r += 1

        # Reverse the self.checkBoxes list if we are reversed, since
        # if that is the case, then previously in this function we
        # added the checkBoxes in the reverse order.
        if self.artifact.isReversed():
            self.checkBoxes.reverse()
            
    def saveValues(self):
        """Saves the values in the widgets to the internally stored
        PriceBarChartTimeModalScaleArtifact object.
        """

        self.log.debug("Entered saveValues()")

        # Get the colors.
        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.
        startPointPrice = \
            self.startPointPriceValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)
        #endPointPrice = \
        #    self.endPointPriceValueSpinBox.value()
        #endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        endPointY = startPointY
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()
                          
        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)

        # No need to save the musicalRatios inside self.artifact,
        # because each time there is a rotation or a check-marking
        # action, the internal artifact was updated.
        # The same is the case for the self.artifact.setReversed().

        self.log.debug("Exiting saveValues()")

    def _handleBarHeightValueSpinBoxChanged(self):
        """Called when the self.barHeightValueSpinBox is modified."""

        self.artifact.setBarHeight(self.barHeightValueSpinBox.value())
        
    def _handleTextFontSizeValueSpinBoxChanged(self):
        """Called when the self.textFontSizeValueSpinBox is modified."""

        self.artifact.setFontSize(self.textFontSizeValueSpinBox.value())
        
    def _handleTextEnabledCheckBoxToggled(self):
        """Called when the textEnabledCheckBox is checked or unchecked."""

        newValue = None
        
        if self.textEnabledCheckBox.checkState() == Qt.Checked:
            newValue = True
        else:
            newValue = False
        
        self.artifact.setTextEnabled(newValue)
        
    def _handleCheckMarkToggled(self):
        """Called when one of the check-mark boxes on the
        musicalRatios is checked or unchecked.
        """

        # Go through all the musicalRatios in the widget, and set them
        # as enabled or disabled in the artifact, based on the check
        # state of the QCheckBox objects in self.checkBoxes.
        for i in range(len(self.checkBoxes)):
            oldValue = self.artifact.getMusicalRatios()[i].isEnabled()
            newValue = None
            if self.checkBoxes[i].checkState() == Qt.Checked:
                newValue = True
            else:
                newValue = False

            if oldValue != newValue:
                self.log.debug("Updating enabled state of " +
                               "musicalRatio[{}] from {} to {}".\
                               format(i, oldValue, newValue))
                self.artifact.getMusicalRatios()[i].setEnabled(newValue)
            else:
                #self.log.debug("No update to musicalRatio[{}]".format(i))
                pass

    def _saveAndReloadMusicalRatios(self):
        """Saves and reloads the musical ratio widgets."""
        
        # Save values from what is in the widgets to the internal artifact.
        self.saveValues()
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateDownButtonClicked(self):
        """Called when the 'Rotate Down' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()

        if self.artifact.isReversed() == False:
            # Put the last musical ratio in the front.
            if len(musicalRatios) > 0:
                lastRatio = musicalRatios.pop(len(musicalRatios) - 1)
                musicalRatios.insert(0, lastRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
            
        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateUpButtonClicked(self):
        """Called when the 'Rotate Up' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()
        
        if self.artifact.isReversed() == False:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)

        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleReverseButtonClicked(self):
        """Called when the 'Reverse' button is clicked."""

        # Flip the flag that indicates that the musical ratios are reversed.
        self.artifact.setReversed(not self.artifact.isReversed())
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleCheckMarkAllButtonClicked(self):
        """Called when the 'Check All' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Checked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleCheckMarkNoneButtonClicked(self):
        """Called when the 'Check None' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Unchecked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartTimeModalScaleArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartTimeModalScaleArtifact.
    """

    def __init__(self,
                 priceBarChartTimeModalScaleArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartTimeModalScaleArtifact.
        
        Note: The 'priceBarChartTimeModalScaleArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartTimeModalScaleArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartTimeModalScaleArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartTimeModalScaleArtifact Data")

        # Check input.
        if not isinstance(priceBarChartTimeModalScaleArtifact,
                          PriceBarChartTimeModalScaleArtifact):
            self.log.error("Input type invalid to " + \
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartTimeModalScaleArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartTimeModalScaleArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartTimeModalScaleArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartTimeModalScaleArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the artifact object.  If the 'Okay'
        button was previously clicked, then this object contains new
        values as set with the widget, otherwise it is unchanged.
        """

        # The edit widget keeps its own copy of the artifact, which it
        # modifies directly.
        if self.result() == QDialog.Accepted:
            return self.editWidget.getArtifact()
        else:
            return self.artifact


class PriceBarChartPriceModalScaleArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartPriceModalScaleArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartPriceModalScaleArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartPriceModalScaleArtifact object.

        Arguments:
        artifact - PriceBarChartPriceModalScaleArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartPriceModalScaleArtifactEditWidget")

        # This variable holds a copy of the artifact passed in.  We
        # set this value via self.loadValues(), which is called later
        # in this funtion on parameter 'artifact'.
        self.artifact = None

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 
        
        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.barWidthValueSpinBox.valueChanged.\
            connect(self._handleBarWidthValueSpinBoxChanged)
        self.textFontSizeValueSpinBox.valueChanged.\
            connect(self._handleTextFontSizeValueSpinBoxChanged)
        self.textEnabledCheckBox.stateChanged.\
            connect(self._handleTextEnabledCheckBoxToggled)
        
        # Connect rotateUp and rotateDown buttons.
        self.rotateUpButton.clicked.\
            connect(self._handleRotateUpButtonClicked)
        self.rotateDownButton.clicked.\
            connect(self._handleRotateDownButtonClicked)
        self.reverseButton.clicked.\
            connect(self._handleReverseButtonClicked)
        self.checkMarkAllButton.clicked.\
            connect(self._handleCheckMarkAllButtonClicked)
        self.checkMarkNoneButton.clicked.\
            connect(self._handleCheckMarkNoneButtonClicked)

        # Connect the signals for the price and time values changing,
        # so that we can update the start and end points in the
        # artifact and update all the prices and datetimes in
        # between.
        self.startPointPriceValueSpinBox.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.endPointPriceValueSpinBox.valueChanged.\
            connect(self. _saveAndReloadMusicalRatios)
        self.startPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        #self.endPointDatetimeLocationWidget.valueChanged.\
        #    connect(self._saveAndReloadMusicalRatios)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartPriceModalScaleArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.colorLabel = QLabel("Bar color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.barWidthValueLabel = QLabel("PriceModalScale bar width:")
        self.barWidthValueSpinBox = QDoubleSpinBox()
        self.barWidthValueSpinBox.setMinimum(0.0)
        self.barWidthValueSpinBox.setMaximum(999999999.0)

        self.textFontSizeValueLabel = \
            QLabel("Text font size:")
        self.textFontSizeValueSpinBox = QDoubleSpinBox()
        self.textFontSizeValueSpinBox.setMinimum(0.0)
        self.textFontSizeValueSpinBox.setMaximum(999999999.0)

        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)
        
        self.startPointPriceValueLabel = \
            QLabel("PriceModalScale Start Point (in price):")
        self.startPointPriceValueSpinBox = QDoubleSpinBox()
        self.startPointPriceValueSpinBox.setDecimals(4)
        self.startPointPriceValueSpinBox.setMinimum(0.0)
        self.startPointPriceValueSpinBox.setMaximum(999999999.0)
        startPointPriceValueLayout = QHBoxLayout()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueLabel)
        startPointPriceValueLayout.addStretch()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueSpinBox)
        
        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("PriceModalScale Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.endPointPriceValueLabel = \
            QLabel("PriceModalScale End Point (in price):")
        self.endPointPriceValueSpinBox = QDoubleSpinBox()
        self.endPointPriceValueSpinBox.setDecimals(4)
        self.endPointPriceValueSpinBox.setMinimum(0.0)
        self.endPointPriceValueSpinBox.setMaximum(999999999.0)
        endPointPriceValueLayout = QHBoxLayout()
        endPointPriceValueLayout.addWidget(self.endPointPriceValueLabel)
        endPointPriceValueLayout.addStretch()
        endPointPriceValueLayout.addWidget(self.endPointPriceValueSpinBox)
        
        #self.endPointDatetimeLocationWidget = TimestampEditWidget()
        #self.endPointDatetimeLocationWidget.groupBox.\
        #    setTitle("PriceModalScale End Point (in time)")
        #self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        #self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.barWidthValueLabel, r, 0, al)
        gridLayout.addWidget(self.barWidthValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textFontSizeValueLabel, r, 0, al)
        gridLayout.addWidget(self.textFontSizeValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(startPointPriceValueLayout, r, 0, al)
        gridLayout.addLayout(endPointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        #gridLayout.addWidget(self.endPointDatetimeLocationWidget,
        #                          r, 1, al)
        r += 1

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1
    
    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartPriceModalScaleArtifact Data (page 2):")

        self.rotateDownButton = QPushButton("Rotate Down")
        self.rotateUpButton = QPushButton("Rotate Up")
        self.reverseButton = QPushButton("Reverse")
        self.checkMarkAllButton = QPushButton("Check All")
        self.checkMarkNoneButton = QPushButton("Check None")
        
        rotateButtonsLayout = QHBoxLayout()
        rotateButtonsLayout.addWidget(self.rotateDownButton)
        rotateButtonsLayout.addWidget(self.rotateUpButton)
        rotateButtonsLayout.addWidget(self.reverseButton)
        rotateButtonsLayout.addWidget(self.checkMarkAllButton)
        rotateButtonsLayout.addWidget(self.checkMarkNoneButton)
        rotateButtonsLayout.addStretch()
        
        # Layout for the musical ratio intervals.
        self.musicalRatiosGridLayout = QGridLayout()
        self.numMusicalRatios = 0

        # Holds the list of QCheckBox objects corresponding to the
        # MusicalRatios (ordered) in the artifact. 
        self.checkBoxes = []
        
        layout = QVBoxLayout()
        layout.addLayout(rotateButtonsLayout)
        layout.addLayout(self.musicalRatiosGridLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2
        
    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.barWidthValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textFontSizeValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        self.rotateDownButton.setEnabled(not self.readOnlyFlag)
        self.rotateUpButton.setEnabled(not self.readOnlyFlag)
        self.reverseButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkAllButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkNoneButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.endPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        #self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.checkBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartPriceModalScaleArtifact.

        Arguments:
        
        artifact - PriceBarChartPriceModalScaleArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        elif self.artifact is artifact:
            # They are the same, so no need to do a deep copy.
            # Just continue on, creating and loading the widgets.
            self.log.debug("Same artifact, no need for deep copy.")
        else:
            # Store a deep copy of the artifact because we manipulate
            # the musicalRatios list and its ordering.
            self.log.debug("Deep copying artifact...")
            self.artifact = copy.deepcopy(artifact)

        self.log.debug("Setting the widgets...")
        
        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        self.colorEditButton.\
            setColor(self.artifact.getColor())
        self.textColorEditButton.\
            setColor(self.artifact.getTextColor())
        self.barWidthValueSpinBox.\
            setValue(self.artifact.getBarWidth())
        self.textFontSizeValueSpinBox.\
            setValue(self.artifact.getFontSize())
        
        if self.artifact.isTextEnabled():
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        self.endPointPriceValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        #self.endPointDatetimeLocationWidget.\
        #    loadTimestamp(endPointDatetime)

        self._reloadMusicalRatiosGrid()
        
        self.log.debug("Exiting loadValues()")

    def _reloadMusicalRatiosGrid(self):
        """Clears and recreates the self.musicalRatiosGridLayout
        according to teh values in self.artifact.
        """
        
        # Remove any old widgets that were in the grid layout from
        # the grid layout..
        for r in range(self.musicalRatiosGridLayout.rowCount()):
            for c in range(self.musicalRatiosGridLayout.columnCount()):
                # Get the QLayoutItem.
                item = self.musicalRatiosGridLayout.itemAtPosition(r, c)
                if item != None:
                    # Get the widget in the layout item.
                    widget = item.widget()
                    if widget != None:
                        widget.setEnabled(False)
                        widget.setVisible(False)
                        widget.setParent(None)

                        # Actually remove the widget from the
                        # QGridLayout.  
                        self.musicalRatiosGridLayout.removeWidget(widget)
                                
        # Row.
        r = 0
        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        # Create the musical ratio items in the
        # self.musicalRatiosGridLayout QGridLayout.
        musicalRatios = self.artifact.getMusicalRatios()
        self.numMusicalRatios = len(musicalRatios)

        # Clear the checkboxes list.
        self.checkBoxes = []

        rangeUsed = None
        if self.artifact.isReversed() == False:
            rangeUsed = range(self.numMusicalRatios)
        else:
            rangeUsed = reversed(range(self.numMusicalRatios))
            
        for i in rangeUsed:
            musicalRatio = musicalRatios[i]

            checkBox = QCheckBox("{}".format(musicalRatio.getRatio()))

            # Set the check state based on whether or not the musical
            # ratio is enabled.
            if musicalRatio.isEnabled():
                checkBox.setCheckState(Qt.Checked)
            else:
                checkBox.setCheckState(Qt.Unchecked)

            # Connect the signal to the slot function
            # _handleCheckMarkToggled().  That function will update
            # the self.artifact's musicalRatios with new check state.
            checkBox.stateChanged.connect(self._handleCheckMarkToggled)
            
            # Append to our list of checkboxes so that we can
            # reference them later and see what values are used in
            # them.  Remember, if we are reversed, then we will need
            # to reverse this list later.
            self.checkBoxes.append(checkBox)
            
            descriptionLabel = QLabel(musicalRatio.getDescription())

            # Use QLabels to
            # display the price and timestamp information.
            (x, y) = self.artifact.getXYForMusicalRatio(i)
                
            price = self.convertObj.sceneYPosToPrice(y)
            priceStr = "{}".format(price)
            priceWidget = QLabel(priceStr)

            timestamp = self.convertObj.sceneXPosToDatetime(x)
            timestampStr = Ephemeris.datetimeToDayStr(timestamp)
            timestampWidget = QLabel(timestampStr)

            # Actually add the widgets to the grid layout.
            self.musicalRatiosGridLayout.addWidget(checkBox, r, 0, al)
            self.musicalRatiosGridLayout.addWidget(descriptionLabel, r, 1, al)
            self.musicalRatiosGridLayout.addWidget(priceWidget, r, 2, al)
            self.musicalRatiosGridLayout.addWidget(timestampWidget, r, 3, al)

            r += 1

        # Reverse the self.checkBoxes list if we are reversed, since
        # if that is the case, then previously in this function we
        # added the checkBoxes in the reverse order.
        if self.artifact.isReversed():
            self.checkBoxes.reverse()
            
    def saveValues(self):
        """Saves the values in the widgets to the internally stored
        PriceBarChartPriceModalScaleArtifact object.
        """

        self.log.debug("Entered saveValues()")

        # Get the colors.
        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        #self.endPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.
        startPointPrice = \
            self.startPointPriceValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)
        endPointPrice = \
            self.endPointPriceValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        #endPointDatetime = \
        #    self.endPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = startPointDatetime
                          
        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)

        # No need to save the musicalRatios inside self.artifact,
        # because each time there is a rotation or a check-marking
        # action, the internal artifact was updated.
        # The same is the case for the self.artifact.setReversed().

        self.log.debug("Exiting saveValues()")

    def _handleBarWidthValueSpinBoxChanged(self):
        """Called when the self.barWidthValueSpinBox is modified."""

        self.artifact.setBarWidth(\
            self.barWidthValueSpinBox.value())
        
    def _handleTextFontSizeValueSpinBoxChanged(self):
        """Called when the self.textFontSizeValueSpinBox is modified."""

        self.artifact.setFontSize(\
            self.textFontSizeValueSpinBox.value())
        
    def _handleTextEnabledCheckBoxToggled(self):
        """Called when the textEnabledCheckBox is checked or unchecked."""

        newValue = None
        
        if self.textEnabledCheckBox.checkState() == Qt.Checked:
            newValue = True
        else:
            newValue = False
        
        self.artifact.setTextEnabled(newValue)
        
    def _handleCheckMarkToggled(self):
        """Called when one of the check-mark boxes on the
        musicalRatios is checked or unchecked.
        """

        # Go through all the musicalRatios in the widget, and set them
        # as enabled or disabled in the artifact, based on the check
        # state of the QCheckBox objects in self.checkBoxes.
        for i in range(len(self.checkBoxes)):
            oldValue = self.artifact.getMusicalRatios()[i].isEnabled()
            newValue = None
            if self.checkBoxes[i].checkState() == Qt.Checked:
                newValue = True
            else:
                newValue = False

            if oldValue != newValue:
                self.log.debug("Updating enabled state of " +
                               "musicalRatio[{}] from {} to {}".\
                               format(i, oldValue, newValue))
                self.artifact.getMusicalRatios()[i].setEnabled(newValue)
            else:
                #self.log.debug("No update to musicalRatio[{}]".format(i))
                pass

    def _saveAndReloadMusicalRatios(self):
        """Saves and reloads the musical ratio widgets."""
        
        # Save values from what is in the widgets to the internal artifact.
        self.saveValues()
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateDownButtonClicked(self):
        """Called when the 'Rotate Down' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()

        if self.artifact.isReversed() == False:
            # Put the last musical ratio in the front.
            if len(musicalRatios) > 0:
                lastRatio = musicalRatios.pop(len(musicalRatios) - 1)
                musicalRatios.insert(0, lastRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
            
        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateUpButtonClicked(self):
        """Called when the 'Rotate Up' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()
        
        if self.artifact.isReversed() == False:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)

        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleReverseButtonClicked(self):
        """Called when the 'Reverse' button is clicked."""

        # Flip the flag that indicates that the musical ratios are reversed.
        self.artifact.setReversed(not self.artifact.isReversed())
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleCheckMarkAllButtonClicked(self):
        """Called when the 'Check All' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Checked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleCheckMarkNoneButtonClicked(self):
        """Called when the 'Check None' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Unchecked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartPriceModalScaleArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartPriceModalScaleArtifact.
    """

    def __init__(self,
                 priceBarChartPriceModalScaleArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartPriceModalScaleArtifact.
        
        Note: The 'priceBarChartPriceModalScaleArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartPriceModalScaleArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartPriceModalScaleArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartPriceModalScaleArtifact Data")

        # Check input.
        if not isinstance(priceBarChartPriceModalScaleArtifact,
                          PriceBarChartPriceModalScaleArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartPriceModalScaleArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartPriceModalScaleArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartPriceModalScaleArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartPriceModalScaleArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the artifact object.  If the 'Okay'
        button was previously clicked, then this object contains new
        values as set with the widget, otherwise it is unchanged.
        """

        # The edit widget keeps its own copy of the artifact, which it
        # modifies directly.
        if self.result() == QDialog.Accepted:
            return self.editWidget.getArtifact()
        else:
            return self.artifact


class PriceBarChartTextArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartTextArtifact within the context of a
    PriceBarChart.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartTextArtifact object.

        Arguments:
        artifact - PriceBarChartTextArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartTextArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartTextArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.priceLocationValueLabel = QLabel("Artifact location (in price):")
        self.priceLocationValueSpinBox = QDoubleSpinBox()
        self.priceLocationValueSpinBox.setDecimals(4)
        self.priceLocationValueSpinBox.setMinimum(0.0)
        self.priceLocationValueSpinBox.setMaximum(999999999.0)

        self.datetimeLocationLabel = QLabel("Artifact location (in time)")
        self.datetimeLocationWidget = TimestampEditWidget()
        self.datetimeLocationWidget.groupBox.setTitle("")
        self.datetimeLocationWidget.okayButton.setVisible(False)
        self.datetimeLocationWidget.cancelButton.setVisible(False)
        
        self.textLabel = QLabel("Text:")
        self.textEdit = QTextEdit()
        self.textEdit.setMinimumWidth(lineEditWidth)
        self.textEdit.setTabChangesFocus(True)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color of text:")
        self.colorEditPushButton = ColorEditPushButton()

        self.xScalingLabel = QLabel("X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)
        
        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.priceLocationValueLabel, r, 0, al)
        self.gridLayout.addWidget(self.priceLocationValueSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.datetimeLocationLabel, r, 0, al)
        self.gridLayout.addWidget(self.datetimeLocationWidget, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.textLabel, r, 0, al)
        self.gridLayout.addWidget(self.textEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditPushButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
                
        self.groupBox.setLayout(self.gridLayout)
        
        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.priceLocationValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.datetimeLocationWidget.setReadOnly(not self.readOnlyFlag)
        self.textEdit.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditPushButton.setEnabled(not self.readOnlyFlag)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartTextArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartTextArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))

        locationPointY = self.artifact.getPos().y()
        locationPointPrice = self.convertObj.sceneYPosToPrice(locationPointY)
        self.priceLocationValueSpinBox.setValue(locationPointPrice)
        
        locationPointX = self.artifact.getPos().x()
        locationPointDatetime = \
            self.convertObj.sceneXPosToDatetime(locationPointX)
        self.datetimeLocationWidget.\
            loadTimestamp(locationPointDatetime)

        self.textEdit.clear()
        self.textEdit.setText(self.artifact.getText())

        self.font = self.artifact.getFont()
        self.fontValueLabel.\
            setText(self._convertFontToNiceText(self.artifact.getFont()))
        
        self.colorEditPushButton.setColor(self.artifact.getColor())

        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())
        
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartTextArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widget.
        self.datetimeLocationWidget.saveTimestamp()
        
        # Position and start point are the same values for this artifact.

        price = self.priceLocationValueSpinBox.value()
        y = self.convertObj.priceToSceneYPos(price)

        locationPointDatetime = \
            self.datetimeLocationWidget.getTimestamp()
        x = \
            self.convertObj.datetimeToSceneXPos(locationPointDatetime)

        posF = QPointF(x, y)

        text = self.textEdit.toPlainText()

        font = self.font

        color = self.colorEditPushButton.getColor()

        xScaling = self.xScalingDoubleSpinBox.value()
        yScaling = self.yScalingDoubleSpinBox.value()

        
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setText(text)
        self.artifact.setFont(font)
        self.artifact.setColor(color)
        self.artifact.setTextXScaling(xScaling)
        self.artifact.setTextYScaling(yScaling)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv
        
    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))

    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()

        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartTextArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartTextArtifact.
    """

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartTextArtifact.
        
        Arguments:
        artifact - PriceBarChartTextArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartTextArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartTextArtifact Data")

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartTextArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = artifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartTextArtifactEditWidget(self.artifact,
                                                self.convertObj,
                                                self.readOnlyFlag)

        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def exec_(self):
        """Overwrites the QDialog.exec_() function.  Used so that we
        can set the focus to the text box right away before actually
        running exec_().
        """

        self.editWidget.textEdit.setFocus()
        return super().exec_()
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartTextArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartTextArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        """

        return self.editWidget.getArtifact()



class PriceBarChartPriceTimeInfoArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartPriceTimeInfoArtifact within the context of a
    PriceBarChart.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartPriceTimeInfoArtifact object.

        Arguments:
        artifact - PriceBarChartPriceTimeInfoArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartPriceTimeInfoArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartPriceTimeInfoArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.priceLocationValueLabel = QLabel("Artifact location (in price):")
        self.priceLocationValueSpinBox = QDoubleSpinBox()
        self.priceLocationValueSpinBox.setDecimals(4)
        self.priceLocationValueSpinBox.setMinimum(0.0)
        self.priceLocationValueSpinBox.setMaximum(999999999.0)

        self.datetimeLocationLabel = QLabel("Artifact location (in time)")
        self.datetimeLocationWidget = TimestampEditWidget()
        self.datetimeLocationWidget.groupBox.setTitle("")
        self.datetimeLocationWidget.okayButton.setVisible(False)
        self.datetimeLocationWidget.cancelButton.setVisible(False)
        
        self.priceTimeInfoPointPriceLocationValueLabel = \
            QLabel("PriceTimeInfo location (in price):")
        self.priceTimeInfoPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.priceTimeInfoPointPriceLocationValueSpinBox.setDecimals(4)
        self.priceTimeInfoPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.priceTimeInfoPointPriceLocationValueSpinBox.setMaximum(999999999.0)

        self.priceTimeInfoPointDatetimeLocationLabel = \
            QLabel("PriceTimeInfo location (in time)")
        self.priceTimeInfoPointDatetimeLocationWidget = TimestampEditWidget()
        self.priceTimeInfoPointDatetimeLocationWidget.groupBox.setTitle("")
        self.priceTimeInfoPointDatetimeLocationWidget.okayButton.\
            setVisible(False)
        self.priceTimeInfoPointDatetimeLocationWidget.cancelButton.\
            setVisible(False)

        self.showTimestampCheckBox = \
            QCheckBox("Show timestamp")
        self.showPriceCheckBox = \
            QCheckBox("Show price")
        self.showSqrtPriceCheckBox = \
            QCheckBox("Show square root of price")
        self.showTimeElapsedSinceBirthCheckBox = \
            QCheckBox("Show time elapsed since birth")
        self.showSqrtTimeElapsedSinceBirthCheckBox = \
            QCheckBox("Show square root of time elapsed since birth")
        self.showPriceScaledValueCheckBox = \
            QCheckBox("Show price scaled value")
        self.showSqrtPriceScaledValueCheckBox = \
            QCheckBox("Show sqrt price scaled value")
        self.showTimeScaledValueCheckBox = \
            QCheckBox("Show time scaled value")
        self.showSqrtTimeScaledValueCheckBox = \
            QCheckBox("Show sqrt time scaled value")
        self.showLineToInfoPointCheckBox = \
            QCheckBox("Show line from text to the InfoPoint")

        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color of text:")
        self.colorEditPushButton = ColorEditPushButton()

        self.xScalingLabel = QLabel("X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)
        
        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.priceLocationValueLabel, r, 0, al)
        self.gridLayout.addWidget(self.priceLocationValueSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.datetimeLocationLabel, r, 0, al)
        self.gridLayout.addWidget(self.datetimeLocationWidget, r, 1, al)
        r += 1
        self.gridLayout.addWidget(\
            self.priceTimeInfoPointPriceLocationValueLabel, r, 0, al)
        self.gridLayout.addWidget(\
            self.priceTimeInfoPointPriceLocationValueSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(\
            self.priceTimeInfoPointDatetimeLocationLabel, r, 0, al)
        self.gridLayout.addWidget(\
            self.priceTimeInfoPointDatetimeLocationWidget, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.showTimestampCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(self.showPriceCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(self.showSqrtPriceCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showTimeElapsedSinceBirthCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showSqrtTimeElapsedSinceBirthCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showPriceScaledValueCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showSqrtPriceScaledValueCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showTimeScaledValueCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showSqrtTimeScaledValueCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(\
            self.showLineToInfoPointCheckBox, r, 0, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditPushButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
                
        self.groupBox.setLayout(self.gridLayout)
        
        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.priceLocationValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.datetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.priceTimeInfoPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.priceTimeInfoPointDatetimeLocationWidget.\
            setReadOnly(self.readOnlyFlag)
        self.showTimestampCheckBox.setEnabled(not self.readOnlyFlag)
        self.showPriceCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtPriceCheckBox.setEnabled(not self.readOnlyFlag)
        self.showTimeElapsedSinceBirthCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtTimeElapsedSinceBirthCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showPriceScaledValueCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtPriceScaledValueCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showTimeScaledValueCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtTimeScaledValueCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showLineToInfoPointCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditPushButton.setEnabled(not self.readOnlyFlag)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartPriceTimeInfoArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartPriceTimeInfoArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))

        # position in price and time.
        locationPointY = self.artifact.getPos().y()
        locationPointPrice = self.convertObj.sceneYPosToPrice(locationPointY)
        self.priceLocationValueSpinBox.setValue(locationPointPrice)
        
        locationPointX = self.artifact.getPos().x()
        locationPointDatetime = \
            self.convertObj.sceneXPosToDatetime(locationPointX)
        self.datetimeLocationWidget.\
            loadTimestamp(locationPointDatetime)

        # priceTimeInfoPoint in price and time.
        locationPointY = self.artifact.getInfoPointF().y()
        locationPointPrice = self.convertObj.sceneYPosToPrice(locationPointY)
        self.priceTimeInfoPointPriceLocationValueSpinBox.\
            setValue(locationPointPrice)
        
        locationPointX = self.artifact.getInfoPointF().x()
        locationPointDatetime = \
            self.convertObj.sceneXPosToDatetime(locationPointX)
        self.priceTimeInfoPointDatetimeLocationWidget.\
            loadTimestamp(locationPointDatetime)

        # Checkboxes.
        if self.artifact.getShowTimestampFlag():
            self.showTimestampCheckBox.setCheckState(Qt.Checked)
        else:
            self.showTimestampCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowPriceFlag():
            self.showPriceCheckBox.setCheckState(Qt.Checked)
        else:
            self.showPriceCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtPriceFlag():
            self.showSqrtPriceCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtPriceCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowTimeElapsedSinceBirthFlag():
            self.showTimeElapsedSinceBirthCheckBox.setCheckState(Qt.Checked)
        else:
            self.showTimeElapsedSinceBirthCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtTimeElapsedSinceBirthFlag():
            self.showSqrtTimeElapsedSinceBirthCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrtTimeElapsedSinceBirthCheckBox.\
                setCheckState(Qt.Unchecked)

        if self.artifact.getShowPriceScaledValueFlag():
            self.showPriceScaledValueCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showPriceScaledValueCheckBox.\
                setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtPriceScaledValueFlag():
            self.showSqrtPriceScaledValueCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrtPriceScaledValueCheckBox.\
                setCheckState(Qt.Unchecked)

        if self.artifact.getShowTimeScaledValueFlag():
            self.showTimeScaledValueCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showTimeScaledValueCheckBox.\
                setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowSqrtTimeScaledValueFlag():
            self.showSqrtTimeScaledValueCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrtTimeScaledValueCheckBox.\
                setCheckState(Qt.Unchecked)

        if self.artifact.getShowLineToInfoPointFlag():
            self.showLineToInfoPointCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showLineToInfoPointCheckBox.\
                setCheckState(Qt.Unchecked)

        # Font.
        self.font = self.artifact.getFont()
        self.fontValueLabel.\
            setText(self._convertFontToNiceText(self.artifact.getFont()))

        # Color.
        self.colorEditPushButton.setColor(self.artifact.getColor())

        # Scaling.
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())
        
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartPriceTimeInfoArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widget.
        self.datetimeLocationWidget.saveTimestamp()
        self.priceTimeInfoPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point for this artifact are the same values.
        price = self.priceLocationValueSpinBox.value()
        y = self.convertObj.priceToSceneYPos(price)
        locationPointDatetime = \
            self.datetimeLocationWidget.getTimestamp()
        x = \
            self.convertObj.datetimeToSceneXPos(locationPointDatetime)
        posF = QPointF(x, y)

        # Position of the priceTimeInfoPoint.
        price = self.priceTimeInfoPointPriceLocationValueSpinBox.value()
        y = self.convertObj.priceToSceneYPos(price)
        locationPointDatetime = \
            self.priceTimeInfoPointDatetimeLocationWidget.getTimestamp()
        x = \
            self.convertObj.datetimeToSceneXPos(locationPointDatetime)
        priceTimeInfoPoint = QPointF(x, y)

        # Checkboxes.
        showTimestampFlag = None
        if self.showTimestampCheckBox.checkState() == Qt.Checked:
            showTimestampFlag = True
        else:
            showTimestampFlag = False

        showPriceFlag = None
        if self.showPriceCheckBox.checkState() == Qt.Checked:
            showPriceFlag = True
        else:
            showPriceFlag = False

        showSqrtPriceFlag = None
        if self.showSqrtPriceCheckBox.checkState() == Qt.Checked:
            showSqrtPriceFlag = True
        else:
            showSqrtPriceFlag = False

        showTimeElapsedSinceBirthFlag = None
        if self.showTimeElapsedSinceBirthCheckBox.checkState() == Qt.Checked:
            showTimeElapsedSinceBirthFlag = True
        else:
            showTimeElapsedSinceBirthFlag = False
            
        showSqrtTimeElapsedSinceBirthFlag = None
        if self.showSqrtTimeElapsedSinceBirthCheckBox.checkState() == \
               Qt.Checked:
            
            showSqrtTimeElapsedSinceBirthFlag = True
        else:
            showSqrtTimeElapsedSinceBirthFlag = False

        showPriceScaledValueFlag = None
        if self.showPriceScaledValueCheckBox.checkState() == Qt.Checked:
            showPriceScaledValueFlag = True
        else:
            showPriceScaledValueFlag = False

        showSqrtPriceScaledValueFlag = None
        if self.showSqrtPriceScaledValueCheckBox.checkState() == Qt.Checked:
            showSqrtPriceScaledValueFlag = True
        else:
            showSqrtPriceScaledValueFlag = False

        showTimeScaledValueFlag = None
        if self.showTimeScaledValueCheckBox.checkState() == Qt.Checked:
            showTimeScaledValueFlag = True
        else:
            showTimeScaledValueFlag = False

        showSqrtTimeScaledValueFlag = None
        if self.showSqrtTimeScaledValueCheckBox.checkState() == Qt.Checked:
            showSqrtTimeScaledValueFlag = True
        else:
            showSqrtTimeScaledValueFlag = False

        showLineToInfoPointFlag = None
        if self.showLineToInfoPointCheckBox.checkState() == Qt.Checked:
            showLineToInfoPointFlag = True
        else:
            showLineToInfoPointFlag = False

        
        font = self.font

        color = self.colorEditPushButton.getColor()

        xScaling = self.xScalingDoubleSpinBox.value()
        yScaling = self.yScalingDoubleSpinBox.value()

        
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setInfoPointF(priceTimeInfoPoint)
        self.artifact.setShowTimestampFlag(showTimestampFlag)
        self.artifact.setShowPriceFlag(showPriceFlag)
        self.artifact.setShowSqrtPriceFlag(showSqrtPriceFlag)
        self.artifact.setShowTimeElapsedSinceBirthFlag(\
            showTimeElapsedSinceBirthFlag)
        self.artifact.setShowSqrtTimeElapsedSinceBirthFlag(\
            showSqrtTimeElapsedSinceBirthFlag)
        self.artifact.setShowPriceScaledValueFlag(\
            showPriceScaledValueFlag)
        self.artifact.setShowSqrtPriceScaledValueFlag(\
            showSqrtPriceScaledValueFlag)
        self.artifact.setShowTimeScaledValueFlag(\
            showTimeScaledValueFlag)
        self.artifact.setShowSqrtTimeScaledValueFlag(\
            showSqrtTimeScaledValueFlag)
        self.artifact.setShowLineToInfoPointFlag(\
            showLineToInfoPointFlag)
        self.artifact.setFont(font)
        self.artifact.setColor(color)
        self.artifact.setTextXScaling(xScaling)
        self.artifact.setTextYScaling(yScaling)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv
        
    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))

    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()

        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartPriceTimeInfoArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartPriceTimeInfoArtifact.
    """

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartPriceTimeInfoArtifact.
        
        Arguments:
        artifact - PriceBarChartPriceTimeInfoArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartPriceTimeInfoArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartPriceTimeInfoArtifact Data")

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartPriceTimeInfoArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = artifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartPriceTimeInfoArtifactEditWidget(self.artifact,
                                                         self.convertObj,
                                                         self.readOnlyFlag)

        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartPriceTimeInfoArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartPriceTimeInfoArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        """

        return self.editWidget.getArtifact()



class PriceBarChartPriceMeasurementArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartPriceMeasurementArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartPriceMeasurementArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartPriceMeasurementArtifact object.

        Arguments:
        artifact - PriceBarChartPriceMeasurementArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to price, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger("pricebarchart_dialogs.PriceBarChartPriceMeasurementArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartPriceMeasurementArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.startPointPriceLocationValueLabel = \
            QLabel("PriceMeasurement start location (in price):")
        self.startPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.startPointPriceLocationValueSpinBox.setDecimals(4)
        self.startPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.startPointPriceLocationValueSpinBox.setMaximum(999999999.0)

        self.endPointPriceLocationValueLabel = \
            QLabel("PriceMeasurement end location (in price):")
        self.endPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.endPointPriceLocationValueSpinBox.setDecimals(4)
        self.endPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.endPointPriceLocationValueSpinBox.setMaximum(999999999.0)

        self.datetimeLocationWidget = TimestampEditWidget()
        self.datetimeLocationWidget.groupBox.\
            setTitle("PriceMeasurement location (in time)")
        self.datetimeLocationWidget.okayButton.setVisible(False)
        self.datetimeLocationWidget.cancelButton.setVisible(False)
        
        self.showPriceRangeTextFlagCheckBox = \
            QCheckBox("Show Price Range Text")
        self.showSqrtPriceRangeTextFlagCheckBox = \
            QCheckBox("Show Sqrt Price Range Text")
        self.showScaledValueRangeTextFlagCheckBox = \
            QCheckBox("Show scaled value range text")
        self.showSqrtScaledValueRangeTextFlagCheckBox = \
            QCheckBox("Show sqrt scaled value range text")
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.textColorLabel, r, 0, al)
        self.gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.startPointPriceLocationValueLabel,
                                  r, 0, al)
        self.gridLayout.addWidget(self.startPointPriceLocationValueSpinBox,
                                  r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.endPointPriceLocationValueLabel,
                                  r, 0, al)
        self.gridLayout.addWidget(self.endPointPriceLocationValueSpinBox,
                                  r, 1, al)
        r += 1

        # Layout just for the checkboxes for showing text.
        self.showTextCheckBoxesLayout = QVBoxLayout()
        self.showTextCheckBoxesLayout.addWidget(\
            self.showPriceRangeTextFlagCheckBox)
        self.showTextCheckBoxesLayout.addWidget(\
            self.showSqrtPriceRangeTextFlagCheckBox)
        self.showTextCheckBoxesLayout.addWidget(\
            self.showScaledValueRangeTextFlagCheckBox)
        self.showTextCheckBoxesLayout.addWidget(\
            self.showSqrtScaledValueRangeTextFlagCheckBox)
        tempLayout = self.showTextCheckBoxesLayout
        self.showTextCheckBoxesLayout = QHBoxLayout()
        self.showTextCheckBoxesLayout.addLayout(tempLayout)
        self.showTextCheckBoxesLayout.addStretch()

        # Put all the layouts together.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addWidget(self.datetimeLocationWidget)
        self.layout.addLayout(self.showTextCheckBoxesLayout)
        self.groupBox.setLayout(self.layout)

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.endPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.datetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        self.showPriceRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtPriceRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showScaledValueRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtScaledValueRangeTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)

        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartPriceMeasurementArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartPriceMeasurementArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        
        startPointY = self.artifact.startPointF.y()
        startLocationPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceLocationValueSpinBox.\
            setValue(startLocationPointPrice)
        
        endPointY = self.artifact.endPointF.y()
        endLocationPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        self.endPointPriceLocationValueSpinBox.\
            setValue(endLocationPointPrice)
        
        pointX = self.artifact.startPointF.x()
        dt = self.convertObj.sceneXPosToDatetime(pointX)
        self.datetimeLocationWidget.loadTimestamp(dt)
        
        if self.artifact.getShowPriceRangeTextFlag() == True:
            self.showPriceRangeTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showPriceRangeTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtPriceRangeTextFlag() == True:
            self.showSqrtPriceRangeTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtPriceRangeTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowScaledValueRangeTextFlag() == True:
            
            self.showScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtScaledValueRangeTextFlag() == True:
            
            self.showSqrtScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrtScaledValueRangeTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)
            
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartPriceMeasurementArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widget.
        self.datetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.

        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)

        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        dt = self.datetimeLocationWidget.getTimestamp()
        x = self.convertObj.datetimeToSceneXPos(dt)

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()

        posF = QPointF(x, startPointY)
        startPointF = QPointF(x, startPointY)
        endPointF = QPointF(x, endPointY)

        showPriceRangeTextFlag = \
            (self.showPriceRangeTextFlagCheckBox.checkState() == Qt.Checked)
        showSqrtPriceRangeTextFlag = \
            (self.showSqrtPriceRangeTextFlagCheckBox.checkState() == Qt.Checked)
        showScaledValueRangeTextFlag = \
            (self.showScaledValueRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        showSqrtScaledValueRangeTextFlag = \
            (self.showSqrtScaledValueRangeTextFlagCheckBox.checkState() == \
             Qt.Checked)
        
        
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)
        self.artifact.setShowPriceRangeTextFlag(showPriceRangeTextFlag)
        self.artifact.setShowSqrtPriceRangeTextFlag(showSqrtPriceRangeTextFlag)
        self.artifact.setShowScaledValueRangeTextFlag(\
            showScaledValueRangeTextFlag)
        self.artifact.setShowSqrtScaledValueRangeTextFlag(\
            showSqrtScaledValueRangeTextFlag)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartPriceMeasurementArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartPriceMeasurementArtifact.
    """

    def __init__(self,
                 priceBarChartPriceMeasurementArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartPriceMeasurementArtifact.
        
        Note: The 'priceBarChartPriceMeasurementArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartPriceMeasurementArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartPriceMeasurementArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartPriceMeasurementArtifact Data")

        # Check input.
        if not isinstance(priceBarChartPriceMeasurementArtifact,
                          PriceBarChartPriceMeasurementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartPriceMeasurementArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartPriceMeasurementArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartPriceMeasurementArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartPriceMeasurementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartTimeRetracementArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartTimeRetracementArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartTimeRetracementArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartTimeRetracementArtifact object.

        Arguments:
        artifact - PriceBarChartTimeRetracementArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger(\
            "pricebarchart_dialogs.PriceBarChartTimeRetracementArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartTimeRetracementArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.startPointPriceLocationValueLabel = \
            QLabel("TimeRetracement Start Point (in price):")
        self.startPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.startPointPriceLocationValueSpinBox.setDecimals(4)
        self.startPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.startPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        startPointPriceLocationValueLayout = QHBoxLayout()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueLabel)
        startPointPriceLocationValueLayout.addStretch()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueSpinBox)

        #self.endPointPriceLocationValueLabel = \
        #    QLabel("TimeRetracement End Point (in price):")
        #self.endPointPriceLocationValueSpinBox = QDoubleSpinBox()
        #self.endPointPriceLocationValueSpinBox.setDecimals(4)
        #self.endPointPriceLocationValueSpinBox.setMinimum(0.0)
        #self.endPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        #endPointPriceLocationValueLayout = QHBoxLayout()
        #endPointPriceLocationValueLayout.\
        #    addWidget(self.endPointPriceLocationValueLabel)
        #endPointPriceLocationValueLayout.addStretch()
        #endPointPriceLocationValueLayout.\
        #    addWidget(self.endPointPriceLocationValueSpinBox)

        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("TimeRetracement Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("TimeRetracement End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.showFullLinesFlagCheckBox = \
            QCheckBox("Show Full Lines")
        self.showTimeTextFlagCheckBox = \
            QCheckBox("Show Time Text")
        self.showPercentTextFlagCheckBox = \
            QCheckBox("Show Percent Text")
        
        self.ratioCheckBoxes = []
        for ratio in artifact.getRatios():
            checkBox = \
                QCheckBox("Ratio " + ratio.getDescription() + " enabled")
            self.ratioCheckBoxes.append(checkBox)
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.textColorLabel, r, 0, al)
        self.gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addLayout(startPointPriceLocationValueLayout, r, 0, al)
        #self.gridLayout.addLayout(endPointPriceLocationValueLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        self.gridLayout.addWidget(self.endPointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1

        # Layout just for the checkboxes for showing lines/text, and
        # for enabled ratios.
        self.checkBoxesLayout = QVBoxLayout()
        self.checkBoxesLayout.addWidget(\
            self.showFullLinesFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showTimeTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showPercentTextFlagCheckBox)
        for checkBox in self.ratioCheckBoxes:
            self.checkBoxesLayout.addWidget(checkBox)
        tempLayout = self.checkBoxesLayout
        self.checkBoxesLayout = QHBoxLayout()
        self.checkBoxesLayout.addLayout(tempLayout)
        self.checkBoxesLayout.addStretch()

        # Put all the layouts together.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addLayout(self.checkBoxesLayout)
        self.groupBox.setLayout(self.layout)

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        #self.endPointPriceLocationValueSpinBox.\
        #    setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        self.showFullLinesFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showTimeTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showPercentTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        
        for checkBox in self.ratioCheckBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
            
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartTimeRetracementArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartTimeRetracementArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        
        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceLocationValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        #self.endPointPriceLocationValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        if self.artifact.getShowFullLinesFlag() == True:
            self.showFullLinesFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showFullLinesFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowTimeTextFlag() == True:
            self.showTimeTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showTimeTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowPercentTextFlag() == True:
            self.showPercentTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showPercentTextFlagCheckBox.setCheckState(Qt.Unchecked)

        ratios = self.artifact.getRatios()
        for i in range(len(ratios)):
            ratio = ratios[i]
            
            if ratio.isEnabled() == True:
                self.ratioCheckBoxes[i].setCheckState(Qt.Checked)
            else:
                self.ratioCheckBoxes[i].setCheckState(Qt.Unchecked)
            
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartTimeRetracementArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        #endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        #endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        endPointY = startPointY
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        # Position and start point should be the same values.

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        showFullLinesFlag = \
            (self.showFullLinesFlagCheckBox.checkState() == Qt.Checked)
        showTimeTextFlag = \
            (self.showTimeTextFlagCheckBox.checkState() == Qt.Checked)
        showPercentTextFlag = \
            (self.showPercentTextFlagCheckBox.checkState() == Qt.Checked)
        ratioEnabledFlags = []
        for checkBox in self.ratioCheckBoxes:
            if checkBox.checkState() == Qt.Checked:
                ratioEnabledFlags.append(True)
            else:
                ratioEnabledFlags.append(False)
                
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)
        self.artifact.setShowFullLinesFlag(showFullLinesFlag)
        self.artifact.setShowTimeTextFlag(showTimeTextFlag)
        self.artifact.setShowPercentTextFlag(showPercentTextFlag)

        ratios = self.artifact.getRatios()
        for i in range(len(ratioEnabledFlags)):
            flag = ratioEnabledFlags[i]
            ratios[i].setEnabled(flag)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartTimeRetracementArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartTimeRetracementArtifact.
    """

    def __init__(self,
                 priceBarChartTimeRetracementArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartTimeRetracementArtifact.
        
        Note: The 'priceBarChartTimeRetracementArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartTimeRetracementArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
        "pricebarchart_dialogs.PriceBarChartTimeRetracementArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartTimeRetracementArtifact Data")

        # Check input.
        if not isinstance(priceBarChartTimeRetracementArtifact,
                          PriceBarChartTimeRetracementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartTimeRetracementArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartTimeRetracementArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartTimeRetracementArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartTimeRetracementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartPriceRetracementArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartPriceRetracementArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartPriceRetracementArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartPriceRetracementArtifact object.

        Arguments:
        artifact - PriceBarChartPriceRetracementArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartPriceRetracementArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartPriceRetracementArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.startPointPriceLocationValueLabel = \
            QLabel("PriceRetracement Start Point (in price):")
        self.startPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.startPointPriceLocationValueSpinBox.setDecimals(4)
        self.startPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.startPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        startPointPriceLocationValueLayout = QHBoxLayout()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueLabel)
        startPointPriceLocationValueLayout.addStretch()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueSpinBox)

        self.endPointPriceLocationValueLabel = \
            QLabel("PriceRetracement End Point (in price):")
        self.endPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.endPointPriceLocationValueSpinBox.setDecimals(4)
        self.endPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.endPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        endPointPriceLocationValueLayout = QHBoxLayout()
        endPointPriceLocationValueLayout.\
            addWidget(self.endPointPriceLocationValueLabel)
        endPointPriceLocationValueLayout.addStretch()
        endPointPriceLocationValueLayout.\
            addWidget(self.endPointPriceLocationValueSpinBox)

        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("PriceRetracement Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        #self.endPointDatetimeLocationWidget = TimestampEditWidget()
        #self.endPointDatetimeLocationWidget.groupBox.\
        #    setTitle("PriceRetracement End Point (in time)")
        #self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        #self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.showFullLinesFlagCheckBox = \
            QCheckBox("Show Full Lines")
        self.showPriceTextFlagCheckBox = \
            QCheckBox("Show Price Text")
        self.showPercentTextFlagCheckBox = \
            QCheckBox("Show Percent Text")
        
        self.ratioCheckBoxes = []
        for ratio in artifact.getRatios():
            checkBox = \
                QCheckBox("Ratio " + ratio.getDescription() + " enabled")
            self.ratioCheckBoxes.append(checkBox)
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.textColorLabel, r, 0, al)
        self.gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addLayout(startPointPriceLocationValueLayout, r, 0, al)
        self.gridLayout.addLayout(endPointPriceLocationValueLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        #self.gridLayout.addWidget(self.endPointDatetimeLocationWidget,
        #                          r, 1, al)
        r += 1

        # Layout just for the checkboxes for showing lines/text, and
        # for enabled ratios.
        self.checkBoxesLayout = QVBoxLayout()
        self.checkBoxesLayout.addWidget(\
            self.showFullLinesFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showPriceTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showPercentTextFlagCheckBox)
        for checkBox in self.ratioCheckBoxes:
            self.checkBoxesLayout.addWidget(checkBox)
        tempLayout = self.checkBoxesLayout
        self.checkBoxesLayout = QHBoxLayout()
        self.checkBoxesLayout.addLayout(tempLayout)
        self.checkBoxesLayout.addStretch()

        # Put all the layouts together.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addLayout(self.checkBoxesLayout)
        self.groupBox.setLayout(self.layout)

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.endPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        #self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        self.showFullLinesFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showPriceTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showPercentTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        
        for checkBox in self.ratioCheckBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
            
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartPriceRetracementArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartPriceRetracementArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        
        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceLocationValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        self.endPointPriceLocationValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        #self.endPointDatetimeLocationWidget.\
        #    loadTimestamp(endPointDatetime)

        if self.artifact.getShowFullLinesFlag() == True:
            self.showFullLinesFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showFullLinesFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowPriceTextFlag() == True:
            self.showPriceTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showPriceTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowPercentTextFlag() == True:
            self.showPercentTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showPercentTextFlagCheckBox.setCheckState(Qt.Unchecked)

        ratios = self.artifact.getRatios()
        for i in range(len(ratios)):
            ratio = ratios[i]
            
            if ratio.isEnabled() == True:
                self.ratioCheckBoxes[i].setCheckState(Qt.Checked)
            else:
                self.ratioCheckBoxes[i].setCheckState(Qt.Unchecked)
            
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartPriceRetracementArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        #self.endPointDatetimeLocationWidget.saveTimestamp()
        
        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        #endPointDatetime = \
        #    self.endPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = startPointDatetime

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        # Position and start point should be the same values.

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        showFullLinesFlag = \
            (self.showFullLinesFlagCheckBox.checkState() == Qt.Checked)
        showPriceTextFlag = \
            (self.showPriceTextFlagCheckBox.checkState() == Qt.Checked)
        showPercentTextFlag = \
            (self.showPercentTextFlagCheckBox.checkState() == Qt.Checked)
        ratioEnabledFlags = []
        for checkBox in self.ratioCheckBoxes:
            if checkBox.checkState() == Qt.Checked:
                ratioEnabledFlags.append(True)
            else:
                ratioEnabledFlags.append(False)
                
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)
        self.artifact.setShowFullLinesFlag(showFullLinesFlag)
        self.artifact.setShowPriceTextFlag(showPriceTextFlag)
        self.artifact.setShowPercentTextFlag(showPercentTextFlag)

        ratios = self.artifact.getRatios()
        for i in range(len(ratioEnabledFlags)):
            flag = ratioEnabledFlags[i]
            ratios[i].setEnabled(flag)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartPriceRetracementArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartPriceRetracementArtifact.
    """

    def __init__(self,
                 priceBarChartPriceRetracementArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartPriceRetracementArtifact.
        
        Note: The 'priceBarChartPriceRetracementArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartPriceRetracementArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
        "pricebarchart_dialogs.PriceBarChartPriceRetracementArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartPriceRetracementArtifact Data")

        # Check input.
        if not isinstance(priceBarChartPriceRetracementArtifact,
                          PriceBarChartPriceRetracementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartPriceRetracementArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartPriceRetracementArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartPriceRetracementArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartPriceRetracementArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartPriceTimeVectorArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartPriceTimeVectorArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartPriceTimeVectorArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartPriceTimeVectorArtifact object.

        Arguments:
        artifact - PriceBarChartPriceTimeVectorArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartPriceTimeVectorArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartPriceTimeVectorArtifact Data:")


        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.startPointPriceLocationValueLabel = \
            QLabel("PriceTimeVector Start Point (in price):")
        self.startPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.startPointPriceLocationValueSpinBox.setDecimals(4)
        self.startPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.startPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        startPointPriceLocationValueLayout = QHBoxLayout()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueLabel)
        startPointPriceLocationValueLayout.addStretch()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueSpinBox)

        self.endPointPriceLocationValueLabel = \
            QLabel("PriceTimeVector End Point (in price):")
        self.endPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.endPointPriceLocationValueSpinBox.setDecimals(4)
        self.endPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.endPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        endPointPriceLocationValueLayout = QHBoxLayout()
        endPointPriceLocationValueLayout.\
            addWidget(self.endPointPriceLocationValueLabel)
        endPointPriceLocationValueLayout.addStretch()
        endPointPriceLocationValueLayout.\
            addWidget(self.endPointPriceLocationValueSpinBox)

        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("PriceTimeVector Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("PriceTimeVector End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.showDistanceTextFlagCheckBox = \
            QCheckBox("Show distance text")
        self.showSqrtDistanceTextFlagCheckBox = \
            QCheckBox("Show sqrt distance text")
        self.showDistanceScaledValueTextFlagCheckBox = \
            QCheckBox("Show distance scaled value text")
        self.showSqrtDistanceScaledValueTextFlagCheckBox = \
            QCheckBox("Show sqrt distance scaled value text")
        self.angleTextFlagCheckBox = \
            QCheckBox("Show angle of the PriceTimeVector text")
        self.tiltedTextFlagCheckBox = \
            QCheckBox("Tilted Text")
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.textColorLabel, r, 0, al)
        self.gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addLayout(startPointPriceLocationValueLayout, r, 0, al)
        self.gridLayout.addLayout(endPointPriceLocationValueLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        self.gridLayout.addWidget(self.endPointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1

        # Layout just for the checkboxes for showing lines/text, and
        # for enabled ratios.
        self.checkBoxesLayout = QVBoxLayout()
        self.checkBoxesLayout.addWidget(\
            self.showDistanceTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showSqrtDistanceTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showDistanceScaledValueTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.showSqrtDistanceScaledValueTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.angleTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.tiltedTextFlagCheckBox)
        tempLayout = self.checkBoxesLayout
        self.checkBoxesLayout = QHBoxLayout()
        self.checkBoxesLayout.addLayout(tempLayout)
        self.checkBoxesLayout.addStretch()

        # Put all the layouts together.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addLayout(self.checkBoxesLayout)
        self.groupBox.setLayout(self.layout)

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.endPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        self.showDistanceTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showSqrtDistanceTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.showDistanceScaledValueTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.showSqrtDistanceScaledValueTextFlagCheckBox.\
            setEnabled(not self.readOnlyFlag)
        self.tiltedTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.angleTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartPriceTimeVectorArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartPriceTimeVectorArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())

        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceLocationValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        self.endPointPriceLocationValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        if self.artifact.getShowDistanceTextFlag() == True:
            self.showDistanceTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showDistanceTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtDistanceTextFlag() == True:
            self.showSqrtDistanceTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.showSqrtDistanceTextFlagCheckBox.setCheckState(Qt.Unchecked)
            
        if self.artifact.getShowDistanceScaledValueTextFlag() == True:
            self.showDistanceScaledValueTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showDistanceScaledValueTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)

        if self.artifact.getShowSqrtDistanceScaledValueTextFlag() == True:
            self.showSqrtDistanceScaledValueTextFlagCheckBox.\
                setCheckState(Qt.Checked)
        else:
            self.showSqrtDistanceScaledValueTextFlagCheckBox.\
                setCheckState(Qt.Unchecked)
            
        if self.artifact.getTiltedTextFlag() == True:
            self.tiltedTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.tiltedTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getAngleTextFlag() == True:
            self.angleTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.angleTextFlagCheckBox.setCheckState(Qt.Unchecked)

        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartPriceTimeVectorArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        # Position and start point should be the same values.

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        showDistanceTextFlag = \
            (self.showDistanceTextFlagCheckBox.checkState() == Qt.Checked)
        showSqrtDistanceTextFlag = \
            (self.showSqrtDistanceTextFlagCheckBox.checkState() == Qt.Checked)
        showDistanceScaledValueTextFlag = \
            (self.showDistanceScaledValueTextFlagCheckBox.\
             checkState() == Qt.Checked)
        showSqrtDistanceScaledValueTextFlag = \
            (self.showSqrtDistanceScaledValueTextFlagCheckBox.\
             checkState() == Qt.Checked)
        tiltedTextFlag = \
            (self.tiltedTextFlagCheckBox.checkState() == Qt.Checked)
        angleTextFlag = \
            (self.angleTextFlagCheckBox.checkState() == Qt.Checked)
        
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)
        self.artifact.setShowDistanceTextFlag(showDistanceTextFlag)
        self.artifact.setShowSqrtDistanceTextFlag(showSqrtDistanceTextFlag)
        self.artifact.setShowDistanceScaledValueTextFlag(\
            showDistanceScaledValueTextFlag)
        self.artifact.setShowSqrtDistanceScaledValueTextFlag(\
            showSqrtDistanceScaledValueTextFlag)
        self.artifact.setTiltedTextFlag(tiltedTextFlag)
        self.artifact.setAngleTextFlag(angleTextFlag)

        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartPriceTimeVectorArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartPriceTimeVectorArtifact.
    """

    def __init__(self,
                 priceBarChartPriceTimeVectorArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartPriceTimeVectorArtifact.
        
        Note: The 'priceBarChartPriceTimeVectorArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartPriceTimeVectorArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
        "pricebarchart_dialogs.PriceBarChartPriceTimeVectorArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartPriceTimeVectorArtifact Data")

        # Check input.
        if not isinstance(priceBarChartPriceTimeVectorArtifact,
                          PriceBarChartPriceTimeVectorArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartPriceTimeVectorArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartPriceTimeVectorArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartPriceTimeVectorArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartPriceTimeVectorArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartLineSegmentArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartLineSegmentArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartLineSegmentArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartLineSegmentArtifact object.

        Arguments:
        artifact - PriceBarChartLineSegmentArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger("pricebarchart_dialogs.PriceBarChartLineSegmentArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBox = QGroupBox("PriceBarChartLineSegmentArtifact Data:")

        # Settings object.
        settings = QSettings()

        # Value for extending the line segment by a certain multiple
        # of the length.
        # initialExtendMultiple (float).
        initialExtendMultiple = 1.6

        # Width of the QLineEdit, so it that it displays nicely.
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.startPointPriceLocationValueLabel = \
            QLabel("LineSegment Start Point (in price):")
        self.startPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.startPointPriceLocationValueSpinBox.setDecimals(4)
        self.startPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.startPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        startPointPriceLocationValueLayout = QHBoxLayout()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueLabel)
        startPointPriceLocationValueLayout.addStretch()
        startPointPriceLocationValueLayout.\
            addWidget(self.startPointPriceLocationValueSpinBox)

        self.endPointPriceLocationValueLabel = \
            QLabel("LineSegment End Point (in price):")
        self.endPointPriceLocationValueSpinBox = QDoubleSpinBox()
        self.endPointPriceLocationValueSpinBox.setDecimals(4)
        self.endPointPriceLocationValueSpinBox.setMinimum(0.0)
        self.endPointPriceLocationValueSpinBox.setMaximum(999999999.0)
        endPointPriceLocationValueLayout = QHBoxLayout()
        endPointPriceLocationValueLayout.\
            addWidget(self.endPointPriceLocationValueLabel)
        endPointPriceLocationValueLayout.addStretch()
        endPointPriceLocationValueLayout.\
            addWidget(self.endPointPriceLocationValueSpinBox)

        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("LineSegment Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("LineSegment End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.extendStartPointLabel = QLabel("Extend start point by: ")
        self.extendStartPointSpinBox = QDoubleSpinBox()
        self.extendStartPointSpinBox.setDecimals(2)
        self.extendStartPointSpinBox.setMinimum(0.0)
        self.extendStartPointSpinBox.setMaximum(999999999.0)
        self.extendStartPointSpinBox.setValue(initialExtendMultiple)
        self.extendStartPointButton = QPushButton("Extend")
        extendStartPointLayout = QHBoxLayout()
        extendStartPointLayout.addWidget(self.extendStartPointLabel)
        extendStartPointLayout.addWidget(self.extendStartPointSpinBox)
        extendStartPointLayout.addWidget(self.extendStartPointButton)
        
        self.extendEndPointLabel = QLabel("Extend end point by: ")
        self.extendEndPointSpinBox = QDoubleSpinBox()
        self.extendEndPointSpinBox.setDecimals(2)
        self.extendEndPointSpinBox.setMinimum(0.0)
        self.extendEndPointSpinBox.setMaximum(999999999.0)
        self.extendEndPointSpinBox.setValue(initialExtendMultiple)
        self.extendEndPointButton = QPushButton("Extend")
        extendEndPointLayout = QHBoxLayout()
        extendEndPointLayout.addWidget(self.extendEndPointLabel)
        extendEndPointLayout.addWidget(self.extendEndPointSpinBox)
        extendEndPointLayout.addWidget(self.extendEndPointButton)
        
        self.angleTextFlagCheckBox = \
            QCheckBox("Show angle of the LineSegment text")
        self.tiltedTextFlagCheckBox = \
            QCheckBox("Tilted Text")
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        self.gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        self.gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        self.gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.uuidLabel, r, 0, al)
        self.gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        self.gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.fontLabel, r, 0, al)
        self.gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.colorLabel, r, 0, al)
        self.gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.textColorLabel, r, 0, al)
        self.gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        self.gridLayout.addLayout(startPointPriceLocationValueLayout, r, 0, al)
        self.gridLayout.addLayout(endPointPriceLocationValueLayout, r, 1, al)
        r += 1
        self.gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        self.gridLayout.addWidget(self.endPointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1
        self.gridLayout.addLayout(extendStartPointLayout, r, 0, al)
        self.gridLayout.addLayout(extendEndPointLayout, r, 1, al)
        r += 1

        # Layout just for the checkboxes for showing lines/text, and
        # for enabled ratios.
        self.checkBoxesLayout = QVBoxLayout()
        self.checkBoxesLayout.addWidget(\
            self.angleTextFlagCheckBox)
        self.checkBoxesLayout.addWidget(\
            self.tiltedTextFlagCheckBox)
        tempLayout = self.checkBoxesLayout
        self.checkBoxesLayout = QHBoxLayout()
        self.checkBoxesLayout.addLayout(tempLayout)
        self.checkBoxesLayout.addStretch()

        # Put all the layouts together.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addLayout(self.checkBoxesLayout)
        self.groupBox.setLayout(self.layout)

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.groupBox) 
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        self.setReadOnly(self.readOnlyFlag)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(self.artifact)

        # Connect signals and slots.

        self.fontEditButton.clicked.connect(self._handleFontEditButtonClicked)
        self.extendStartPointButton.clicked.\
            connect(self._handleExtendStartPointButtonClicked)
        self.extendEndPointButton.clicked.\
            connect(self._handleExtendEndPointButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.endPointPriceLocationValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.extendStartPointSpinBox.setReadOnly(self.readOnlyFlag)
        self.extendStartPointButton.setEnabled(not self.readOnlyFlag)
        self.extendEndPointSpinBox.setReadOnly(self.readOnlyFlag)
        self.extendEndPointButton.setEnabled(not self.readOnlyFlag)
        
        self.tiltedTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        self.angleTextFlagCheckBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartLineSegmentArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartLineSegmentArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())

        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceLocationValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        self.endPointPriceLocationValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        if self.artifact.getTiltedTextFlag() == True:
            self.tiltedTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.tiltedTextFlagCheckBox.setCheckState(Qt.Unchecked)

        if self.artifact.getAngleTextFlag() == True:
            self.angleTextFlagCheckBox.setCheckState(Qt.Checked)
        else:
            self.angleTextFlagCheckBox.setCheckState(Qt.Unchecked)

        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartLineSegmentArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        # Position and start point should be the same values.

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        tiltedTextFlag = \
            (self.tiltedTextFlagCheckBox.checkState() == Qt.Checked)
        angleTextFlag = \
            (self.angleTextFlagCheckBox.checkState() == Qt.Checked)
        
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)
        self.artifact.setTiltedTextFlag(tiltedTextFlag)
        self.artifact.setAngleTextFlag(angleTextFlag)

        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))

    def _handleExtendStartPointButtonClicked(self):
        """Called when the 'Extend' button is clicked for the start
        point.  This will modify the start point so that it is a
        multiple of the distance between the start and end points.
        That multiple is indicated by the value in the
        self.extendStartPointSpinBox.
        """

        # First get the start and end points' X and Y values.
        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        # Get the X and Y deltas between the start and end points.
        deltaX = endPointX - startPointX
        deltaY = endPointY - startPointY

        # Calculate the new offsets from the end point.
        extendMultiple = self.extendStartPointSpinBox.value()
        offsetX = deltaX * extendMultiple
        offsetY = deltaY * extendMultiple

        # Calculate new start point X and Y values.
        newStartPointX = endPointX - offsetX
        newStartPointY = endPointY - offsetY

        # Convert the new X and Y values to datetime and price.
        newStartPointDatetime = \
            self.convertObj.sceneXPosToDatetime(newStartPointX)
        newStartPointPrice = \
            self.convertObj.sceneYPosToPrice(newStartPointY)

        # Set the edit widgets with these new values.
        self.startPointPriceLocationValueSpinBox.\
            setValue(newStartPointPrice)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(newStartPointDatetime)

    def _handleExtendEndPointButtonClicked(self):
        """Called when the 'Extend' button is clicked for the end
        point.  This will modify the end point so that it is a
        multiple of the distance between the start and end points.
        That multiple is indicated by the value in the
        self.extendEndPointSpinBox.
        """

        # First get the start and end points' X and Y values.
        startPointPrice = self.startPointPriceLocationValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)

        endPointPrice = self.endPointPriceLocationValueSpinBox.value()
        endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()

        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        # Get the X and Y deltas between the start and end points.
        deltaX = endPointX - startPointX
        deltaY = endPointY - startPointY

        # Calculate the new offsets from the end point.
        extendMultiple = self.extendEndPointSpinBox.value()
        offsetX = deltaX * extendMultiple
        offsetY = deltaY * extendMultiple

        # Calculate new start point X and Y values.
        newEndPointX = startPointX + offsetX
        newEndPointY = startPointY + offsetY

        # Convert the new X and Y values to datetime and price.
        newEndPointDatetime = \
            self.convertObj.sceneXPosToDatetime(newEndPointX)
        newEndPointPrice = \
            self.convertObj.sceneYPosToPrice(newEndPointY)

        # Set the edit widgets with these new values.
        self.endPointPriceLocationValueSpinBox.\
            setValue(newEndPointPrice)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(newEndPointDatetime)

    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartLineSegmentArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartLineSegmentArtifact.
    """

    def __init__(self,
                 priceBarChartLineSegmentArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartLineSegmentArtifact.
        
        Note: The 'priceBarChartLineSegmentArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartLineSegmentArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
        "pricebarchart_dialogs.PriceBarChartLineSegmentArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartLineSegmentArtifact Data")

        # Check input.
        if not isinstance(priceBarChartLineSegmentArtifact,
                          PriceBarChartLineSegmentArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartLineSegmentArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartLineSegmentArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartLineSegmentArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartLineSegmentArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartOctaveFanArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartOctaveFanArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartOctaveFanArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartOctaveFanArtifact object.

        Arguments:
        artifact - PriceBarChartOctaveFanArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartOctaveFanArtifactEditWidget")

        # This variable holds a copy of the artifact passed in.  We
        # set this value via self.loadValues(), which is called later
        # in this funtion on parameter 'artifact'.
        self.artifact = None

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.textFontSizeValueSpinBox.valueChanged.\
            connect(self._handleTextFontSizeValueSpinBoxChanged)
        self.textEnabledCheckBox.stateChanged.\
            connect(self._handleTextEnabledCheckBoxToggled)
        
        # Connect rotateUp and rotateDown buttons.
        self.rotateUpButton.clicked.\
            connect(self._handleRotateUpButtonClicked)
        self.rotateDownButton.clicked.\
            connect(self._handleRotateDownButtonClicked)
        self.reverseButton.clicked.\
            connect(self._handleReverseButtonClicked)
        self.checkMarkAllButton.clicked.\
            connect(self._handleCheckMarkAllButtonClicked)
        self.checkMarkNoneButton.clicked.\
            connect(self._handleCheckMarkNoneButtonClicked)

        # Connect the signals for the price and time values changing,
        # so that we can update the origin, leg1, and leg2 points in
        # the artifact and update all the prices and datetimes in
        # between.
        self.originPointPriceValueSpinBox.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.leg1PointPriceValueSpinBox.valueChanged.\
            connect(self. _saveAndReloadMusicalRatios)
        self.leg2PointPriceValueSpinBox.valueChanged.\
            connect(self. _saveAndReloadMusicalRatios)
        self.originPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.leg1PointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.leg2PointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartOctaveFanArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.colorLabel = QLabel("Bar color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.textFontSizeValueLabel = \
            QLabel("Text font size:")
        self.textFontSizeValueSpinBox = QDoubleSpinBox()
        self.textFontSizeValueSpinBox.setMinimum(0.0)
        self.textFontSizeValueSpinBox.setMaximum(999999999.0)

        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        self.originPointPriceValueLabel = \
            QLabel("OctaveFan Origin Point (in price):")
        self.originPointPriceValueSpinBox = QDoubleSpinBox()
        self.originPointPriceValueSpinBox.setDecimals(4)
        self.originPointPriceValueSpinBox.setMinimum(0.0)
        self.originPointPriceValueSpinBox.setMaximum(999999999.0)
        originPointPriceValueLayout = QHBoxLayout()
        originPointPriceValueLayout.addWidget(self.originPointPriceValueLabel)
        originPointPriceValueLayout.addStretch()
        originPointPriceValueLayout.addWidget(self.originPointPriceValueSpinBox)
        
        self.originPointDatetimeLocationWidget = TimestampEditWidget()
        self.originPointDatetimeLocationWidget.groupBox.\
            setTitle("OctaveFan Origin Point (in time)")
        self.originPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.originPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.leg1PointPriceValueLabel = \
            QLabel("OctaveFan Leg1 Point (in price):")
        self.leg1PointPriceValueSpinBox = QDoubleSpinBox()
        self.leg1PointPriceValueSpinBox.setDecimals(4)
        self.leg1PointPriceValueSpinBox.setMinimum(0.0)
        self.leg1PointPriceValueSpinBox.setMaximum(999999999.0)
        leg1PointPriceValueLayout = QHBoxLayout()
        leg1PointPriceValueLayout.addWidget(self.leg1PointPriceValueLabel)
        leg1PointPriceValueLayout.addStretch()
        leg1PointPriceValueLayout.addWidget(self.leg1PointPriceValueSpinBox)
        
        self.leg1PointDatetimeLocationWidget = TimestampEditWidget()
        self.leg1PointDatetimeLocationWidget.groupBox.\
            setTitle("OctaveFan Leg1 Point (in time)")
        self.leg1PointDatetimeLocationWidget.okayButton.setVisible(False)
        self.leg1PointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.leg2PointPriceValueLabel = \
            QLabel("OctaveFan Leg2 Point (in price):")
        self.leg2PointPriceValueSpinBox = QDoubleSpinBox()
        self.leg2PointPriceValueSpinBox.setDecimals(4)
        self.leg2PointPriceValueSpinBox.setMinimum(0.0)
        self.leg2PointPriceValueSpinBox.setMaximum(999999999.0)
        leg2PointPriceValueLayout = QHBoxLayout()
        leg2PointPriceValueLayout.addWidget(self.leg2PointPriceValueLabel)
        leg2PointPriceValueLayout.addStretch()
        leg2PointPriceValueLayout.addWidget(self.leg2PointPriceValueSpinBox)
        
        self.leg2PointDatetimeLocationWidget = TimestampEditWidget()
        self.leg2PointDatetimeLocationWidget.groupBox.\
            setTitle("OctaveFan Leg2 Point (in time)")
        self.leg2PointDatetimeLocationWidget.okayButton.setVisible(False)
        self.leg2PointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textFontSizeValueLabel, r, 0, al)
        gridLayout.addWidget(self.textFontSizeValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(originPointPriceValueLayout, r, 0, al)
        gridLayout.addLayout(leg1PointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.originPointDatetimeLocationWidget,
                                  r, 0, al)
        gridLayout.addWidget(self.leg1PointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1
        gridLayout.addLayout(leg2PointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.leg2PointDatetimeLocationWidget,
                                  r, 1, al)
        
        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1
    
    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartOctaveFanArtifact Data (page 2):")
        
        self.rotateDownButton = QPushButton("Rotate Down")
        self.rotateUpButton = QPushButton("Rotate Up")
        self.reverseButton = QPushButton("Reverse")
        self.checkMarkAllButton = QPushButton("Check All")
        self.checkMarkNoneButton = QPushButton("Check None")
        
        rotateButtonsLayout = QHBoxLayout()
        rotateButtonsLayout.addWidget(self.rotateDownButton)
        rotateButtonsLayout.addWidget(self.rotateUpButton)
        rotateButtonsLayout.addWidget(self.reverseButton)
        rotateButtonsLayout.addWidget(self.checkMarkAllButton)
        rotateButtonsLayout.addWidget(self.checkMarkNoneButton)
        rotateButtonsLayout.addStretch()
        
        # Layout for the musical ratio intervals.
        self.musicalRatiosGridLayout = QGridLayout()
        self.numMusicalRatios = 0

        # Holds the list of QCheckBox objects corresponding to the
        # MusicalRatios (ordered) in the artifact. 
        self.checkBoxes = []
        
        layout = QVBoxLayout()
        layout.addLayout(rotateButtonsLayout)
        layout.addLayout(self.musicalRatiosGridLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2
        
    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.textFontSizeValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        self.rotateDownButton.setEnabled(not self.readOnlyFlag)
        self.rotateUpButton.setEnabled(not self.readOnlyFlag)
        self.reverseButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkAllButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkNoneButton.setEnabled(not self.readOnlyFlag)
        self.originPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.originPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.leg1PointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.leg1PointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.leg2PointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.leg2PointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.checkBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartOctaveFanArtifact.

        Arguments:
        
        artifact - PriceBarChartOctaveFanArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        elif self.artifact is artifact:
            # They are the same, so no need to do a deep copy.
            # Just continue on, creating and loading the widgets.
            self.log.debug("Same artifact, no need for deep copy.")
        else:
            # Store a deep copy of the artifact because we manipulate
            # the musicalRatios list and its ordering.
            self.log.debug("Deep copying artifact...")
            self.artifact = copy.deepcopy(artifact)

        self.log.debug("Setting the widgets...")
        
        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        self.colorEditButton.setColor(self.artifact.getColor())
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        self.textFontSizeValueSpinBox.setValue(self.artifact.getFontSize())
                                        
        if self.artifact.isTextEnabled():
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        originPointY = self.artifact.originPointF.y()
        originPointPrice = self.convertObj.sceneYPosToPrice(originPointY)
        self.originPointPriceValueSpinBox.setValue(originPointPrice)
        
        originPointX = self.artifact.originPointF.x()
        originPointDatetime = self.convertObj.sceneXPosToDatetime(originPointX)
        self.originPointDatetimeLocationWidget.\
            loadTimestamp(originPointDatetime)
        
        leg1PointY = self.artifact.leg1PointF.y()
        leg1PointPrice = self.convertObj.sceneYPosToPrice(leg1PointY)
        self.leg1PointPriceValueSpinBox.setValue(leg1PointPrice)
        
        leg1PointX = self.artifact.leg1PointF.x()
        leg1PointDatetime = self.convertObj.sceneXPosToDatetime(leg1PointX)
        self.leg1PointDatetimeLocationWidget.\
            loadTimestamp(leg1PointDatetime)

        leg2PointY = self.artifact.leg2PointF.y()
        leg2PointPrice = self.convertObj.sceneYPosToPrice(leg2PointY)
        self.leg2PointPriceValueSpinBox.setValue(leg2PointPrice)
        
        leg2PointX = self.artifact.leg2PointF.x()
        leg2PointDatetime = self.convertObj.sceneXPosToDatetime(leg2PointX)
        self.leg2PointDatetimeLocationWidget.\
            loadTimestamp(leg2PointDatetime)

        self._reloadMusicalRatiosGrid()
        
        self.log.debug("Exiting loadValues()")

    def _reloadMusicalRatiosGrid(self):
        """Clears and recreates the self.musicalRatiosGridLayout
        according to teh values in self.artifact.
        """
        
        # Remove any old widgets that were in the grid layout from
        # the grid layout..
        for r in range(self.musicalRatiosGridLayout.rowCount()):
            for c in range(self.musicalRatiosGridLayout.columnCount()):
                # Get the QLayoutItem.
                item = self.musicalRatiosGridLayout.itemAtPosition(r, c)
                if item != None:
                    # Get the widget in the layout item.
                    widget = item.widget()
                    if widget != None:
                        widget.setEnabled(False)
                        widget.setVisible(False)
                        widget.setParent(None)

                        # Actually remove the widget from the
                        # QGridLayout.  
                        self.musicalRatiosGridLayout.removeWidget(widget)
                                
        # Row.
        r = 0
        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        # Create the musical ratio items in the
        # self.musicalRatiosGridLayout QGridLayout.
        musicalRatios = self.artifact.getMusicalRatios()
        self.numMusicalRatios = len(musicalRatios)

        # Clear the checkboxes list.
        self.checkBoxes = []

        rangeUsed = None
        if self.artifact.isReversed() == False:
            rangeUsed = range(self.numMusicalRatios)
        else:
            rangeUsed = reversed(range(self.numMusicalRatios))
            
        for i in rangeUsed:
            musicalRatio = musicalRatios[i]

            checkBox = QCheckBox("{}".format(musicalRatio.getRatio()))

            # Set the check state based on whether or not the musical
            # ratio is enabled.
            if musicalRatio.isEnabled():
                checkBox.setCheckState(Qt.Checked)
            else:
                checkBox.setCheckState(Qt.Unchecked)

            # Connect the signal to the slot function
            # _handleCheckMarkToggled().  That function will update
            # the self.artifact's musicalRatios with new check state.
            checkBox.stateChanged.connect(self._handleCheckMarkToggled)
            
            # Append to our list of checkboxes so that we can
            # reference them later and see what values are used in
            # them.  Remember, if we are reversed, then we will need
            # to reverse this list later.
            self.checkBoxes.append(checkBox)
            
            descriptionLabel = QLabel(musicalRatio.getDescription())


            # Get the unscaled originPointF, leg1PointF, and leg2PointF.
            unscaledOriginPointF = self.artifact.getOriginPointF()
            unscaledLeg1PointF = self.artifact.getLeg1PointF()
            unscaledLeg2PointF = self.artifact.getLeg2PointF()

            self.log.debug("unscaledOriginPointF is: ({}, {})".
                           format(unscaledOriginPointF.x(),
                                  unscaledOriginPointF.y()))
            self.log.debug("unscaledLeg1PointF is: ({}, {})".
                           format(unscaledLeg1PointF.x(),
                                  unscaledLeg1PointF.y()))
            self.log.debug("unscaledLeg2PointF is: ({}, {})".
                           format(unscaledLeg2PointF.x(),
                                  unscaledLeg2PointF.y()))

            # Calculate scaled originPointF, leg1PointF and
            # leg2PointF points.
            scaledOriginPointF = \
                self.convertObj.convertScenePointToScaledPoint(\
                self.artifact.getOriginPointF())
            scaledLeg1PointF = \
                self.convertObj.convertScenePointToScaledPoint(\
                self.artifact.getLeg1PointF())
            scaledLeg2PointF = \
                self.convertObj.convertScenePointToScaledPoint(\
                self.artifact.getLeg2PointF())
        
            self.log.debug("scaledOriginPointF is: ({}, {})".
                           format(scaledOriginPointF.x(),
                                  scaledOriginPointF.y()))
            self.log.debug("scaledLeg1PointF is: ({}, {})".
                           format(scaledLeg1PointF.x(),
                          scaledLeg1PointF.y()))
            self.log.debug("scaledLeg2PointF is: ({}, {})".
                           format(scaledLeg2PointF.x(),
                                  scaledLeg2PointF.y()))

            # Get the x and y position that will be the endpoint of
            # the fan line.  This function returns
            # the x and y in scaled coordinates so we must
            # remember to convert those values afterwards.
            (x, y) = \
                self.artifact.getXYForMusicalRatio(i,
                                                   scaledOriginPointF,
                                                   scaledLeg1PointF,
                                                   scaledLeg2PointF)

            # Map those x and y to scene coordinates.
            scenePointF = \
                self.convertObj.convertScaledPointToScenePoint(\
                QPointF(x, y))
            
            # Use QLabels to display the price and timestamp
            # information.
            price = self.convertObj.sceneYPosToPrice(scenePointF.y())
            priceStr = "{}".format(price)
            priceWidget = QLabel(priceStr)

            timestamp = self.convertObj.sceneXPosToDatetime(scenePointF.x())
            timestampStr = Ephemeris.datetimeToDayStr(timestamp)
            timestampWidget = QLabel(timestampStr)

            # Actually add the widgets to the grid layout.
            self.musicalRatiosGridLayout.addWidget(checkBox, r, 0, al)
            self.musicalRatiosGridLayout.addWidget(descriptionLabel, r, 1, al)
            self.musicalRatiosGridLayout.addWidget(priceWidget, r, 2, al)
            self.musicalRatiosGridLayout.addWidget(timestampWidget, r, 3, al)

            r += 1

        # Reverse the self.checkBoxes list if we are reversed, since
        # if that is the case, then previously in this function we
        # added the checkBoxes in the reverse order.
        if self.artifact.isReversed():
            self.checkBoxes.reverse()
            
    def saveValues(self):
        """Saves the values in the widgets to the internally stored
        PriceBarChartOctaveFanArtifact object.
        """

        self.log.debug("Entered saveValues()")

        # Get the colors.
        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        # Call save on the timestamp widgets.
        self.originPointDatetimeLocationWidget.saveTimestamp()
        self.leg1PointDatetimeLocationWidget.saveTimestamp()
        self.leg2PointDatetimeLocationWidget.saveTimestamp()
        
        # Position and origin point should be the same values.
        originPointPrice = \
            self.originPointPriceValueSpinBox.value()
        originPointY = self.convertObj.priceToSceneYPos(originPointPrice)
        leg1PointPrice = \
            self.leg1PointPriceValueSpinBox.value()
        leg1PointY = self.convertObj.priceToSceneYPos(leg1PointPrice)
        leg1PointY = originPointY
        leg2PointPrice = \
            self.leg2PointPriceValueSpinBox.value()
        leg2PointY = self.convertObj.priceToSceneYPos(leg2PointPrice)
        leg2PointY = originPointY

        originPointDatetime = \
            self.originPointDatetimeLocationWidget.getTimestamp()
        leg1PointDatetime = \
            self.leg1PointDatetimeLocationWidget.getTimestamp()
        leg2PointDatetime = \
            self.leg2PointDatetimeLocationWidget.getTimestamp()
                          
        originPointX = self.convertObj.datetimeToSceneXPos(originPointDatetime)
        leg1PointX = self.convertObj.datetimeToSceneXPos(leg1PointDatetime)
        leg2PointX = self.convertObj.datetimeToSceneXPos(leg2PointDatetime)

        posF = QPointF(originPointX, originPointY)
        originPointF = QPointF(originPointX, originPointY)
        leg1PointF = QPointF(leg1PointX, leg1PointY)
        leg2PointF = QPointF(leg2PointX, leg2PointY)

        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setOriginPointF(originPointF)
        self.artifact.setLeg1PointF(leg1PointF)
        self.artifact.setLeg2PointF(leg2PointF)

        # No need to save the musicalRatios inside self.artifact,
        # because each time there is a rotation or a check-marking
        # action, the internal artifact was updated.
        # The same is the case for the self.artifact.setReversed().

        self.log.debug("Exiting saveValues()")

    def _handleTextFontSizeValueSpinBoxChanged(self):
        """Called when the self.textFontSizeValueSpinBox is modified."""

        self.artifact.setFontSize(self.textFontSizeValueSpinBox.value())
        
    def _handleTextEnabledCheckBoxToggled(self):
        """Called when the textEnabledCheckBox is checked or unchecked."""

        newValue = None
        
        if self.textEnabledCheckBox.checkState() == Qt.Checked:
            newValue = True
        else:
            newValue = False
        
        self.artifact.setTextEnabled(newValue)
        
    def _handleCheckMarkToggled(self):
        """Called when one of the check-mark boxes on the
        musicalRatios is checked or unchecked.
        """

        # Go through all the musicalRatios in the widget, and set them
        # as enabled or disabled in the artifact, based on the check
        # state of the QCheckBox objects in self.checkBoxes.
        for i in range(len(self.checkBoxes)):
            oldValue = self.artifact.getMusicalRatios()[i].isEnabled()
            newValue = None
            if self.checkBoxes[i].checkState() == Qt.Checked:
                newValue = True
            else:
                newValue = False

            if oldValue != newValue:
                self.log.debug("Updating enabled state of " +
                               "musicalRatio[{}] from {} to {}".\
                               format(i, oldValue, newValue))
                self.artifact.getMusicalRatios()[i].setEnabled(newValue)
            else:
                #self.log.debug("No update to musicalRatio[{}]".format(i))
                pass

    def _saveAndReloadMusicalRatios(self):
        """Saves and reloads the musical ratio widgets."""
        
        # Save values from what is in the widgets to the internal artifact.
        self.saveValues()
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateDownButtonClicked(self):
        """Called when the 'Rotate Down' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()

        if self.artifact.isReversed() == False:
            # Put the last musical ratio in the front.
            if len(musicalRatios) > 0:
                lastRatio = musicalRatios.pop(len(musicalRatios) - 1)
                musicalRatios.insert(0, lastRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
            
        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateUpButtonClicked(self):
        """Called when the 'Rotate Up' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()
        
        if self.artifact.isReversed() == False:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)

        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleReverseButtonClicked(self):
        """Called when the 'Reverse' button is clicked."""

        # Flip the flag that indicates that the musical ratios are reversed.
        self.artifact.setReversed(not self.artifact.isReversed())
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleCheckMarkAllButtonClicked(self):
        """Called when the 'Check All' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Checked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleCheckMarkNoneButtonClicked(self):
        """Called when the 'Check None' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Unchecked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartOctaveFanArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartOctaveFanArtifact.
    """

    def __init__(self,
                 priceBarChartOctaveFanArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartOctaveFanArtifact.
        
        Note: The 'priceBarChartOctaveFanArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartOctaveFanArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartOctaveFanArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartOctaveFanArtifact Data")

        # Check input.
        if not isinstance(priceBarChartOctaveFanArtifact,
                          PriceBarChartOctaveFanArtifact):
            self.log.error("Input type invalid to " + \
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartOctaveFanArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartOctaveFanArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartOctaveFanArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartOctaveFanArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the artifact object.  If the 'Okay'
        button was previously clicked, then this object contains new
        values as set with the widget, otherwise it is unchanged.
        """

        # The edit widget keeps its own copy of the artifact, which it
        # modifies directly.
        if self.result() == QDialog.Accepted:
            return self.editWidget.getArtifact()
        else:
            return self.artifact


class PriceBarChartFibFanArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartFibFanArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartFibFanArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartFibFanArtifact object.

        Arguments:
        artifact - PriceBarChartFibFanArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger(\
            "pricebarchart_dialogs.PriceBarChartFibFanArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.fontEditButton.clicked.\
            connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartFibFanArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        self.originPointPriceValueLabel = \
            QLabel("FibFan Origin Point (in price):")
        self.originPointPriceValueSpinBox = QDoubleSpinBox()
        self.originPointPriceValueSpinBox.setDecimals(4)
        self.originPointPriceValueSpinBox.setMinimum(0.0)
        self.originPointPriceValueSpinBox.setMaximum(999999999.0)
        originPointPriceValueLayout = QHBoxLayout()
        originPointPriceValueLayout.addWidget(self.originPointPriceValueLabel)
        originPointPriceValueLayout.addStretch()
        originPointPriceValueLayout.addWidget(self.originPointPriceValueSpinBox)
        
        self.originPointDatetimeLocationWidget = TimestampEditWidget()
        self.originPointDatetimeLocationWidget.groupBox.\
            setTitle("FibFan Origin Point (in time)")
        self.originPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.originPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.leg1PointPriceValueLabel = \
            QLabel("FibFan Leg1 Point (in price):")
        self.leg1PointPriceValueSpinBox = QDoubleSpinBox()
        self.leg1PointPriceValueSpinBox.setDecimals(4)
        self.leg1PointPriceValueSpinBox.setMinimum(0.0)
        self.leg1PointPriceValueSpinBox.setMaximum(999999999.0)
        leg1PointPriceValueLayout = QHBoxLayout()
        leg1PointPriceValueLayout.addWidget(self.leg1PointPriceValueLabel)
        leg1PointPriceValueLayout.addStretch()
        leg1PointPriceValueLayout.addWidget(self.leg1PointPriceValueSpinBox)
        
        self.leg1PointDatetimeLocationWidget = TimestampEditWidget()
        self.leg1PointDatetimeLocationWidget.groupBox.\
            setTitle("FibFan Leg1 Point (in time)")
        self.leg1PointDatetimeLocationWidget.okayButton.setVisible(False)
        self.leg1PointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.leg2PointPriceValueLabel = \
            QLabel("FibFan Leg2 Point (in price):")
        self.leg2PointPriceValueSpinBox = QDoubleSpinBox()
        self.leg2PointPriceValueSpinBox.setDecimals(4)
        self.leg2PointPriceValueSpinBox.setMinimum(0.0)
        self.leg2PointPriceValueSpinBox.setMaximum(999999999.0)
        leg2PointPriceValueLayout = QHBoxLayout()
        leg2PointPriceValueLayout.addWidget(self.leg2PointPriceValueLabel)
        leg2PointPriceValueLayout.addStretch()
        leg2PointPriceValueLayout.addWidget(self.leg2PointPriceValueSpinBox)
        
        self.leg2PointDatetimeLocationWidget = TimestampEditWidget()
        self.leg2PointDatetimeLocationWidget.groupBox.\
            setTitle("FibFan Leg2 Point (in time)")
        self.leg2PointDatetimeLocationWidget.okayButton.setVisible(False)
        self.leg2PointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.fontLabel, r, 0, al)
        gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(originPointPriceValueLayout, r, 0, al)
        gridLayout.addLayout(leg1PointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.originPointDatetimeLocationWidget,
                                  r, 0, al)
        gridLayout.addWidget(self.leg1PointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1
        #gridLayout.addWidget(self.,
        #                          r, 0, al)
        gridLayout.addLayout(leg2PointPriceValueLayout,
                                  r, 1, al)
        r += 1
        #gridLayout.addWidget(self.,
        #                          r, 0, al)
        gridLayout.addWidget(self.leg2PointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1


        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1

    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartFibFanArtifact Data (page 2):")

        
        self.ratioCheckBoxes = []
        for ratio in self.artifact.getRatios():
            checkBox = \
                QCheckBox("Ratio " + ratio.getDescription() + " enabled")
            self.ratioCheckBoxes.append(checkBox)
        
        # Layout just for the checkboxes (enabled ratios, etc.).
        checkBoxesLayout = QVBoxLayout()
        for checkBox in self.ratioCheckBoxes:
            checkBoxesLayout.addWidget(checkBox)
        tempLayout = checkBoxesLayout
        
        checkBoxesLayout = QHBoxLayout()
        checkBoxesLayout.addLayout(tempLayout)
        checkBoxesLayout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(checkBoxesLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        
        self.originPointPriceValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.leg1PointPriceValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.leg2PointPriceValueSpinBox.\
            setEnabled(not self.readOnlyFlag)

        self.originPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.leg1PointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.leg2PointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.ratioCheckBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
            
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartFibFanArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartFibFanArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())

        if self.artifact.isTextEnabled() == True:
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        originPointY = self.artifact.originPointF.y()
        originPointPrice = self.convertObj.sceneYPosToPrice(originPointY)
        self.originPointPriceValueSpinBox.setValue(originPointPrice)
        
        originPointX = self.artifact.originPointF.x()
        originPointDatetime = self.convertObj.sceneXPosToDatetime(originPointX)
        self.originPointDatetimeLocationWidget.\
            loadTimestamp(originPointDatetime)
        

        leg1PointY = self.artifact.leg1PointF.y()
        leg1PointPrice = self.convertObj.sceneYPosToPrice(leg1PointY)
        self.leg1PointPriceValueSpinBox.setValue(leg1PointPrice)
        
        leg1PointX = self.artifact.leg1PointF.x()
        leg1PointDatetime = self.convertObj.sceneXPosToDatetime(leg1PointX)
        self.leg1PointDatetimeLocationWidget.\
            loadTimestamp(leg1PointDatetime)

        
        leg2PointY = self.artifact.leg2PointF.y()
        leg2PointPrice = self.convertObj.sceneYPosToPrice(leg2PointY)
        self.leg2PointPriceValueSpinBox.setValue(leg2PointPrice)
        
        leg2PointX = self.artifact.leg2PointF.x()
        leg2PointDatetime = self.convertObj.sceneXPosToDatetime(leg2PointX)
        self.leg2PointDatetimeLocationWidget.\
            loadTimestamp(leg2PointDatetime)
        

        ratios = self.artifact.getRatios()
        for i in range(len(ratios)):
            ratio = ratios[i]
            
            if ratio.isEnabled() == True:
                self.ratioCheckBoxes[i].setCheckState(Qt.Checked)
            else:
                self.ratioCheckBoxes[i].setCheckState(Qt.Unchecked)
            
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartFibFanArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.originPointDatetimeLocationWidget.saveTimestamp()
        self.leg1PointDatetimeLocationWidget.saveTimestamp()
        self.leg2PointDatetimeLocationWidget.saveTimestamp()
        
        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        originPointPrice = self.originPointPriceValueSpinBox.value()
        originPointY = self.convertObj.priceToSceneYPos(originPointPrice)

        leg1PointPrice = self.leg1PointPriceValueSpinBox.value()
        leg1PointY = self.convertObj.priceToSceneYPos(leg1PointPrice)

        leg2PointPrice = self.leg2PointPriceValueSpinBox.value()
        leg2PointY = self.convertObj.priceToSceneYPos(leg2PointPrice)

        
        originPointDatetime = \
            self.originPointDatetimeLocationWidget.getTimestamp()
        leg1PointDatetime = \
            self.leg1PointDatetimeLocationWidget.getTimestamp()
        leg2PointDatetime = \
            self.leg2PointDatetimeLocationWidget.getTimestamp()

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        originPointX = self.convertObj.datetimeToSceneXPos(originPointDatetime)
        leg1PointX = self.convertObj.datetimeToSceneXPos(leg1PointDatetime)
        leg2PointX = self.convertObj.datetimeToSceneXPos(leg2PointDatetime)
        
        # Position and start point should be the same values.
        
        posF = QPointF(originPointX, originPointY)
        originPointF = QPointF(originPointX, originPointY)
        leg1PointF = QPointF(leg1PointX, leg1PointY)
        leg2PointF = QPointF(leg2PointX, leg2PointY)
        
        textEnabledFlag = \
            (self.textEnabledCheckBox.checkState() == Qt.Checked)
        
        ratioEnabledFlags = []
        for checkBox in self.ratioCheckBoxes:
            if checkBox.checkState() == Qt.Checked:
                ratioEnabledFlags.append(True)
            else:
                ratioEnabledFlags.append(False)
                
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setOriginPointF(originPointF)
        self.artifact.setLeg1PointF(leg1PointF)
        self.artifact.setLeg2PointF(leg2PointF)
        self.artifact.setTextEnabled(textEnabledFlag)

        ratios = self.artifact.getRatios()
        for i in range(len(ratioEnabledFlags)):
            flag = ratioEnabledFlags[i]
            ratios[i].setEnabled(flag)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartFibFanArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartFibFanArtifact.
    """

    def __init__(self,
                 priceBarChartFibFanArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartFibFanArtifact.
        
        Note: The 'priceBarChartFibFanArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartFibFanArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
        "pricebarchart_dialogs.PriceBarChartFibFanArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartFibFanArtifact Data")

        # Check input.
        if not isinstance(priceBarChartFibFanArtifact,
                          PriceBarChartFibFanArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartFibFanArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartFibFanArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartFibFanArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartFibFanArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact


class PriceBarChartGannFanArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartGannFanArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartGannFanArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """
    
    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartGannFanArtifact object.

        Arguments:
        artifact - PriceBarChartGannFanArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.\
            getLogger(\
            "pricebarchart_dialogs.PriceBarChartGannFanArtifactEditWidget")

        # Save off the artifact object.
        self.artifact = artifact

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.fontEditButton.clicked.\
            connect(self._handleFontEditButtonClicked)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartGannFanArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.xScalingLabel = QLabel("Text X Scaling:")
        self.xScalingDoubleSpinBox = QDoubleSpinBox()
        self.xScalingDoubleSpinBox.setMinimum(0.0)
        self.xScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.yScalingLabel = QLabel("Text Y Scaling:")
        self.yScalingDoubleSpinBox = QDoubleSpinBox()
        self.yScalingDoubleSpinBox.setMinimum(0.0)
        self.yScalingDoubleSpinBox.setMaximum(999999999.0)
        
        self.font = QFont()
        self.fontLabel = QLabel("Font:")
        self.fontValueLabel = QLabel(self.font.toString())
        self.fontEditButton = QPushButton("Modify")

        self.colorLabel = QLabel("Color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        self.originPointPriceValueLabel = \
            QLabel("GannFan Origin Point (in price):")
        self.originPointPriceValueSpinBox = QDoubleSpinBox()
        self.originPointPriceValueSpinBox.setDecimals(4)
        self.originPointPriceValueSpinBox.setMinimum(0.0)
        self.originPointPriceValueSpinBox.setMaximum(999999999.0)
        originPointPriceValueLayout = QHBoxLayout()
        originPointPriceValueLayout.addWidget(self.originPointPriceValueLabel)
        originPointPriceValueLayout.addStretch()
        originPointPriceValueLayout.addWidget(self.originPointPriceValueSpinBox)
        
        self.originPointDatetimeLocationWidget = TimestampEditWidget()
        self.originPointDatetimeLocationWidget.groupBox.\
            setTitle("GannFan Origin Point (in time)")
        self.originPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.originPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.leg1PointPriceValueLabel = \
            QLabel("GannFan Leg1 Point (in price):")
        self.leg1PointPriceValueSpinBox = QDoubleSpinBox()
        self.leg1PointPriceValueSpinBox.setDecimals(4)
        self.leg1PointPriceValueSpinBox.setMinimum(0.0)
        self.leg1PointPriceValueSpinBox.setMaximum(999999999.0)
        leg1PointPriceValueLayout = QHBoxLayout()
        leg1PointPriceValueLayout.addWidget(self.leg1PointPriceValueLabel)
        leg1PointPriceValueLayout.addStretch()
        leg1PointPriceValueLayout.addWidget(self.leg1PointPriceValueSpinBox)
        
        self.leg1PointDatetimeLocationWidget = TimestampEditWidget()
        self.leg1PointDatetimeLocationWidget.groupBox.\
            setTitle("GannFan Leg1 Point (in time)")
        self.leg1PointDatetimeLocationWidget.okayButton.setVisible(False)
        self.leg1PointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        self.leg2PointPriceValueLabel = \
            QLabel("GannFan Leg2 Point (in price):")
        self.leg2PointPriceValueSpinBox = QDoubleSpinBox()
        self.leg2PointPriceValueSpinBox.setDecimals(4)
        self.leg2PointPriceValueSpinBox.setMinimum(0.0)
        self.leg2PointPriceValueSpinBox.setMaximum(999999999.0)
        leg2PointPriceValueLayout = QHBoxLayout()
        leg2PointPriceValueLayout.addWidget(self.leg2PointPriceValueLabel)
        leg2PointPriceValueLayout.addStretch()
        leg2PointPriceValueLayout.addWidget(self.leg2PointPriceValueSpinBox)
        
        self.leg2PointDatetimeLocationWidget = TimestampEditWidget()
        self.leg2PointDatetimeLocationWidget.groupBox.\
            setTitle("GannFan Leg2 Point (in time)")
        self.leg2PointDatetimeLocationWidget.okayButton.setVisible(False)
        self.leg2PointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        
        # Layout for just the font info.
        self.fontLayout = QHBoxLayout()
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontLayout.addStretch()
        self.fontLayout.addWidget(self.fontEditButton)

        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.xScalingLabel, r, 0, al)
        gridLayout.addWidget(self.xScalingDoubleSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.yScalingLabel, r, 0, al)
        gridLayout.addWidget(self.yScalingDoubleSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.fontLabel, r, 0, al)
        gridLayout.addLayout(self.fontLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(originPointPriceValueLayout, r, 0, al)
        gridLayout.addLayout(leg1PointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.originPointDatetimeLocationWidget,
                                  r, 0, al)
        gridLayout.addWidget(self.leg1PointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1
        #gridLayout.addWidget(self.,
        #                          r, 0, al)
        gridLayout.addLayout(leg2PointPriceValueLayout,
                                  r, 1, al)
        r += 1
        #gridLayout.addWidget(self.,
        #                          r, 0, al)
        gridLayout.addWidget(self.leg2PointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1


        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1

    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartGannFanArtifact Data (page 2):")

        
        self.ratioCheckBoxes = []
        for ratio in self.artifact.getRatios():
            checkBox = \
                QCheckBox("Ratio " + ratio.getDescription() + " enabled")
            self.ratioCheckBoxes.append(checkBox)
        
        # Layout just for the checkboxes (enabled ratios, etc.).
        checkBoxesLayout = QVBoxLayout()
        for checkBox in self.ratioCheckBoxes:
            checkBoxesLayout.addWidget(checkBox)
        tempLayout = checkBoxesLayout
        
        checkBoxesLayout = QHBoxLayout()
        checkBoxesLayout.addLayout(tempLayout)
        checkBoxesLayout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(checkBoxesLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.xScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.yScalingDoubleSpinBox.setEnabled(not self.readOnlyFlag)
        self.fontEditButton.setEnabled(not self.readOnlyFlag)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        
        self.originPointPriceValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.leg1PointPriceValueSpinBox.\
            setEnabled(not self.readOnlyFlag)
        self.leg2PointPriceValueSpinBox.\
            setEnabled(not self.readOnlyFlag)

        self.originPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.leg1PointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        self.leg2PointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.ratioCheckBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
            
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartGannFanArtifact.

        Note: Upon calling saveValues(), the edit widget overwrites
        the values in the object pointed to by 'artifact' with the
        values in the edit widgets.

        Arguments:
        
        artifact - PriceBarChartGannFanArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        else:
            self.artifact = artifact

        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        
        self.xScalingDoubleSpinBox.setValue(self.artifact.getTextXScaling())
        self.yScalingDoubleSpinBox.setValue(self.artifact.getTextYScaling())

        self.font = self.artifact.getFont()
        self.fontValueLabel.setText(\
            self._convertFontToNiceText(self.font))
        
        self.colorEditButton.setColor(self.artifact.getColor())
        
        self.textColorEditButton.setColor(self.artifact.getTextColor())

        if self.artifact.isTextEnabled() == True:
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        originPointY = self.artifact.originPointF.y()
        originPointPrice = self.convertObj.sceneYPosToPrice(originPointY)
        self.originPointPriceValueSpinBox.setValue(originPointPrice)
        
        originPointX = self.artifact.originPointF.x()
        originPointDatetime = self.convertObj.sceneXPosToDatetime(originPointX)
        self.originPointDatetimeLocationWidget.\
            loadTimestamp(originPointDatetime)
        

        leg1PointY = self.artifact.leg1PointF.y()
        leg1PointPrice = self.convertObj.sceneYPosToPrice(leg1PointY)
        self.leg1PointPriceValueSpinBox.setValue(leg1PointPrice)
        
        leg1PointX = self.artifact.leg1PointF.x()
        leg1PointDatetime = self.convertObj.sceneXPosToDatetime(leg1PointX)
        self.leg1PointDatetimeLocationWidget.\
            loadTimestamp(leg1PointDatetime)

        
        leg2PointY = self.artifact.leg2PointF.y()
        leg2PointPrice = self.convertObj.sceneYPosToPrice(leg2PointY)
        self.leg2PointPriceValueSpinBox.setValue(leg2PointPrice)
        
        leg2PointX = self.artifact.leg2PointF.x()
        leg2PointDatetime = self.convertObj.sceneXPosToDatetime(leg2PointX)
        self.leg2PointDatetimeLocationWidget.\
            loadTimestamp(leg2PointDatetime)
        

        ratios = self.artifact.getRatios()
        for i in range(len(ratios)):
            ratio = ratios[i]
            
            if ratio.isEnabled() == True:
                self.ratioCheckBoxes[i].setCheckState(Qt.Checked)
            else:
                self.ratioCheckBoxes[i].setCheckState(Qt.Unchecked)
            
        self.log.debug("Exiting loadValues()")
        
    def saveValues(self):
        """Saves the values in the widgets to the
        PriceBarChartGannFanArtifact object passed in this class's
        constructor or the loadValues() function.
        """
    
        self.log.debug("Entered saveValues()")

        # Call save on the timestamp widgets.
        self.originPointDatetimeLocationWidget.saveTimestamp()
        self.leg1PointDatetimeLocationWidget.saveTimestamp()
        self.leg2PointDatetimeLocationWidget.saveTimestamp()
        
        textXScaling = self.xScalingDoubleSpinBox.value()
        textYScaling = self.yScalingDoubleSpinBox.value()

        originPointPrice = self.originPointPriceValueSpinBox.value()
        originPointY = self.convertObj.priceToSceneYPos(originPointPrice)

        leg1PointPrice = self.leg1PointPriceValueSpinBox.value()
        leg1PointY = self.convertObj.priceToSceneYPos(leg1PointPrice)

        leg2PointPrice = self.leg2PointPriceValueSpinBox.value()
        leg2PointY = self.convertObj.priceToSceneYPos(leg2PointPrice)

        
        originPointDatetime = \
            self.originPointDatetimeLocationWidget.getTimestamp()
        leg1PointDatetime = \
            self.leg1PointDatetimeLocationWidget.getTimestamp()
        leg2PointDatetime = \
            self.leg2PointDatetimeLocationWidget.getTimestamp()

        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        originPointX = self.convertObj.datetimeToSceneXPos(originPointDatetime)
        leg1PointX = self.convertObj.datetimeToSceneXPos(leg1PointDatetime)
        leg2PointX = self.convertObj.datetimeToSceneXPos(leg2PointDatetime)
        
        # Position and start point should be the same values.
        
        posF = QPointF(originPointX, originPointY)
        originPointF = QPointF(originPointX, originPointY)
        leg1PointF = QPointF(leg1PointX, leg1PointY)
        leg2PointF = QPointF(leg2PointX, leg2PointY)
        
        textEnabledFlag = \
            (self.textEnabledCheckBox.checkState() == Qt.Checked)
        
        ratioEnabledFlags = []
        for checkBox in self.ratioCheckBoxes:
            if checkBox.checkState() == Qt.Checked:
                ratioEnabledFlags.append(True)
            else:
                ratioEnabledFlags.append(False)
                
        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setFont(self.font)
        self.artifact.setTextXScaling(textXScaling)
        self.artifact.setTextYScaling(textYScaling)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setOriginPointF(originPointF)
        self.artifact.setLeg1PointF(leg1PointF)
        self.artifact.setLeg2PointF(leg2PointF)
        self.artifact.setTextEnabled(textEnabledFlag)

        ratios = self.artifact.getRatios()
        for i in range(len(ratioEnabledFlags)):
            flag = ratioEnabledFlags[i]
            ratios[i].setEnabled(flag)
        
        self.log.debug("Exiting saveValues()")


    def _convertFontToNiceText(self, font):
        """Converts the given QFont to some nice str for decribing in a label.
        """

        rv = "Family: {}".format(font.family()) + os.linesep + \
             "Size: {}".format(font.pointSizeF())

        return rv

    def _handleFontEditButtonClicked(self):
        """Called when the self.fontEditButton is clicked."""

        dialog = QFontDialog(self.font)

        rv = dialog.exec_()

        if rv == QDialog.Accepted:
            # Store the font in the member variable (not in the artifact).
            self.font = dialog.selectedFont()
            self.fontValueLabel.setText(self._convertFontToNiceText(self.font))
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartGannFanArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartGannFanArtifact.
    """

    def __init__(self,
                 priceBarChartGannFanArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartGannFanArtifact.
        
        Note: The 'priceBarChartGannFanArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartGannFanArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
        "pricebarchart_dialogs.PriceBarChartGannFanArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartGannFanArtifact Data")

        # Check input.
        if not isinstance(priceBarChartGannFanArtifact,
                          PriceBarChartGannFanArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartGannFanArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartGannFanArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartGannFanArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartGannFanArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the internally stored artifact object.
        
        Note: If the 'Okay' button was previously clicked, then this
        object is modified with the widget's values, otherwise it is
        unchanged.
        """

        return self.artifact

class PriceBarChartVimsottariDasaArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartVimsottariDasaArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartVimsottariDasaArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartVimsottariDasaArtifact object.

        Arguments:
        artifact - PriceBarChartVimsottariDasaArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartVimsottariDasaArtifactEditWidget")

        # This variable holds a copy of the artifact passed in.  We
        # set this value via self.loadValues(), which is called later
        # in this funtion on parameter 'artifact'.
        self.artifact = None

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.barHeightValueSpinBox.valueChanged.\
            connect(self._handleBarHeightValueSpinBoxChanged)
        self.textFontSizeValueSpinBox.valueChanged.\
            connect(self._handleTextFontSizeValueSpinBoxChanged)
        self.textEnabledCheckBox.stateChanged.\
            connect(self._handleTextEnabledCheckBoxToggled)
        
        # Connect rotateUp and rotateDown buttons.
        self.rotateUpButton.clicked.\
            connect(self._handleRotateUpButtonClicked)
        self.rotateDownButton.clicked.\
            connect(self._handleRotateDownButtonClicked)
        self.reverseButton.clicked.\
            connect(self._handleReverseButtonClicked)
        self.checkMarkAllButton.clicked.\
            connect(self._handleCheckMarkAllButtonClicked)
        self.checkMarkNoneButton.clicked.\
            connect(self._handleCheckMarkNoneButtonClicked)

        # Connect the signals for the price and time values changing,
        # so that we can update the start and end points in the
        # artifact and update all the prices and datetimes in
        # between.
        self.startPointPriceValueSpinBox.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        #self.endPointPriceValueSpinBox.valueChanged.\
        #    connect(self. _saveAndReloadMusicalRatios)
        self.startPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.endPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartVimsottariDasaArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.colorLabel = QLabel("Bar color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.barHeightValueLabel = \
            QLabel("VimsottariDasa bar height:")
        self.barHeightValueSpinBox = QDoubleSpinBox()
        self.barHeightValueSpinBox.setMinimum(0.0)
        self.barHeightValueSpinBox.setMaximum(999999999.0)

        self.textFontSizeValueLabel = \
            QLabel("Text font size:")
        self.textFontSizeValueSpinBox = QDoubleSpinBox()
        self.textFontSizeValueSpinBox.setMinimum(0.0)
        self.textFontSizeValueSpinBox.setMaximum(999999999.0)

        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        self.startPointPriceValueLabel = \
            QLabel("VimsottariDasa Start Point (in price):")
        self.startPointPriceValueSpinBox = QDoubleSpinBox()
        self.startPointPriceValueSpinBox.setDecimals(4)
        self.startPointPriceValueSpinBox.setMinimum(0.0)
        self.startPointPriceValueSpinBox.setMaximum(999999999.0)
        startPointPriceValueLayout = QHBoxLayout()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueLabel)
        startPointPriceValueLayout.addStretch()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueSpinBox)
        
        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("VimsottariDasa Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        #self.endPointPriceValueLabel = \
        #    QLabel("VimsottariDasa End Point (in price):")
        #self.endPointPriceValueSpinBox = QDoubleSpinBox()
        #self.endPointPriceValueSpinBox.setDecimals(4)
        #self.endPointPriceValueSpinBox.setMinimum(0.0)
        #self.endPointPriceValueSpinBox.setMaximum(999999999.0)
        #endPointPriceValueLayout = QHBoxLayout()
        #endPointPriceValueLayout.addWidget(self.endPointPriceValueLabel)
        #endPointPriceValueLayout.addStretch()
        #endPointPriceValueLayout.addWidget(self.endPointPriceValueSpinBox)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("VimsottariDasa End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.barHeightValueLabel, r, 0, al)
        gridLayout.addWidget(self.barHeightValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textFontSizeValueLabel, r, 0, al)
        gridLayout.addWidget(self.textFontSizeValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(startPointPriceValueLayout, r, 0, al)
        #gridLayout.addLayout(endPointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        gridLayout.addWidget(self.endPointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1
    
    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartVimsottariDasaArtifact Data (page 2):")
        
        self.rotateDownButton = QPushButton("Rotate Down")
        self.rotateUpButton = QPushButton("Rotate Up")
        self.reverseButton = QPushButton("Reverse")
        self.checkMarkAllButton = QPushButton("Check All")
        self.checkMarkNoneButton = QPushButton("Check None")
        
        rotateButtonsLayout = QHBoxLayout()
        rotateButtonsLayout.addWidget(self.rotateDownButton)
        rotateButtonsLayout.addWidget(self.rotateUpButton)
        rotateButtonsLayout.addWidget(self.reverseButton)
        rotateButtonsLayout.addWidget(self.checkMarkAllButton)
        rotateButtonsLayout.addWidget(self.checkMarkNoneButton)
        rotateButtonsLayout.addStretch()
        
        # Layout for the musical ratio intervals.
        self.musicalRatiosGridLayout = QGridLayout()
        self.numMusicalRatios = 0

        # Holds the list of QCheckBox objects corresponding to the
        # MusicalRatios (ordered) in the artifact. 
        self.checkBoxes = []
        
        layout = QVBoxLayout()
        layout.addLayout(rotateButtonsLayout)
        layout.addLayout(self.musicalRatiosGridLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2
        
    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.barHeightValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textFontSizeValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        self.rotateDownButton.setEnabled(not self.readOnlyFlag)
        self.rotateUpButton.setEnabled(not self.readOnlyFlag)
        self.reverseButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkAllButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkNoneButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        #self.endPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.checkBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartVimsottariDasaArtifact.

        Arguments:
        
        artifact - PriceBarChartVimsottariDasaArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        elif self.artifact is artifact:
            # They are the same, so no need to do a deep copy.
            # Just continue on, creating and loading the widgets.
            self.log.debug("Same artifact, no need for deep copy.")
        else:
            # Store a deep copy of the artifact because we manipulate
            # the musicalRatios list and its ordering.
            self.log.debug("Deep copying artifact...")
            self.artifact = copy.deepcopy(artifact)

        self.log.debug("Setting the widgets...")
        
        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        self.colorEditButton.setColor(self.artifact.getColor())
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        self.barHeightValueSpinBox.setValue(self.artifact.getBarHeight())
        self.textFontSizeValueSpinBox.setValue(self.artifact.getFontSize())
                                        
        if self.artifact.isTextEnabled():
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        #self.endPointPriceValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        self._reloadMusicalRatiosGrid()
        
        self.log.debug("Exiting loadValues()")

    def _reloadMusicalRatiosGrid(self):
        """Clears and recreates the self.musicalRatiosGridLayout
        according to teh values in self.artifact.
        """
        
        # Remove any old widgets that were in the grid layout from
        # the grid layout..
        for r in range(self.musicalRatiosGridLayout.rowCount()):
            for c in range(self.musicalRatiosGridLayout.columnCount()):
                # Get the QLayoutItem.
                item = self.musicalRatiosGridLayout.itemAtPosition(r, c)
                if item != None:
                    # Get the widget in the layout item.
                    widget = item.widget()
                    if widget != None:
                        widget.setEnabled(False)
                        widget.setVisible(False)
                        widget.setParent(None)

                        # Actually remove the widget from the
                        # QGridLayout.  
                        self.musicalRatiosGridLayout.removeWidget(widget)
                                
        # Row.
        r = 0
        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        # Create the musical ratio items in the
        # self.musicalRatiosGridLayout QGridLayout.
        musicalRatios = self.artifact.getMusicalRatios()
        self.numMusicalRatios = len(musicalRatios)

        # Clear the checkboxes list.
        self.checkBoxes = []

        rangeUsed = None
        if self.artifact.isReversed() == False:
            rangeUsed = range(self.numMusicalRatios)
        else:
            rangeUsed = reversed(range(self.numMusicalRatios))
            
        for i in rangeUsed:
            musicalRatio = musicalRatios[i]

            checkBox = QCheckBox("{}".format(musicalRatio.getRatio()))

            # Set the check state based on whether or not the musical
            # ratio is enabled.
            if musicalRatio.isEnabled():
                checkBox.setCheckState(Qt.Checked)
            else:
                checkBox.setCheckState(Qt.Unchecked)

            # Connect the signal to the slot function
            # _handleCheckMarkToggled().  That function will update
            # the self.artifact's musicalRatios with new check state.
            checkBox.stateChanged.connect(self._handleCheckMarkToggled)
            
            # Append to our list of checkboxes so that we can
            # reference them later and see what values are used in
            # them.  Remember, if we are reversed, then we will need
            # to reverse this list later.
            self.checkBoxes.append(checkBox)
            
            descriptionLabel = QLabel(musicalRatio.getDescription())

            # Use QLabels to
            # display the price and timestamp information.
            (x, y) = self.artifact.getXYForMusicalRatio(i)
                
            price = self.convertObj.sceneYPosToPrice(y)
            priceStr = "{}".format(price)
            priceWidget = QLabel(priceStr)

            timestamp = self.convertObj.sceneXPosToDatetime(x)
            timestampStr = Ephemeris.datetimeToDayStr(timestamp)
            timestampWidget = QLabel(timestampStr)

            # Actually add the widgets to the grid layout.
            self.musicalRatiosGridLayout.addWidget(checkBox, r, 0, al)
            self.musicalRatiosGridLayout.addWidget(descriptionLabel, r, 1, al)
            self.musicalRatiosGridLayout.addWidget(priceWidget, r, 2, al)
            self.musicalRatiosGridLayout.addWidget(timestampWidget, r, 3, al)

            r += 1

        # Reverse the self.checkBoxes list if we are reversed, since
        # if that is the case, then previously in this function we
        # added the checkBoxes in the reverse order.
        if self.artifact.isReversed():
            self.checkBoxes.reverse()
            
    def saveValues(self):
        """Saves the values in the widgets to the internally stored
        PriceBarChartVimsottariDasaArtifact object.
        """

        self.log.debug("Entered saveValues()")

        # Get the colors.
        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.
        startPointPrice = \
            self.startPointPriceValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)
        #endPointPrice = \
        #    self.endPointPriceValueSpinBox.value()
        #endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        endPointY = startPointY
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()
                          
        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)

        # No need to save the musicalRatios inside self.artifact,
        # because each time there is a rotation or a check-marking
        # action, the internal artifact was updated.
        # The same is the case for the self.artifact.setReversed().

        self.log.debug("Exiting saveValues()")

    def _handleBarHeightValueSpinBoxChanged(self):
        """Called when the self.barHeightValueSpinBox is modified."""

        self.artifact.setBarHeight(self.barHeightValueSpinBox.value())
        
    def _handleTextFontSizeValueSpinBoxChanged(self):
        """Called when the self.textFontSizeValueSpinBox is modified."""

        self.artifact.setFontSize(self.textFontSizeValueSpinBox.value())
        
    def _handleTextEnabledCheckBoxToggled(self):
        """Called when the textEnabledCheckBox is checked or unchecked."""

        newValue = None
        
        if self.textEnabledCheckBox.checkState() == Qt.Checked:
            newValue = True
        else:
            newValue = False
        
        self.artifact.setTextEnabled(newValue)
        
    def _handleCheckMarkToggled(self):
        """Called when one of the check-mark boxes on the
        musicalRatios is checked or unchecked.
        """

        # Go through all the musicalRatios in the widget, and set them
        # as enabled or disabled in the artifact, based on the check
        # state of the QCheckBox objects in self.checkBoxes.
        for i in range(len(self.checkBoxes)):
            oldValue = self.artifact.getMusicalRatios()[i].isEnabled()
            newValue = None
            if self.checkBoxes[i].checkState() == Qt.Checked:
                newValue = True
            else:
                newValue = False

            if oldValue != newValue:
                self.log.debug("Updating enabled state of " +
                               "musicalRatio[{}] from {} to {}".\
                               format(i, oldValue, newValue))
                self.artifact.getMusicalRatios()[i].setEnabled(newValue)
            else:
                #self.log.debug("No update to musicalRatio[{}]".format(i))
                pass

    def _saveAndReloadMusicalRatios(self):
        """Saves and reloads the musical ratio widgets."""
        
        # Save values from what is in the widgets to the internal artifact.
        self.saveValues()
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateDownButtonClicked(self):
        """Called when the 'Rotate Down' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()

        if self.artifact.isReversed() == False:
            # Put the last musical ratio in the front.
            if len(musicalRatios) > 0:
                lastRatio = musicalRatios.pop(len(musicalRatios) - 1)
                musicalRatios.insert(0, lastRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
            
        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateUpButtonClicked(self):
        """Called when the 'Rotate Up' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()
        
        if self.artifact.isReversed() == False:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)

        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleReverseButtonClicked(self):
        """Called when the 'Reverse' button is clicked."""

        # Flip the flag that indicates that the musical ratios are reversed.
        self.artifact.setReversed(not self.artifact.isReversed())
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleCheckMarkAllButtonClicked(self):
        """Called when the 'Check All' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Checked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleCheckMarkNoneButtonClicked(self):
        """Called when the 'Check None' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Unchecked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartVimsottariDasaArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartVimsottariDasaArtifact.
    """

    def __init__(self,
                 priceBarChartVimsottariDasaArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartVimsottariDasaArtifact.
        
        Note: The 'priceBarChartVimsottariDasaArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartVimsottariDasaArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartVimsottariDasaArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartVimsottariDasaArtifact Data")

        # Check input.
        if not isinstance(priceBarChartVimsottariDasaArtifact,
                          PriceBarChartVimsottariDasaArtifact):
            self.log.error("Input type invalid to " + \
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartVimsottariDasaArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartVimsottariDasaArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartVimsottariDasaArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartVimsottariDasaArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the artifact object.  If the 'Okay'
        button was previously clicked, then this object contains new
        values as set with the widget, otherwise it is unchanged.
        """

        # The edit widget keeps its own copy of the artifact, which it
        # modifies directly.
        if self.result() == QDialog.Accepted:
            return self.editWidget.getArtifact()
        else:
            return self.artifact

class PriceBarChartAshtottariDasaArtifactEditWidget(QWidget):
    """QWidget for editing some of the member objects in a
    PriceBarChartAshtottariDasaArtifact within the context of a
    PriceBarChart.  This means that fields that are editable in the
    widgets are not actually a one-to-one mapping with the members in
    a PriceBarChartAshtottariDasaArtifact.  They are derivatives of it such
    that the user can modify it without having to do the underlying
    conversions.
    """

    # Signal emitted when the Okay button is clicked and 
    # validation succeeded.
    okayButtonClicked = QtCore.pyqtSignal()

    # Signal emitted when the Cancel button is clicked.
    cancelButtonClicked = QtCore.pyqtSignal()

    def __init__(self,
                 artifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """QWidget for editing some of the fields of a
        PriceBarChartAshtottariDasaArtifact object.

        Arguments:
        artifact - PriceBarChartAshtottariDasaArtifact object to edit.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartAshtottariDasaArtifactEditWidget")

        # This variable holds a copy of the artifact passed in.  We
        # set this value via self.loadValues(), which is called later
        # in this funtion on parameter 'artifact'.
        self.artifact = None

        # Save off the scene object used for unit conversions.
        self.convertObj = convertObj
        
        # Save off the readOnlyFlag
        self.readOnlyFlag = readOnlyFlag
        
        # QGroupBox to hold the edit widgets and form.
        self.groupBoxPage1 = self._createGroupBoxPage1()
        self.groupBoxPage2 = self._createGroupBoxPage2()

        # Create a QTabWidget to stack all the QGroupBox that have our
        # edit widgets.
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.groupBoxPage1, "Page 1")
        self.tabWidget.addTab(self.groupBoxPage2, "Page 2")

        # Buttons at bottom.
        self.okayButton = QPushButton("&Okay")
        self.cancelButton = QPushButton("&Cancel")
        self.buttonsAtBottomLayout = QHBoxLayout()
        self.buttonsAtBottomLayout.addStretch()
        self.buttonsAtBottomLayout.addWidget(self.okayButton)
        self.buttonsAtBottomLayout.addWidget(self.cancelButton)

        # Put all layouts/groupboxes together into the widget.
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonsAtBottomLayout) 

        self.setLayout(self.mainLayout)
        
        # Now that all the widgets are created, load the values from the
        # artifact object.
        self.loadValues(artifact)

        self.setReadOnly(self.readOnlyFlag)
        
        # Connect signals and slots.

        self.barHeightValueSpinBox.valueChanged.\
            connect(self._handleBarHeightValueSpinBoxChanged)
        self.textFontSizeValueSpinBox.valueChanged.\
            connect(self._handleTextFontSizeValueSpinBoxChanged)
        self.textEnabledCheckBox.stateChanged.\
            connect(self._handleTextEnabledCheckBoxToggled)
        
        # Connect rotateUp and rotateDown buttons.
        self.rotateUpButton.clicked.\
            connect(self._handleRotateUpButtonClicked)
        self.rotateDownButton.clicked.\
            connect(self._handleRotateDownButtonClicked)
        self.reverseButton.clicked.\
            connect(self._handleReverseButtonClicked)
        self.checkMarkAllButton.clicked.\
            connect(self._handleCheckMarkAllButtonClicked)
        self.checkMarkNoneButton.clicked.\
            connect(self._handleCheckMarkNoneButtonClicked)

        # Connect the signals for the price and time values changing,
        # so that we can update the start and end points in the
        # artifact and update all the prices and datetimes in
        # between.
        self.startPointPriceValueSpinBox.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        #self.endPointPriceValueSpinBox.valueChanged.\
        #    connect(self. _saveAndReloadMusicalRatios)
        self.startPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        self.endPointDatetimeLocationWidget.valueChanged.\
            connect(self._saveAndReloadMusicalRatios)
        
        # Connect okay and cancel buttons.
        self.okayButton.clicked.connect(self._handleOkayButtonClicked)
        self.cancelButton.clicked.connect(self._handleCancelButtonClicked)

    def _createGroupBoxPage1(self):
        """Creates a QGroupBox (and the widgets within it) for page1
        of the edit widget, and then returns it.
        """

        self.groupBoxPage1 = \
            QGroupBox("PriceBarChartAshtottariDasaArtifact Data (page 1):")
        
        lineEditWidth = 420
        
        self.internalNameLabel = QLabel("Internal name:")
        self.internalNameLineEdit = QLineEdit()
        self.internalNameLineEdit.setMinimumWidth(lineEditWidth)

        self.uuidLabel = QLabel("Uuid:")
        self.uuidLineEdit = QLineEdit()
        self.uuidLineEdit.setMinimumWidth(lineEditWidth)

        self.colorLabel = QLabel("Bar color: ")
        self.colorEditButton = ColorEditPushButton()

        self.textColorLabel = QLabel("Text color: ")
        self.textColorEditButton = ColorEditPushButton()
        
        self.barHeightValueLabel = \
            QLabel("AshtottariDasa bar height:")
        self.barHeightValueSpinBox = QDoubleSpinBox()
        self.barHeightValueSpinBox.setMinimum(0.0)
        self.barHeightValueSpinBox.setMaximum(999999999.0)

        self.textFontSizeValueLabel = \
            QLabel("Text font size:")
        self.textFontSizeValueSpinBox = QDoubleSpinBox()
        self.textFontSizeValueSpinBox.setMinimum(0.0)
        self.textFontSizeValueSpinBox.setMaximum(999999999.0)

        self.textEnabledLabel = QLabel("Text is enabled:")
        self.textEnabledCheckBox = QCheckBox()
        self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        self.startPointPriceValueLabel = \
            QLabel("AshtottariDasa Start Point (in price):")
        self.startPointPriceValueSpinBox = QDoubleSpinBox()
        self.startPointPriceValueSpinBox.setDecimals(4)
        self.startPointPriceValueSpinBox.setMinimum(0.0)
        self.startPointPriceValueSpinBox.setMaximum(999999999.0)
        startPointPriceValueLayout = QHBoxLayout()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueLabel)
        startPointPriceValueLayout.addStretch()
        startPointPriceValueLayout.addWidget(self.startPointPriceValueSpinBox)
        
        self.startPointDatetimeLocationWidget = TimestampEditWidget()
        self.startPointDatetimeLocationWidget.groupBox.\
            setTitle("AshtottariDasa Start Point (in time)")
        self.startPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.startPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        #self.endPointPriceValueLabel = \
        #    QLabel("AshtottariDasa End Point (in price):")
        #self.endPointPriceValueSpinBox = QDoubleSpinBox()
        #self.endPointPriceValueSpinBox.setDecimals(4)
        #self.endPointPriceValueSpinBox.setMinimum(0.0)
        #self.endPointPriceValueSpinBox.setMaximum(999999999.0)
        #endPointPriceValueLayout = QHBoxLayout()
        #endPointPriceValueLayout.addWidget(self.endPointPriceValueLabel)
        #endPointPriceValueLayout.addStretch()
        #endPointPriceValueLayout.addWidget(self.endPointPriceValueSpinBox)
        
        self.endPointDatetimeLocationWidget = TimestampEditWidget()
        self.endPointDatetimeLocationWidget.groupBox.\
            setTitle("AshtottariDasa End Point (in time)")
        self.endPointDatetimeLocationWidget.okayButton.setVisible(False)
        self.endPointDatetimeLocationWidget.cancelButton.setVisible(False)
        
        # Layout.
        gridLayout = QGridLayout()

        # Row.
        r = 0

        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        gridLayout.addWidget(self.internalNameLabel, r, 0, al)
        gridLayout.addWidget(self.internalNameLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.uuidLabel, r, 0, al)
        gridLayout.addWidget(self.uuidLineEdit, r, 1, al)
        r += 1
        gridLayout.addWidget(self.colorLabel, r, 0, al)
        gridLayout.addWidget(self.colorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textColorLabel, r, 0, al)
        gridLayout.addWidget(self.textColorEditButton, r, 1, al)
        r += 1
        gridLayout.addWidget(self.barHeightValueLabel, r, 0, al)
        gridLayout.addWidget(self.barHeightValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textFontSizeValueLabel, r, 0, al)
        gridLayout.addWidget(self.textFontSizeValueSpinBox, r, 1, al)
        r += 1
        gridLayout.addWidget(self.textEnabledLabel, r, 0, al)
        gridLayout.addWidget(self.textEnabledCheckBox, r, 1, al)
        r += 1
        gridLayout.addLayout(startPointPriceValueLayout, r, 0, al)
        #gridLayout.addLayout(endPointPriceValueLayout, r, 1, al)
        r += 1
        gridLayout.addWidget(self.startPointDatetimeLocationWidget,
                                  r, 0, al)
        gridLayout.addWidget(self.endPointDatetimeLocationWidget,
                                  r, 1, al)
        r += 1

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addStretch()
        
        self.groupBoxPage1.setLayout(layout)

        return self.groupBoxPage1
    
    def _createGroupBoxPage2(self):
        """Creates a QGroupBox (and the widgets within it) for page2
        of the edit widget, and then returns it.
        """

        self.groupBoxPage2 = \
            QGroupBox("PriceBarChartAshtottariDasaArtifact Data (page 2):")
        
        self.rotateDownButton = QPushButton("Rotate Down")
        self.rotateUpButton = QPushButton("Rotate Up")
        self.reverseButton = QPushButton("Reverse")
        self.checkMarkAllButton = QPushButton("Check All")
        self.checkMarkNoneButton = QPushButton("Check None")
        
        rotateButtonsLayout = QHBoxLayout()
        rotateButtonsLayout.addWidget(self.rotateDownButton)
        rotateButtonsLayout.addWidget(self.rotateUpButton)
        rotateButtonsLayout.addWidget(self.reverseButton)
        rotateButtonsLayout.addWidget(self.checkMarkAllButton)
        rotateButtonsLayout.addWidget(self.checkMarkNoneButton)
        rotateButtonsLayout.addStretch()
        
        # Layout for the musical ratio intervals.
        self.musicalRatiosGridLayout = QGridLayout()
        self.numMusicalRatios = 0

        # Holds the list of QCheckBox objects corresponding to the
        # MusicalRatios (ordered) in the artifact. 
        self.checkBoxes = []
        
        layout = QVBoxLayout()
        layout.addLayout(rotateButtonsLayout)
        layout.addLayout(self.musicalRatiosGridLayout)
        layout.addStretch()
        
        self.groupBoxPage2.setLayout(layout)

        return self.groupBoxPage2
        
    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        # Need to reload the artifact, so that the proper conversion
        # is done with the new conversion object.
        self.loadValues(self.artifact)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
        
    def getArtifact(self):
        """Returns the internally stored artifact object.

        Note: If saveValues() was called previously, then this object
        was updated with the values from the edit widgets.
        """

        return self.artifact
        
    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
        ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        # Set the internal widgets as readonly or not depending on this flag.
        self.internalNameLineEdit.setReadOnly(True)
        self.uuidLineEdit.setReadOnly(True)
        self.colorEditButton.setEnabled(not self.readOnlyFlag)
        self.textColorEditButton.setEnabled(not self.readOnlyFlag)
        self.barHeightValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textFontSizeValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.textEnabledCheckBox.setEnabled(not self.readOnlyFlag)
        self.rotateDownButton.setEnabled(not self.readOnlyFlag)
        self.rotateUpButton.setEnabled(not self.readOnlyFlag)
        self.reverseButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkAllButton.setEnabled(not self.readOnlyFlag)
        self.checkMarkNoneButton.setEnabled(not self.readOnlyFlag)
        self.startPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.startPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)
        #self.endPointPriceValueSpinBox.setEnabled(not self.readOnlyFlag)
        self.endPointDatetimeLocationWidget.setReadOnly(self.readOnlyFlag)

        for checkBox in self.checkBoxes:
            checkBox.setEnabled(not self.readOnlyFlag)
        
        # Don't allow the Okay button to be pressed for saving.
        self.okayButton.setEnabled(not self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields in the PriceBar.
        """
        
        return self.readOnlyFlag

    def loadValues(self, artifact):
        """Loads the widgets with values from the given
        PriceBarChartAshtottariDasaArtifact.

        Arguments:
        
        artifact - PriceBarChartAshtottariDasaArtifact object to load the
        values into the edit widgets.  
        """

        self.log.debug("Entered loadValues()")

        # Check inputs.
        if artifact == None:
            self.log.error("Invalid parameter to " + \
                           "loadValues().  artifact can't be None.")
            self.log.debug("Exiting loadValues()")
            return
        elif self.artifact is artifact:
            # They are the same, so no need to do a deep copy.
            # Just continue on, creating and loading the widgets.
            self.log.debug("Same artifact, no need for deep copy.")
        else:
            # Store a deep copy of the artifact because we manipulate
            # the musicalRatios list and its ordering.
            self.log.debug("Deep copying artifact...")
            self.artifact = copy.deepcopy(artifact)

        self.log.debug("Setting the widgets...")
        
        # Set the widgets.
        self.internalNameLineEdit.\
            setText(self.artifact.getInternalName())
        self.uuidLineEdit.\
            setText(str(self.artifact.getUuid()))
        self.colorEditButton.setColor(self.artifact.getColor())
        self.textColorEditButton.setColor(self.artifact.getTextColor())
        self.barHeightValueSpinBox.setValue(self.artifact.getBarHeight())
        self.textFontSizeValueSpinBox.setValue(self.artifact.getFontSize())
                                        
        if self.artifact.isTextEnabled():
            self.textEnabledCheckBox.setCheckState(Qt.Checked)
        else:
            self.textEnabledCheckBox.setCheckState(Qt.Unchecked)

        startPointY = self.artifact.startPointF.y()
        startPointPrice = self.convertObj.sceneYPosToPrice(startPointY)
        self.startPointPriceValueSpinBox.setValue(startPointPrice)
        
        startPointX = self.artifact.startPointF.x()
        startPointDatetime = self.convertObj.sceneXPosToDatetime(startPointX)
        self.startPointDatetimeLocationWidget.\
            loadTimestamp(startPointDatetime)
        
        endPointY = self.artifact.endPointF.y()
        endPointPrice = self.convertObj.sceneYPosToPrice(endPointY)
        #self.endPointPriceValueSpinBox.setValue(endPointPrice)
        
        endPointX = self.artifact.endPointF.x()
        endPointDatetime = self.convertObj.sceneXPosToDatetime(endPointX)
        self.endPointDatetimeLocationWidget.\
            loadTimestamp(endPointDatetime)

        self._reloadMusicalRatiosGrid()
        
        self.log.debug("Exiting loadValues()")

    def _reloadMusicalRatiosGrid(self):
        """Clears and recreates the self.musicalRatiosGridLayout
        according to teh values in self.artifact.
        """
        
        # Remove any old widgets that were in the grid layout from
        # the grid layout..
        for r in range(self.musicalRatiosGridLayout.rowCount()):
            for c in range(self.musicalRatiosGridLayout.columnCount()):
                # Get the QLayoutItem.
                item = self.musicalRatiosGridLayout.itemAtPosition(r, c)
                if item != None:
                    # Get the widget in the layout item.
                    widget = item.widget()
                    if widget != None:
                        widget.setEnabled(False)
                        widget.setVisible(False)
                        widget.setParent(None)

                        # Actually remove the widget from the
                        # QGridLayout.  
                        self.musicalRatiosGridLayout.removeWidget(widget)
                                
        # Row.
        r = 0
        # Alignments.
        al = Qt.AlignLeft
        ar = Qt.AlignRight

        # Create the musical ratio items in the
        # self.musicalRatiosGridLayout QGridLayout.
        musicalRatios = self.artifact.getMusicalRatios()
        self.numMusicalRatios = len(musicalRatios)

        # Clear the checkboxes list.
        self.checkBoxes = []

        rangeUsed = None
        if self.artifact.isReversed() == False:
            rangeUsed = range(self.numMusicalRatios)
        else:
            rangeUsed = reversed(range(self.numMusicalRatios))
            
        for i in rangeUsed:
            musicalRatio = musicalRatios[i]

            checkBox = QCheckBox("{}".format(musicalRatio.getRatio()))

            # Set the check state based on whether or not the musical
            # ratio is enabled.
            if musicalRatio.isEnabled():
                checkBox.setCheckState(Qt.Checked)
            else:
                checkBox.setCheckState(Qt.Unchecked)

            # Connect the signal to the slot function
            # _handleCheckMarkToggled().  That function will update
            # the self.artifact's musicalRatios with new check state.
            checkBox.stateChanged.connect(self._handleCheckMarkToggled)
            
            # Append to our list of checkboxes so that we can
            # reference them later and see what values are used in
            # them.  Remember, if we are reversed, then we will need
            # to reverse this list later.
            self.checkBoxes.append(checkBox)
            
            descriptionLabel = QLabel(musicalRatio.getDescription())

            # Use QLabels to
            # display the price and timestamp information.
            (x, y) = self.artifact.getXYForMusicalRatio(i)
                
            price = self.convertObj.sceneYPosToPrice(y)
            priceStr = "{}".format(price)
            priceWidget = QLabel(priceStr)

            timestamp = self.convertObj.sceneXPosToDatetime(x)
            timestampStr = Ephemeris.datetimeToDayStr(timestamp)
            timestampWidget = QLabel(timestampStr)

            # Actually add the widgets to the grid layout.
            self.musicalRatiosGridLayout.addWidget(checkBox, r, 0, al)
            self.musicalRatiosGridLayout.addWidget(descriptionLabel, r, 1, al)
            self.musicalRatiosGridLayout.addWidget(priceWidget, r, 2, al)
            self.musicalRatiosGridLayout.addWidget(timestampWidget, r, 3, al)

            r += 1

        # Reverse the self.checkBoxes list if we are reversed, since
        # if that is the case, then previously in this function we
        # added the checkBoxes in the reverse order.
        if self.artifact.isReversed():
            self.checkBoxes.reverse()
            
    def saveValues(self):
        """Saves the values in the widgets to the internally stored
        PriceBarChartAshtottariDasaArtifact object.
        """

        self.log.debug("Entered saveValues()")

        # Get the colors.
        color = self.colorEditButton.getColor()
        textColor = self.textColorEditButton.getColor()
        
        # Call save on the timestamp widgets.
        self.startPointDatetimeLocationWidget.saveTimestamp()
        self.endPointDatetimeLocationWidget.saveTimestamp()
        
        # Position and start point should be the same values.
        startPointPrice = \
            self.startPointPriceValueSpinBox.value()
        startPointY = self.convertObj.priceToSceneYPos(startPointPrice)
        #endPointPrice = \
        #    self.endPointPriceValueSpinBox.value()
        #endPointY = self.convertObj.priceToSceneYPos(endPointPrice)
        endPointY = startPointY
        
        startPointDatetime = \
            self.startPointDatetimeLocationWidget.getTimestamp()
        endPointDatetime = \
            self.endPointDatetimeLocationWidget.getTimestamp()
                          
        startPointX = self.convertObj.datetimeToSceneXPos(startPointDatetime)
        endPointX = self.convertObj.datetimeToSceneXPos(endPointDatetime)

        posF = QPointF(startPointX, startPointY)
        startPointF = QPointF(startPointX, startPointY)
        endPointF = QPointF(endPointX, endPointY)

        # Set the values in the artifact.
        self.artifact.setPos(posF)
        self.artifact.setColor(color)
        self.artifact.setTextColor(textColor)
        self.artifact.setStartPointF(startPointF)
        self.artifact.setEndPointF(endPointF)

        # No need to save the musicalRatios inside self.artifact,
        # because each time there is a rotation or a check-marking
        # action, the internal artifact was updated.
        # The same is the case for the self.artifact.setReversed().

        self.log.debug("Exiting saveValues()")

    def _handleBarHeightValueSpinBoxChanged(self):
        """Called when the self.barHeightValueSpinBox is modified."""

        self.artifact.setBarHeight(self.barHeightValueSpinBox.value())
        
    def _handleTextFontSizeValueSpinBoxChanged(self):
        """Called when the self.textFontSizeValueSpinBox is modified."""

        self.artifact.setFontSize(self.textFontSizeValueSpinBox.value())
        
    def _handleTextEnabledCheckBoxToggled(self):
        """Called when the textEnabledCheckBox is checked or unchecked."""

        newValue = None
        
        if self.textEnabledCheckBox.checkState() == Qt.Checked:
            newValue = True
        else:
            newValue = False
        
        self.artifact.setTextEnabled(newValue)
        
    def _handleCheckMarkToggled(self):
        """Called when one of the check-mark boxes on the
        musicalRatios is checked or unchecked.
        """

        # Go through all the musicalRatios in the widget, and set them
        # as enabled or disabled in the artifact, based on the check
        # state of the QCheckBox objects in self.checkBoxes.
        for i in range(len(self.checkBoxes)):
            oldValue = self.artifact.getMusicalRatios()[i].isEnabled()
            newValue = None
            if self.checkBoxes[i].checkState() == Qt.Checked:
                newValue = True
            else:
                newValue = False

            if oldValue != newValue:
                self.log.debug("Updating enabled state of " +
                               "musicalRatio[{}] from {} to {}".\
                               format(i, oldValue, newValue))
                self.artifact.getMusicalRatios()[i].setEnabled(newValue)
            else:
                #self.log.debug("No update to musicalRatio[{}]".format(i))
                pass

    def _saveAndReloadMusicalRatios(self):
        """Saves and reloads the musical ratio widgets."""
        
        # Save values from what is in the widgets to the internal artifact.
        self.saveValues()
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateDownButtonClicked(self):
        """Called when the 'Rotate Down' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()

        if self.artifact.isReversed() == False:
            # Put the last musical ratio in the front.
            if len(musicalRatios) > 0:
                lastRatio = musicalRatios.pop(len(musicalRatios) - 1)
                musicalRatios.insert(0, lastRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
            
        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleRotateUpButtonClicked(self):
        """Called when the 'Rotate Up' button is clicked."""

        # Get all the musicalRatios in the internally stored artifact.
        musicalRatios = self.artifact.getMusicalRatios()
        
        if self.artifact.isReversed() == False:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)
        else:
            # Put the first musical ratio in the back.
            if len(musicalRatios) > 0:
                firstRatio = musicalRatios.pop(0)
                musicalRatios.append(firstRatio)

        # Overwrite the old list in the internally stored artifact.
        self.artifact.setMusicalRatios(musicalRatios)

        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleReverseButtonClicked(self):
        """Called when the 'Reverse' button is clicked."""

        # Flip the flag that indicates that the musical ratios are reversed.
        self.artifact.setReversed(not self.artifact.isReversed())
        
        # Reload the musicalRatiosGrid.
        self._reloadMusicalRatiosGrid()
    
    def _handleCheckMarkAllButtonClicked(self):
        """Called when the 'Check All' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Checked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleCheckMarkNoneButtonClicked(self):
        """Called when the 'Check None' button is clicked."""


        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Unchecked)

        # Call this to update the internal artifact object according
        # to what the widgets have set (in this case, the 'enabled'
        # checkboxes).
        self._handleCheckMarkToggled()
        
    def _handleOkayButtonClicked(self):
        """Called when the okay button is clicked."""

        self.saveValues()
        self.okayButtonClicked.emit()

    def _handleCancelButtonClicked(self):
        """Called when the cancel button is clicked."""

        self.cancelButtonClicked.emit()


class PriceBarChartAshtottariDasaArtifactEditDialog(QDialog):
    """QDialog for editing some of the members objects in a 
    PriceBarChartAshtottariDasaArtifact.
    """

    def __init__(self,
                 priceBarChartAshtottariDasaArtifact,
                 convertObj,
                 readOnlyFlag=False,
                 parent=None):
        """Initializes the dialog and internal widget with the values
        from the given PriceBarChartAshtottariDasaArtifact.
        
        Note: The 'priceBarChartAshtottariDasaArtifact' object gets modified
        if the user clicks the 'Okay' button.

        Arguments:
        artifact - PriceBarChartAshtottariDasaArtifact object to edit.
                   This object gets modified if the user clicks the
                   'Okay' button.
        convertObj - PriceBarChartGraphicsScene object that is used for
                unit conversions (x position to time, y position to price).
        readOnlyFlag - bool value used to set the widgets in readonly mode.
        """

        super().__init__(parent)

        # Logger object for this class.
        self.log = logging.getLogger(\
            "pricebarchart_dialogs.PriceBarChartAshtottariDasaArtifactEditDialog")

        self.setWindowTitle("Edit PriceBarChartAshtottariDasaArtifact Data")

        # Check input.
        if not isinstance(priceBarChartAshtottariDasaArtifact,
                          PriceBarChartAshtottariDasaArtifact):
            self.log.error("Input type invalid to " + \
                           self.__class__.__name__ +
                           " constructor.")
            return

        # Save a reference to the artifact object.
        self.artifact = priceBarChartAshtottariDasaArtifact

        # Save a reference to the conversion object.
        self.convertObj = convertObj
        
        # Save the readOnlyFlag value.
        self.readOnlyFlag = readOnlyFlag
        
        # Create the contents.
        self.editWidget = \
            PriceBarChartAshtottariDasaArtifactEditWidget(self.artifact,
                                                    self.convertObj,
                                                    self.readOnlyFlag)
        
        # Setup the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.editWidget)
        self.setLayout(layout)

        self.editWidget.okayButtonClicked.connect(self.accept)
        self.editWidget.cancelButtonClicked.connect(self.reject)

    def setReadOnly(self, readOnlyFlag):
        """Sets the internal edit widgets to be read only or not
        depending on the bool state of readOnlyFlag.

        Arguments:
        readOnlyFlag - bool value indicating whether the widget is in
                       ReadOnly mode.
        """

        self.readOnlyFlag = readOnlyFlag

        self.editWidget.setReadOnly(self.readOnlyFlag)
        
    def getReadOnly(self):
        """Returns the flag that indicates that this widget is in
        read-only mode.  If the returned value is True, then it means
        the user cannot edit any of the fields.
        """
        
        return self.readOnlyFlag

    def setConvertObj(self, convertObj):
        """Sets the object that is used for the conversion between
        scene position and timestamp or price.

        Arguments:
        convertObj - PriceBarChartGraphicsScene object that is used
                     for scene position conversions of X point to
                     timestamp and Y point to price.
        """

        self.convertObj = convertObj

        self.editWidget.setConvertObj(self.convertObj)
        
    def getConvertObj(self):
        """Returns the object used for conversion calculations between
        scene position point and timestamp or price.

        Returns:
        PriceBarChartGraphicsScene object that is used
        for scene position conversions of X point to
        timestamp and Y point to price.
        """

        return self.convertObj
    
    def setArtifact(self, artifact):
        """Loads the edit widget with the given artifact object.
        
        Note:  Upon clicking 'Okay' this object will be modified.

        Arguments:
        artifact - PriceBarChartAshtottariDasaArtifact object to load the
                   widgets with.
        """

        # Check input.
        if not isinstance(artifact,
                          PriceBarChartAshtottariDasaArtifact):
            self.log.error("Input type invalid to " +
                           self.__class__.__name__ +
                           ".setArtifact()")
            return

        self.artifact = artifact

        self.editWidget.loadValues(self.artifact)

    def getArtifact(self):
        """Returns a reference to the artifact object.  If the 'Okay'
        button was previously clicked, then this object contains new
        values as set with the widget, otherwise it is unchanged.
        """

        # The edit widget keeps its own copy of the artifact, which it
        # modifies directly.
        if self.result() == QDialog.Accepted:
            return self.editWidget.getArtifact()
        else:
            return self.artifact


##############################################################################
    

def testPriceBarChartBarCountArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartBarCountArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y()))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartBarCountArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartBarCountArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartBarCountArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartBarCountArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartBarCountArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartBarCountArtifact: {}".\
          format(artifact.toString()))

def testPriceBarChartTimeMeasurementArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartTimeMeasurementArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y()))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartTimeMeasurementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTimeMeasurementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartTimeMeasurementArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartTimeMeasurementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTimeMeasurementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartTimeMeasurementArtifact: {}".\
          format(artifact.toString()))
    

def testPriceBarChartTimeModalScaleArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartTimeModalScaleArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartTimeModalScaleArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTimeModalScaleArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartTimeModalScaleArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartTimeModalScaleArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTimeModalScaleArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartTimeModalScaleArtifact: {}".\
          format(artifact.toString()))
    
def testPriceBarChartPriceModalScaleArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartPriceModalScaleArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartPriceModalScaleArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceModalScaleArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartPriceModalScaleArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartPriceModalScaleArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceModalScaleArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartPriceModalScaleArtifact: {}".\
          format(artifact.toString()))
    
def testPriceBarChartTextArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartTextArtifact()

    # Set the artifact's position.  It needs to be at a position where
    # the converted datetime.datetime is greater than the
    # datetime.datetime.MINYEAR.  A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartTextArtifactEditDialog: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTextArtifactEditDialog(artifact,
                                                 convertObj,
                                                 readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartTextArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartTextArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTextArtifactEditDialog(artifact,
                                                 convertObj,
                                                 readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartTextArtifact: {}".\
          format(artifact.toString()))

    
def testPriceBarChartPriceTimeInfoArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartPriceTimeInfoArtifact()

    # Set the artifact's position.  It needs to be at a position where
    # the converted datetime.datetime is greater than the
    # datetime.datetime.MINYEAR.  A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartPriceTimeInfoArtifactEditDialog: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceTimeInfoArtifactEditDialog(artifact,
                                                 convertObj,
                                                 readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartPriceTimeInfoArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartPriceTimeInfoArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceTimeInfoArtifactEditDialog(artifact,
                                                 convertObj,
                                                 readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartPriceTimeInfoArtifact: {}".\
          format(artifact.toString()))

    
def testPriceBarChartPriceMeasurementArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartPriceMeasurementArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x(), pos.y() + 5.0))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartPriceMeasurementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceMeasurementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartPriceMeasurementArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartPriceMeasurementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceMeasurementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartPriceMeasurementArtifact: {}".\
          format(artifact.toString()))
    

def testPriceBarChartTimeRetracementArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartTimeRetracementArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 10))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartTimeRetracementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTimeRetracementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartTimeRetracementArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartTimeRetracementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartTimeRetracementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartTimeRetracementArtifact: {}".\
          format(artifact.toString()))

    
def testPriceBarChartPriceRetracementArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartPriceRetracementArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 10))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartPriceRetracementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceRetracementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartPriceRetracementArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartPriceRetracementArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceRetracementArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartPriceRetracementArtifact: {}".\
          format(artifact.toString()))
    

def testPriceBarChartPriceTimeVectorArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartPriceTimeVectorArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 10))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartPriceTimeVectorArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceTimeVectorArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartPriceTimeVectorArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartPriceTimeVectorArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartPriceTimeVectorArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartPriceTimeVectorArtifact: {}".\
          format(artifact.toString()))
    
def testPriceBarChartLineSegmentArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartLineSegmentArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 10))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartLineSegmentArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartLineSegmentArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartLineSegmentArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartLineSegmentArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartLineSegmentArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartLineSegmentArtifact: {}".\
          format(artifact.toString()))
    
def testPriceBarChartOctaveFanArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartOctaveFanArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartOctaveFanArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartOctaveFanArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartOctaveFanArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartOctaveFanArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartOctaveFanArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartOctaveFanArtifact: {}".\
          format(artifact.toString()))
    

def testPriceBarChartFibFanArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartFibFanArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartFibFanArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartFibFanArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartFibFanArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartFibFanArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartFibFanArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartFibFanArtifact: {}".\
          format(artifact.toString()))
    

def testPriceBarChartGannFanArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartGannFanArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartGannFanArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartGannFanArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartGannFanArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartGannFanArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartGannFanArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartGannFanArtifact: {}".\
          format(artifact.toString()))
    
def testPriceBarChartVimsottariDasaArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartVimsottariDasaArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartVimsottariDasaArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartVimsottariDasaArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartVimsottariDasaArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartVimsottariDasaArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartVimsottariDasaArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartVimsottariDasaArtifact: {}".\
          format(artifact.toString()))
    
def testPriceBarChartAshtottariDasaArtifactEditDialog():
    print("Running " + inspect.stack()[0][3] + "()")
    
    # Create an artifact.
    artifact = PriceBarChartAshtottariDasaArtifact()

    # Set the artifact's position and start/end points.  It needs to
    # be at a position where the converted datetime.datetime is
    # greater than the datetime.datetime.MINYEAR.
    # A X value of 2450000 is in year 1995.
    pos = QPointF(2450000, -1000)
    artifact.setPos(pos)
    artifact.setStartPointF(pos)
    artifact.setEndPointF(QPoint(pos.x() + 1000, pos.y() - 1000))

    # Create an object for doing unit conversions.
    eastern = pytz.timezone('US/Eastern')
    from pricebarchart import PriceBarChartGraphicsScene
    convertObj = PriceBarChartGraphicsScene()
    convertObj.setTimezone(eastern)
    
    # Run the dialog in readonly mode.
    print("Before (readonly), " +
          "PriceBarChartAshtottariDasaArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartAshtottariDasaArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=True)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (readonly), " +
          "PriceBarChartAshtottariDasaArtifact: {}".\
          format(artifact.toString()))

    
    # Run the dialog in non-readonly mode.
    print("Before (not readonly), " +
          "PriceBarChartAshtottariDasaArtifact: {}".\
          format(artifact.toString()))
    dialog = PriceBarChartAshtottariDasaArtifactEditDialog(artifact,
                                                     convertObj,
                                                     readOnlyFlag=False)
    rv = dialog.exec_()
    if rv == QDialog.Accepted:
        print("Accepted")
    else:
        print("Rejected")
    print("After  (not readonly), " +
          "PriceBarChartAshtottariDasaArtifact: {}".\
          format(artifact.toString()))
    

##############################################################################
    
# For debugging the module during development.  
if __name__=="__main__":
    # For inspect.stack().
    import inspect
    
    import os
    import sys
    
    from ephemeris import Ephemeris
    
    # Initialize the Ephemeris (required).
    Ephemeris.initialize()

    # Set a default location (required).
    Ephemeris.setGeographicPosition(-77.084444, 38.890277)
    
    # Initialize logging.
    LOG_CONFIG_FILE = os.path.join(sys.path[0], "../conf/logging.conf")
    logging.config.fileConfig(LOG_CONFIG_FILE)

    # Create the Qt application.
    app = QApplication(sys.argv)

    # Various tests to run:
    #testPriceBarChartBarCountArtifactEditDialog()
    #testPriceBarChartTimeMeasurementArtifactEditDialog()
    #testPriceBarChartTimeModalScaleArtifactEditDialog()
    #testPriceBarChartPriceModalScaleArtifactEditDialog()
    #testPriceBarChartTextArtifactEditDialog()
    #testPriceBarChartPriceTimeInfoArtifactEditDialog()
    #testPriceBarChartPriceMeasurementArtifactEditDialog()
    #testPriceBarChartTimeRetracementArtifactEditDialog()
    #testPriceBarChartPriceRetracementArtifactEditDialog()
    #testPriceBarChartPriceTimeVectorArtifactEditDialog()
    #testPriceBarChartLineSegmentArtifactEditDialog()
    #testPriceBarChartOctaveFanArtifactEditDialog()
    testPriceBarChartFibFanArtifactEditDialog()
    testPriceBarChartGannFanArtifactEditDialog()
    testPriceBarChartVimsottariDasaArtifactEditDialog()
    testPriceBarChartAshtottariDasaArtifactEditDialog()
    
    # Exit the app when all windows are closed.
    app.connect(app, SIGNAL("lastWindowClosed()"), logging.shutdown)
    app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))

    # Quit.
    print("Exiting.")
    import sys
    sys.exit()
    #app.exec_()
    

