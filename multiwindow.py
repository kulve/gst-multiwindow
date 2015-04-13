#!/usr/bin/python3

# Originally from
# http://bazaar.launchpad.net/~jderose/+junk/gst-examples/view/head:/video-player-1.0

from os import path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk
import argparse
import math
from time import sleep

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

# Workaround: If > 0, sleep between enabling pipelines (0.1 == 100ms)
WORKAROUND_SLEEP_SEC = 0.0

GObject.threads_init()
Gst.init(None)

class Player(object):
    def __init__(self):
        self.hbox = []
        self.xid = []
        self.bus = []
        self.pipeline = []
        self.drawingarea = []

        self.window = Gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(800, 450)

        self.dim = math.ceil(math.sqrt(len(args.uris)))

        # Vertical box
        self.vbox = Gtk.VBox(homogeneous=True, spacing=0)

        # Pack vbox to window
        self.window.add(self.vbox)

        # Add hboxes to the vbox
        for y in range(self.dim):
            self.hbox.append(Gtk.HBox(homogeneous=True, spacing=0))
            self.vbox.pack_end(self.hbox[y], expand=True, fill=True, padding=0)

            # Pack drawing areas to the hbox[y]
            for x in range(self.dim):
                id = y * self.dim + x
                self.drawingarea.append(Gtk.DrawingArea())
                self.hbox[y].pack_end(self.drawingarea[id], expand=True, fill=True, padding=0)

                # Create new GStreamer pipeline
                if (id < len(args.uris)):
                    self.pipeline.append(self.new_pipeline(args.uris[id]))

    def new_pipeline(self, mediauri):

        pipeline = Gst.Pipeline()

        if (not pipeline):
            print ('Failed to create pipeline')
            exit (-1)

        # Create bus to get events from GStreamer pipeline
        bus = pipeline.get_bus()
        self.bus.append(bus)
        bus.add_signal_watch()
        bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.on_sync_message)

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
        # Link decodebin to video sink
        dbin.link(videosink)
        pipeline.set_state(Gst.State.PLAYING)
        if (WORKAROUND_SLEEP_SEC > 0):
            sleep(WORKAROUND_SLEEP_SEC)

    def run(self):
        self.window.show_all()

        for y in range(self.dim):
            for x in range(self.dim):
                id = y * self.dim + x
                if (id < len(args.uris)):
                    # Store XID
                    # FIXME: why the drawing are index order must be reversed to get first video on the top left corner?
                    self.xid.append(self.drawingarea[self.dim*self.dim - id - 1].get_property('window').get_xid())

                    # Prepare the pipeline
                    self.pipeline[id].set_state(Gst.State.PAUSED)

        Gtk.main()

    def quit(self, window):
        for y in range(self.dim):
            for x in range(self.dim):
                id = y * self.dim + x
                if (id < len(args.uris)):
                    self.pipeline[id].set_state(Gst.State.NULL)

        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() != 'prepare-window-handle':
            return

        # Find which bus matches this one
        for y in range(self.dim):
            for x in range(self.dim):
                id = y * self.dim + x
                if (id == len(args.uris)):
                    return

                if (self.bus[id] == bus):
                    # Set XID
                    msg.src.set_window_handle(self.xid[id])

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())

parser = argparse.ArgumentParser(description='Show NxN video windows')
parser.add_argument('uris', metavar='uri', nargs='+',  help='URI to show')
args = parser.parse_args()

p = Player()
p.run()
