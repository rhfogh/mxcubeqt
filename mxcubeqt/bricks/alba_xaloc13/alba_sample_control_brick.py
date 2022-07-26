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

from mxcubeqt.bricks.sample_control_brick import (
    SampleControlBrick, MonoStateButton, DuoStateButton, 
    create_line_clicked, draw_grid_clicked, auto_focus_clicked,
    refresh_camera_clicked, visual_align_clicked, select_all_clicked, 
    clear_all_clicked, auto_center_clicked
)
from mxcubecore import HardwareRepository as HWR

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import qt_import

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"

class AlbaSampleControlBrick(SampleControlBrick):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.inside_data_collection = None
        self.prefix = "snapshot"
        self.file_index = 1

        # Properties ----------------------------------------------------------
        self.add_property("enableAutoFocus", "boolean", True)
        self.add_property("enableRefreshCamera", "boolean", False)
        self.add_property("enableVisualAlign", "boolean", True)
        self.add_property("enableAutoCenter", "boolean", True)
        self.add_property("enableRealignBeam", "boolean", False)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.centre_button = DuoStateButton(self, "Centre")
        self.centre_button.set_icons("VCRPlay2", "Delete")
        self.accept_button = MonoStateButton(self, "Save", "ThumbUp")
        self.standard_color = self.accept_button.palette().color(
            qt_import.QPalette.Window
        )
        self.reject_button = MonoStateButton(self, "Reject", "ThumbDown")
        self.reject_button.hide()
        self.create_line_button = MonoStateButton(self, "Line", "Line")
        self.draw_grid_button = MonoStateButton(self, "Grid", "Grid")
        self.auto_focus_button = MonoStateButton(self, "Focus", "Eyeball")
        self.snapshot_button = MonoStateButton(self, "Snapshot", "Camera")
        self.refresh_camera_button = MonoStateButton(self, "Refresh", "Refresh")
        self.visual_align_button = MonoStateButton(self, "Align", "Align")
        self.select_all_button = MonoStateButton(self, "Select all", "Check")
        self.clear_all_button = MonoStateButton(self, "Clear all", "Delete")
        self.auto_center_button = DuoStateButton(self, "Auto")
        self.auto_center_button.set_icons("VCRPlay2", "Delete")        
        self.auto_center_button.setText("Auto")
        self.realign_button = MonoStateButton(self, "Realign beam", "QuickRealign")
        # ALBA specific
        self.beam_align_mode_button = DuoStateButton(self, "BeamView")
        self.beam_align_mode_button.set_icons("BeamAlign", "Delete")

        
        # Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.centre_button)
        _main_vlayout.addWidget(self.auto_center_button)
        _main_vlayout.addWidget(self.accept_button)
        _main_vlayout.addWidget(self.reject_button)
        _main_vlayout.addWidget(self.create_line_button)
        _main_vlayout.addWidget(self.draw_grid_button)
        _main_vlayout.addWidget(self.auto_focus_button)
        _main_vlayout.addWidget(self.snapshot_button)
        # ALBA specific
        _main_vlayout.addWidget(self.beam_align_mode_button)
        _main_vlayout.addWidget(self.refresh_camera_button)
        _main_vlayout.addWidget(self.visual_align_button)
        _main_vlayout.addWidget(self.select_all_button)
        _main_vlayout.addWidget(self.clear_all_button)
        _main_vlayout.addWidget(self.realign_button)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.centre_button.commandExecuteSignal.connect(self.centre_button_clicked)
        self.accept_button.clicked.connect(self.accept_clicked)
        self.reject_button.clicked.connect(self.reject_clicked)
        self.create_line_button.clicked.connect(create_line_clicked)
        self.draw_grid_button.clicked.connect(draw_grid_clicked)
        self.auto_focus_button.clicked.connect(auto_focus_clicked)
        self.snapshot_button.clicked.connect(self.save_snapshot_clicked)
        self.refresh_camera_button.clicked.connect(refresh_camera_clicked)
        self.visual_align_button.clicked.connect(visual_align_clicked)
        self.select_all_button.clicked.connect(select_all_clicked)
        self.clear_all_button.clicked.connect(clear_all_clicked)
        # ALBA specific
        self.auto_center_button.commandExecuteSignal.connect(self.auto_center_duo_clicked)
        self.beam_align_mode_button.commandExecuteSignal.connect(self.beam_align_mode_clicked)

        # Other ---------------------------------------------------------------
        self.centre_button.setToolTip("3 click centring")
        self.accept_button.setToolTip(
            "Accept 3 click centring or "
            "create a point\nbased on current position"
        )
        self.reject_button.setToolTip("Reject centring")
        self.create_line_button.setToolTip(
            "Create helical line between two points"
        )
        self.draw_grid_button.setToolTip("Create grid with drag and drop")
        self.select_all_button.setToolTip("Select all centring points")
        self.clear_all_button.setToolTip("Clear all items")
        # self.instanceSynchronize("")

        #TODO: check why the diffractometer signals are not used, and if the QtGraphicsManager signals are connected well
        self.connect(HWR.beamline.sample_view, "centringStarted", self.centring_started)
        self.connect(HWR.beamline.sample_view, "centringFailed", self.centring_failed)
        self.connect(
            HWR.beamline.sample_view, "centringSuccessful", self.centring_successful
        )
        self.connect(
            HWR.beamline.sample_view,
            "diffractometerPhaseChanged",
            self.diffractometer_phase_changed,
        )

    def beam_align_mode_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        mode =  HWR.beamline.sample_view.camera_hwobj.align_mode
        if mode:
            HWR.beamline.sample_view.camera.align_mode = False
        else:
            HWR.beamline.sample_view.camera.align_mode = True

    def centre_button_clicked(self, state):
        if state:
            HWR.beamline.sample_changer.sample_can_be_centered = True
            HWR.beamline.sample_view.start_centring(tree_click=True)
            self.auto_center_button.command_started()
        else:
            HWR.beamline.sample_view.cancel_centring(reject=False)
            self.auto_center_button.command_failed()
            self.accept_button.setEnabled(True)

    def auto_center_duo_clicked(self, state):
        logging.getLogger("HWR").debug('auto_center_duo_clicked')
        if state:
            HWR.beamline.sample_changer.sample_can_be_centered = True
            HWR.beamline.sample_view.start_auto_centring()
            self.auto_center_button.command_started()
        else:
            HWR.beamline.sample_view.cancel_centring(reject=False)
            self.auto_center_button.command_failed()
            self.accept_button.setEnabled(True)

    def centring_started(self):
        self.setEnabled(True)
        self.centre_button.command_started()
        self.auto_center_button.command_started()
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(True)

    def centring_successful(self, method, centring_status):
        self.centre_button.command_done()
        self.auto_center_button.command_done()
        self.accept_button.setEnabled(True)
        self.reject_button.setEnabled(True)
        if self.inside_data_collection:
            colors.set_widget_color(self.accept_button, colors.LIGHT_GREEN)
            colors.set_widget_color(self.reject_button, colors.LIGHT_RED)

        self.setEnabled(True)

    def centring_failed(self, method, centring_status):
        self.centre_button.command_failed()
        self.auto_center_button.command_failed()
        self.accept_button.setEnabled(True)
        if self.inside_data_collection:
            colors.set_widget_color(self.accept_button, self.standard_color)
            self.reject_button.setEnabled(True)
            colors.set_widget_color(self.reject_button, qt_import.Qt.red)
        else:
            self.reject_button.setEnabled(False)
