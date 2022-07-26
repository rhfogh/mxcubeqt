#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging

from mxcubeqt.utils import colors, icons, qt_import
from mxcubeqt.base_components import BaseWidget
from mxcubecore import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ALBA"


#
# These state list is as in ALBAEpsActuator.py
#
STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)

STATES = {
    STATE_IN: colors.LIGHT_GREEN,
    STATE_OUT: colors.LIGHT_GRAY,
    STATE_MOVING: colors.LIGHT_YELLOW,
    STATE_FAULT: colors.LIGHT_RED,
    STATE_ALARM: colors.LIGHT_RED,
    STATE_UNKNOWN: colors.LIGHT_GRAY,
}


class AlbaLightControlBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)
        self.logger = logging.getLogger("HWR")
        #self.logger.info("__init__()")

        self.on_color = colors.color_to_hexa(colors.LIGHT_GREEN)
        self.off_color = colors.color_to_hexa(colors.LIGHT_GRAY)
        self.fault_color = colors.color_to_hexa(colors.LIGHT_RED)
        self.unknown_color = colors.color_to_hexa(colors.DARK_GRAY)

        # Hardware objects ----------------------------------------------------
        self.light_ho = None

        self.state = None # True = "on", False = "off"
        self.level = None
        self.icon_list = None
        self.level_limits = [None, None]

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("icon_list", "string", "")

        # Graphic elements ----------------------------------------------------
        self.widget = qt_import.load_ui_file("alba_lightcontrol.ui")
        self.widget.slider.setSingleStep(5)

        qt_import.QHBoxLayout(self)

        self.layout().addWidget(self.widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.widget.button.clicked.connect(self.do_switch)
        self.widget.slider.valueChanged.connect(self.do_set_level)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.MinimumExpanding
        )

        # Slots --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        if HWR.beamline.machine_info is not None:
            self.connect(
                HWR.beamline.sample_changer, "path_safeChanged", self.enable_backlight_widget_toggle
            )
        if HWR.beamline.collect is not None:
            self.connect(
                HWR.beamline.collect, "collectStarted", self.collect_started
            )
            self.connect(
                HWR.beamline.collect, "collectOscillationFinished", self.collect_finished
            )
            self.connect(
                HWR.beamline.collect, "collectOscillationFailed", self.collect_failed
            )

        # Defaults
        self.set_icons("BulbCheck,BulbDelete")

        # Other ---------------------------------------------------------------
        self.setToolTip("Control of light (set level and on/off switch.")

    def property_changed(self, property_name, old_value, new_value):
        #self.logger.info("New property %s, new_value: %s" % (property_name, str(new_value) ) )
        if property_name == "mnemonic":
            if self.light_ho is not None:
                self.disconnect(
                    self.light_ho, qt_import.SIGNAL("levelChanged"), self.level_changed
                )
                self.disconnect(
                    self.light_ho, qt_import.SIGNAL("stateChanged"), self.state_changed
                )

            self.light_ho = self.get_hardware_object(new_value)

            if self.light_ho is not None:
                self.setEnabled(True)
                self.connect(
                    self.light_ho, qt_import.SIGNAL("levelChanged"), self.level_changed
                )
                self.connect(
                    self.light_ho, qt_import.SIGNAL("stateChanged"), self.state_changed
                )
                self.light_ho.re_emit_values()
                self.setToolTip(
                    "Control of %s (light level and on/off switch."
                    % self.light_ho.get_user_name()
                )
                self.set_level_limits( self.light_ho.get_limits() )
                self.set_label( self.light_ho.get_user_name() )
            else:
                logging.getLogger.debug("Can't load alba light control widget")
                self.setEnabled(False)
        elif property_name == "icon_list":
            self.set_icons(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def update(self, state=None):
        if self.light_ho is not None:
            self.setEnabled(True)
            if self.state:
                color = self.off_color
                self.widget.slider.setEnabled(True)
                if self.icon_list:
                    self.widget.button.setIcon(self.icon_list["off"])
                    self.widget.button.setToolTip("Set light Off")
            else:
                color = self.on_color
                self.widget.slider.setEnabled(True)
                if self.icon_list:
                    self.widget.button.setIcon(self.icon_list["on"])
                    self.widget.button.setToolTip("Set light On")
            #else:
                #color = self.fault_color
                #self.setEnabled(False)

            if self.level is not None and None not in self.level_limits:
                self.widget.slider.blockSignals(True)
                self.widget.slider.setValue(self.level)
                self.widget.slider.blockSignals(False)
                self.widget.slider.setToolTip("Light Level: %s" % self.level)
        else:
            self.setEnabled(False)
            color = self.unknown_color

        self.widget.button.setStyleSheet("background-color: %s;" % color)

    def enable_backlight_widget_toggle(self, value):
        if self.light_ho.name() == 'backlight': 
            if value: self.setEnabled(True)
            else: self.setEnabled(False)

    def enable_backlight_widget(self):
        if self.light_ho.name() == 'backlight': 
            self.setEnabled(True)

    def disable_backlight_widget(self):
        if self.light_ho.name() == 'backlight': 
            self.setEnabled(False)

    def set_icons(self, icon_string):
        icon_list = icon_string.split(",")
        if len(icon_list) == 2:
            self.icon_list = {
                "on": icons.load_icon(icon_list[0]),
                "off": icons.load_icon(icon_list[1]),
            }
            self.widget.button.setIcon(self.icon_list["on"])

    def level_changed(self, level):
        self.level = level
        self.update()

    def state_changed(self, state):
        self.state = state
        self.update()

    def set_label(self, text):
        self.widget.label.setText(text)

    def set_level_limits(self, limits):
        self.level_limits = limits
        if None not in self.level_limits:
            self.widget.slider.setMinimum(self.level_limits[0])
            self.widget.slider.setMaximum(self.level_limits[1])

    def do_set_level(self):  # when slider is moved
        newvalue = self.widget.slider.value()
        self.light_ho.set_level(newvalue)

    def do_switch(self):
        #self.logger.info("self.state = %s" % self.state )
        if self.state:
            self.light_ho.set_off()
        else:
            self.logger.info("Setting light on" )
            self.light_ho.set_on()

    def collect_started(self, owner, num_oscillations):
        self.disable_backlight_widget()

    def collect_finished(self, owner, state, message, *args):
        self.enable_backlight_widget()
        
    def collect_failed(self, owner, state, message, *args):
        self.enable_backlight_widget()
 
