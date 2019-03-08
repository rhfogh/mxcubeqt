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
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'ALBA'

# 
# These state list is as in ALBAEpsActuator.py
# 
STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = \
         (0,1,9,11,13,23)

STATES = {STATE_IN: Qt4_widget_colors.LIGHT_GREEN,
          STATE_OUT: Qt4_widget_colors.LIGHT_GRAY,
          STATE_MOVING: Qt4_widget_colors.LIGHT_YELLOW,
          STATE_FAULT: Qt4_widget_colors.LIGHT_RED,
          STATE_ALARM: Qt4_widget_colors.LIGHT_RED,
          STATE_UNKNOWN: Qt4_widget_colors.LIGHT_GRAY}

class Qt4_ALBA_LightControlBrick(BlissWidget):
    """
    Descript. :
    """
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)
        self.logger = logging.getLogger("GUI Alba Actuator")
        self.logger.info("__init__()")

        self.on_color = Qt4_widget_colors.color_to_hexa(Qt4_widget_colors.LIGHT_GREEN)
        self.off_color = Qt4_widget_colors.color_to_hexa(Qt4_widget_colors.LIGHT_GRAY)
        self.fault_color = Qt4_widget_colors.color_to_hexa(Qt4_widget_colors.LIGHT_RED)
        self.unknown_color = Qt4_widget_colors.color_to_hexa(Qt4_widget_colors.DARK_GRAY)

        # Hardware objects ----------------------------------------------------
        self.light_ho = None

        self.state = None
        self.level = None
        self.icons = None
        self.level_limits = [None, None]

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', 'BulbDelete,BulbCheck')

        # Graphic elements ----------------------------------------------------
        self.widget = loadUi(os.path.join(os.path.dirname(__file__),
             'widgets/ui_files/alba_lightcontrol.ui'))

        QHBoxLayout(self)
  
        self.layout().addWidget(self.widget)
        self.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.horizontalLayout.setContentsMargins(0,0,0,0)

        self.widget.button.clicked.connect(self.do_switch)
        self.widget.slider.valueChanged.connect(self.do_set_level)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        # Defaults 
        self.set_icons('BulbDelete,BulbCheck')

        # Other --------------------------------------------------------------- 
        self.setToolTip("Control of light (set level and on/off switch.")

        #self.update()

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == 'mnemonic':
            if self.light_ho is not None:
                self.disconnect(self.light_ho, 'levelChanged', self.level_changed)
                self.disconnect(self.light_ho, 'stateChanged', self.state_changed)

            self.light_ho = self.getHardwareObject(new_value)

            if self.light_ho is not None:
                self.setEnabled(True)
                self.connect(self.light_ho, 'levelChanged', self.level_changed)
                self.connect(self.light_ho, 'stateChanged', self.state_changed)
                self.light_ho.update_values()
                self.setToolTip("Control of %s (light level and on/off switch." % self.light_ho.getUserName())
                self.set_level_limits(self.light_ho.getLimits())
                self.set_label(self.light_ho.getUserName())
            else:
                self.setEnabled(False)
        elif property_name == 'icons':
            self.set_icons(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def update(self, state=None):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        logging.getLogger("HWR").debug(" updating light control. state is %s" % self.state)
        if self.light_ho is not None:
            self.set_enabled()
            if self.state is "on":
                self.widget.slider.setEnabled(True)
                if self.icons:
                    self.widget.button.setIcon(self.icons["on"])
                    self.widget.button.setToolTip("Set light Off")
            elif self.state is "off":
                self.widget.slider.setEnabled(False)
                if self.icons:
                    self.widget.button.setIcon(self.icons["off"])
                    self.widget.button.setToolTip("Set light On")
            else:
                self.set_disabled()

            if self.level is not None and None not in self.level_limits:
                self.widget.slider.blockSignals(True)
                self.widget.slider.setValue(self.level) 
                self.widget.slider.blockSignals(False)
                self.widget.slider.setToolTip("Light Level: %s" % self.level) 
        #else:
        #    self.set_disabled()

    def set_disabled(self):
        if self.light_ho is not None:
            logging.getLogger("HWR").debug(" setting %s light_disabled" % self.light_ho.getUserName())
        else:
            logging.getLogger("HWR").debug(" setting light_disabled coz no hwo " )
        self.setEnabled(False)
        color = self.unknown_color
        self.widget.button.setStyleSheet("background-color: %s;" % color)

    def set_enabled(self):
        logging.getLogger("HWR").debug(" setting %s light_enabled" % self.light_ho.getUserName())
        self.setEnabled(True)
        self.widget.button.setEnabled(True)
        self.widget.slider.setEnabled(True)
        color = self.on_color
        self.widget.button.setStyleSheet("background-color: %s;" % color)

    def set_icons(self, icons):
        icons = [icon.strip() for icon in icons.split(",")]
        if len(icons) == 2:
            self.icons = {'on': Qt4_Icons.load_icon(icons[0]), 
                          'off': Qt4_Icons.load_icon(icons[1])} 
            self.widget.button.setIcon(self.icons["on"])

    def level_changed(self, level):
        self.level = level
        self.update()

    def state_changed(self, state):
        logging.getLogger("HWR").debug(" state changed for light control. state is %s" % self.state)
        self.state = state
        self.update()
  
    def set_label(self, text):
        self.widget.label.setText(text)

    def set_level_limits(self, limits):
        self.level_limits = limits
        if None not in self.level_limits:
           self.widget.slider.setMinimum(self.level_limits[0])
           self.widget.slider.setMaximum(self.level_limits[1])

    def do_set_level(self): # when slider is moved
        newvalue = self.widget.slider.value()
        self.light_ho.setLevel(newvalue)

    def do_switch(self):
        if self.state == "on":
            self.light_ho.setOff()
        elif self.state == "off":
            self.light_ho.setOn()
        else:
            pass

