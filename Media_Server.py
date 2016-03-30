__author__ = 'giacomo'

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import os
import gi
import sys
import time
import Media_Streams_Class
try:
    gi.require_version('Gst', '1.0')
except ValueError:
    print('Could not find required Gstreamer library')
try:
    gi.require_version('GdkX11', '3.0')
except ValueError:
    print('Could not find required GdkX11 library')
try:
    gi.require_version('Gtk', '3.0')
except ValueError:
    print('Could not find required Gtk library')
try:
    gi.require_version('GstVideo', '1.0')
except ValueError:
    print('Could not find required GstVideo library')
    sys.exit(1)
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import GdkX11    # Needed for window.get_xid(), xvimagesink.set_window_handle()
from gi.repository import GstVideo  # for sink.set_window_handle()
from Media_Streams_Class import Media_Streams_Class
from os import listdir
from os.path import isfile, join


os.environ["GST_DEBUG"] = "1"
GObject.threads_init()
Gst.init(None)



class Regia(object):

    def exit(self, widget, data=None):
        Gtk.main_quit ()
        self.media_streams.saving_path = self.entry_savePath.get_text()
        self.media_streams.close()

    def on_destroy(self, window):
        self.media_streams.close()
        Gtk.main_quit ()

    def change_camera(self, button, index):
        self.media_streams.select_branch_onair(index)

    def button_clicked(self, button):
        self.media_streams.saving_path = self.entry_savePath.get_text()
        self.media_streams.add_stream(self.entry_URI.get_text())
        # if self.media_streams.list_of_streams[self.media_streams.n_branch-1].get_state() == Gst.State.NULL:
        button = Gtk.Button("Camera "+str(self.media_streams.n_branch))
        button.connect("clicked", self.change_camera, self.media_streams.n_branch)
        self.hbox3.pack_start(button, False, False, 0)
        self.window.show_all()


    def buttonStream_clicked(self, button):
        print("ho cliccato")
        tree_iter = self.combo.get_active_iter()
        if tree_iter != None:
            model = self.combo.get_model()
            row_id, name = model[tree_iter][:2]
            self.media_streams.get_stream(self.entry_savePath.get_text()+name)
        else:
            print("Please, select a file from the list!")




    def on_name_combo1_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            self.streaming_type=name
        else:
            entry = combo.get_child()
            print("Entered: %s" % entry.get_text())


    def __init__(self):
        # Create transcoding media_streams
        self.media_streams = Media_Streams_Class()

        #Create a window with two buttons
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title("LYS - Broadcaster Console")
        self.window.set_default_size(600, 500)
        self.window.connect('destroy', self.on_destroy)

        self.vbox = Gtk.VBox()
        self.window.add(self.vbox)

        # self.hbox1 = Gtk.HBox()
        self.hbox1 = self.media_streams.video_streams_Windows
        self.vbox.pack_start(self.hbox1, True, True, 0)
        #
        self.hbox2 = self.media_streams.on_air_Window
        self.vbox.pack_start(self.hbox2, True, True, 0)

        self.hbox3 = Gtk.HBox()
        self.vbox.pack_start(self.hbox3, False, False, 0)

        self.hbox3.set_border_width(10)
        button = Gtk.Button("Quit")
        button.connect("clicked", self.exit)
        self.hbox3.pack_start(button, False, False, 0)

        self.entry_URI = Gtk.Entry()
        self.entry_URI.set_text("rtsp://127.0.0.1:8554/stream")

        label_archive = Gtk.Label("Path where you save your streams: ")
        label_URI = Gtk.Label("Insert a valid URI for RTP/RTSP: ")

        button = Gtk.Button("Add stream")
        button.connect("clicked", self.button_clicked)

        self.entry_savePath = Gtk.Entry()
        self.entry_savePath.set_text("/home/giacomo/streams_salvati/")

        table = Gtk.Table(2,4,False)
        table.attach(label_URI,0,1,0,1)
        table.attach(self.entry_URI,0,1,1,2)
        # table.attach(label_port,1,2,0,1)
        # table.attach(self.entry_port,1,2,1,2)
        table.attach(label_archive,2,3,0,1)
        table.attach(self.entry_savePath,2,3,1,2)
        table.attach(button,3,4,1,2)
        self.vbox.pack_start(table, False, False, 0)


        label_toStream = Gtk.Label("Select a file to stream via rtsp (video on demand): ")
        buttonStream = Gtk.Button("Stream")
        buttonStream.connect("clicked", self.buttonStream_clicked)

        store = Gtk.ListStore(int, str)
        n = 0
        for f in listdir("/home/giacomo/streams_salvati/"):
            if isfile(join("/home/giacomo/streams_salvati/", f)):
                n = n + 1
                store.append([n, f])

        self.combo = Gtk.ComboBox.new_with_model_and_entry(store)
        self.combo.set_entry_text_column(1)

        table1 = Gtk.Table(2,4,False)
        table1.attach(label_toStream,0,1,0,1)
        table1.attach(self.combo,0,1,1,2)
        table1.attach(buttonStream,2,3,1,2)
        self.vbox.pack_start(table1, False, False, 0)


        self.window.show_all()

Regia()
Gtk.main()
