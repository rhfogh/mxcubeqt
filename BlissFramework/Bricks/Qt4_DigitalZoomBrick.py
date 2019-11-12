#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.
import logging

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors

__credits__ = ["ALBA"]
__licence__ = "LGPLv3+"
__version__ = "2.3"
__category__ = "General"


class Qt4_DigitalZoomBrick(BlissWidget):

    STATE_COLORS = {}

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.zoom_hwobj = None

        # Internal values -----------------------------------------------------
        self.positions = None

        # Properties ----------------------------------------------------------
        self.addProperty("label", "string", "")
        self.addProperty("mnemonic", "string", "")
        self.addProperty("icons", "string", "")
        self.addProperty("showMoveButtons", "boolean", True)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("setEnabled", ())

        # Graphic elements ----------------------------------------------------
        _main_gbox = QGroupBox(self)
        self.label = QLabel("zoom:", _main_gbox)
        self.positions_combo = QComboBox(self)
        self.previous_position_button = QPushButton(_main_gbox)
        self.next_position_button = QPushButton(_main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_hlayout = QHBoxLayout(_main_gbox)
        _main_gbox_hlayout.addWidget(self.label)
        _main_gbox_hlayout.addWidget(self.positions_combo)
        _main_gbox_hlayout.addWidget(self.previous_position_button)
        _main_gbox_hlayout.addWidget(self.next_position_button)
        _main_gbox_hlayout.setSpacing(2)
        _main_gbox_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(_main_gbox)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.positions_combo.activated.connect(self.position_selected)
        self.previous_position_button.clicked.connect(self.select_previous_position)
        self.next_position_button.clicked.connect(self.select_next_position)

        # Other ---------------------------------------------------------------
        self.positions_combo.setFixedHeight(27)
        self.positions_combo.setToolTip("Selects zoom level")
        self.previous_position_button.setIcon(Qt4_Icons.load_icon("Minus2"))
        self.previous_position_button.setFixedSize(27, 27)
        self.next_position_button.setIcon(Qt4_Icons.load_icon("Plus2"))
        self.next_position_button.setFixedSize(27, 27)

    def _init_state_colors(self):
        """
        Map state to widget colors.

        Returns: None

        """
        # TODO: it there a generic method for this?
        # This mapping should be universal for all widgets --> unique set of states
        state = self.zoom_hwobj.STATE
        self.STATE_COLORS[state.UNKNOWN] = Qt4_widget_colors.DARK_GRAY
        self.STATE_COLORS[state.READY] = Qt4_widget_colors.LIGHT_GREEN
        self.STATE_COLORS[state.LOW_LIMIT] = Qt4_widget_colors.LIGHT_GREEN
        self.STATE_COLORS[state.HIGH_LIMIT] = Qt4_widget_colors.LIGHT_GREEN
        self.STATE_COLORS[state.DISABLED] = Qt4_widget_colors.DARK_GRAY
        self.STATE_COLORS[state.FAULT] = Qt4_widget_colors.LIGHT_RED

    def setToolTip(self, name=None, state=None):
        """
        Helper function that sets the tooltip for the label widget. It reports the
        current status of the zoom device.

        Args:
            name: Name of the HwObj (mnemonic).
            state: Current HwObj state.

        Returns: None

        """
        if name is None:
            name = self["mnemonic"]
        if self.zoom_hwobj is None:
            tip = "Unknown zoom device with name {}".format(name)
        else:
            if state is None:
                state = self.zoom_hwobj.getState()
            try:
                state_str = state.name
            except IndexError:
                state_str = "UNKNOWN"
            tip = "State: {}".format(state_str)

        self.label.setToolTip(tip)

    def motor_state_changed(self, state):
        """
        Update combo box color according to zoom state

        Args:
            state: New zoom tango state.

        Returns: None

        """
        # TODO: state is a Tango state, but we need a DigitalZoomState instead.
        state = self.zoom_hwobj.getState()

        found = state in list(self.zoom_hwobj.STATE)

        self.positions_combo.setEnabled(found)
        Qt4_widget_colors.set_widget_color(
            self.positions_combo, self.STATE_COLORS[state], QPalette.Button
        )
        self.setToolTip(state=state)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Updates Brick property values (Bliss API).

        Args:
            property_name: Name of the property to be changed
            old_value: old property value
            new_value: new_property value

        Returns: None

        """
        if property_name == "label":
            if new_value == "" and self.zoom_hwobj is not None:
                self.label.setText("<i>" + self.zoom_hwobj.username + ":</i>")
            else:
                self.label.setText(new_value)

        elif property_name == "mnemonic":
            if self.zoom_hwobj is not None:
                self.disconnect(
                    self.zoom_hwobj, "stateChanged", self.motor_state_changed
                )
                self.disconnect(
                    self.zoom_hwobj, "newPredefinedPositions", self.fill_positions
                )
                self.disconnect(
                    self.zoom_hwobj,
                    "predefinedPositionChanged",
                    self.predefined_position_changed,
                )

            self.zoom_hwobj = self.getHardwareObject(new_value)

            if self.zoom_hwobj is not None:
                self.connect(
                    self.zoom_hwobj, "newPredefinedPositions", self.fill_positions
                )
                self.connect(self.zoom_hwobj, "stateChanged", self.motor_state_changed)
                self.connect(
                    self.zoom_hwobj,
                    "predefinedPositionChanged",
                    self.predefined_position_changed,
                )
                self.fill_positions()
                self._init_state_colors()

                if self.zoom_hwobj.is_ready():
                    self.predefined_position_changed(
                        self.zoom_hwobj.getCurrentPositionName()
                    )

                if self["label"] == "":
                    lbl = self.zoom_hwobj.username
                    self.label.setText("<i>" + lbl + ":</i>")

                Qt4_widget_colors.set_widget_color(
                    self.positions_combo, Qt4_widget_colors.DARK_GRAY, QPalette.Button
                )
                self.motor_state_changed(self.zoom_hwobj.getState())

        elif property_name == "showMoveButtons":
            if new_value:
                self.previous_position_button.show()
                self.next_position_button.show()
            else:
                self.previous_position_button.hide()
                self.next_position_button.hide()

        elif property_name == "icons":
            icons = new_value.split()
            if icons:
                try:
                    self.previous_position_button.setIcon(Qt4_Icons.load_icon(icons[0]))
                    self.next_position_button.setIcon(Qt4_Icons.load_icon(icons[1]))
                except Exception as e:
                    msg = "Cannot set icons {} for {}\n{}".format(
                        icons, self.objectName(), e
                    )
                    logging.getLogger().warning(msg)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def fill_positions(self, positions=None):
        """
        Update combo box with positions list from the hardware object.
        Args:
            positions: list of strings

        Returns: None

        """
        self.positions_combo.clear()
        if self.zoom_hwobj is not None:
            if positions is None:
                positions = self.zoom_hwobj.getPredefinedPositionsList()
        if positions is None:
            positions = []
        for p in positions:
            self.positions_combo.addItem(str(p))
        self.positions = positions
        if self.zoom_hwobj is not None:
            if self.zoom_hwobj.is_ready():
                self.predefined_position_changed(
                    self.zoom_hwobj.getCurrentPositionName()
                )

    def position_selected(self, index):
        """
        Slot for setting the position selected in the combo box.

        Args:
            index: Index for the combo box position list.

        Returns: None

        """
        if index >= 0:
            if self.zoom_hwobj.is_ready():
                self.zoom_hwobj.moveToPosition(self.positions[index])
            else:
                self.positions_combo.setCurrentIndex(0)
        self.next_position_button.setEnabled(index < (len(self.positions) - 1))
        self.previous_position_button.setEnabled(index >= 0)

    def predefined_position_changed(self, position_name):
        """
        Slot for update the current position list.
        Args:
            position_name:

        Returns: None

        """
        if self.positions:
            index = 0
            for index in range(len(self.positions)):
                if str(self.positions[index]) == position_name:
                    break

            self.positions_combo.setCurrentIndex(index)
            self.next_position_button.setEnabled(index < (len(self.positions) - 1))
            self.previous_position_button.setEnabled(index > 0)

    def select_previous_position(self):
        """
        Selects previous position.

        Returns: None

        """
        self.position_selected(self.positions_combo.currentIndex() - 1)

    def select_next_position(self):
        """
        Selects next position.

        Returns: None

        """
        self.position_selected(self.positions_combo.currentIndex() + 1)
