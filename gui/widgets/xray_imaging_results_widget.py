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

import os

import api

from gui.utils import Icons, QtImport
from gui.widgets.matplot_widget import TwoDimenisonalPlotWidget

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class XrayImagingResultsWidget(QtImport.QWidget):
    def __init__(self, parent=None, name=None, fl=0, xray_imaging_params=None):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.current_image_num = 0
        self.total_image_num = 0

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        results_gbox = QtImport.QGroupBox("Results", self)
        
        self.graphics_view_widget = QtImport.QWidget(results_gbox)
        self.results_widget = QtImport.load_ui_file(
            "xray_imaging_results_widget_layout.ui"
        )
        tools_widget = QtImport.QGroupBox(self) 
        button_widget = QtImport.QWidget(self)
        self.start_centering_button = QtImport.QPushButton(
            Icons.load_icon("VCRPlay2"), "3 Click", tools_widget
        )
        self.start_n_centering_button = QtImport.QPushButton(
            Icons.load_icon("VCRPlay"), "n Click", tools_widget
        )
        self.accept_centering_button = QtImport.QPushButton(
            Icons.load_icon("ThumbUp"), "Save", tools_widget
        )
        self.histogram_plot = TwoDimenisonalPlotWidget(self)

        self.popup_menu = QtImport.QMenu(self)
        self.popup_menu.menuAction().setIconVisibleInMenu(True)

        self.popup_menu.addAction(
            Icons.load_icon("VCRPlay2"),
            "Start 3-click centering",
            self.start_centering_clicked,
        )
        self.popup_menu.addAction(
            Icons.load_icon("VCRPlay"),
            "Start n-click centering",
            self.start_n_centering_clicked,
        )
        self.popup_menu.addAction(
            Icons.load_icon("ThumbUp"),
            "Create centering point",
            self.accept_centering_clicked,
        )
        self.popup_menu.addAction(
            Icons.load_icon("ThumbUp"),
            "Set beam position",
            self.set_beam_position_clicked,
        )

        self.popup_menu.addSeparator()
        self.measure_distance_action = self.popup_menu.addAction(
            Icons.load_icon("measure_distance"),
            "Distance and histogram",
            self.measure_distance_clicked,
        )

        # Layout --------------------------------------------------------------
        self._graphics_view_widget_vlayout = QtImport.QVBoxLayout(
            self.graphics_view_widget
        )
        self._graphics_view_widget_vlayout.setSpacing(0)
        self._graphics_view_widget_vlayout.setContentsMargins(0, 0, 0, 0)

        __button_widget_hlayout = QtImport.QHBoxLayout(button_widget)
        __button_widget_hlayout.addWidget(self.start_centering_button)
        __button_widget_hlayout.addWidget(self.start_n_centering_button)
        __button_widget_hlayout.addWidget(self.accept_centering_button)
        __button_widget_hlayout.addStretch()
        __button_widget_hlayout.setSpacing(2)
        __button_widget_hlayout.setContentsMargins(2, 2, 2, 2)

        __tools_widget_vlayout = QtImport.QVBoxLayout(tools_widget)
        __tools_widget_vlayout.addWidget(button_widget)
        __tools_widget_vlayout.addWidget(self.results_widget)
        __tools_widget_vlayout.addWidget(self.histogram_plot)
        __tools_widget_vlayout.addStretch()
        __tools_widget_vlayout.setSpacing(2)
        __tools_widget_vlayout.setContentsMargins(2, 2, 2, 2)

        __main_hlayout = QtImport.QHBoxLayout(self)
        __main_hlayout.addWidget(self.graphics_view_widget)
        __main_hlayout.addWidget(tools_widget)
        __main_hlayout.setSpacing(0)
        __main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.results_widget.data_browse_button.clicked.connect(
            self.data_browse_button_clicked
        )
        self.results_widget.ff_browse_button.clicked.connect(
            self.ff_browse_button_clicked
        )
        self.results_widget.config_browse_button.clicked.connect(
            self.config_browse_button_clicked
        ) 
        self.results_widget.load_button.clicked.connect(
            self.load_button_clicked
        )
        self.results_widget.first_image_button.clicked.connect(
            self.first_image_button_clicked
        )
        self.results_widget.prev_image_button.clicked.connect(
            self.prev_image_button_clicked
        )
        self.results_widget.next_image_button.clicked.connect(
            self.next_image_button_clicked
        )
        self.results_widget.last_image_button.clicked.connect(
            self.last_image_button_clicked
        )
        self.results_widget.minus_quarter_button.clicked.connect(
            self.minus_quater_button_clicked
        )
        self.results_widget.last_image_button.clicked.connect(
            self.last_image_button_clicked
        )
        self.results_widget.plus_quarter_button.clicked.connect(
            self.plus_quater_button_clicked
        )
        self.results_widget.image_dial.valueChanged.connect(
            self.dial_value_changed
        )
        self.results_widget.image_dial.sliderReleased.connect(
            self.dial_released
        )
        self.results_widget.image_spinbox.valueChanged.connect(
            self.spinbox_value_changed
        )
        self.results_widget.omega_move_cbox.stateChanged.connect(
            self.omega_move_state_changed
        )

        self.results_widget.play_button.clicked.connect(self.play_button_clicked)
        self.results_widget.stop_button.clicked.connect(self.stop_button_clicked)
        self.results_widget.repeat_cbox.stateChanged.connect(self.repeat_state_changed)
        self.results_widget.ff_apply_cbox.stateChanged.connect(
            self.ff_apply_state_changed
        )

        self.start_centering_button.clicked.connect(self.start_centering_clicked)
        self.accept_centering_button.clicked.connect(self.accept_centering_clicked)

        # Other ---------------------------------------------------------------
        self.results_widget.first_image_button.setIcon(Icons.load_icon("VCRRewind"))
        self.results_widget.prev_image_button.setIcon(Icons.load_icon("VCRPlay4"))
        self.results_widget.next_image_button.setIcon(Icons.load_icon("VCRPlay2"))
        self.results_widget.last_image_button.setIcon(
            Icons.load_icon("VCRFastForward2")
        )
        self.results_widget.play_button.setIcon(Icons.load_icon("VCRPlay"))
        self.results_widget.stop_button.setIcon(Icons.load_icon("Stop2"))

        self.start_centering_button.setFixedSize(70, 50)
        self.start_n_centering_button.setFixedSize(70, 50)
        self.start_n_centering_button.setEnabled(False)
        self.accept_centering_button.setFixedSize(70, 50)

        api.xray_imaging.connect("imageInit", self.image_init)
        api.xray_imaging.connect("imageLoaded", self.image_loaded)
        api.xray_imaging.connect("measureItemChanged", self.measure_item_changed)

        self.graphics_view = api.xray_imaging.get_graphics_view()
        self._graphics_view_widget_vlayout.addWidget(self.graphics_view)
        self.graphics_view_widget.setFixedSize(
            self.graphics_view.scene().width(), self.graphics_view.scene().height()
        )

    def contextMenuEvent(self, event):
        self.popup_menu.popup(QtImport.QCursor.pos())

    def populate_widget(self, item):
        data_model = item.get_model()
        acq_params = data_model.acquisitions[0].acquisition_parameters
        imaging_params = data_model.xray_imaging_parameters
        path_template = data_model.acquisitions[0].path_template

        self.results_widget.data_path_ledit.setText(path_template.get_image_path() % 1)
        if imaging_params.ff_pre or imaging_params.ff_post:
            ff_file_path = os.path.join(
                path_template.directory, "ff_" + path_template.get_image_file_name() % 1
            )
            self.results_widget.ff_path_ledit.setText(ff_file_path)
            self.results_widget.ff_path_ledit.setEnabled(True)
            self.results_widget.ff_apply_cbox.setChecked(True)
        else:
            self.results_widget.ff_path_ledit.setText("")
            self.results_widget.ff_path_ledit.setEnabled(False)
            self.results_widget.ff_apply_cbox.setChecked(False)

        config_filename = "%s_%d_00001.json" % (path_template.base_prefix,
                                                path_template.run_number)
        self.results_widget.config_path_ledit.setText(os.path.join(path_template.get_archive_directory(),
                                                                    config_filename))

        api.xray_imaging.set_osc_start(acq_params.osc_start)

    def measure_distance_clicked(self):
        api.xray_imaging.start_measure_distance(wait_click=True)

    def measure_item_changed(self, image_slice):
        self.histogram_plot.clear()
        self.histogram_plot.add_curve("pixel values", image_slice)

    def image_init(self, image_descr_dict):
        self.total_image_num = image_descr_dict
        self.current_image_num = 0
        #self.results_widget.image_slider.blockSignals(True)
        self.results_widget.image_dial.blockSignals(True)
        self.results_widget.image_spinbox.blockSignals(True)

        #self.results_widget.image_slider.setMinimum(0)
        #self.results_widget.image_slider.setMaximum(self.total_image_num - 1)
        self.results_widget.image_dial.setMinimum(0)
        self.results_widget.image_dial.setMaximum(self.total_image_num - 1)
        self.results_widget.image_spinbox.setMinimum(1)
        self.results_widget.image_spinbox.setMaximum(self.total_image_num)
        self.refresh_gui()

        #self.results_widget.image_slider.blockSignals(False)
        self.results_widget.image_dial.blockSignals(False)
        #self.results_widget.image_spinbox.blockSignals(False)

    def image_loaded(self, index):
        self.current_image_num = index
        # self.results_widget.data_path_ledit.setText(filename)
        self.refresh_gui()

    def ff_apply_state_changed(self, state):
        api.xray_imaging.set_ff_apply(state)

    def omega_move_state_changed(self, state):
        api.xray_imaging.set_omega_move_enabled(state)

    def data_browse_button_clicked(self):
        file_dialog = QtImport.QFileDialog(self)
       
        try:
            base_image_dir = os.path.dirname(str(self.results_widget.data_path_ledit.text()))
        except:
            base_image_dir = os.environ["HOME"]

        selected_filename = str(
            file_dialog.getOpenFileName(self, "Select an image", base_image_dir)
        )
        self.results_widget.data_path_ledit.setText(selected_filename)

        ff_path, config_path = api.xray_imaging.get_ff_and_config_path(selected_filename)
        if ff_path:
            self.results_widget.ff_path_ledit.setText(ff_path)
        else:
            self.results_widget.ff_path_ledit.setText("")

        if config_path:
            self.results_widget.config_path_ledit.setText(config_path)
        else:
            self.results_widget.config_path_ledit.setText("")     

    def ff_browse_button_clicked(self):
        file_dialog = QtImport.QFileDialog(self)
        base_image_dir = os.environ["HOME"]

        selected_filename = str(
            file_dialog.getOpenFileName(self, "Select an image", base_image_dir)
        )
        self.results_widget.ff_path_ledit.setText(selected_filename)

    def config_browse_button_clicked(self):
        file_dialog = QtImport.QFileDialog(self)
        base_image_dir = os.environ["HOME"]

        selected_filename = str(
            file_dialog.getOpenFileName(self, "Select a configuration file", base_image_dir)
        )
        self.results_widget.config_path_ledit.setText(selected_filename)

    def load_button_clicked(self):
        api.xray_imaging.load_images(
            str(self.results_widget.data_path_ledit.text()),
            str(self.results_widget.ff_path_ledit.text()),
            str(self.results_widget.config_path_ledit.text())
        )

    def first_image_button_clicked(self):
        api.xray_imaging.display_image(0)

    def prev_image_button_clicked(self):
        api.xray_imaging.display_image_relative(-1)

    def next_image_button_clicked(self):
        api.xray_imaging.display_image_relative(1)

    def last_image_button_clicked(self):
        api.xray_imaging.display_image(self.total_image_num - 1)

    def minus_quater_button_clicked(self):
        api.xray_imaging.display_image_relative(-90)

    def plus_quater_button_clicked(self):
        api.xray_imaging.display_image_relative(90)

    def dial_value_changed(self, value):
        api.xray_imaging.display_image(value)

    def dial_released(self):
        #api.xray_imaging.move_omega(self.results_widget.image_dial.value())
        pass

    def spinbox_value_changed(self, value):
        api.xray_imaging.display_image(value - 1)

    def play_button_clicked(self):
        api.xray_imaging.play_images(
            repeat=self.results_widget.repeat_cbox.isChecked()
        )

    def stop_button_clicked(self):
        api.xray_imaging.stop_image_play()

    def repeat_state_changed(self, state):
        api.xray_imaging.set_repeate_image_play(state)

    def start_centering_clicked(self):
        api.xray_imaging.start_centering()

    def start_n_centering_clicked(self):
        api.xray_imaging.start_n_centering()

    def accept_centering_clicked(self):
        api.graphics.accept_centring()

    def set_beam_position_clicked(self):
        api.xray_imaging.start_move_beam_mark()

    def refresh_gui(self):
        self.results_widget.image_dial.blockSignals(True)
        self.results_widget.image_dial.setValue(self.current_image_num)
        self.results_widget.image_dial.blockSignals(False)

        self.results_widget.image_spinbox.blockSignals(True)
        self.results_widget.image_spinbox.setValue(self.current_image_num)
        self.results_widget.image_spinbox.blockSignals(False)

        self.results_widget.prev_image_button.setDisabled(self.current_image_num == 0)
        self.results_widget.next_image_button.setDisabled(
            self.current_image_num == self.total_image_num - 1
        )
