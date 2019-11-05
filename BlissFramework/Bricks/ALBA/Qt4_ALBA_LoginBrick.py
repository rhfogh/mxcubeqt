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

from __future__ import print_function

from BlissFramework.Utils import Qt4_widget_colors
from Qt4_ProposalBrick2 import Qt4_ProposalBrick2

from BlissFramework.Qt4_BaseComponents import BlissWidget

import logging
import time

__credits__ = ["ALBA Synchrotron"]
__version__ = "2.3"
__category__ = "General"


class Qt4_ALBA_LoginBrick(Qt4_ProposalBrick2):

    def __init__(self, *args):
        Qt4_ProposalBrick2.__init__(self, *args)
        self.logger = logging.getLogger("GUI")
        self.logger.info("ALBA_LoginBrick.__init__()")
        self.proposal_number_ledit.setFixedWidth(100)
        self.proposal_password_ledit.setFixedWidth(100)

    # Handler for the Login button (check the password in LDAP)
    def login(self):
        """
        Descript. :
        """
        self.saved_group = False
        Qt4_widget_colors.set_widget_color(self.user_group_ledit,
                                           Qt4_widget_colors.WHITE)
        self.user_group_ledit.setText('')
        self.setEnabled(False)

        if not self.login_as_user:
            prop_type = str(self.proposal_type_combox.currentText())
            prop_number = str(self.proposal_number_ledit.text())
            prop_password = str(self.proposal_password_ledit.text())
            self.proposal_password_ledit.setText("")

            if prop_number == "":
                if self.local_login_hwobj is None:
                    return self.refuseLogin(False, "Local login not configured.")

                try:
                    locallogin_password = self.local_login_hwobj.password
                except AttributeError:
                    return self.refuseLogin(False, "Local login not configured.")

                if str(prop_password) != str(locallogin_password):
                    return self.refuseLogin(None, "Invalid local login password")

                now = time.strftime("%Y-%m-%d %H:%M:S")
                prop_dict = {'code': '', 'number': '', 'title': '', 'proposalId': ''}
                ses_dict = {'sessionId': '', 'startDate': now, 'endDate': now,
                            'comments': ''}
                # TODO: Unused code
                # try:
                #     locallogin_person = self.local_login_hwobj.person
                # except AttributeError:
                #     locallogin_person = "local user"
                logging.getLogger().debug("ProposalBrick: local login password OK")
                return self.acceptLogin(prop_dict, ses_dict)

            if self.lims_hwobj is None:
                return self.refuseLogin(False, 'Not connected to the ISPyB database,'
                                               'unable to get proposal.')

            self._do_login_as_proposal(prop_type, prop_number, prop_password,
                                       self.lims_hwobj.beamline_name)

    def _do_login_as_proposal(self, proposal_code, proposal_number, proposal_password,
                              beamline_name, impersonate=False):
        """
        Descript. :
        """
        # Get proposal and sessions
        proposal = "%s%s" % (proposal_code, proposal_number)
        # logging.getLogger("HWR").debug('ProposalBrick: querying ISPyB database... %s'
        #                                % proposal)

        prop = self.lims_hwobj.login(proposal, proposal_password)
        # logging.getLogger("HWR").debug('   prop returned by lims is %s' % str(prop))

        if prop['status']['code'] != "ok":
            msg = prop['status']['msg'] 
            self.refuseLogin(False, msg)
            return

        # We need to translate the proposal_code to acces ispyb database:
        t_proposal_code = self.lims_hwobj.translate(proposal_code, 'ispyb')
        # logging.getLogger("HWR").debug('Translating proposal code from %s to %s'
        #                                % (proposal_code, t_proposal_code))
        prop = self.lims_hwobj.getProposal(t_proposal_code, proposal_number)

        # logging.getLogger("HWR").debug('ALBALoginBrick:got proposal info from lims: %s'
        #                                % str(prop))
        # Check if everything went ok
        try:
            prop_ok = (prop['status']['code'] == 'ok')
        except KeyError:
            prop_ok = False

        if not prop_ok:
            self.ispybDown()
        else:
            self.select_proposal(prop)
            BlissWidget.set_status_info("user", "%s%s@%s" %
                                        (proposal_code, str(proposal_number),
                                         beamline_name))
