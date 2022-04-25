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

from mxcubeqt.utils import colors
from mxcubeqt.bricks.resolution_brick import ResolutionBrick

from mxcubecore import HardwareRepository as HWR


__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"


class AlbaResolutionBrick(ResolutionBrick):

    def __init__(self, *args):

        ResolutionBrick.__init__(self, *args)

    def resolution_state_changed(self, state):
        detector_distance = HWR.beamline.detector.distance
        if detector_distance is not None:
            if state:
                color = ResolutionBrick.STATE_COLORS[state.value[1]]
            else:
                color = colors.LIGHT_RED

            unit = self.units_combobox.currentText()
            if unit is chr(197):
                if state == detector_distance.STATES.READY:
                    self.new_value_ledit.blockSignals(True)
                    self.new_value_ledit.setText("")
                    self.new_value_ledit.blockSignals(False)
                    self.new_value_ledit.setEnabled(True)
                else:
                    self.new_value_ledit.setEnabled(False)
                # or state == detector_distance.motor_states.MOVESTARTED:
                if state == detector_distance.STATES.BUSY:
                    self.stop_button.setEnabled(True)
                else:
                    self.stop_button.setEnabled(False)

                colors.set_widget_color(self.new_value_ledit, color)
                
    def detector_distance_state_changed(self, state):
        if state is None:
            return

        detector_distance = HWR.beamline.detector.distance
        color = ResolutionBrick.STATE_COLORS[state.value[1]]
        unit = self.units_combobox.currentText()

        if state == detector_distance.STATES.FAULT:
            self.setEnabled(False)
            return

        if unit == "mm":
            if state == detector_distance.STATES.READY:
                self.new_value_ledit.blockSignals(True)
                self.new_value_ledit.setText("")
                self.new_value_ledit.blockSignals(False)
                self.new_value_ledit.setEnabled(True)
            else:
                self.new_value_ledit.setEnabled(False)
            if state == detector_distance.STATES.BUSY:
                # or \
                # state == detector_distance.motor_states.MOVESTARTED:
                self.stop_button.setEnabled(True)
            else:
                self.stop_button.setEnabled(False)

            colors.set_widget_color(self.new_value_ledit, color)
                
