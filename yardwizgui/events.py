# Copyright (c) 2013 Luke Pinner

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import wx,logging
#######################################################################
#Custom WX Events
#######################################################################
wizEVT_ADDPROGRAM = wx.NewEventType()
EVT_ADDPROGRAM = wx.PyEventBinder(wizEVT_ADDPROGRAM, 1)
class AddProgram(wx.PyCommandEvent):
    """Event to signal that a program is ready to be added"""
    def __init__(self, etype, eid, program=None, index=-1):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.program = program
        self.index = index

wizEVT_CHECKCOMPLETE = wx.NewEventType()
EVT_CHECKCOMPLETE = wx.PyEventBinder(wizEVT_CHECKCOMPLETE, 1)
class CheckComplete(wx.PyCommandEvent):
    """Event to signal that we have finished checking the recordings on the Wiz"""
    def __init__(self, etype, eid, checked, message):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.checked = checked
        self.message = message

wizEVT_CONNECTED = wx.NewEventType()
EVT_CONNECTED = wx.PyEventBinder(wizEVT_CONNECTED, 1)
class Connected(wx.PyCommandEvent):
    """Event to signal that we are connected to the Wiz and all program info has been downloaded"""
    def __init__(self, etype, eid, connected, message=''):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.connected = connected
        self.message = message

wizEVT_CONVERTCOMPLETE = wx.NewEventType()
EVT_CONVERTCOMPLETE = wx.PyEventBinder(wizEVT_CONVERTCOMPLETE, 1)
class ConvertComplete(wx.PyCommandEvent):
    """Event to signal that we have finished converting the TVWIZ files"""
    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        
wizEVT_DATETIMEUPDATED= wx.NewEventType()
EVT_DATETIMEUPDATED = wx.PyEventBinder(wizEVT_DATETIMEUPDATED, 1)
class DateTimeUpdated(wx.PyCommandEvent):
    """Event to signal that the DateTime has been updated"""
    def __init__(self, etype, eid, DateTime):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.DateTime = DateTime

wizEVT_DELETECOMPLETE = wx.NewEventType()
EVT_DELETECOMPLETE = wx.PyEventBinder(wizEVT_DELETECOMPLETE, 1)
class DeleteComplete(wx.PyCommandEvent):
    """Event to signal that deletions are complete"""
    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)

wizEVT_DELETEPROGRAM = wx.NewEventType()
EVT_DELETEPROGRAM = wx.PyEventBinder(wizEVT_DELETEPROGRAM, 1)
class DeleteProgram(wx.PyCommandEvent):
    """Event to signal that a program should be deleted"""
    def __init__(self, etype, eid, program=None, index=-1):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.program = program
        self.index = index

        wizEVT_DELETEPROGRAM = wx.NewEventType()
        EVT_DELETEPROGRAM = wx.PyEventBinder(wizEVT_DELETEPROGRAM, 1)
        class DeleteProgram(wx.PyCommandEvent):
            """Event to signal that a program should be deleted"""
            def __init__(self, etype, eid, program=None, index=-1):
                """Creates the event object"""
                wx.PyCommandEvent.__init__(self, etype, eid)
                self.program = program
                self.index = index
        
                wizEVT_DELETEPROGRAM = wx.NewEventType()
                EVT_DELETEPROGRAM = wx.PyEventBinder(wizEVT_DELETEPROGRAM, 1)
                class DeleteProgram(wx.PyCommandEvent):
                    """Event to signal that a program should be deleted"""
                    def __init__(self, etype, eid, program=None, index=-1):
                        """Creates the event object"""
                        wx.PyCommandEvent.__init__(self, etype, eid)
                        self.program = program
                        self.index = index
                
wizEVT_DOWNLOADCOMPLETE = wx.NewEventType()
EVT_DOWNLOADCOMPLETE = wx.PyEventBinder(wizEVT_DOWNLOADCOMPLETE, 1)
class DownloadComplete(wx.PyCommandEvent):
    """Event to signal that the recording has been downloaded or the download has stopped"""
    def __init__(self, etype, eid,index=-1,stopped=False):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.index=index
        self.stopped=stopped

wizEVT_LOG = wx.NewEventType()
EVT_LOG = wx.PyEventBinder(wizEVT_LOG, 1)
class Log(wx.PyCommandEvent):
    """Event to signal that there is a message to log"""
    def __init__(self, etype, eid, message=None, severity=logging.INFO):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.message = message
        self.severity = severity

wizEVT_PLAYCOMPLETE = wx.NewEventType()
EVT_PLAYCOMPLETE = wx.PyEventBinder(wizEVT_PLAYCOMPLETE, 1)
class PlayComplete(wx.PyCommandEvent):
    """Event to signal that VLC has finished playing"""
    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)

wizEVT_SCHEDULERCOMPLETE = wx.NewEventType()
EVT_SCHEDULERCOMPLETE = wx.PyEventBinder(wizEVT_SCHEDULERCOMPLETE, 1)
class SchedulerComplete(wx.PyCommandEvent):
    """Event to signal that all scheduled downloads are complete"""
    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)

wizEVT_SCHEDULEDDWONLOADCOMPLETE = wx.NewEventType()
EVT_SCHEDULEDDWONLOADCOMPLETE = wx.PyEventBinder(wizEVT_SCHEDULEDDWONLOADCOMPLETE, 1)
class ScheduledDownloadComplete(wx.PyCommandEvent):
    """Event to signal that a scheduled download is complete"""
    def __init__(self, etype, eid, program):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.program = program

wizEVT_UPDATEPROGRAM = wx.NewEventType()
EVT_UPDATEPROGRAM = wx.PyEventBinder(wizEVT_UPDATEPROGRAM, 1)
wizEVT_STREAMCOMPLETE = wx.NewEventType()
EVT_STREAMCOMPLETE = wx.PyEventBinder(wizEVT_STREAMCOMPLETE, 1)
class StreamComplete(wx.PyCommandEvent):
    """Event to signal that VLC has finished playing"""
    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)

class UpdateProgram(wx.PyCommandEvent):
    """Event to signal that program info has been updated"""
    def __init__(self, etype, eid, program=None,index=-1):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.program = program
        self.index = index

wizEVT_UPDATEPROGRESS = wx.NewEventType()
EVT_UPDATEPROGRESS = wx.PyEventBinder(wizEVT_UPDATEPROGRESS, 1)
class UpdateProgress(wx.PyCommandEvent):
    """Event to signal that the progress meter needs to be updated"""
    def __init__(self, etype, eid, progress=[], message=''):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.progress = progress
        self.message = message
