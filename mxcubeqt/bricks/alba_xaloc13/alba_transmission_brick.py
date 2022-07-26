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

#from mxcubeqt.utils import colors
from mxcubeqt.bricks.transmission_brick import TransmissionBrick

from mxcubecore import HardwareRepository as HWR

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"

class AlbaTransmissionBrick(TransmissionBrick):

    def __init__(self, *args):
        TransmissionBrick.__init__(self, *args)
        if HWR.beamline.transmission is not None:
            HWR.beamline.transmission.update_values()
    
    # If the transmission has a problem during a change due to falied insertion of foils,
    #    the widget stays frozen. This may be related to some FAULT state, 
    #    leaving the transmission HO in not ready state, which calls disconnected method, 
    #    which disables the widget...
    #    To diagnose the problem, I added some prints
    #def _state_changed(self, state):
        #"""Updates new value QLineEdit based on the state"""
        #logging.getLogger("HWR").debug("Transmission state_changed, state is %s" % state)
        #if HWR.beamline.transmission.is_ready():
            #self.connected()
        #else:
            #self.disconnected()
        #self._update_ledit_color(colors.COLOR_STATES[state])

