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


from mxcubeqt.utils import icons, colors, qt_import
from mxcubeqt.base_components import BaseWidget
from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"


class KappaPhiBrick(BaseWidget):

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("label", "string", "")
        self.add_property("showStop", "boolean", True)
        self.add_property("defaultStep", "string", "10.0")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements-----------------------------------------------------
        _main_gbox = qt_import.QGroupBox(self)

        self.kappa_dspinbox = qt_import.QDoubleSpinBox(_main_gbox)
        self.kappa_dspinbox.setRange(-360, 360)
        self.kappaphi_dspinbox = qt_import.QDoubleSpinBox(_main_gbox)
        self.kappaphi_dspinbox.setRange(-360, 360)
        self.step_cbox = qt_import.QComboBox(_main_gbox)
        self.step_button_icon = icons.load_icon("TileCascade2")
        self.close_button = qt_import.QPushButton(_main_gbox)
        self.stop_button = qt_import.QPushButton(_main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_hlayout = qt_import.QHBoxLayout(_main_gbox)
        _main_gbox_hlayout.addWidget(qt_import.QLabel("Kappa:", _main_gbox))
        _main_gbox_hlayout.addWidget(self.kappa_dspinbox)
        _main_gbox_hlayout.addWidget(qt_import.QLabel("Phi:", _main_gbox))
        _main_gbox_hlayout.addWidget(self.kappaphi_dspinbox)
        _main_gbox_hlayout.addWidget(self.step_cbox)
        _main_gbox_hlayout.addWidget(self.close_button)
        _main_gbox_hlayout.addWidget(self.stop_button)
        _main_gbox_hlayout.setSpacing(2)
        _main_gbox_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = qt_import.QHBoxLayout(self)
        _main_hlayout.addWidget(_main_gbox)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        kappa_dspinbox_event = SpinBoxEvent(self.kappa_dspinbox)
        kappaphi_dspinbox_event = SpinBoxEvent(self.kappaphi_dspinbox)
        self.kappa_dspinbox.installEventFilter(kappa_dspinbox_event)
        self.kappaphi_dspinbox.installEventFilter(kappaphi_dspinbox_event)
        kappa_dspinbox_event.returnPressedSignal.connect(self.change_position)
        kappaphi_dspinbox_event.returnPressedSignal.connect(self.change_position)
        self.kappa_dspinbox.lineEdit().textEdited.connect(self.kappa_value_edited)
        self.kappaphi_dspinbox.lineEdit().textEdited.connect(self.kappaphi_value_edited)

        self.step_cbox.activated.connect(self.go_to_step)
        self.step_cbox.activated.connect(self.step_changed)
        self.step_cbox.editTextChanged.connect(self.step_edited)

        self.close_button.clicked.connect(self.close_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)

        # self.stop_button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Minimum)
        # Other ---------------------------------------------------------------
        self.kappa_dspinbox.setAlignment(qt_import.Qt.AlignRight)
        self.kappa_dspinbox.setFixedWidth(75)
        self.kappaphi_dspinbox.setAlignment(qt_import.Qt.AlignRight)
        self.kappaphi_dspinbox.setFixedWidth(75)

        self.step_cbox.setEditable(True)
        self.step_cbox.setValidator(
            qt_import.QDoubleValidator(0, 360, 5, self.step_cbox)
        )
        self.step_cbox.setDuplicatesEnabled(False)
        self.step_cbox.setFixedHeight(27)

        self.close_button.setIcon(icons.load_icon("Home2"))
        self.close_button.setFixedSize(27, 27)

        self.stop_button.setIcon(icons.load_icon("Stop2"))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedSize(27, 27)

        self.connect(HWR.beamline.diffractometer, "kappaMotorMoved", self.kappa_motor_moved)
        self.connect(HWR.beamline.diffractometer, "kappaPhiMotorMoved", self.kappaphi_motor_moved)
        self.connect(HWR.beamline.diffractometer, "minidiffStatusChanged", self.diffractometer_state_changed)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "showStop":
            if new_value:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif property_name == "defaultStep":
            if new_value != "":
                self.set_line_step(float(new_value))
                self.step_changed(None)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def stop_clicked(self):
        HWR.beamline.diffractometer.stop_kappa_phi_move()

    def close_clicked(self):
        HWR.beamline.diffractometer.close_kappa()

    def change_position(self):
        HWR.beamline.diffractometer.move_kappa_and_phi(
            self.kappa_dspinbox.value(), self.kappaphi_dspinbox.value()
        )

    def kappa_value_edited(self, text):
        colors.set_widget_color(
            self.kappa_dspinbox.lineEdit(),
            colors.LINE_EDIT_CHANGED,
            qt_import.QPalette.Base,
        )

    def kappaphi_value_edited(self, text):
        colors.set_widget_color(
            self.kappaphi_dspinbox.lineEdit(),
            colors.LINE_EDIT_CHANGED,
            qt_import.QPalette.Base,
        )

    def kappa_value_accepted(self):
        HWR.beamline.diffractometer.move_kappa_and_phi(
            self.kappa_dspinbox.value(), self.kappaphi_dspinbox.value()
        )

    def kappa_motor_moved(self, value):
        self.kappa_dspinbox.blockSignals(True)
        # txt = '?' if value is None else '%s' %\
        #      str(self['formatString'] % value)
        self.kappa_dspinbox.setValue(value)
        self.kappa_dspinbox.blockSignals(False)

    def kappaphi_motor_moved(self, value):
        self.kappaphi_dspinbox.blockSignals(True)
        # txt = '?' if value is None else '%s' %\
        #      str(self['formatString'] % value)
        self.kappaphi_dspinbox.setValue(value)
        self.kappaphi_dspinbox.blockSignals(False)

    def diffractometer_state_changed(self, state):
        self.setDisabled(HWR.beamline.diffractometer.in_plate_mode())
        self.kappa_dspinbox.setEnabled(HWR.beamline.diffractometer.is_ready())
        self.kappaphi_dspinbox.setEnabled(HWR.beamline.diffractometer.is_ready())
        self.close_button.setEnabled(HWR.beamline.diffractometer.is_ready())
        self.stop_button.setEnabled(not HWR.beamline.diffractometer.is_ready())

        colors.set_widget_color_by_state(
            self.kappa_dspinbox.lineEdit(),
            state,
            qt_import.QPalette.Base,
        )
        colors.set_widget_color_by_state(
            self.kappaphi_dspinbox.lineEdit(),
            state,    
            qt_import.QPalette.Base,
        )

    def go_to_step(self, step_index):
        step = str(self.step_cbox.currentText())
        if step != "":
            self.set_line_step(step)

    def set_line_step(self, val):
        self.kappa_dspinbox.setSingleStep(float(val))
        self.kappaphi_dspinbox.setSingleStep(float(val))
        found = False
        for i in range(self.step_cbox.count()):
            if float(str(self.step_cbox.itemText(i))) == float(val):
                found = True
                self.step_cbox.setItemIcon(i, self.step_button_icon)
        if not found:
            self.step_cbox.addItem(self.step_button_icon, str(val))
            self.step_cbox.setCurrentIndex(self.step_cbox.count() - 1)

    def step_changed(self, step):
        colors.set_widget_color(
            self.step_cbox.lineEdit(), qt_import.Qt.white, qt_import.QPalette.Base
        )

    def step_edited(self, step):
        """Paints step combobox when value is edited
        """
        colors.set_widget_color(
            self.step_cbox.lineEdit(),
            colors.LINE_EDIT_CHANGED,
            qt_import.QPalette.Button,
        )


class SpinBoxEvent(qt_import.QObject):

    returnPressedSignal = qt_import.pyqtSignal()
    contextMenuSignal = qt_import.pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() == qt_import.QEvent.KeyPress:
            if event.key() in [qt_import.Qt.Key_Enter, qt_import.Qt.Key_Return]:
                self.returnPressedSignal.emit()

        elif event.type() == qt_import.QEvent.MouseButtonRelease:
            self.returnPressedSignal.emit()
        elif event.type() == qt_import.QEvent.ContextMenu:
            self.contextMenuSignal.emit()
        return False
