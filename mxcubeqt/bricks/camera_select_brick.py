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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, qt_import

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class CameraSelectBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("confirmCameraChange", "boolean", False)

        # Properties to initialize hardware objects --------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = qt_import.QGroupBox(self)
        self.select_combobox = qt_import.QComboBox(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_vlayout = qt_import.QVBoxLayout(self.group_box)
        _group_box_vlayout.addWidget(self.select_combobox)
        _group_box_vlayout.addStretch()
        _group_box_vlayout.setSpacing(0)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setAlignment(qt_import.Qt.AlignBottom)
        
        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.select_combobox.activated.connect(self.change_camera)

        # Other ---------------------------------------------------------------
        colors.set_widget_color(
            self.select_combobox, colors.LIGHT_GREEN, qt_import.QPalette.Button
        )

        self.init_camera_list()

        self.connect(
            HWR.beamline.diffractometer, "minidiffPhaseChanged", self.camera_changed
        )

    def init_camera_list(self):
        self.select_combobox.clear()
        camera_list = HWR.beamline.diffractometer.get_camera_list()
        
        if len(camera_list) > 0:
            for phase in camera_list:
                self.select_combobox.addItem(phase)
            self.setEnabled(True)
            self.select_combobox.setCurrentIndex(self.select_combobox.findText(HWR.beamline.diffractometer.get_current_camera()))
        else:
            self.setEnabled(False)
        
    def change_camera(self):
        if HWR.beamline.diffractometer is not None:
            requested_camera = self.select_combobox.currentText()
            HWR.beamline.diffractometer.set_current_camera(requested_camera)

    def camera_changed(self, phase):
        if phase.lower() != "unknown" and self.select_combobox.count() > 0:
            # index = self.select_combobox.findText(phase)
            # self.select_combobox.setEditText(phase)
            self.select_combobox.setCurrentIndex(self.select_combobox.findText(phase))
        else:
            self.select_combobox.setCurrentIndex(-1)
