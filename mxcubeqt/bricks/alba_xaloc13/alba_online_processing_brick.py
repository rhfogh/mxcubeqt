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


import logging

from mxcubeqt.base_components import BaseWidget 
from mxcubeqt.utils import qt_import
from mxcubeqt.widgets.hit_map_widget import HitMapWidget
from mxcubeqt.bricks.online_processing_brick import OnlineProcessingBrick

from mxcubecore import HardwareRepository as HWR

__credits__ = ["ALBA Synchrotron"]
__version__ = "3"
__category__ = "General"

class AlbaOnlineProcessingBrick(OnlineProcessingBrick):
    def __init__(self, *args):
        self.logger = logging.getLogger("GUI")
        self.logger.info("AlbaOnlineProcessingBrick.__init__()")
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.hit_map_visible = False
        
        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.hit_map_widget = HitMapWidget(self)
        self.visibility_button = qt_import.QPushButton("Show/Hide hit map")
 
        # Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.hit_map_widget)
        _main_vlayout.addWidget(self.visibility_button)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

        if HWR.beamline.online_processing is not None:
            HWR.beamline.online_processing.connect(
               "processingStarted", self.processing_started
            )
            HWR.beamline.online_processing.connect(
               "processingResultsUpdate", self.update_processing_results
            )
        else:
            self.setEnabled(False)

        if HWR.beamline.collect is not None:
            HWR.beamline.collect.connect(
               "collectStarted", self.collect_started
            )

        self.hit_map_widget.__score_key = "score" # default is spots_resolution
        self.hit_map_widget._score_type_cbox.setCurrentIndex(1)
        
        self.hit_map_widget._grid_hit_map_plot.mouseMovedSignal.connect(self.hit_map_widget.mouse_moved)
        self.hit_map_widget._grid_hit_map_plot.mouseClickedSignal.connect(self.hit_map_widget.mouse_clicked)
        self.hit_map_widget._grid_hit_map_plot.mouseDoubleClickedSignal.connect(
            self.hit_map_widget.move_to_position_clicked
        )
        #TODO: this signal is not received from pyqt_signal
        self.visibility_button.clicked.connect(self.show_hit_map_toggle)

        self.hit_map_widget._grid_hit_map_plot.mouseMovedSignal.\
             connect(self.hit_map_widget.mouse_moved)
        self.hit_map_widget._grid_hit_map_plot.mouseMovedSignal.\
             connect(self.hit_map_widget.mouse_moved)
        self.hit_map_widget._grid_hit_map_plot.mouseClickedSignal.\
             connect(self.hit_map_widget.mouse_clicked)
        self.hit_map_widget._grid_hit_map_plot.mouseDoubleClickedSignal.\
             connect(self.hit_map_widget.move_to_position_clicked)
        self.hit_map_widget._grid_hit_map_plot.mouseLeftSignal.connect(\
             self.hit_map_widget.mouse_left_plot)
        self.hit_map_widget.__enable_continues_image_display = True
        self.hit_map_widget.image_display_cbox.setChecked(True)
        self.hit_map_widget.image_display_cbox.hide()
        self.hit_map_widget._osc_hit_map_plot.hide()
        self.hit_map_widget._osc_hit_map_plot.setEnabled(True)
        self.hit_map_widget.setHidden(True)
        
        #TODO: set hit_map_widget x axis limits using set_x_axis_limits
        
    def show_hit_map_toggle(self, state):
        if self.hit_map_visible == False: 
            self.show_hit_map()
            self.hit_map_widget.setEnabled(True)
            self.hit_map_visible = True
        else: 
            self.hide_hit_map()
            self.hit_map_visible = False
    
    def show_hit_map(self):
        self.hit_map_widget.setHidden(False)
        self.hit_map_widget.setEnabled(True)
	
    def hide_hit_map(self):
        self.hit_map_widget.setHidden(True)

    def update_processing_results(self, last_results):
        self.hit_map_widget.update_results(last_results)
        self.show_hit_map()

    def collect_started(self, owner, num_oscillations):
        if HWR.beamline.collect.collect_experiment_type() != "Mesh":
            self.hide_hit_map()
        else:
            self.show_hit_map()
