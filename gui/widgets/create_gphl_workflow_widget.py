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
from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

import api

from gui.utils import queue_item, QtImport
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.gphl_acquisition_widget import GphlAcquisitionWidget
from gui.widgets.gphl_acquisition_widget import GphlDiffractcalWidget
from gui.widgets.gphl_data_dialog import GphlDataDialog

from HardwareRepository import ConvertUtils
from HardwareRepository.HardwareObjects import queue_model_objects

__copyright__ = """ Copyright © 2016 - 2019 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"


class CreateGphlWorkflowWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):

        CreateTaskBase.__init__(
            self, parent, name, QtImport.Qt.WindowFlags(fl), "GphlWorkflow"
        )

        if not name:
            self.setObjectName("create_gphl_workflow_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.current_prefix = None

        self.init_models()

    def _initialize_graphics(self):
        # Graphic elements ----------------------------------------------------
        self._workflow_type_widget = QtImport.QGroupBox("Workflow type", self)

        self._workflow_cbox = QtImport.QComboBox(self._workflow_type_widget)
        self._gphl_acq_widget = QtImport.QGroupBox("Acquisition", self)
        self._gphl_acq_param_widget = GphlAcquisitionWidget(
            self._gphl_acq_widget, "gphl_acquisition_parameter_widget"
        )
        self._gphl_diffractcal_widget = GphlDiffractcalWidget(
            self._gphl_acq_widget, "gphl_diffractcal_widget"
        )

        self._data_path_widget = DataPathWidget(
            self,
            "create_dc_path_widget",
            data_model=self._path_template,
            layout="vertical"
        )
        self._data_path_widget._base_image_dir = (
            api.session.get_base_image_directory()
        )
        self._data_path_widget._base_process_dir = (
            api.session.get_base_process_directory()
        )
        data_path_layout = self._data_path_widget.data_path_layout
        data_path_layout.run_number_ledit.setReadOnly(True)
        data_path_layout.run_number_ledit.setEnabled(False)
        # data_path_layout.folder_ledit.setReadOnly(True)

        # Layout --------------------------------------------------------------
        _workflow_type_vlayout = QtImport.QVBoxLayout(self._workflow_type_widget)
        _workflow_type_vlayout.addWidget(self._workflow_cbox)
        _gphl_acq_vlayout = QtImport.QVBoxLayout(self._gphl_acq_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_acq_param_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_diffractcal_widget)
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._workflow_type_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._gphl_acq_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._workflow_cbox.currentIndexChanged.connect(self.workflow_selected)
        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )

        # set up popup data dialog
        self.gphl_data_dialog = GphlDataDialog(self, "GPhL Workflow Data")
        self.gphl_data_dialog.setModal(True)

    def initialise_workflows(self):

        workflow_hwobj = api.gphl_workflow
        if workflow_hwobj is not None:
            workflow_hwobj.setup_workflow_object()
            workflow_names = list(workflow_hwobj.get_available_workflows())
            self._initialize_graphics()
            self._workflow_cbox.clear()
            for workflow_name in workflow_names:
                self._workflow_cbox.addItem(workflow_name)
            self.workflow_selected()
            workflow_hwobj.connect(
                "gphlParametersNeeded", self.gphl_data_dialog.open_dialog
            )

    def init_data_path_model(self):
        # Initialize the path_template of the widget to default
        # values read from the beamline setup
        if self._data_path_widget:
            self._data_path_widget._base_image_dir = (
                api.session.get_base_image_directory()
            )
            self._data_path_widget._base_process_dir = (
                api.session.get_base_process_directory()
            )
            self._path_template.run_number = api.queue_model.get_next_run_number(
                self._path_template
            )
        else:
            self._path_template = queue_model_objects.PathTemplate()

        (data_directory, proc_directory) = self.get_default_directory()
        self._path_template = api.beamline_setup.get_default_path_template()
        self._path_template.directory = data_directory
        self._path_template.process_directory = proc_directory
        self._path_template.base_prefix = self.get_default_prefix()
        self._path_template.compression = self._enable_compression

    def workflow_selected(self):
        # necessary as this comes in as a QString object
        name = ConvertUtils.text_type(self._workflow_cbox.currentText())
        # if reset or name != self._previous_workflow:
        xx0 = self._workflow_cbox
        xx0.setCurrentIndex(xx0.findText(name))
        # self.init_models()
        # self._data_path_widget.update_data_model(self._path_template)

        parameters = api.gphl_workflow.get_available_workflows()[name]
        strategy_type = parameters.get("strategy_type")
        if strategy_type.startswith("transcal"):
            # NB Once we do not have to set unique prefixes, this should be readOnly
            # self._data_path_widget.data_path_layout.prefix_ledit.setReadOnly(False)
            self._gphl_acq_widget.hide()
        elif strategy_type.startswith("diffractcal"):
            # TODO update this
            # self._data_path_widget.data_path_layout.prefix_ledit.setReadOnly(True)
            self._gphl_diffractcal_widget.populate_widget()
            self._gphl_acq_widget.show()
            self._gphl_diffractcal_widget.show()
            self._gphl_acq_param_widget.hide()
        else:
            # acquisition type strategy
            # self._data_path_widget.data_path_layout.prefix_ledit.setReadOnly(True)
            self._gphl_acq_param_widget.populate_widget()
            self._gphl_acq_widget.show()
            self._gphl_diffractcal_widget.hide()
            self._gphl_acq_param_widget.show()

        self.current_prefix = parameters.get("prefix")

    def get_default_directory(self, tree_item=None, sub_dir=''):
        # Add placeholder for enactment number
        if sub_dir:
            sub_dir += "_000"
        #
        return super(CreateGphlWorkflowWidget, self).get_default_directory(
            tree_item=tree_item, sub_dir=sub_dir
        )

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        wf_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.GphlWorkflowQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if wf_model.get_path_template():
                self._path_template = wf_model.get_path_template()

            elif isinstance(tree_item, queue_item.BasketQueueItem):
                self.setDisabled(False)
            elif not isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
                self.setDisabled(True)

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._init_models()

    def _init_models(self):
        pass

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        tasks = []

        path_template = self._create_path_template(sample, self._path_template)
        path_template.num_files = 0
        # path_template.compression = False

        workflow_hwobj = api.gphl_workflow
        if workflow_hwobj.get_state() == workflow_hwobj.STATES.OFF:
            # We will be setting up the connection now - time to connect to quit
            QtImport.QApplication.instance().aboutToQuit.connect(
                workflow_hwobj.shutdown
            )

        wf = queue_model_objects.GphlWorkflow(workflow_hwobj)
        wf_type = ConvertUtils.text_type(self._workflow_cbox.currentText())
        wf.set_type(wf_type)

        if self.current_prefix:
            path_template.base_prefix = self.current_prefix
        wf.path_template = path_template
        wf.set_name(path_template.get_prefix())
        wf.set_number(path_template.run_number)

        wf_parameters = workflow_hwobj.get_available_workflows()[wf_type]
        strategy_type = wf_parameters.get("strategy_type")
        wf.set_interleave_order(wf_parameters.get("interleaveOrder", ""))
        if strategy_type.startswith("transcal"):
            pass

        elif strategy_type.startswith("diffractcal"):
            ss0 = self._gphl_diffractcal_widget.get_parameter_value("test_crystal")
            crystal_data = self._gphl_diffractcal_widget.test_crystals.get(ss0)
            wf.set_space_group(crystal_data.space_group)
            wf.set_cell_parameters(
                tuple(
                    getattr(crystal_data, tag)
                    for tag in ("a", "b", "c", "alpha", "beta", "gamma")
                )
            )
            val = self._gphl_diffractcal_widget.get_parameter_value(
                "relative_rad_sensitivity"
            )
            wf.set_relative_rad_sensitivity(val)
            # The entire strategy runs as a 'characterisation'
            wf.set_characterisation_budget_fraction(1.0)
            wf.set_decay_limit(
                api.gphl_workflow.getProperty("default_decay_limit", 0.25)
            )
        else:
            # Coulds be native_... phasing_... etc.

            wf.set_space_group(
                self._gphl_acq_param_widget.get_parameter_value("space_group")
            )
            wf.set_characterisation_strategy(
                self._gphl_acq_param_widget.get_parameter_value("characterisation_strategy")
            )
            tag = self._gphl_acq_param_widget.get_parameter_value("crystal_system")
            crystal_system, point_group = None, None
            if tag:
                data = self._gphl_acq_param_widget._CRYSTAL_SYSTEM_DATA[tag]
                crystal_system = data.crystal_system
                point_groups = data.point_groups
                if len(point_groups) == 1 or point_groups[0] == "32":
                    # '32' is a special case; '312' and '321' are also returned as '32'
                    point_group = point_groups[0]
            wf.set_point_group(point_group)
            wf.set_crystal_system(crystal_system)
            val = self._gphl_acq_param_widget.get_parameter_value(
                "relative_rad_sensitivity"
            )
            wf.set_relative_rad_sensitivity(val)
            wf.set_characterisation_budget_fraction(
                api.gphl_workflow.getProperty("characterisation_budget_percent", 5.0)
                / 100.0
            )
            wf.set_decay_limit(
                api.gphl_workflow.getProperty("default_decay_limit", 0.25)
            )
        beam_energy_tags = wf_parameters.get("beam_energy_tags")
        if beam_energy_tags:
            wf.set_beam_energy_tags(beam_energy_tags)

        tasks.append(wf)

        return tasks

    # NB do we need this? Check what happens when prefix is changed
    # # Added in porting to master branch
    # def _prefix_ledit_change(self, new_value):
    #     prefix = self._data_path_widget._data_model.base_prefix
    #     self._data_collection.set_name(prefix)
    #     self._tree_view_item.setText(0, self._data_collection.get_name())
