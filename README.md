
############## 
A simple ROS wrapper for using Pocketsphinx (via gstreamer) with ROS. See docs here http://wiki.ros.org/pocketsphinx
##




Tested in:
- ROS Kinectic 
- Ubuntu 16.04
 
 
Requirements:
```
sudo apt-get install gstreamer1.0-pocketsphinx  gstreamer1.0-plugins-base  gst-inspect-1.0 pocketsphinx
```
FAQ
1. Issue associated with those robots with no display
    * Install the [Xvfb − virtual framebuffer X server for X Version 11](https://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
        ```
            sudo apt-get install xvfb
        ```   
    * Now, in the terminal where you are (ros)launching the pocksphinx
        ``` 
            export DISPLAY=:1        
        ```   
2. 
  

References>

1. [Michael Ferguson](https://github.com/mikeferguson/pocketsphinx)
2. [Using PocketSphinx with GStreamer and Python](http://cmusphinx.sourceforge.net/wiki/gstreamer)
3. [Vadimreutskiy](https://github.com/vadimreutskiy/pocketsphinx)