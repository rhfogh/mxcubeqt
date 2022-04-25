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

from mxcubeqt.bricks.cats_maint_brick import CatsMaintBrick
from mxcubeqt.utils import sample_changer_helper

import logging

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"

class AlbaCatsMaintBrick(CatsMaintBrick):
    def __init__(self, *args):
        CatsMaintBrick.__init__(self, *args)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.device is not None:
                self.disconnect(self.device, "lid1StateChanged", self.update_lid1_state)
                self.disconnect(self.device, "lid2StateChanged", self.update_lid2_state)
                self.disconnect(self.device, "lid3StateChanged", self.update_lid3_state)
                self.disconnect(
                    self.device, "runningStateChanged", self.update_path_running
                )
                self.disconnect(self.device, "powerStateChanged", self.update_powered)
                self.disconnect(self.device, "messageChanged", self.update_message)
                self.disconnect(
                    self.device, "regulationStateChanged", self.update_regulation
                )
                self.disconnect(self.device, "barcodeChanged", self.update_barcode)
                self.disconnect(self.device, "toolStateChanged", self.update_tool_state)
                self.disconnect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATUS_CHANGED_EVENT,
                    self.update_status,
                )
                self.disconnect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATE_CHANGED_EVENT,
                    self.update_state,
                )

            # load the new hardware object
            self.device = self.get_hardware_object(new_value)
            if self.device is not None:
                self.connect(self.device, "lid1StateChanged", self.update_lid1_state)
                self.connect(self.device, "lid2StateChanged", self.update_lid2_state)
                self.connect(self.device, "lid3StateChanged", self.update_lid3_state)
                self.connect(
                    self.device, "runningStateChanged", self.update_path_running
                )
                self.connect(self.device, "powerStateChanged", self.update_powered)
                self.connect(self.device, "messageChanged", self.update_message)
                self.connect(
                    self.device, "regulationStateChanged", self.update_regulation
                )
                self.connect(self.device, "barcodeChanged", self.update_barcode)
                self.connect(self.device, "toolStateChanged", self.update_tool_state)
                self.connect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATUS_CHANGED_EVENT,
                    self.update_status,
                )
                self.connect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATE_CHANGED_EVENT,
                    self.update_state,
                )
                self.device.re_emit_signals()

                
    def regulation_set_on(self):
        try:
            if self.device is not None:
                self.device._do_enable_regulation()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def regulation_set_off(self):
        try:
            if self.device is not None:
                self.device._do_disable_regulation()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def power_on(self):
        try:
            if self.device is not None:
                self.device._do_power_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def power_off(self):
        try:
            if self.device is not None:
                self.device._do_power_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid1_open(self):
        try:
            if self.device is not None:
                self.device._do_lid1_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid1_close(self):
        try:
            if self.device is not None:
                self.device._do_lid1_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid2_open(self):
        try:
            if self.device is not None:
                self.device._do_lid2_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid2_close(self):
        try:
            if self.device is not None:
                self.device._do_lid2_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid3_open(self):
        try:
            if self.device is not None:
                self.device._doL_lid3_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid3_close(self):
        try:
            if self.device is not None:
                self.device._do_lid3_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def tool_open(self):
        try:
            if self.device is not None:
                self.device._do_tool_open()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def tool_close(self):
        try:
            if self.device is not None:
                self.device._do_tool_close()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def tool_calibrate(self):
        try:
            if self.device is not None:
                self.device._do_calibration()  # adds a parameter 2 (for tool) in device
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def magnet_on(self):
        try:
            if self.device is not None:
                self.device._do_magnet_on()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def magnet_off(self):
        try:
            if self.device is not None:
                self.device._do_magnet_off()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def resetError(self):
        try:
            if self.device is not None:
                self.device._do_reset()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def home(self):
        try:
            if self.device is not None:
                self.device._do_home()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def dry(self):
        try:
            if self.device is not None:
                self.device._do_dry_gripper()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def soak(self):
        try:
            if self.device is not None:
                self.device._do_soak()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def back_traj(self):
        try:
            if self.device is not None:
                # self.device._doBack()
                self.device.back_traj()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def safe_traj(self):
        try:
            if self.device is not None:
                # self.device._doSafe()
                self.device.safe_traj()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def abort(self):
        try:
            if self.device is not None:
                self.device._do_abort()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def panic(self):
        try:
            if self.device is not None:
                self.device._do_panic()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def restart(self):
        try:
            if self.device is not None:
                self.device._doRestart()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def reset_motion(self):
        try:
            if self.device is not None:
                self.device._do_reset_motion()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def reset_put_get(self):
        try:
            if self.device is not None:
                self.device._do_recover_failure()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def clear(self):
        try:
            if self.device is not None:
                self.device._do_reset()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def clear_memory(self):
        try:
            if self.device is not None:
                self.device._do_reset_memory()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))
