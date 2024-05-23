#! /usr/bin/env python
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

"""GPhL runtime-set parameter input widget. """
import logging

from typing import Any, Optional, Dict
from mxcubecore import HardwareRepository as HWR
from mxcubecore.dispatcher import dispatcher
from mxcubeqt.utils import qt_import
from mxcubeqt.utils.jsonparamsgui import create_widgets, LayoutWidget

__copyright__ = """ Copyright © 2016 - 2022 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"


class GphlJsonDialog(qt_import.QDialog):
    """Global phasing parammeter popup dialog

    Contents are set by jsonparamsgui"""

    continueClickedSignal = qt_import.pyqtSignal()

    def __init__(
        self,
        parent: Optional[qt_import.QWidget] = None,
        name: Optional[str] = None,
    ):
        qt_import.QDialog.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        # Internal variables --------------------------------------------------

        # Layout
        qt_import.QVBoxLayout(self)
        main_layout: qt_import.QVBoxLayout = self.layout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(6, 6, 6, 6)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

        self.setWindowTitle("GΦL Workflow parameters")

        # Parameter box
        self.parameter_gbox = qt_import.QGroupBox(self)
        parameter_vbox: qt_import.QVBoxLayout = qt_import.QVBoxLayout()
        self.parameter_gbox.setLayout(parameter_vbox)
        main_layout.addWidget(self.parameter_gbox, stretch=1)
        self.parameter_gbox.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.params_widget: Optional[LayoutWidget] = None

        # Button bar
        self.button_widget: qt_import.QWidget = qt_import.QWidget(self)
        button_layout: qt_import.QHBoxLayout = qt_import.QHBoxLayout(None)
        self.button_widget.setLayout(button_layout)
        hspacer: qt_import.QSpacerItem = qt_import.QSpacerItem(
            1, 20, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum
        )
        button_layout.addItem(hspacer)
        self.continue_button: qt_import.QPushButton = qt_import.QPushButton(
            "Continue", self
        )
        button_layout.addWidget(self.continue_button)
        self.cancel_button: qt_import.QPushButton = qt_import.QPushButton("Abort", self)
        button_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.button_widget)

        self.continue_button.clicked.connect(self.continue_button_click)
        self.cancel_button.clicked.connect(self.cancel_button_click)

        self.resize(qt_import.QSize(1200, 578).expandedTo(self.minimumSizeHint()))

    def keyPressEvent(self, event: qt_import.QKeyEvent) -> None:
        """Unused, but needed to disable having Qt interpret [Return] as [Continue]
        NB overrides Qt function so cannot be renamed"""
        if (not event.modifiers() and event.key() == qt_import.Qt.Key_Return) or (
            event.modifiers() == qt_import.Qt.KeypadModifier
            and event.key() == qt_import.Qt.Key_Enter
        ):
            event.accept()
        else:
            super(qt_import.QDialog, self).keyPressEvent(event)

    def continue_button_click(self) -> None:
        """Action when pressing Continue
        - send PARAMETER_RETURN_SIGNAL with values and PARAMETERS_READY"""
        result: dict = {}
        result.update(self.params_widget.get_values_map())
        self.accept()
        responses: list = dispatcher.send(
            HWR.beamline.config.gphl_workflow.PARAMETER_RETURN_SIGNAL,
            self,
            HWR.beamline.config.gphl_workflow.PARAMETERS_READY,
            result,
        )
        if not responses:
            self._return_parameters.set_exception(
                RuntimeError(
                    "Signal %s is not connected"
                    % HWR.beamline.config.gphl_workflow.PARAMETER_RETURN_SIGNAL
                )
            )

    def cancel_button_click(self) -> None:
        """Action when pressing Cancel
        - send PARAMETER_RETURN_SIGNAL with values and PARAMETERS_CANCELLED"""
        logging.getLogger("HWR").debug("GΦL Data dialog abort pressed.")
        result = {}
        result.update(self.params_widget.get_values_map())
        self.reject()
        return_signal = HWR.beamline.config.gphl_workflow.PARAMETER_RETURN_SIGNAL
        responses = dispatcher.send(
            return_signal,
            self,
            HWR.beamline.config.gphl_workflow.PARAMETERS_CANCELLED,
            result,
        )
        if not responses:
            self._return_parameters.set_exception(
                RuntimeError("Signal '%s' is not connected" % return_signal)
            )

    def open_dialog(self, schema: Dict[str, Any], ui_schema: Dict[str, Any]) -> None:
        """Open GPhL UI dialog"""

        msg: str = (
            "GΦL Workflow waiting for input, verify parameters and press continue."
        )
        logging.getLogger("user_level_log").info(msg)

        # parameters widget
        if self.params_widget is not None:
            self.params_widget.parametersValidSignal.disconnect(
                self.continue_button.setEnabled
            )
            self.params_widget.close()
            self.params_widget = None

        params_widget: LayoutWidget = create_widgets(
            schema, ui_schema, parent_widget=self
        )
        self.params_widget: LayoutWidget = params_widget
        self.parameter_gbox.layout().addWidget(params_widget)
        self.parameter_gbox.show()
        params_widget.parametersValidSignal.connect(self.continue_button.setEnabled)
        params_widget.validate_fields()
        self.show()
        self.setEnabled(True)
        self.update()
