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

import os
import logging

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, icons, qt_import

from mxcubecore import HardwareRepository as HWR

from sample_control_brick import SampleControlBrick, MonoStateButton, DuoStateButton
from useful_routines import get_redis_connection

__credits__ = ["MXCuBE colaboration"]
__version__ = "0.0.2"
__category__ = "SOLEIL"

class SoleilSampleControlBrick(SampleControlBrick):
    """
    Descript. : SampleControlBrick is used to align and reorient sample
    """
    def create_graphics_elements(self):
        self.centre_button = DuoStateButton(self, "Centre")
        self.centre_button.set_icons("manual_align", "Delete")
        self.accept_button = MonoStateButton(self, "Save", "mark")
        self.standard_color = self.accept_button.palette().color(
            qt_import.QPalette.Window
        )
        self.reject_button = MonoStateButton(self, "Reject", "close")
        self.reject_button.hide()
        self.create_line_button = MonoStateButton(self, "Line", "Line")
        self.draw_grid_button = MonoStateButton(self, "Grid", "Grid")
        self.auto_focus_button = MonoStateButton(self, "Focus", "focus")
        self.snapshot_button = MonoStateButton(self, "Snapshot", "Camera")
        self.refresh_camera_button = MonoStateButton(self, "Refresh", "Refresh")
        self.visual_align_button = MonoStateButton(self, "Orient", "exchange")
        self.select_all_button = MonoStateButton(self, "Select all", "Check")
        self.clear_all_button = MonoStateButton(self, "Clear all", "Delete")
        self.auto_center_button = MonoStateButton(self, "Auto", "auto_align")
        self.realign_button = MonoStateButton(self, "Beam", "QuickRealign")
        self.anneal_button = MonoStateButton(self, "Anneal", "new_snowflake")
        self.excenter_button = MonoStateButton(self, "XCentre", "excenter")
        
    def create_layout(self):
        _main_layout = qt_import.QHBoxLayout(self)
        buttons = [ self.centre_button,
                    self.accept_button,
                    self.reject_button,
                    self.create_line_button,
                    self.draw_grid_button,
                    self.auto_focus_button,
                    self.snapshot_button,
                    self.refresh_camera_button,
                    self.visual_align_button,
                    self.select_all_button,
                    self.clear_all_button,
                    self.auto_center_button,
                    self.realign_button,
                    self.anneal_button,
                    self.excenter_button
                   ]
        for button in buttons:
            _main_layout.addWidget(button)
            
        size = qt_import.QSize(10, 10)
        policy = qt_import.QSizePolicy(qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Fixed)
        for button in buttons:
            button.setMinimumSize(size)
            button.setFixedWidth(57)
            button.setFixedHeight(35)
            button.setSizePolicy(policy)

        self.select_all_button.setVisible(False)
        self.create_line_button.setVisible(False)
        self.draw_grid_button.setVisible(False)
        self.auto_focus_button.setVisible(False)
        #self.auto_focus_button.setEnabled(False)
        self.snapshot_button.setVisible(False)
        self.refresh_camera_button.setVisible(False)
        self.clear_all_button.setVisible(False)
        self.auto_center_button.setVisible(False)
        #self.auto_center_button.setEnabled(False)
        self.anneal_button.setEnabled(True)
        self.realign_button.setEnabled(False)
        self.realign_button.setVisible(False)
        _main_layout.addStretch(0)
        _main_layout.setSpacing(0)
        _main_layout.setContentsMargins(0, 0, 0, 0)
        _main_layout.setAlignment(qt_import.Qt.AlignBottom)
                              
        return _main_layout

    def create_connections(self):
        self.centre_button.commandExecuteSignal.connect(self.centre_button_clicked)
        self.accept_button.clicked.connect(self.accept_clicked)
        self.reject_button.clicked.connect(self.reject_clicked)
        self.create_line_button.clicked.connect(self.create_line_clicked)
        self.draw_grid_button.clicked.connect(self.draw_grid_clicked)
        #self.auto_focus_button.clicked.connect(self.auto_focus_clicked)
        self.snapshot_button.clicked.connect(self.save_snapshot_clicked)
        self.refresh_camera_button.clicked.connect(self.refresh_camera_clicked)
        self.visual_align_button.clicked.connect(self.visual_align_clicked)
        self.select_all_button.clicked.connect(self.select_all_clicked)
        self.clear_all_button.clicked.connect(self.clear_all_clicked)
        #self.auto_center_button.clicked.connect(self.auto_center_clicked)
        self.realign_button.clicked.connect(self.realign_beam_clicked)
        self.anneal_button.clicked.connect(self.anneal_clicked)
        self.excenter_button.clicked.connect(self.excenter_clicked)
    
    def diffractometer_phase_changed(self, phase):
        # TODO connect this to minidiff
        status = phase != "BeamLocation"
        self.centre_button.setEnabled(status)
        self.accept_button.setEnabled(status)
        self.reject_button.setEnabled(status)
        self.create_line_button.setEnabled(status)
        self.draw_grid_button.setEnabled(status)
        #self.auto_focus_button.setEnabled(status)
        #self.refresh_camera_button.setEnabled(status)
        self.visual_align_button.setEnabled(status)
        self.select_all_button.setEnabled(status)
        self.clear_all_button.setEnabled(status)
        #self.auto_center_button.setEnabled(status)
        self.anneal_button.setEnabled(status)
        self.excenter_button.setEnabled(status)
        
    def realign_beam_clicked(self):
        HWR.beamline.sample_view.realign_beam()

    def anneal_clicked(self):
        anneal_dialog = AnnealDialog(self, name='Anneal')
        anneal_dialog.setModal(True)
        anneal_dialog.continueClickedSignal.connect(self.set_anneal_time)
        anneal_dialog.continueClickedSignal.connect(self.execute_anneal)
        logging.getLogger().info('anneal_clicked')
        anneal_dialog.show()

    def set_anneal_time(self, time):
        logging.getLogger().info('set_anneal_time %s' % time)
        self.anneal_time = time

    def execute_anneal(self):
        logging.getLogger().info('execute_anneal time %s' % self.anneal_time)
        HWR.beamline.diffractometer.anneal(duration=self.anneal_time)
        #os.system('anneal.py -t %f' % self.anneal_time)

    def excenter_clicked(self):
        excenter_dialog = ExcenterDialog(self, name='Excenter')
        excenter_dialog.setModal(True)
        excenter_dialog.continueClickedSignal.connect(self.execute_excenter)
        logging.getLogger().info('excenter_clicked')
        excenter_dialog.show()

    #def execute_excenter_b(self, scan_length, step):
        #logging.getLogger().info('execute_excenter scan_length %.2f, step %.2f' % (scan_length, step))
        #HWR.beamline.sample_view.show_excenter_finished_dialog(scan_length=scan_length, step=step, parent=self)
    
    #def execute_excenter(self, scan_length, step):
        #logging.getLogger().info('execute_excenter scan_length %.2f, step %.2f' % (scan_length, step))
        #HWR.beamline.sample_view.excenter(scan_length=scan_length, step=step, parent=self)

    def execute_excenter(
        self, 
        scan_length, 
        step, 
        dozor=True, 
        colspot=False,
        along=False,
    ):
        logging.getLogger().info(f'execute_excenter: {scan_length:.2f} mm, dozor {dozor}, colspot {colspot}, along {along}')
        
        HWR.beamline.sample_view.excenter(
            scan_length=scan_length, 
            step=step, 
            dozor=dozor, 
            colspot=colspot, 
            along=along, 
            parent=self,
        )
        
    def refresh_camera_clicked():
        HWR.beamline.sample_view.refresh_camera()

    def visual_align_clicked(self):
        HWR.beamline.sample_view.start_visual_align()

    def select_all_clicked(self):
        HWR.beamline.sample_view.select_all_points()

    def clear_all_clicked(self):
        """
        Clears all shapes (points, lines and meshes)
        """
        HWR.beamline.sample_view.clear_all_shapes()

    def auto_focus_clicked(self):
        HWR.beamline.sample_view.auto_focus()

    def auto_center_clicked(self):
        HWR.beamline.sample_view.start_auto_centring()

    def create_line_clicked(self):
        HWR.beamline.sample_view.create_line()

    def draw_grid_clicked(self):
        HWR.beamline.sample_view.create_grid()

        
