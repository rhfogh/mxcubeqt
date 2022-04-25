# encoding: utf-8
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

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.bricks.motor_spinbox_brick import MotorSpinboxBrick
from mxcubecore.HardwareObjects.abstract.AbstractMotor import MotorStates
from mxcubecore.BaseHardwareObjects import HardwareObjectState

import logging

__credits__ = ["ALBA Synchrotron"]
__version__ = "3"
__category__ = "General"

class AlbaMotorSpinboxBrick(MotorSpinboxBrick):
    
    STATE_COLORS = (colors.LIGHT_YELLOW,  # INITIALIZING
                    colors.LIGHT_GREEN,   # ON
                    colors.DARK_GRAY,     # OFF
                    colors.LIGHT_GREEN,   # READY
                    colors.LIGHT_YELLOW,  # MOVING
                    colors.LIGHT_YELLOW,  # BUSY
                    colors.LIGHT_YELLOW,  # MOVING
                    colors.LIGHT_GREEN,   # STANDBY
                    colors.DARK_GRAY,     # DISABLED
                    colors.DARK_GRAY,     # UNKNOWN
                    colors.LIGHT_RED,     # ALARM
                    colors.LIGHT_RED,     # FAULT
                    colors.LIGHT_RED,     # INVALID
                    colors.DARK_GRAY,     # OFFLINE
                    colors.LIGHT_RED,     # LOWLIMIT
                    colors.LIGHT_RED,     # HIGHLIMIT
                    colors.DARK_GRAY)     # NOTINITIALIZED

    def __init__(self, *args):
        MotorSpinboxBrick.__init__(self, *args)

    def set_position_spinbox_color(self, state):
        """Changes color of the spinbox based on the state"""
        #logging.getLogger("HWR").debug("set_position_spinbox_color state %s, value %d" % ( str(state) , state.value[1] ) )
        color = AlbaMotorSpinboxBrick.STATE_COLORS[state.value[1]]
        colors.set_widget_color(
            self.position_spinbox.lineEdit(), color, qt_import.QPalette.Base
        )

