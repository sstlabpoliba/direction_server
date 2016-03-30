__author__ = 'Giacomo Difruscolo'

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
import ctypes
if sys.platform.startswith('linux'):
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except:
        print("Warning: failed to XInitThreads()")
try:
    gi.require_version('Gst', '1.0')
except ValueError:
    print('Could not find required Gstreamer library')
try:
    gi.require_version('GstRtspServer', '1.0')
except ValueError:
    print('Could not find required GstRtspServer library')
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
from gi.repository import GstRtspServer
from gi.repository import Gtk
from gi.repository import GdkX11    # Needed for window.get_xid(), xvimagesink.set_window_handle()
from gi.repository import GstVideo  # for sink.set_window_handle()


os.environ["GST_DEBUG"] = "1"
os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/home/giacomo/streams_salvati"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', "/home/giacomo/streams_salvati")

GObject.threads_init()
Gst.init(None)

class Media_Streams_Class():
    n_branch = 0
    saving_path = ""
    pipeline_ON_AIR = None
    list_of_URI = []
    list_of_streams = []
    video_streams_Windows = Gtk.HBox()
    on_air_Window = Gtk.HBox()

    # This method captures messages and errors from pipelines
    # for video streaming cameras
    def on_message(self, bus, message, pipeline):
        t = message.type
        if t == Gst.MessageType.EOS:
            pipeline.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            pipeline.set_state(Gst.State.NULL)

    # autovideosink hasn't set_window_handle(xid) method.
    # So I have to capture it in "on sync message" event
    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            newimagesink = message.src
            newimagesink.set_property("force-aspect-ratio", True)
            movie_window = Gtk.DrawingArea()
            self.video_streams_Windows.add(movie_window)
            self.video_streams_Windows.show_all()
            xid = movie_window.get_property('window').get_xid()
            newimagesink.set_window_handle(xid)

    # This method captures messages and errors from pipeline
    # for "ON AIR" camera
    def on_message_ON_AIR(self, bus, message,pipeline_on_air):
        t = message.type
        if t == Gst.MessageType.EOS:
            pipeline_on_air.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            pipeline_on_air.set_state(Gst.State.NULL)

    # autovideosink hasn't set_window_handle(xid) method.
    # So I have to capture it in "on sync message" event
    def on_sync_message_ON_AIR(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            newimagesink = message.src
            newimagesink.set_property("force-aspect-ratio", True)
            movie_window = Gtk.DrawingArea()
            self.on_air_Window.add(movie_window)
            self.on_air_Window.show_all()
            xid = movie_window.get_property('window').get_xid()
            newimagesink.set_window_handle(xid)


    # Close all pipelines cameras and "ON AIR" pipeline
    # Draw ON AIR pipeline in PNG and DOT files
    def close(self):
        if self.n_branch > 0:
            if not os.path.exists(self.saving_path):
                os.mkdir(self.saving_path)
            elif not os.path.isdir(self.saving_path):
                raise Exception("Output directory %s already exists as a file" % self.saving_path)
            for stream in self.list_of_streams:
                stream.set_state(Gst.State.NULL)


            # Gst.debug_bin_to_dot_file(self.pipeline_ON_AIR, Gst.DebugGraphDetails.ALL, "pipeline_ON_AIR")
            # os.system("dot -Tpng -o " + self.saving_path + "pipeline_ON_AIR.png " + self.saving_path+ "pipeline_ON_AIR.dot" )



            dotfile = self.saving_path+ "pipeline_ON_AIR.dot"
            pngfile = self.saving_path + "pipeline_ON_AIR.png "
            if os.access(dotfile, os.F_OK):
                os.remove(dotfile)
            if os.access(pngfile, os.F_OK):
                os.remove(pngfile)
            Gst.debug_bin_to_dot_file(self.pipeline_ON_AIR, Gst.DebugGraphDetails.ALL, "pipeline_ON_AIR")
            # # check if graphviz is installed with a simple test
            # try:
            #     dot = which.which("dot")
            os.system("dot" + " -Tpng -o " + pngfile + " " + dotfile)
            #     Gtk.show_uri(None, "file://"+pngfile, 0)
            # except which.WhichError:
            #     print "The debug feature requires graphviz (dot) to be installed."
            #     print "Transmageddon can not find the (dot) binary."




            time.sleep(.10)
            self.pipeline_ON_AIR.send_event(Gst.Event.new_eos())

    # Call this method to change ON AIR camera (audio and video)
    def select_branch_onair(self, index):
        # Switch video input-selector to selected video ON AIR
        videoselector = self.pipeline_ON_AIR.get_by_name('videoswitcher')
        new_pad = videoselector.get_static_pad("sink_%s" %(index-1))
        videoselector.set_property("active-pad", new_pad)
        # Switch audio input-selector to selected audio ON AIR
        audioselector = self.pipeline_ON_AIR.get_by_name('audioswitcher')
        new_pad = audioselector.get_static_pad("sink_%s" %(index-1))
        audioselector.set_property("active-pad", new_pad)

    # Call this method to stream Video On Demand
    def get_stream(self, uri):
        server = GstRtspServer.RTSPServer()
        server.set_service('8555')
        # server.connect("client-connected",self.new_client_handler)

        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(" filesrc location=" + uri + " ! decodebin name=d ! videoconvert ! videoscale ! video/x-raw,width=320,height=240,pixel-aspect-ratio=1/1 ! x264enc ! rtph264pay name=pay0 pt=96 d. ! audioconvert ! audioresample ! audio/x-raw ! mulawenc ! rtppcmupay  name=pay1 pt=96 ")

        # factory.connect("media-configure", self.on_media_configure)
        factory.set_shared(True)
        server.get_mount_points().add_factory("/video", factory)
        server.attach(None)
        print("stream ready at rtsp://127.0.0.1:8555/video")



    # Call this method to add another incoming stream from RTSP uri.
    def add_stream(self, uri):
        video_added = ""

        self.n_branch = self.n_branch + 1
        self.list_of_URI.append(uri)
        # For each incoming stream a new pipeline has been added
        p_description = "playbin uri=%s " %uri + "mute=true"
        new_pipeline = Gst.parse_launch(p_description)
        new_pipeline.name = "pipeline_" + str(self.n_branch)
        videobin = Gst.Bin.new("videobin"+str(self.n_branch))
        timeoverlay = Gst.ElementFactory.make("timeoverlay","timeoverlay"+str(self.n_branch))
        videobin.add(timeoverlay)
        textoverlay = Gst.ElementFactory.make("textoverlay","textoverlay"+str(self.n_branch))
        textoverlay.set_property("text","CAM " + str(self.n_branch))
        textoverlay.set_property("font-desc","Sans 24")
        textoverlay.set_property("valignment","top")
        textoverlay.set_property("halignment","right")
        textoverlay.set_property("shaded-background","true")
        videobin.add(textoverlay)
        pad = timeoverlay.get_static_pad("video_sink")
        ghostpad = Gst.GhostPad.new("sink", pad)
        videobin.add_pad(ghostpad)
        queuesink = Gst.ElementFactory.make("queue","queuesink"+str(self.n_branch))
        videobin.add(queuesink)
        videosink = Gst.ElementFactory.make("autovideosink","autovideosink"+str(self.n_branch))
        # videosink.set_property("sync","false")
        videobin.add(videosink)

        if not timeoverlay.link(textoverlay):
            return None
        if not textoverlay.link(queuesink):
            return None
        if not queuesink.link(videosink):
            return None

        new_pipeline.set_property("video-sink", videobin)

        # Sets buses for events on the pipeline
        bus = new_pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message, new_pipeline)
        bus.connect("sync-message::element", self.on_sync_message)

        ret = new_pipeline.set_state(Gst.State.PLAYING)
        # ret = new_pipeline.get_state(Gst.CLOCK_TIME_NONE)
        if ret == Gst.StateChangeReturn.FAILURE:
                print("Unable to set the pipeline to the playing state.\n")
                return -1

        self.list_of_streams.append(new_pipeline)


        # To save each incoming stream a new pipeline has been added
        p_description = "uridecodebin uri=" + uri + " name=src ! \
        queue ! theoraenc ! queue !  oggmux name=mux \
         src. ! queue ! audioconvert ! vorbisenc ! queue ! mux.\
          mux. ! queue ! filesink location=" + self.saving_path + "stream_%s.ogg"%str(self.n_branch)

        new_pipeline = Gst.parse_launch(p_description)
        new_pipeline.name = "pipeline_to_save_" + str(self.n_branch)

        # Sets buses for events on the pipeline
        bus = new_pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message, new_pipeline)
        bus.connect("sync-message::element", self.on_sync_message)

        ret = new_pipeline.set_state(Gst.State.PLAYING)
        # ret = new_pipeline.get_state(Gst.CLOCK_TIME_NONE)
        if ret == Gst.StateChangeReturn.FAILURE:
                print("Unable to set the pipeline to the playing state.\n")
                return -1

        self.list_of_streams.append(new_pipeline)


        # If it is the first branch, it becomes ON AIR camera. It has "input-selector" for the audio and the video so
        # you can switch between them to do your directing
        if self.n_branch == 1:
            ################### CREATE VIDEO ON_AIR BRANCH ###################
            p_description = "input-selector  name = videoswitcher input-selector name = audioswitcher \
                uridecodebin uri=%s " %uri + " name =uridecodebin_1_ON_AIR uridecodebin_1_ON_AIR. ! \
                queue name = queue_1v_ON_AIR  ! videoswitcher.sink_%u  videoswitcher. ! queue name = queue_v_ON_AIR ! \
                videoconvert name =videoconvert_v_ON_AIR ! autovideosink  name= autovideosink_ON_AIR \
                uridecodebin_1_ON_AIR. ! queue name = queue_1a_ON_AIR  ! audioswitcher.sink_%u  audioswitcher. ! queue name = queue_a_ON_AIR ! \
                audioconvert name =audioconvert_ON_AIR !  audioresample name =audioresample_ON_AIR  ! \
                autoaudiosink name =autoaudiosink_ON_AIR  "

            self.pipeline_ON_AIR = Gst.parse_launch(p_description)
            bus = self.pipeline_ON_AIR.get_bus()
            bus.add_signal_watch()
            bus.enable_sync_message_emission()
            bus.connect("message", self.on_message_ON_AIR, self.pipeline_ON_AIR)
            bus.connect("sync-message::element", self.on_sync_message_ON_AIR)
            ret = self.pipeline_ON_AIR.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                    print("Unable to set the pipeline to the playing state.\n")
                    return -1
        else:
            # Create a new videobranch for the added stream. This branch is connected to input-selector for the video
            new_uridecodebin = Gst.ElementFactory.make("uridecodebin","uridecodebin_" + str(self.n_branch) + "_ON_AIR")
            new_uridecodebin.set_property("uri", uri)
            self.pipeline_ON_AIR.add(new_uridecodebin)

            videoswitcher = self.pipeline_ON_AIR.get_by_name('videoswitcher')

            new_videoqueue = Gst.ElementFactory.make("queue","queue_" + str(self.n_branch) + "v_ON_AIR")
            self.pipeline_ON_AIR.add(new_videoqueue)

            # Create a new audiobranch for the added stream.This branch is connected to input-selector for the audio
            audioswitcher = self.pipeline_ON_AIR.get_by_name('audioswitcher')

            new_audioqueue = Gst.ElementFactory.make("queue","queue_" + str(self.n_branch) + "a_ON_AIR")
            self.pipeline_ON_AIR.add(new_audioqueue)

            new_uridecodebin.connect("pad-added", self.uridecodebin_pad_added, [new_videoqueue,new_audioqueue])

            # here I link elements (video and audio) and I set their states to PLAYING in correct order!!
            new_sinkpad = videoswitcher.get_request_pad("sink_%u")
            (new_videoqueue.get_static_pad('src')).link(new_sinkpad)
            new_uridecodebin.set_state(Gst.State.PLAYING)
            new_videoqueue.set_state(Gst.State.PLAYING)

            new_sinkpad = audioswitcher.get_request_pad("sink_%u")
            (new_audioqueue.get_static_pad('src')).link(new_sinkpad)
            new_uridecodebin.set_state(Gst.State.PLAYING)
            new_audioqueue.set_state(Gst.State.PLAYING)


    # This method captures "pad added" event on rtspsrc when a new
    # incoming stream has been added to ON AIR pipeline
    def uridecodebin_pad_added(self, element, new_pad, elements_to_link):
        if new_pad.direction != Gst.PadDirection.SRC:
            return
        caps = new_pad.query_caps(None)
        name = new_pad.get_name()
        print('on_pad_added:', name)
        capsTostring = caps.to_string()
        print(capsTostring)
        # pad.get_property("template").name_template == "video_%02d"
        if name=='src_0':
            new_pad.link(elements_to_link[0].get_static_pad("sink"))
            print("Video stream is coming")
        elif name=='src_1':
            new_pad.link(elements_to_link[1].get_static_pad("sink"))
            print("Audio stream is coming")


