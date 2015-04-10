#!/usr/bin/python3

# Originally from
# http://bazaar.launchpad.net/~jderose/+junk/gst-examples/view/head:/video-player-1.0

from os import path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk
import argparse

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

GObject.threads_init()
Gst.init(None)
uri=""

class Player(object):
    def __init__(self):
        self.window = Gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(800, 450)

        # Vertical box
        self.vbox = Gtk.VBox(homogeneous=True, spacing=0)

        # Upper and lower horizontal boxes
        self.hbox_up = Gtk.HBox(homogeneous=True, spacing=0)
        self.hbox_down = Gtk.HBox(homogeneous=True, spacing=0)

        # Pack boxes to window
        self.window.add(self.vbox)
        self.vbox.pack_end(self.hbox_up, expand=True, fill=True, padding=0)
        self.vbox.pack_end(self.hbox_down, expand=True, fill=True, padding=0)

        # 2x2 drawing areas
        self.drawingarea_tl = Gtk.DrawingArea()
        self.drawingarea_tr = Gtk.DrawingArea()
        self.drawingarea_bl = Gtk.DrawingArea()
        self.drawingarea_br = Gtk.DrawingArea()

        # Pack drawing areas to boxes
        self.hbox_up.pack_end(self.drawingarea_tl, expand=True, fill=True, padding=0)
        self.hbox_up.pack_end(self.drawingarea_tr, expand=True, fill=True, padding=0)
        self.hbox_down.pack_end(self.drawingarea_bl, expand=True, fill=True, padding=0)
        self.hbox_down.pack_end(self.drawingarea_br, expand=True, fill=True, padding=0)

        # Create 2x2 GStreamer pipelines
        self.pipeline_tl = self.new_pipeline(self.on_sync_message_tl, args.uris[0])
        self.pipeline_tr = self.new_pipeline(self.on_sync_message_tr, args.uris[1])
        self.pipeline_bl = self.new_pipeline(self.on_sync_message_bl, args.uris[2])
        self.pipeline_br = self.new_pipeline(self.on_sync_message_br, args.uris[3])

    def new_pipeline(self, sync_msg_cb, mediauri):

        pipeline = Gst.Pipeline()

        if (not pipeline):
            print ('Failed to create pipeline')
            exit (-1)

        # Create bus to get events from GStreamer pipeline
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', sync_msg_cb)

        # Create GStreamer elements
        decodebin = Gst.ElementFactory.make('uridecodebin', 'decodebin')
        videosink = Gst.ElementFactory.make('nveglglessink', 'videosink')

        if (not decodebin or not videosink):
            print ('Failed to create uridecodebin and/or nveglglessink')
            exit(-1)

        # Set properties
        decodebin.set_property('uri', mediauri)
        videosink.set_property('create-window', False)

        # Add elements to the pipeline
        pipeline.add(decodebin)
        pipeline.add(videosink)

        decodebin.connect("pad-added", self.decodebin_pad_added)

        return pipeline

    def decodebin_pad_added(self, dbin, pad):
        pipeline = dbin.get_parent()
        videosink = pipeline.get_by_name('videosink')
        dbin.link(videosink)
        pipeline.set_state(Gst.State.PLAYING)
        print('Decodebin linked to videosink')

    def run(self):
        self.window.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid_tl = self.drawingarea_tl.get_property('window').get_xid()
        self.xid_tr = self.drawingarea_tr.get_property('window').get_xid()
        self.xid_bl = self.drawingarea_bl.get_property('window').get_xid()
        self.xid_br = self.drawingarea_br.get_property('window').get_xid()

        # Prepare all pipelines
        self.pipeline_tl.set_state(Gst.State.PAUSED)
        self.pipeline_tr.set_state(Gst.State.PAUSED)
        self.pipeline_bl.set_state(Gst.State.PAUSED)
        self.pipeline_br.set_state(Gst.State.PAUSED)
        Gtk.main()

    def quit(self, window):
        self.pipeline_tl.set_state(Gst.State.NULL)
        self.pipeline_tr.set_state(Gst.State.NULL)
        self.pipeline_bl.set_state(Gst.State.NULL)
        self.pipeline_br.set_state(Gst.State.NULL)
        Gtk.main_quit()


    def set_xid(self, msg, xid):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_window_handle(xid)

    def on_sync_message_tl(self, bus, msg):
        self.set_xid(msg, self.xid_tl)

    def on_sync_message_tr(self, bus, msg):
        self.set_xid(msg, self.xid_tr)

    def on_sync_message_bl(self, bus, msg):
        self.set_xid(msg, self.xid_bl)

    def on_sync_message_br(self, bus, msg):
        self.set_xid(msg, self.xid_br)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())

parser = argparse.ArgumentParser(description='Show 2x2 video windows')
parser.add_argument('uris', metavar='uri', nargs=4,  help='URI to show')
args = parser.parse_args()

print("URI 1: {}".format(args.uris[0]))
print("URI 2: {}".format(args.uris[1]))
print("URI 3: {}".format(args.uris[2]))
print("URI 4: {}".format(args.uris[3]))

p = Player()
p.run()
