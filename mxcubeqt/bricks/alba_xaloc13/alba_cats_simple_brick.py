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
"""
File: CatsSimpleBrick.py

Description
-------------
The CatsSimpleBrick.py is a simplified version of the SampleChangerBrick3.py

It presents the samples in the same way as SampleChangerBrick3.py. It allows to
select a sample by single clicking on it then perform the Load/Unload and Abort
operations on the Cats sample changer.

The CatsSimpleBrick.py adds a new property "use_basket_HT", to declare a "High Temperature"
puck. This HT puck has special handling by the Cats sample changer.

"""

import logging

from mxcubeqt.bricks.cats_simple_brick import CatsSimpleBrick
from mxcubeqt.bricks.sample_changer_brick import SampleChangerBrick
from mxcubecore import HardwareRepository as HWR
from mxcubeqt.utils import qt_import

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__version__ = "3"
__category__ = "Sample changer"


class AlbaCatsSimpleBrick(CatsSimpleBrick):
    def __init__(self, *args):
       CatsSimpleBrick.__init__(self, *args)
       
    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            # RB: I could only make this work as below. disconnecting the HWR.beamline.sample_changer does not work
            #if HWR.beamline.sample_changer is not None:
            if self.device is not None:
                self.disconnect(
                    self.device, "runningStateChanged", self._updatePathRunning
                )
                self.disconnect(
                    self.device, "powerStateChanged", self._updatePowerState
                )
                    
        SampleChangerBrick.property_changed(self, property_name, old_value, new_value)

        if property_name == "mnemonic":
            # load the new hardware object

            if HWR.beamline.sample_changer is not None:
                self.connect(
                    HWR.beamline.sample_changer,
                    "runningStateChanged",
                    self._updatePathRunning,
                )
                self.connect(
                    HWR.beamline.sample_changer,
                    "powerStateChanged",
                    self._updatePowerState,
                )
                #RB: maintain error messages
                self.connect(
                    HWR.beamline.sample_changer,
                    'taskFailed', 
                    self._reportTaskFailed
                )
                
                self._poweredOn = HWR.beamline.sample_changer.is_powered()
                self._pathRunning = HWR.beamline.sample_changer.is_path_running()
                self._updateButtons()

        elif property_name == "basketCount":
            # make sure that HT basket is added after Parent class has created all
            # baskets
            if self.has_basket_HT:
                self.add_basket_HT()
        elif property_name == "use_basket_HT":
            if new_value:
                if self.basket_count is not None:
                    self.has_basket_HT = True
                    self.add_basket_HT()
                else:
                    self.has_basket_HT = True

    def _reportTaskFailed(self, msg):
        qt_import.QMessageBox.warning( self, "Error", msg )

    #def load_selected_sample(self):

        #basket, vial = self.user_selected_sample

        #try:
            #if basket is not None and vial is not None:
                ##if basket != 100:
                    #sample_loc = "%d:%02d" % (basket + 1, vial)
                    #HWR.beamline.sample_changer.load(sample_loc, wait=False)
                ##else:
                    ##HWR.beamline.sample_changer.load_ht(vial, wait=False)
                    ##logging.getLogger("GUI").info(
                        ##"Is an HT sample: idx=%s (not implemented yet)" % (vial)
                    ##)
        #except:
            #qt_import.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))


    #def unload_selected_sample(self):
        #try:
            #HWR.beamline.sample_changer.unload()
        #except:
            #qt_import.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
