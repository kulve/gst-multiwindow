GStreamer multiwindow example
=============================

The code is originally taken from:
* https://wiki.ubuntu.com/Novacut/GStreamer1.0
* http://bazaar.launchpad.net/~jderose/+junk/gst-examples/view/head:/video-player-1.0
* https://github.com/kulve/gst-multiwindow

Licensed under Creative Commons Attribution-ShareAlike 3.0 Unported

Install dependencies
--------------------

```
 sudo apt-get install python-gi python3-gi \
    gstreamer1.0-tools \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-libav
```

Running
-------
```
$ ./multiwindow.py uri1 uri2 uri3 uri4


$ ./multiwindow-rtsp.py rtsp://192.168.1.168:8557/PSIA/Streaming/channels/2?videoCodecType=H.264 \
 rtsp://192.168.1.168:8557/PSIA/#Streaming/channels/2?videoCodecType=H.264 \
 rtsp://192.168.1.168:8557/PSIA/Streaming/channels/2?videoCodecType=H.264 \
 rtsp://192.168.1.168:8557/PSIA/Streaming/channels/2?videoCodecType=H.264

```
How to do test RTSP
--------------------

$ gst-launch-1.0 -v rtspsrc \
  location=rtsp://192.168.1.168:8557/PSIA/Streaming/channels/2?videoCodecType=H.264 caps="video/x-h264,mapping=/video " \
  ! rtph264depay ! h264parse  ! omxh264dec \
  ! nveglglessink -e

