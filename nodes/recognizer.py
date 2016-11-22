#!/usr/bin/env python2

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system. See LICENSE for more information.


"""
recognizer.py is a wrapper for pocketsphinx.
  parameters:
    ~lm - filename of language model
    ~dict - filename of dictionary
    ~mic_name - set the pulsesrc device name for the microphone input.
                e.g. a Logitech G35 Headset has the following device name: alsa_input.usb-Logitech_Logitech_G35_Headset-00-Headset_1.analog-mono
                To list audio device info on your machine, in a terminal type: pacmd list-sources
  publications:
    ~output (std_msgs/String) - text output
  services:
    ~start (std_srvs/Empty) - start speech recognition
    ~stop (std_srvs/Empty) - stop speech recognition
"""

import roslib; roslib.load_manifest('pocketsphinx')
import rospy


from gi import pygtkcompat
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
GObject.threads_init()
Gst.init(None)
    
gst = Gst
    
print("Using pygtkcompat and Gst from gi")

pygtkcompat.enable() 
pygtkcompat.enable_gtk(version='3.0')

import gtk

from std_msgs.msg import String
from std_srvs.srv import *
import os
import commands

from pprint import pprint

LOG_ACTIVE=False

class Recognizer(object):
    """GStreamer/PocketSphinx Demo Application"""

    def __init__(self):
     
        """Initialize ROS components"""
        self.init_ros()
        
        """Initialize gstreamer components"""
        self.init_gst()
        

    
    """Method: Initialize ROS components"""
    def init_ros(self):
        rospy.init_node("recognizer")

        self._device_name_param = "~mic_name"  # Find the name of your microphone by typing pacmd list-sources in the terminal
        self._lm_param = "~lm"
        self._dic_param = "~dict"

        # Configure mics with gstreamer launch config
        if rospy.has_param(self._device_name_param):
            self.device_name = rospy.get_param(self._device_name_param)
            self.device_index = self.pulse_index_from_name(self.device_name)
            self.launch_config = "pulsesrc device=" + str(self.device_index)
            rospy.loginfo("Using: pulsesrc device=%s name=%s", self.device_index, self.device_name)
        elif rospy.has_param('~source'):
            # common sources: 'alsasrc'
            self.launch_config = rospy.get_param('~source')
        else:
            self.launch_config = 'gconfaudiosrc'

        rospy.loginfo("Launch config: %s", self.launch_config)
        
        # Configure ROS settings
        self.started = False
        rospy.on_shutdown(self.shutdown)
        self.pub = rospy.Publisher('~output', String, queue_size=10)
        rospy.Service("~start", Empty, self.start)
        rospy.Service("~stop", Empty, self.stop)

        if rospy.has_param(self._lm_param) and rospy.has_param(self._dic_param):
            rospy.loginfo("We are running the recognizer with the roslaunch parameters")
        else:
            rospy.logwarn("lm and dic parameters need to be set to start recognizer for your system.")
            rospy.logwarn("We are running with the parameters by default.")
          
            
        
    def init_gst(self):
        """Initialize the speech components"""
        self.pipeline = gst.parse_launch('autoaudiosrc ! audioconvert ! audioresample '
                                         + '! pocketsphinx name=asr lm=/usr/share/pocketsphinx/model/en-us/en-us.lm.bin dict=/usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict ! fakesink')
        
        self.asr = self.pipeline.get_by_name('asr')
        
        
        # Configure language model
        if rospy.has_param(self._lm_param):
            lm = rospy.get_param(self._lm_param)
        else:
            rospy.logerr('Recognizer not started. Please specify a language model file.')
            return

        # Configure Dictionary
        if rospy.has_param(self._dic_param):
            dic = rospy.get_param(self._dic_param)
        else:
            rospy.logerr('Recognizer not started. Please specify a dictionary.')
            return
        
        
        self.asr.set_property('lm', lm)
        self.asr.set_property('dict', dic)
        self.asr.set_property('configured', True)
        self.asr.set_property('dsratio', 1)
        
        
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::element', self.element_message)
        
        self.pipeline.set_state(gst.State.PLAYING)
       
        
        

    def element_message(self, bus, msg):
        """Receive element messages from the bus."""
        msgtype = msg.get_structure().get_name()
        
        if LOG_ACTIVE:
            rospy.loginfo("XXXXX > %s",msg.get_structure().get_value('timestamp'))
            rospy.loginfo("XXXXX > %s",msg.get_structure().get_value('final'))
            rospy.loginfo("XXXXX > %s",msg.get_structure().get_value('hypothesis'))
            rospy.loginfo("XXXXX > %f",msg.get_structure().get_value('confidence'))
            #rospy.loginfo(msg.get_structure().get_value('confidence'))
            #print dir(msg.get_structure())
            #pprint (vars(msg))
        
        
        if msgtype != 'pocketsphinx':
            return

        if msg.get_structure().get_value('final'):
            self.final_result(msg.get_structure().get_value('hypothesis'), msg.get_structure().get_value('confidence'))
        elif msg.get_structure().get_value('hypothesis'):
            self.partial_result(msg.get_structure().get_value('hypothesis'))


    def partial_result(self, hyp):
        msg = String()
        msg.data = str(hyp.lower())
        rospy.loginfo("Partial > %s", msg.data)
        

    def final_result(self, hyp, confidence):
        """ Insert the final result. """
        msg = String()
        msg.data = str(hyp.lower())
        rospy.loginfo("Final > %s",msg.data)
        self.pub.publish(msg)
        
          
            
    def pulse_index_from_name(self, name):
        output = commands.getstatusoutput("pacmd list-sources | grep -B 1 'name: <" + name + ">' | grep -o -P '(?<=index: )[0-9]*'")

        if len(output) == 2:
            return output[1]
        else:
            raise Exception("Error. pulse index doesn't exist for name: " + name)
    def stop_recognizer(self):
        if self.started:
            self.pipeline.set_state(gst.STATE_NULL)
            self.pipeline.remove(self.asr)
            self.bus.disconnect(self.bus_id)
            self.started = False

    def shutdown(self):
        """ Delete any remaining parameters so they don't affect next launch """
        for param in [self._device_name_param, self._lm_param, self._dic_param]:
            if rospy.has_param(param):
                rospy.delete_param(param)

        """ Shutdown the GTK thread. """
        gtk.main_quit()

    def start(self, req):
        self.start_recognizer()
        rospy.loginfo("recognizer started")
        return EmptyResponse()

    def stop(self, req):
        self.stop_recognizer()
        rospy.loginfo("recognizer stopped")
        return EmptyResponse()
    

if __name__ == "__main__":
    try:
        rospy.loginfo("Starting ....")
        start = Recognizer()
        gtk.main()
    except rospy.ROSInterruptException:
        pass
