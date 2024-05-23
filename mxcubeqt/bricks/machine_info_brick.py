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
from mxcubeqt.utils import icons, colors, qt_import
from mxcubeqt.widgets.matplot_widget import TwoAxisPlotWidget

from mxcubecore import HardwareRepository as HWR


STATES = {"unknown": colors.GRAY, "ready": colors.LIGHT_BLUE, "error": colors.LIGHT_RED}


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class MachineInfoBrick(BaseWidget):
    """Brick to display information about synchrotron and beamline"""

    def __init__(self, *args):
        """Main init"""

        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.graphics_initialized = False
        self.value_label_list = []

        # Properties (name, type, default value, comment)----------------------
        self.add_property(
            "maxPlotPoints", "integer", 100, comment="Maximal number of plot points"
        )

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------

        # Layout --------------------------------------------------------------
        self.main_vlayout = qt_import.QVBoxLayout(self)
        self.main_vlayout.setSpacing(1)
        self.main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.setToolTip("Main information about the beamline")

    def run(self):
        """Method called when user changes a property in the gui builder"""
        if HWR.beamline.config.machine_info is not None:
            self.setEnabled(True)
            self.connect(HWR.beamline.config.machine_info, "valuesChanged", self.set_value)
        else:
            self.setEnabled(False)

    def set_value(self, values_dict):
        """Slot connected to the valuesChanged signal
           At first time initializes gui by adding necessary labels.
           If the gui is initialized then update labels with values
        """
        if not self.graphics_initialized:
            for item in values_dict.values():
                temp_widget = CustomInfoWidget(self)
                temp_widget.init_info(item, self["maxPlotPoints"])
                self.value_label_list.append(temp_widget)
                self.main_vlayout.addWidget(temp_widget)
        self.graphics_initialized = True
        for index, value in enumerate(values_dict.values()):
            self.value_label_list[index].update_info(value)


class CustomInfoWidget(qt_import.QWidget):
    """Custom information widget"""

    def __init__(self, *args):
        qt_import.QWidget.__init__(self, *args)

        self.value_plot = None

        self.title_label = qt_import.QLabel(self)
        self.value_widget = qt_import.QWidget(self)
        self.value_label = qt_import.QLabel(self.value_widget)
        self.value_label.setAlignment(qt_import.Qt.AlignCenter)
        self.history_button = qt_import.QPushButton(
            icons.load_icon("LineGraph"), "", self.value_widget
        )
        self.history_button.hide()
        self.history_button.setFixedWidth(22)
        self.history_button.setFixedHeight(22)

        _value_widget_hlayout = qt_import.QHBoxLayout(self.value_widget)
        _value_widget_hlayout.addWidget(self.value_label)
        _value_widget_hlayout.addWidget(self.history_button)
        _value_widget_hlayout.setSpacing(2)
        _value_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        self.main_vlayout = qt_import.QVBoxLayout(self)
        self.main_vlayout.addWidget(self.title_label)
        self.main_vlayout.addWidget(self.value_widget)
        self.main_vlayout.setSpacing(1)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.history_button.clicked.connect(self.open_history_view)

    def init_info(self, info_dict, max_plot_points=None):
        self.title_label.setText(info_dict.get("title", "???"))
        self.history_button.setVisible(info_dict.get("history", False))
        font = self.value_label.font()
        if info_dict.get("font"):
            font.setPointSize(info_dict.get("font"))
        if info_dict.get("bold"):
            font.setBold(True)
        self.value_label.setFont(font)

        if info_dict.get("align") == "left":
            self.value_label.setAlignment(qt_import.Qt.AlignLeft)
        elif info_dict.get("align") == "right":
            self.value_label.setAlignment(qt_import.Qt.AlignRight)
        elif info_dict.get("align") == "center":
            self.value_label.setAlignment(qt_import.Qt.AlignHCenter)
        elif info_dict.get("align") == "justify":
            self.value_label.setAlignment(qt_import.Qt.AlignJustify)

        if info_dict.get("history"):
            self.history_button.show()
            self.value_plot = TwoAxisPlotWidget(self, realtime_plot=True)
            self.value_plot.hide()
            self.main_vlayout.addWidget(self.value_plot)
            self.value_plot.set_tight_layout()
            self.value_plot.clear()
            self.value_plot.set_max_plot_point(max_plot_points)
            # self.value_plot.set_y_axis_limits([0, None])
        self.update_info(info_dict)

    def update_info(self, info_dict):
        if info_dict.get("value_str"):
            self.value_label.setText(info_dict.get("value_str"))
        else:
            self.value_label.setText(str(info_dict.get("value")))

        if info_dict.get("in_range") is None:
            colors.set_widget_color(self.value_label, colors.GRAY)
        elif info_dict.get("in_range") == True:
            colors.set_widget_color(self.value_label, colors.LIGHT_BLUE)
        else:
            colors.set_widget_color(self.value_label, colors.LIGHT_RED)
        value = info_dict.get("value")
        if type(value) in (int, float) and self.value_plot:
            self.value_plot.add_new_plot_value(value)

    def open_history_view(self):
        self.value_plot.setVisible(not self.value_plot.isVisible())
