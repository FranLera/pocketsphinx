
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
    * Install [Xvfb − virtual framebuffer X server for X Version 11](https://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
        
        ```
            sudo apt-get install xvfb
        ```   
  
    * Now, you can add this in your .bashrc or run in a new terminal:

        ``` 
            Xvfb :1 &        
        ```         
    
    
    
    * Now, in the terminal where you are (ros)launching the pocksphinx
  
        ``` 
            export DISPLAY=:1        
        ```   
        

2. How to get the values by default of the gstreamer and the possible parameters for your application
        ``` 
            gst-inspect-1.0 pocketsphinx
        ``` 

3. The value given as a confidence, seems not useful and maybe is not supported through [gstreamer version](https://sourceforge.net/p/cmusphinx/discussion/help/thread/0197b952/?limit=25) 
The trick will be to move to the pocketsphinx version instead of using this.
The example provided in [Pocketsphinx Repo shows how it works ](https://github.com/cmusphinx/pocketsphinx/blob/master/swig/python/test/decoder_test.py) seems similar to that that most people need.

        
References>

1. [Michael Ferguson](https://github.com/mikeferguson/pocketsphinx)
2. [Using PocketSphinx with GStreamer and Python](http://cmusphinx.sourceforge.net/wiki/gstreamer)
3. [Vadimreutskiy](https://github.com/vadimreutskiy/pocketsphinx)
4. [Python GStreamer Tutorial](http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.pdf)
5. [CMU pocketsphinx](https://github.com/cmusphinx/pocketsphinx/blob/master/)
