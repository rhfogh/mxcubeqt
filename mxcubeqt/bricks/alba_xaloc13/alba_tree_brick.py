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
from mxcubeqt.bricks.tree_brick import TreeBrick
from mxcubeqt.utils import qt_import
from mxcubecore import HardwareRepository as HWR
import os


__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"

###
### Pick Button
###
class AlbaTreeBrick(TreeBrick):

    def __init__(self, *args):
        TreeBrick.__init__(self, *args)
        self.logger = logging.getLogger("GUI")
        self.logger.info("AlbaTreeBrick.__init__()")
        
        self.pick_button = qt_import.QPushButton('Mount & Pick')
        
        #Add the button to the layout created in tree_brick.TreeBrick,
        #below ISPyB button
        self.sample_changer_widget.gridLayout_2.addWidget(self.pick_button, 3, 3)
        self.logger.info(self.pick_button.text())
        
        # Slots -----------------------------------------------------------------
        self.connect(HWR.beamline.lims, "ispyb_sync_successful", self.enable_pick)
        self.sample_changer_widget.centring_cbox.setCurrentIndex(2)
        self.dc_tree_widget.set_centring_method(2)

    def pick(self):
        if HWR.beamline.sample_changer is not None:
            pass
            #if not items[0].get_model().free_pin_mode:
                #HWR.beamline.sample_changer.mount_and_pick = True
                ## now find the next sample. Possible useful functions are
                ## dc_tree_widget get_mounted_sample_item, samples_from_lims
                ## HWR ISPyBClient __find_sample
                
                
                    #lid = HWR.beamline.sample_changer.cats_loaded_lid
                    #sample = HWR.beamline.sample_changer.cats_loaded_num
                    #sample2 = HWR.beamline.sample_changer.chnPickedSample.getValue()
                    #self.logger.info("do_pick: Lid={}, sample={}, sample2={}".format(lid, sample, sample2))
                #items[0].setText(1, "Loading sample...")
                #self.sample_centring_result = gevent.event.AsyncResult()
                #try:
                    #if self.show_sc_during_mount:
                        #self.tree_brick.sample_mount_started.emit()
                    #queue_entry.mount_sample(
                        #items[0],
                        #items[0].get_model(),
                        #self.centring_done,
                        #self.sample_centring_result
                    #)
                    #if self.close_kappa:
                        #HWR.beamline.diffractometer.close_kappa()
            #HWR.beamline.sample_changer.do_pick()
                #except Exception as e:
                    #items[0].setText(1, "Error loading")
                    #items[0].set_background_color(3)
                    #msg = "Error loading sample, " + str(e)
                    #logging.getLogger("GUI").error(msg)
                #finally:
                    #self.enable_collect(True)
                    #self.tree_brick.sample_mount_finished.emit()
            #else:
                #logging.getLogger("GUI").\
                    #info('Its not possible to mount samples in free pin mode')

    def enable_pick(self):
        self.pick_button.setEnabled(True)

    def disable_pick(self):
        self.pick_button.setEnabled(False)

    @qt_import.pyqtSlot(bool)
    def logged_in(self, logged_in):
        if not logged_in:
            self.disable_pick()
        TreeBrick.logged_in(self, logged_in)


    # def updateBeam(self,force=False):
    #     if self["displayBeam"]:
    #           if not self.minidiff.isReady(): time.sleep(0.2)
    #           beam_x = self.minidiff.getBeamPosX()
    #           beam_y = self.minidiff.getBeamPosY()
    #           try:
    #              self.__rectangularBeam.set_xMid_yMid(beam_x,beam_y)
    #           except AttributeError:
    #              pass
    #           try:
    #             self.__beam.move(beam_x, beam_y)
    #             try:
    #                 # TODO FIXME ERROR: get_beam_info is a function - this cannot be right
    #               get_beam_info = self.minidiff.getBeamInfo #getCommandObject("getBeamInfo")
    #               if force or get_beam_info: #.isSpecReady():
    #                   self._updateBeam({"size_x":0.045, "size_y":0.025, "shape": "rectangular"})
    #             except:
    #               logging.getLogger().exception("Could not get beam size: cannot display beam")
    #               self.__beam.hide()
    #           except AttributeError:
    #             pass
