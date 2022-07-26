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

from mxcubeqt.bricks.phase_brick import PhaseBrick                                                                                                                                                                                                         
                                                                                                                                                                                                                                                        
from mxcubecore import HardwareRepository as HWR                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
__credits__ = ["MXCuBE collaboration"]                                                                                                                                                                                                                  
__license__ = "LGPLv3+"                                                                                                                                                                                                                                 
__category__ = "General"                                                                                                                                                                                                                                
      
class AlbaPhaseBrick(PhaseBrick):                                                                                                                                                                                                                           
    def __init__(self, *args):                                                                                                                                                                                                                          
        PhaseBrick.__init__(self, *args)     
        #TODO: disable the brick when in collect or sample exchange processes

        if HWR.beamline.collect is not None:
            self.connect(
                HWR.beamline.collect, "collectStarted", self.collect_started
            )
            self.connect(
                HWR.beamline.collect, "collectOscillationFinished", self.collect_finished
            )
            self.connect(
                HWR.beamline.collect, "collectOscillationFailed", self.collect_failed
            )

    def enable_widget(self, *args):
        self.setEnabled(True)
        
    def disable_widget(self, *args):
        self.setEnabled(False)

    def collect_started(self, owner, num_oscillations):
        self.disable_widget()

    def collect_finished(self, owner, state, message, *args):
        self.enable_widget()
        
    def collect_failed(self, owner, state, message, *args):
        self.enable_widget()
 
