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

from mxcubeqt.utils import colors, qt_import

from proposal_brick import ProposalBrick

from mxcubeqt.base_components import BaseWidget
from mxcubecore import HardwareRepository as HWR

import logging
import time

__credits__ = ["ALBA Synchrotron"]
__version__ = "3"
__category__ = "General"


class AlbaLoginBrick(ProposalBrick):

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.local_login_hwobj = None

        # Internal values -----------------------------------------------------
        self.login_as_user = None

        self.proposal = None
        self.person = None
        self.laboratory = None
        # self.sessionId=None
        self.inhouseProposal = None
        self.instance_server_hwobj = None
        self.secondary_proposals = []

        # Properties ----------------------------------------------------------
        self.add_property('instanceServer', 'string', '')
        self.add_property('localLogin', 'string', '')
        self.add_property("titlePrefix", "string", "")
        self.add_property("autoSessionUsers", "string", "")
        self.add_property("codes", "string", "fx ifx ih im ix ls mx opid")
        self.add_property("secondaryProposals", "string", "")
        self.add_property("icons", "string", "")
        self.add_property("serverStartDelay", "integer", 500)

        # Signals ------------------------------------------------------------
        self.define_signal("sessionSelected", ())
        self.define_signal("setWindowTitle", ())
        self.define_signal("loggedIn", ())
        self.define_signal("userGroupSaved", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("setButtonEnabled", ())
        self.define_slot("impersonateProposal", ())

        # Graphic elements ----------------------------------------------------
        # main_gbox holds all elements of the login brick
        self.main_gbox = qt_import.QGroupBox("ISPyB proposal", self) 

        self.login_as_proposal_widget = qt_import.QWidget(self.main_gbox)
        code_label = qt_import.QLabel("  Code: ", self.login_as_proposal_widget)
        self.proposal_type_combox = qt_import.QComboBox(self.login_as_proposal_widget)
        self.proposal_type_combox.setEditable(True)
        #self.proposal_type_combox.setFixedWidth(60)
        dash_label = qt_import.QLabel(" - ", self.login_as_proposal_widget)
        self.proposal_number_ledit = qt_import.QLineEdit(self.login_as_proposal_widget)
        self.proposal_number_ledit.setFixedWidth(100)
        password_label = qt_import.QLabel("   Password: ", self.login_as_proposal_widget)
        self.proposal_password_ledit = qt_import.QLineEdit(self.login_as_proposal_widget)
        self.proposal_password_ledit.setEchoMode(qt_import.QLineEdit.Password)
        self.proposal_password_ledit.setFixedWidth(100)
        self.login_button = qt_import.QPushButton("Login", self.login_as_proposal_widget)
        self.login_button.setFixedWidth(70)
        self.logout_button = qt_import.QPushButton("Logout", self.main_gbox)
        self.logout_button.hide()
        self.logout_button.setFixedWidth(70)
        self.login_as_proposal_widget.hide()
        self.logged_proposal_label = qt_import.QLabel("", self.main_gbox)
        self.logged_proposal_label.hide()

        self.login_as_user_widget = qt_import.QWidget(self.main_gbox)
        self.proposal_combo = qt_import.QComboBox(self.login_as_user_widget)

        self.user_group_widget = qt_import.QWidget(self.main_gbox)
        # self.title_label = QtGui.QLabel(self.user_group_widget)
        # self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.user_group_label = qt_import.QLabel("  Group: ", self.user_group_widget)
        self.user_group_ledit = qt_import.QLineEdit(self.user_group_widget)
        self.user_group_ledit.setFixedSize(100, 27)
        self.user_group_save_button = qt_import.QToolButton(self.user_group_widget)
        self.user_group_save_button.setText("Set")
        self.user_group_save_button.setFixedHeight(27)
        self.saved_group = True

        # small molecule proposals
        self.is_small_molecule_cbox = qt_import.QCheckBox("Process as small molecule")
        
        # Layout --------------------------------------------------------------
        _user_group_widget_hlayout = qt_import.QHBoxLayout(self.user_group_widget)
        _user_group_widget_hlayout.setSpacing(2)
        # _user_group_widget_hlayout.addWidget(self.title_label)
        _user_group_widget_hlayout.addWidget(self.user_group_label)
        _user_group_widget_hlayout.addWidget(self.user_group_ledit)
        _user_group_widget_hlayout.addWidget(self.user_group_save_button)
        _user_group_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.user_group_widget.hide()

        _login_as_proposal_widget_layout = qt_import.QVBoxLayout(
            self.login_as_proposal_widget
        )
        _login_as_proposal_widget_layout1 = qt_import.QHBoxLayout(self.login_as_proposal_widget)
        _login_as_proposal_widget_layout1.addWidget(code_label)
        _login_as_proposal_widget_layout1.addWidget(self.proposal_type_combox)
        _login_as_proposal_widget_layout1.addWidget(dash_label)
        _login_as_proposal_widget_layout1.addWidget(self.proposal_number_ledit)
        
        _login_as_proposal_widget_layout2 = qt_import.QHBoxLayout(self.login_as_proposal_widget)
        _login_as_proposal_widget_layout2.addWidget(password_label)
        _login_as_proposal_widget_layout2.addWidget(self.proposal_password_ledit)
        _login_as_proposal_widget_layout2.addWidget(self.login_button)
        
        _login_as_proposal_widget_layout.setSpacing(2)
        _login_as_proposal_widget_layout.setContentsMargins(0, 0, 0, 0)

        _login_as_proposal_widget_layout.addLayout(_login_as_proposal_widget_layout1)
        _login_as_proposal_widget_layout.addLayout(_login_as_proposal_widget_layout2)

        _login_as_user_widget_layout = qt_import.QHBoxLayout(self.login_as_user_widget)
        _login_as_user_widget_layout.addWidget(self.proposal_combo)
        _login_as_user_widget_layout.setSpacing(2)
        _login_as_user_widget_layout.setContentsMargins(0, 0, 0, 0)

        _main_gboxlayout = qt_import.QVBoxLayout(self.main_gbox)

        _main_gboxlayout1 = qt_import.QHBoxLayout(self.main_gbox)
        _main_gboxlayout1.addWidget(self.login_as_proposal_widget)
        _main_gboxlayout1.addWidget(self.logged_proposal_label)
        _main_gboxlayout1.addWidget(self.logout_button)
        _main_gboxlayout1.addWidget(self.login_as_user_widget)
        #_main_gboxlayout.addStretch()
        
        _main_gboxlayout2 = qt_import.QHBoxLayout(self.main_gbox)
        _main_gboxlayout2.addWidget(self.user_group_widget)
        
        _main_gboxlayout.setSpacing(2)
        _main_gboxlayout.setContentsMargins(0, 0, 0, 0)

        _main_gboxlayout.addLayout(_main_gboxlayout1)
        _main_gboxlayout.addLayout(_main_gboxlayout2)
        #_main_gboxlayout.addWidget(self.is_small_molecule_cbox)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        #  self.user_group_ledit

        # Qt signal/slot connections ------------------------------------------
        self.proposal_password_ledit.returnPressed.connect(self.login)
        self.login_button.clicked.connect(self.login)
        self.logout_button.clicked.connect(self.logout_clicked)
        self.proposal_combo.activated.connect(self.proposal_combo_activated)
        self.user_group_save_button.clicked.connect(self.save_group)
        self.user_group_ledit.returnPressed.connect(self.save_group)
        self.user_group_ledit.textChanged.connect(self.user_group_changed)
        self.is_small_molecule_cbox.stateChanged.connect(self.molecule_type_toggled)

        # Other ---------------------------------------------------------------
        colors.set_widget_color(
            self.proposal_number_ledit, colors.LIGHT_RED, qt_import.QPalette.Base
        )
        colors.set_widget_color(
            self.proposal_password_ledit, colors.LIGHT_RED, qt_import.QPalette.Base
        )

        self.proposal_number_ledit.setFixedWidth(100)
        self.proposal_password_ledit.setFixedWidth(100)


    # Handler for the Login button (check the password in LDAP)
    def login(self):
        """
        Descript. :
        """
        self.saved_group = False
        colors.set_widget_color(self.user_group_ledit,
                                           colors.WHITE)
        self.user_group_ledit.setText('')
        self.setEnabled(False)

        if not self.login_as_user:
            prop_type = str(self.proposal_type_combox.currentText())
            prop_number = str(self.proposal_number_ledit.text())
            prop_password = str(self.proposal_password_ledit.text())
            self.proposal_password_ledit.setText("")

            if prop_number == "":
                if self.local_login_hwobj is None:
                    return self.refuse_login(False, "Local login not configured.")

                try:
                    locallogin_password = self.local_login_hwobj.password
                except AttributeError:
                    return self.refuse_login(False, "Local login not configured.")

                if str(prop_password) != str(locallogin_password):
                    return self.refuse_login(None, "Invalid local login password")

                now = time.strftime("%Y-%m-%d %H:%M:S")
                prop_dict = {"code": "", "number": "", "title": "", "proposalId": ""}
                ses_dict = {
                              "sessionId": "", 
                              "startDate": now, 
                              "endDate": now,
                              "comments": ""
                }
                return self.accept_login(prop_dict, ses_dict)

            if HWR.beamline.lims is None:
                return self.refuse_login(
                    False, 
                    'Not connected to the ISPyB database, unable to get proposal.'
                )

            self._do_login_as_proposal(
                prop_type, 
                prop_number, 
                prop_password,
                HWR.beamline.lims.beamline_name
            )

    def _do_login_as_proposal(
        self, 
        proposal_code, 
        proposal_number, 
        proposal_password,
        beamline_name, 
        impersonate=False
    ):
        """
        Descript. :
        """
        # Get proposal and sessions
        proposal = "%s%s" % (proposal_code, proposal_number)
        # logging.getLogger("HWR").debug('ProposalBrick: querying ISPyB database... %s'
        #                                % proposal)
        
        prop = HWR.beamline.lims.login(proposal, proposal_password)
        # logging.getLogger("HWR").debug('   prop returned by lims is %s' % str(prop))

        if prop['status']['code'] != "ok":
            msg = prop['status']['msg'] 
            self.refuse_login(False, msg)
            return

        # We need to translate the proposal_code to acces ispyb database:
        t_proposal_code = HWR.beamline.lims.translate(proposal_code, 'ispyb')
        # logging.getLogger("HWR").debug('Translating proposal code from %s to %s'
        #                                % (proposal_code, t_proposal_code))
        prop = HWR.beamline.lims.get_proposal(t_proposal_code, proposal_number)

        logging.getLogger("HWR").debug('ALBALoginBrick:got proposal info from lims: %s'
                                        % str(prop))
        # Check if everything went ok
        prop_ok = True
        try:
            prop_ok = (prop['status']['code'] == 'ok')
        except KeyError:
            prop_ok = False

        if not prop_ok:
            self.set_ispyb_down()
            BaseWidget.set_status_info("ispyb", "error")
        else:
            self.select_proposal(prop)
            BaseWidget.set_status_info(
                "user", "%s%s@%s" %  (proposal_code, str(proposal_number), beamline_name)
            )
            BaseWidget.set_status_info("ispyb", "ready")

    # Logout the user; reset the brick; changes from logout mode to login mode
    # redefine to set behaviour of the login brick
    def log_out(self):
        # Reset brick info
        self.proposal_number_ledit.setText("")
        self.proposal = None
        # self.sessionId=None
        self.person = None
        self.laboratory = None
        # Change mode from logout to login
        if not self.login_as_user:
            self.login_as_proposal_widget.setEnabled(True)
            self.login_as_proposal_widget.show()
            self.logged_proposal_label.hide()
            self.logout_button.hide()
            self.logged_proposal_label.setText("")
        # self.title_label.hide()
        self.user_group_widget.hide()

        # resets active proposal
        self.reset_proposal()

        # self.proposalLabel.setText(ProposalBrick2.NOBODY_STR)
        # QToolTip.add(self.proposalLabel,"")

        # Emit signals clearing the proposal and session
        self.setWindowTitle.emit(self["titlePrefix"])
        # self.sessionSelected.emit(None, None, None, None, None, None, None)
        self.loggedIn.emit(False)



    def set_proposal(self, proposal, session):
        HWR.beamline.lims.enable()
        HWR.beamline.session.proposal_code = proposal["code"]
        HWR.beamline.session.session_id = session["sessionId"]
        HWR.beamline.session.proposal_id = proposal["proposalId"]
        HWR.beamline.session.proposal_number = proposal["number"]

        # Change mode
        if not self.login_as_user:
            self.logged_proposal_label.setText("%s%s" % (proposal['code'], str(proposal['number'])))
            self.logged_proposal_label.show()
            self.login_as_proposal_widget.hide()
            self.logout_button.show()

        # Store info in the brick
        self.proposal = proposal

        code = proposal["code"].lower()

        if code == "":
            logging.getLogger().warning(
                "Using local login: the data collected won't be stored in the database"
            )
            HWR.beamline.lims.disable()
            self.loggedIn.emit(False)
        else:
            msg = "Results in ISPyB will be stored under proposal %s%s - '%s'" % (
                proposal["code"],
                str(proposal["number"]),
                proposal["title"],
            )
            logging.getLogger("GUI").debug(msg)
            self.loggedIn.emit(True)


    def accept_login(self, proposal_dict, session_dict):
        self.set_proposal(proposal_dict, session_dict)
        self.setEnabled(True)
        self.user_group_widget.show()

    def molecule_type_toggled(self, state):
        HWR.beamline.offline_processing.set_sample_type( state )