class ExcenterDialog(qt_import.QDialog):

    #continueClickedSignal = qt_import.pyqtSignal(float, float)
    continueClickedSignal = qt_import.pyqtSignal(float, float, bool, bool, bool)
    
    def __init__(self, parent=None, name=None, flags=0):

        qt_import.QDialog.__init__(self, parent, qt_import.Qt.WindowFlags(flags | qt_import.Qt.Dialog))
        
        self.redis = get_redis_connection()
        self.redis_method_key = "diffraction_tomography_spotfinder"
        
        if name is not None:
            self.setObjectName(name) 
            
        self.scan_length = 0.25
        self.step = 45.
        
        # Graphic elements ---------------------------------------------------- 
        self.dialog = qt_import.loadUi(
            os.path.join(
                os.path.dirname(__file__),
                #"../../ui_files/soleil/excenter_improved.ui",
                "../../ui_files/soleil/excenter_radio_methods.ui",
                )
        )

         ## Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.dialog)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0) 

        # Qt signal/slot connections ------------------------------------------
        self.dialog.accepted.connect(\
             self.ok_click)
        self.dialog.rejected.connect(\
             self.cancel_click)
        
        self.dialog.scan_length_ledit.textChanged.connect(self.set_scan_length)
        self.dialog.check_dozor.toggled.connect(self.colspot_toggle)
        self.dialog.check_colspot.toggled.connect(self.dozor_toggle)
        #self.dialog.step_ledit.textChanged.connect(self.set_step)
       
        # Other --------------------------------------------------------------- 
        self.setWindowTitle('Excenter')
    
    def colspot_toggle(self, *args):
        print("colspot_toggle", args)
        if self.dialog.check_colspot.isChecked():
            self.redis.set(self.redis_method_key, b"colspot")
            if self.dialog.check_dozor.isChecked():
                self.dialog.check_dozor.setChecked(False)
        else:
            if not self.dialog.check_dozor.isChecked():
                self.dialog.check_dozor.setChecked(True)
                self.redis.set(self.redis_method_key, b"dozor")
        
    
    def dozor_toggle(self, *args):
        print("dozor_toggle", args)
        if self.dialog.check_dozor.isChecked():
            self.redis.set(self.redis_method_key, b"dozor")
            if self.dialog.check_colspot.isChecked():
                self.dialog.check_colspot.setChecked(False)
        else:
            self.redis.set(self.redis_method_key, b"colspot")
            if not self.dialog.check_colspot.isChecked():
                self.dialog.check_colspot.setChecked(True)
    
    
    def set_methods_from_redis(self, default_method=b"dozor"):
        method = self.redis.get(self.redis_method_key)
        if method is None:
            self.redis.set(self.redis_method_key, default_method)
            method = default_method
        if method == b"colspot":
            self.dialog.check_colspot.setChecked(True)
            self.dialog.check_dozor.setChecked(False)
        else:
            self.dialog.check_dozor.setChecked(True)
            self.dialog.check_colspot.setChecked(False)
            
    def get_colspot(self):
        colspot = self.dialog.check_colspot.isChecked()
        return colspot
    
    def get_dozor(self):
        dozor = self.dialog.check_dozor.isChecked()
        return dozor
    
    def get_explore_along(self):
        explore_along = self.dialog.check_along.isChecked()
        return explore_along
    
    def ok_click(self):
        """
        Descript. :
        """
        self.continueClickedSignal.emit(
            self.scan_length, 
            self.step, 
            self.get_dozor(),
            self.get_colspot(),
            self.get_explore_along(),
        )
        self.accept()
        
    def cancel_click(self):
        """
        Descript. :
        """
        self.reject()
        
    def set_scan_length(self, scan_length=None):
        try:
            self.scan_length = float(scan_length)
        except:
            pass
        
    #def set_step(self, step=None):
        #logging.getLogger().info('set_step %s ' % step)
        #try:
            #self.step = float(step)
        #except:
            #pass
        

