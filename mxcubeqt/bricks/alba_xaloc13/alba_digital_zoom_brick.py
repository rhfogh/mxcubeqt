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

from mxcubeqt.utils import icons, colors, qt_import
from mxcubeqt.base_components import BaseWidget

__credits__ = ["ALBA"]
__licence__ = "LGPLv3+"
__version__ = "3"
__category__ = "General"


class AlbaDigitalZoomBrick(BaseWidget):

    STATE_COLORS = {}

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.zoom_hwobj = None

        # Internal values -----------------------------------------------------
        self.positions = None

        # Properties ----------------------------------------------------------
        self.add_property("label", "string", "")
        self.add_property("mnemonic", "string", "")
        self.add_property("icons", "string", "")
        self.add_property("showMoveButtons", "boolean", True)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("setEnabled", ())

        # Graphic elements ----------------------------------------------------
        _main_gbox = qt_import.QGroupBox(self)
        self.label = qt_import.QLabel("zoom", _main_gbox)
        self.positions_combo = qt_import.QComboBox(self)
        self.previous_position_button = qt_import.QPushButton(_main_gbox)
        self.next_position_button = qt_import.QPushButton(_main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_hlayout = qt_import.QHBoxLayout(_main_gbox)
        _main_gbox_hlayout.addWidget(self.label)
        _main_gbox_hlayout.addWidget(self.positions_combo)
        _main_gbox_hlayout.addWidget(self.previous_position_button)
        _main_gbox_hlayout.addWidget(self.next_position_button)
        _main_gbox_hlayout.setSpacing(2)
        _main_gbox_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = qt_import.QHBoxLayout(self)
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
        self.previous_position_button.setIcon(icons.load_icon("Minus2"))
        self.previous_position_button.setFixedSize(27, 27)
        self.next_position_button.setIcon(icons.load_icon("Plus2"))
        self.next_position_button.setFixedSize(27, 27)

    def _init_state_colors(self):
        """
        Map state to widget colors.

        Returns: None

        """
        # TODO: it there a generic method for this?
        # This mapping should be universal for all widgets --> unique set of states
        state = self.zoom_hwobj.STATE
        self.STATE_COLORS[state.UNKNOWN] = colors.DARK_GRAY
        self.STATE_COLORS[state.READY] = colors.LIGHT_GREEN
        self.STATE_COLORS[state.LOW_LIMIT] = colors.LIGHT_GREEN
        self.STATE_COLORS[state.HIGH_LIMIT] = colors.LIGHT_GREEN
        self.STATE_COLORS[state.DISABLED] = colors.DARK_GRAY
        self.STATE_COLORS[state.FAULT] = colors.LIGHT_RED

    def set_tool_tip(self, name=None, state=None):
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
                state = self.zoom_hwobj.get_state()
            try:
                state_str = state.name
            except IndexError:
                state_str = "UNKNOWN"
            tip = "State: " + state_str

        self.label.setToolTip(tip)

    def motor_state_changed(self, state):
        """
        Update combo box color according to zoom state

        Args:
            state: New zoom tango state.

        Returns: None

        """
        # TODO: state is a Tango state, but we need a DigitalZoomState instead.
        state = self.zoom_hwobj.get_state()

        found = state in list(self.zoom_hwobj.STATE)

        self.positions_combo.setEnabled(found)
        colors.set_widget_color(
            self.positions_combo, self.STATE_COLORS[state], qt_import.QPalette.Button
        )
        self.set_tool_tip(state=state)

    def property_changed(self, property_name, old_value, new_value):
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
                self.label.setText(self.zoom_hwobj.username)
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

            self.zoom_hwobj = self.get_hardware_object(new_value)

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
                        self.zoom_hwobj.get_current_position_name()
                    )

                if self["label"] == "":
                    lbl = self.zoom_hwobj.username
                    self.label.setText(lbl)

                colors.set_widget_color(
                    self.positions_combo, 
                    colors.DARK_GRAY, 
                    qt_import.QPalette.Button
                )
                self.motor_state_changed( self.zoom_hwobj.get_state() )

        elif property_name == "showMoveButtons":
            if new_value:
                self.previous_position_button.show()
                self.next_position_button.show()
            else:
                self.previous_position_button.hide()
                self.next_position_button.hide()

        elif property_name == "icons":
            icon_list = new_value.split()
            if icon_list:
                try:
                    self.previous_position_button.setIcon(icons.load_icon(icon_list[0]))
                    self.next_position_button.setIcon(icons.load_icon(icon_list[1]))
                except Exception as e:
                    msg = "Cannot set icons {} for {}\n{}".format(
                        icon_list, self.objectName(), e
                    )
                    logging.getLogger().warning(msg)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

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
                positions = self.zoom_hwobj.get_predefined_positions_list()
        if positions is None:
            positions = []
        for p in positions:
            self.positions_combo.addItem(str(p))
        self.positions = positions
        if self.zoom_hwobj is not None:
            if self.zoom_hwobj.is_ready():
                self.predefined_position_changed(
                    self.zoom_hwobj.get_current_position_name()
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
                self.zoom_hwobj.move_to_position(self.positions[index])
            else:
                self.positions_combo.setCurrentIndex(0)
        self.next_position_button.setEnabled(index < (len(self.positions) - 1))
        self.previous_position_button.setEnabled(index >= 0)

    def predefined_position_changed(self, position_name, offset=0):
        """
        Slot for update the current position list.
        Args:
            position_name:

        Returns: None

        """
        if self.positions:
            index = 0
            for index in range( len( self.positions ) ):
                if str(self.positions[index]) == position_name[0]:
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