class AnnealDialog(qt_import.QDialog):

    continueClickedSignal = qt_import.pyqtSignal(float)

    def __init__(self, parent=None, name=None, flags=0):

        qt_import.QDialog.__init__(self, parent, qt_import.Qt.WindowFlags(flags | qt_import.Qt.Dialog)) 

        if name is not None:
            self.setObjectName(name) 
            
        self.anneal_time = 1
        
        # Graphic elements ---------------------------------------------------- 
        self.anneal_dialog_layout = qt_import.loadUi(os.path.join(\
             os.path.dirname(__file__),
             "../../ui_files/soleil/anneal.ui"))

         ## Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.anneal_dialog_layout)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0) 

        
        # Qt signal/slot connections ------------------------------------------
        self.anneal_dialog_layout.accepted.connect(\
             self.ok_click)
        self.anneal_dialog_layout.rejected.connect(\
             self.cancel_click)
        
        self.anneal_dialog_layout.time_ledit.textChanged.connect(self.set_anneal_time)
        
       
        # Other --------------------------------------------------------------- 
        self.setWindowTitle('Anneal')
        
    def ok_click(self):
        """
        Descript. :
        """
        self.continueClickedSignal.emit(self.anneal_time) 
        self.accept()
        
    def cancel_click(self):
        """
        Descript. :
        """
        self.reject()

    def set_anneal_time(self, time=None):
        logging.getLogger().info('set_anneal_time %s ' % time)
        try:
            self.anneal_time = float(time)
        except:
            pass    
