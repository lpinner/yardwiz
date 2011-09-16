# Copyright (c) 2011 Luke Pinner

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

'''Subclass of gui.GUI'''
from utilities import *
from events import *
import os,sys,threading,time,ConfigParser,logging,Queue
import re,webbrowser,pickle
import ordereddict
import wx
import gui, configspec
from ordereddict import OrderedDict as odict

APPNAME='YARDWiz'

class GUI( gui.GUI ):

    #tab indices
    idxLog=0
    idxInfo=1
    idxQueue=2


    mincolwidth=60

    def __init__( self):
        gui.GUI.__init__( self, parent=None )

        #Set the icons here as wxFormBuilder relative path is relative to the working dir, not the app dir
        icons=os.path.join(data_path(),u'icons')
        ico = wx.Icon( os.path.join(icons, u"yardwiz.png"), wx.BITMAP_TYPE_ANY )
        self.SetIcon(ico)
        self.btnConnect.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"reload.png"), wx.BITMAP_TYPE_ANY ))
        self.btnConnect.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"reload_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnClearQueue.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"clear.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnClearQueue.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"clear_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnDownload.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"download.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnDownload.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"download_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnPlay.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"play.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnPlay.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"play_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnPause.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"pause.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnPause.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"pause_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnStop.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"stop.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnStop.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"stop_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnVLC.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"vlc.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnVLC.SetBitmapDisabled( wx.Bitmap( os.path.join(icons, u"vlc_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.mitScheduled.Enable(False)
        self.btnVLC.Disable()

        self.version,self.display_version=version()
        self.SetTitle('%s (%s)'%(self.GetTitle(),self.display_version))
        self.StatusBar.SetFieldsCount(1)

        self._downloading=False
        self._connecting=False
        self.player=None
        self.total=0
        self.schedulelist=[]
        self.schedulequeue=Queue.Queue()
        self.scheduletime=None

        self.ThreadedConnector=None
        self.ThreadedDownloader=None
        self.ThreadedScheduler=None

        self.Play=threading.Event()
        self.Stop=threading.Event()

        self.Bind(EVT_ADDPROGRAM, self._AddProgram)
        self.Bind(EVT_CHECKCOMPLETE, self._CheckComplete)
        self.Bind(EVT_CONNECTED, self._Connected)
        self.Bind(EVT_DELETEPROGRAM, self._DeleteProgram)
        self.Bind(EVT_UPDATEPROGRAM, self._UpdateProgram)
        self.Bind(EVT_DOWNLOADCOMPLETE, self.onDownloadComplete)
        self.Bind(EVT_LOG, self.onLog)
        self.Bind(EVT_SCHEDULEDDWONLOADCOMPLETE, self.onScheduledDownloadComplete)
        self.Bind(EVT_SCHEDULERCOMPLETE, self.onSchedulerComplete)
        self.Bind(EVT_PLAYCOMPLETE, self.onPlayComplete)
        self.Bind(EVT_UPDATEPROGRESS, self.onUpdateProgress)
        self.lstPrograms.SetSortEnabled(True)

        #Bind F5 to connect
        for cw in self.GetChildren():
            cw.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
            for cw in cw.GetChildren():
                cw.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
                for cw in cw.GetChildren():
                    cw.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )

        self.tooltips={}
        for cw in self.GetChildren():
            tt=cw.GetToolTip()
            if tt:self.tooltips[cw]=tt

        #Workarounds for crossplatform & wxversion issues
        try:self.lblProgressText.SetLabelText('')
        except:
            self.lblProgressText.SetLabelText=self.lblProgressText.SetLabel
            self.lblProgressText.SetLabelText('')

        if float(wx.version()[0:3]) < 2.9:
            #wx.Gauge does not pulse continuously, have to call it repeatedly
            self.gaugeProgressBar._Pulse=self.gaugeProgressBar.Pulse
            self.gaugeProgressBar._Hide=self.gaugeProgressBar.Hide
            self.gaugeProgressBar.Pulse=self._Pulse
            self.gaugeProgressBar.Hide=self._Hide
            self.progress_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self._Pulse,self.progress_timer)

        self.txtLog.SetForegroundColour(self.lstPrograms.GetForegroundColour())
        self.txtInfo.SetForegroundColour(self.lstPrograms.GetForegroundColour())

        if isosx:
            for item in (self.gaugeProgressBar,self.lblProgressText):
                bs=self.bProgressSizer.GetItem(item)
                bs.SetFlag(wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.LEFT|wx.TOP|wx.EXPAND)
                bs.SetBorder(bs.GetBorder()+5)

        #check for GetWizPnP
        errmsg='''Error: YARDWiz requires getWizPnP to communicate with your Beyonwiz.\n\nPlease install getWizPnP from: http://www.openwiz.org/wiki/GetWizPnP_Release'''
        if not wizexe:
            errdial = wx.MessageDialog(None,errmsg,'Missing getWizPnP', wx.OK | wx.ICON_ERROR)
            errdial.ShowModal()
            sys.exit(1)

        self._ReadConfig()
        self._ApplyConfig()

        #Set focus so the F5 can get fired, doesn't work on startup when the frame has focus
        self.cbxDevice.SetFocus()

        self.lblProgressText.Hide()
        self.gaugeProgressBar.Hide()

        self._FadeIn()
        self.Show()

    #######################################################################
    #Methods
    #######################################################################
    def _AddProgram(self,event=None,program=None):

        if event:
            program=event.program #This will fail when the program is added manually, not via the AddProgram event

        if type(program['date']) is str:
            program['date']=time.strptime(program['date'],self.getwizpnp_dateformat) #Already converted if added manually

        display_date=time.strftime(self.display_dateformat,program['date'])
        program['length']=program.get('length','')
        program['size']=program.get('size',0)
        program['channel']=program.get('channel','')

        if program['index'] in self.programs:
            self.programs[program['index']].update(program)
        else:
            self.programs[program['index']]=program

        if  program['index'] in self.deleted:
            return

        iidx=event.index
        lidx=self.lstPrograms.FindItemData(-1,iidx)
        if lidx>-1:
            self.lstPrograms.SetStringItem(lidx,0,program['title'])
            self.lstPrograms.SetStringItem(lidx,1,program['channel'])
            self.lstPrograms.SetStringItem(lidx,2,time.strftime(self.display_dateformat,program['date']))
            self.lstPrograms.SetStringItem(lidx,3,"%0.1f" % program['size'])
            self.lstPrograms.SetStringItem(lidx,4,program['length'])
        else:
            lidx=self.lstPrograms.GetItemCount()
            self.lstPrograms.Append([program['title'],program['channel'],display_date,program['size'],program['length']])
            self.lstPrograms.SetItemData(lidx,iidx)
            self.total+=program['size']

        if  program['index'] in self.downloaded:
            self.lstPrograms.SetItemTextColour(lidx, wx.Colour(45,83,164))

        if self.total>0 and not self._downloading:
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields(['Total recordings %sMB'%self.total])

        self.lstPrograms.resizeLastColumn(self.mincolwidth)

        if event:self._Log('Added %s - %s'%(program['title'],display_date))
        self.mitDownload.Enable( True )
        self.mitQueue.Enable( True )

    def _ApplyConfig(self):

        #debug
        debug=self.config.getboolean('Debug','debug')
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(' '.join([APPNAME,version()[0],sys.executable, sys.platform]))
            logger.debug(str(which(wizexe)))
            #logger.debug('\n'.join(['%s: %s'%(e,os.environ[e]) for e in os.environ]))
            logger.debug('\n\t'.join(['PATH']+os.environ.get("PATH", os.defpath).split(os.pathsep)))
            sections = self.config.sections()
            config=['Config:']
            for section in sections:
                config.append('  '+section)
                options = self.config.options(section)
                for option in options:
                    val=self.config.get(section, option)
                    if isinstance(val, unicode):val=val.encode(filesysenc)
                    else:val=str(val)
                    config.append('    '+'='.join([option,val]))
            logger.debug('\n'.join(config))

        #write stuff to various controls, eg server & port
        self.devices=odict()
        self.device=None
        devices=self.config.get('Settings','device')
        self.cbxDevice.Clear()
        devices=devices.split(';')
        for device in devices:
            device=Device(device)
            self.devices[device.display]=device
            self.cbxDevice.Append(device.display)

        if self.cbxDevice.GetCount()>0:
            self.cbxDevice.SetSelection(0)
            self.device=self.devices.values()[0]

        #TS or TVWIZ
        self.tsformat=self.config.getboolean('Settings','tsformat')

        #tooltips
        tooltips=self.config.getboolean('Settings','showtooltips')
        for cw in self.tooltips:
            if tooltips:self.tooltips[cw].Enable(True)
            else:self.tooltips[cw].Enable(False)
        if tooltips:
            self.configspec=configspec.configspec
        else:
            for sec in self.configspec:
                for opt in sec:
                    if len(opt)>=3:
                        opt[2]=''

        xsize=self.config.getint('Window','xsize')
        ysize=self.config.getint('Window','ysize')
        xmin=self.config.getint('Window','xmin')
        ymin=self.config.getint('Window','ymin')
        xres,yres=wx.GetClientDisplayRect()[2:]
        if [xsize,ysize,xmin,ymin]==[-1,-1,-1,-1]:
            #Set default sizing
            proportion=0.75
            aspectratio=1.25
            ysize=int(yres*proportion)
            xsize=int(ysize*aspectratio)
            self.SetSize( wx.Size( xsize,ysize ) )
            self.Centre( wx.BOTH )
        else:
            #make sure it's on the screen
            xmin=max([xmin,0])
            ymin=max([ymin,0])
            xmin=min([xmin,xres-xsize])
            ymin=min([ymin,yres-ysize])
            xsize=min([xsize,xres])
            ysize=min([ysize,yres])
            self.SetSize( wx.Size( xsize,ysize ) )
            self.SetPosition(wx.Point(xmin,ymin))
        logger.debug('Window size: xmin %s, ymin %s, xsize %s, ysize %s'%(xmin,ymin,xsize,ysize))
        logger.debug('Window resolution: xres %s, yres %s'%(xres,yres))

        #Window effects
        logger.debug('CanSetTransparent: %s'%self.CanSetTransparent())
        if self.CanSetTransparent():
            showfade=True
            if 'linux' in sys.platform: #Workaround for http://trac.wxwidgets.org/ticket/13240
                try:
                    logger.debug('Checking compiz')
                    proc=subproc(['compiz', '--version'])
                    stdout,stderr=proc.communicate()
                    exit_code=proc.wait()
                    stdout,stderr=stdout.strip(),stderr.strip()
                    logger.debug('exit_code: %s'%exit_code)
                    logger.debug('stdout: %s'%stdout)
                    logger.debug('stderr: %s'%stderr)
                    if exit_code > 0:
                        self.fade=self.config.getboolean('Window','fade') #Assume we're not running compiz, so use the preference
                    else:
                        comver=stdout.split()[-1].split('.')
                        logger.debug('comver: %s'%str(comver))
                        if int(comver[1])==9 and int(comver[2])<=4:
                            showfade=False
                            self.fade=False
                        else:
                            self.fade=self.config.getboolean('Window','fade') #Assume we're not running compiz, so use the preference
                except Exception,err:
                    logger.debug('Exception,err: %s'%str(err))
                    self.fade=self.config.getboolean('Window','fade') #Assume we're not running compiz, so use the preference
            else:

                self.fade=self.config.getboolean('Window','fade')
        else:
            showfade=False
            self.fade=False

        if not self.fade and not showfade:
            self.config.set('Window','fade',False)
            if 'fade' in self.configspec['Window']:
                del self.configspec['Window']['fade']

        #VLC Player
        logger.debug('VLC path: %s'%vlcexe)
        if vlcexe:
            self.vlcargs=self.config.get('Settings','vlcargs').split()
            self.btnVLC.Disable()
        else:
            if 'vlcargs' in self.configspec['Settings']:
                del self.configspec['Settings']['vlcargs']
            self.btnVLC.Hide()

        #Quick listing, can include deleted files
        self.quicklisting=self.config.getboolean('Settings','quicklisting')

        #Date formats
        self.getwizpnp_dateformat='%b.%d.%Y_%H.%M' #Apr.7.2011_21.28 '%a %b %d %H:%M:%S %Y'
        self.getwizpnp_timeformat='%H:%M'
        self.display_dateformat=self.config.get('Settings','display_dateformat')
        self.filename_dateformat=self.config.get('Settings','filename_dateformat')
        self.lstPrograms.datetimeformat=self.display_dateformat
        self.lstPrograms.timeformat=self.getwizpnp_timeformat #Program length

        #post download processing
        postcmd=self.config.get('Settings','postdownloadcommand')
        postcmd=postcmd.replace('%f','%F')
        self.postcmd=postcmd.replace('%d','%D')

        #postdownload sound
        self.playsounds=self.config.getboolean('Sounds','playsounds')
        self.downloadcompletesound=self.config.get('Sounds','downloadcomplete')
        if not self.downloadcompletesound \
           or self.downloadcompletesound.lower()=='<default>' \
           or not self.downloadcompletesound.lower()[-4]=='.wav' \
           or not os.path.exists(self.downloadcompletesound):
            self.downloadcompletesound=os.path.join(data_path(),'sounds','downloadcomplete.wav')
            self.config.set('Sounds','downloadcomplete', self.downloadcompletesound)

    def _CheckWiz(self):
        self._ShowTab(self.idxLog)
        self.mitCheck.Enable( False )
        logger.debug('_CheckWiz')
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
        self._Log('Checking recordings...')
        checker=ThreadedChecker(self,self.Stop,self.device)

    def _CheckComplete(self,event):
        if event and event.message:self._Log(event.message)
        self.mitCheck.Enable( True )
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def _CleanupConfig(self):
        #Bit of cleanup from previous versions
        #configs - format = [oldsection, oldoption] or [oldsection, oldoption, newsection, newoption]
        configs=[('Settings', 'server'),
                 ('Settings', 'port'),
                 ('Settings','xsize','Window', 'xsize'),
                 ('Settings','ysize','Window','ysize'),
                 ('Settings','xmin','Window','xmin'),
                 ('Settings','ymin','Window','ymin'),
                 ('Settings','dateformat','Settings', 'display_dateformat')
                 ]
        for config in configs:
            if len(config)==4:
                try:
                    self.config.set(config[2], config[3], self.config.get(config[0],config[1]))
                except (ConfigParser.NoOptionError,ConfigParser.NoSectionError):
                    pass
            try:
                self.config.remove_option(config[0],config[1])
            except (ConfigParser.NoOptionError,ConfigParser.NoSectionError):
                pass

    def _ClearPrograms(self):
        self.programs=odict()
        self.total=0
        self.lstPrograms.HeaderWidths=[]
        self.lstPrograms.ClearAll()
        self.txtInfo.Clear()
        self.lstPrograms.InsertColumn( 0, u"Title" )
        self.lstPrograms.InsertColumn( 1, u"Channel" )
        self.lstPrograms.InsertColumn( 2, u"Date" )
        self.lstPrograms.InsertColumn( 3, u"Size (MB)" )
        self.lstPrograms.InsertColumn( 4, u"Length" )
        self.lstPrograms.SetSecondarySortColumn(2)#Date

        for j in range(self.lstPrograms.GetColumnCount()):
            self.lstPrograms.HeaderWidths.append(self.lstPrograms.GetColumnWidth(j))
        self.lstPrograms.resizeLastColumn(self.mincolwidth)

    def _ClearQueue(self):
        self.queue=[]
        self.lstQueue.ClearAll()
        self.lstQueue.InsertColumn( 0, u"" )
        self.lstQueue.InsertColumn( 1, u"" )
        self.btnClearQueue.Enable( False )
        self.btnDownload.Enable( False )

    def _Connect(self):
        if self._connecting or self._downloading:return
        self._connecting=True
        self._Reset()
        self.Stop.clear()
        self.lstPrograms.SetSortEnabled(False)
        self.mitCheck.Enable( False )
        self.btnConnect.Enable( False )
        self.cbxDevice.Enable( False )
        self.mitDelete.Enable( False )
        self.gaugeProgressBar.Show()
        self.gaugeProgressBar.Pulse()
        self.lblProgressText.Show()
        self.lblProgressText.SetLabelText('Connecting...')

        device=str(self.cbxDevice.GetValue()).strip()
        if not device:
            self._Discover()
            self._Connected(False)
            if self.cbxDevice.GetCount()==1:self._Connect()
            return

        if device in self.devices:
            self.device=self.devices[device]
        else:
            self.device=Device(device)
            self.devices[self.device.display]=self.device
            self.cbxDevice.Append(self.device.display)

        logger.debug('Connecting to %s'%(str(self.device)))
        self._Log('Connecting to %s...'%self.device.display)

        #Connect to the Wiz etc...
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
        self.ThreadedConnector=ThreadedConnector(self,self.Stop,device=self.device,quick=self.quicklisting)

    def _Connected(self,event=None):

        if event and event.message:
            self._Log(event.message)

        self._connecting=False
        self.Stop.clear()
        self.btnConnect.Enable( True )
        self.cbxDevice.Enable( True )
        self.mitDelete.Enable( True )
        self.lstPrograms.SetSortEnabled(True)
        if not self._downloading:
            self.lblProgressText.SetLabelText('')
            self.lblProgressText.Hide()
            self.gaugeProgressBar.Hide()

        downloaded,deleted=self.downloaded,self.deleted
        for pidx in downloaded:
            if pidx not in self.programs:del self.downloaded[self.downloaded.index(pidx)]
        for pidx in self.deleted:
            if pidx not in self.programs:del self.deleted[self.deleted.index(pidx)]

        if event and event.connected:
            self.mitCheck.Enable( True )

        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def _DeleteFromQueue(self):
        if self.lstQueue.GetSelectedItemCount()==len(self.queue):
            return self._ClearQueue()

        idx = self.lstQueue.GetFirstSelected()
        lst=[]
        while idx != -1:
            lst.append(idx)
            idx = self.lstQueue.GetNextSelected(idx)
        lst.sort()
        lst.reverse() #Loop thru again from the end so we don't mess up the indexing
        for idx in lst:
            del self.queue[idx]
            self.lstQueue.DeleteItem(idx)

    def _DeleteFromWiz(self):
        idx = self.lstPrograms.GetFirstSelected()
        programs=[]
        indices=[]
        prognames=[]

        while idx != -1:
            lidx = self.lstPrograms.GetItem(idx).Data
            pidx = self.programs.keys()[lidx]
            program = self.programs[pidx]

            if '*RECORDING' in program['title']:
                self._Log('Unable to delete %s as it is currently recording.'%program['title'])
                self._ShowTab(self.idxLog)
            elif '*LOCKED' in program['title']:
                self._Log('Unable to delete %s as it is LOCKED.'%program['title'])
                self._ShowTab(self.idxLog)
            else:
                prognames.append('%s-%s'%(program['title'],time.strftime(self.filename_dateformat,program['date'])))
                indices.append(lidx)
                programs.append(program)

            idx = self.lstPrograms.GetNextSelected(idx)

        if not prognames:return

        confirm=self.config.getboolean('Settings','confirmdelete')
        if confirm:
            confirm=ConfirmDelete('\n'+'\n'.join(prognames))
            if confirm.checked:#i.e do not show this dialog again...
                self.config.set('Settings','confirmdelete',0)
            delete=confirm.delete
        else:
            delete=True
        if delete:
            self._ShowTab(self.idxLog)
            indices.reverse()
            programs.reverse()
            logger.debug('_DeleteFromWiz, indices: %s'%str(indices))
            logger.debug('_DeleteFromWiz, programs: %s'%str(programs))
            self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
            deletions=ThreadedDeleter(self,self.Stop,self.device,programs,indices)

    def _DeleteProgram(self,event):
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
        idx=self.lstPrograms.FindItemData(-1,event.index)
        if idx>-1:
            pidx=self.programs.keys()[event.index]
            if pidx not in self.deleted:self.deleted.append(pidx)
            self.lstPrograms.DeleteItem(idx)
            self.total-=self.programs[pidx]['size']
            if not self._downloading:
                self.StatusBar.SetFieldsCount(1)
                self.StatusBar.SetFields(['Total recordings %sMB'%self.total])
        idx=self.lstQueue.FindItemData(-1,event.index)
        if idx>-1:
            del self.queue[self.queue.index(pidx)]
            self.lstQueue.DeleteItem(idx)
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def _Discover(self):
        self._Log('Searching for Wizzes.')
        cmd=[wizexe,'--discover']
        try:
            proc=subproc(cmd)
        except Exception,err:
            logger.error(str(err))
            self._Log('Error searching for Wizzes:')
            self._Log(str(err))
        stdout,stderr=proc.communicate()
        exit_code=proc.wait()
        stdout=stdout.strip()
        logger.debug('_Discover, exit_code: %s'%exit_code)
        logger.debug('_Discover, stdout: %s'%stdout)
        logger.debug('_Discover, stderr: %s'%stderr.strip())
        if stdout:
            self.devices=odict()
            self.cbxDevice.Clear()
            self.cbxDevice.SetValue('')
            for device in stdout.split('\n'):
                device=device.strip()
                if device:
                    device=Device(device)
                    self.devices[device.display]=device
                    self._Log('Discovered %s.'%(device.display))
                    self.cbxDevice.Append(device.display)

            if self.cbxDevice.GetCount()>0:
                self.cbxDevice.SetSelection(0)

        else:
            #self.cbxDevice.Clear()
            #self.cbxDevice.SetValue('')
            self._Log('Unable to discover any Wizzes.')
            self._ShowTab(self.idxLog)

        #Update config
        self.config.set('Settings','device',';'.join([str(dev) for dev in self.devices.values()]))

    def _DownloadQueue(self,*args):
        if self._downloading:return

        programs=[]
        size=0
        for pidx in self.queue:
            program = self.programs[pidx]
            filename = self._GetFileName(program)

            if not filename:return #Stop showing file dialogs if queue download is cancelled

            program['filename']=filename
            self.programs[pidx]['filename']=filename
            programs.append(program)
            size+=program['size']

        self._ShowTab(self.idxLog)
        if not programs:return

        if size==0:
            #Wait for the program info to update
            self.btnClearQueue.Enable( False )
            self.btnDownload.Enable( False )
            self.connecttimer = wx.PyTimer(self._DownloadQueue)
            self.connecttimer.Start(250,wx.TIMER_ONE_SHOT)
            return

        self.btnPlay.Enable( False )
        self.btnPause.Enable( True )
        self.btnStop.Enable( True )
        self.lblProgressText.SetLabelText('')
        self.gaugeProgressBar.Hide()
        self.gaugeProgressBar.Show()
        #self.btnPlay.Show() #This produces 'unexpected results' on ubuntu 10.04 & 10.10
        #self.btnPause.Show()
        #self.btnStop.Show()
        self.btnClearQueue.Enable( False )
        self.btnDownload.Enable( False )
        self.btnConnect.Enable( False )
        self.lstQueue.Enable( False )
        self.mitExit.Enable( False )
        self.mitQueue.Enable( False )
        self.mitDownload.Enable( False )
        self._downloading=True
        self.ThreadedDownloader=ThreadedDownloader(self,self.device,programs,self.Play,self.Stop)

    def _DownloadComplete(self,index,stopped):
        pidx=0
        if len(self.queue)>0:
            pidx=self.queue[0]
            item=self.lstPrograms.FindItemData(-1,self.programs.keys().index(pidx))
            del self.queue[0]
            self.lstQueue.DeleteItem(0)
            if not stopped:
                self.downloaded.append(pidx)
                try:
                    self.lstPrograms.SetItemTextColour(item, wx.Colour(45,83,164))
                    self.lstPrograms.Select(item, 0) #Deselect
                except:pass
                if self.playsounds:
                    try:
                        if not os.path.exists(self.downloadcompletesound):
                            raise IOError, '[Errno 2] No such file or directory: %f'%self.downloadcompletesound
                        sound = wx.Sound(self.downloadcompletesound)
                        sound.Play(wx.SOUND_ASYNC)
                    except Exception, err:
                        self._Log(err)

        if not stopped and pidx:
            program=self.programs[pidx]
            self._PostDownloadCommand(program)

        if len(self.queue)==0 or stopped:
            self._downloading=False
            #self.btnPlay.Hide() #This produces 'unexpected results' on ubuntu 10.04 & 10.10
            #self.btnPause.Hide()
            #self.btnStop.Hide()
            self.gaugeProgressBar.Hide()
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields([''])
            self.lblProgressText.SetLabelText('')
            self.lblProgressText.Hide()
            self.btnPlay.Enable( False )
            self.btnPause.Enable( False )
            self.btnStop.Enable( False )
            self.btnConnect.Enable( True )
            self.mitQueue.Enable(True)
            self.mitExit.Enable( True )
            self.mitDownload.Enable( True )
            self.btnVLC.Disable()
            if len(self.queue)==0:
                self.btnClearQueue.Enable( False )
                self.btnDownload.Enable( False )
                self.lstQueue.Enable( False )
            else:
                self.btnClearQueue.Enable( True )
                self.btnDownload.Enable( True )
                self.lstQueue.Enable( True )

    def _Fade(self,start,stop,delta,callback):
        if self.fade:
            self.SetTransparent(start)
            self.amount=start
            self.stop=stop
            self.delta=delta
            self.callback=callback
            self.fadetimer = wx.PyTimer(self._SetTransparent)
            self.fadetimer.Start(1)
        else:
            if callback:callback()

    def _FadeIn(self,start=0,stop=255,delta=25,callback=None):
        self._Fade(start,stop,delta,callback)

    def _FadeOut(self,start=255,stop=0,delta=-25,callback=None):
        self._Fade(start,stop,delta,callback)

    def _GetFileName(self,program):
            filename = program.get('filename',None)

            if not filename:
                filename_date=time.strftime(self.filename_dateformat,program['date'])
                filename=program['title'].split('/')[-1]
                filename=self._sanitize('%s %s'%(filename,filename_date)).strip('_')
            else:
                filename=os.path.splitext(os.path.basename(filename))[0]
            tsspec='TS Files (*.ts)|*.ts'
            twspec='TVWIZ format (*.tvwiz)|*.tvwiz'
            if self.tsformat:
                filespec='|'.join([tsspec,twspec])
                ext=['.ts','.tvwiz']
            else:
                filespec='|'.join([twspec,tsspec])
                ext=['.tvwiz','.ts']
            dlg = wx.FileDialog(self, "Open", self.config.get('Settings','lastdir'), filename,filespec, wx.FD_SAVE)
            if (dlg.ShowModal() == wx.ID_OK):
                f=dlg.Filename#.encode(filesysenc)
                d=dlg.Directory#.encode(filesysenc)
                if d[-1]==':':d+=os.path.sep
                ext=ext[dlg.GetFilterIndex()]
                if not os.path.splitext(f)[1].lower()==ext:f+=ext
                self.config.set('Settings','lastdir',d)
                filename=os.path.join(d,f)
                return filename
            else:return #Stop showing file dialogs if queue download is cancelled

    def _Hide(self,*args,**kwargs):
        self.progress_timer.Stop()
        self.gaugeProgressBar.SetRange(100)
        self.gaugeProgressBar.SetValue(0)
        self.gaugeProgressBar._Hide()

    def _Log(self,msg):
        self.txtLog.SetInsertionPointEnd()
        msg=msg.strip()
        if msg:
            try:self.txtLog.WriteText(msg+'\n')
            except:self.txtLog.WriteText(str(msg)+'\n')
            self.txtLog.ShowPosition(self.txtLog.GetLastPosition())
            logger.debug(msg)

    def _Play(self,*args,**kwargs):
        self.player=ThreadedPlayer(self, self.Stop, self.Play,self.filename,self.vlcargs)

    def _PostDownloadCommand(self,program):
        cmd=self.postcmd.split('#')[0].strip()
        if cmd:
            cmd=cmd.replace('%F', '"%s"'%program['filename'])
            cmd=cmd.replace('%D', '"%s"'%os.path.dirname(program['filename']))
            logger.debug('Postdownload command: %s'%cmd)
            try:
                pid = subprocess.Popen(cmd).pid #Don't wait, nor check the output, leave that up to the user
            except Exception,err:
                self._Log('Can\'t run post download command on %s'%program['filename'])
                self._Log(str(err))

    def _Pulse(self,*args,**kwargs):
        if not self._downloading:
            self.gaugeProgressBar._Pulse()
            self.progress_timer.Start(100,True)

    def _Queue(self,clear=False):
        if self._downloading:return

        if clear:
            self.queue=[]
            self.lstQueue.ClearAll()
            self.lstQueue.InsertColumn( 0, u"" )
            self.lstQueue.InsertColumn( 1, u"" )

        idx = self.lstPrograms.GetFirstSelected()
        i=-1
        while idx != -1:
            qidx = self.lstPrograms.GetItem(idx).Data
            pidx=self.programs.keys()[qidx]
            program = self.programs[pidx]
            pidx=program['index']
            if '*RECORDING' in program['title']:
                self._Log('Unable to download %s as it is currently recording.'%program['title'])
                self._ShowTab(self.idxLog)
            elif pidx not in self.queue:
                i+=1
                self.queue.append(pidx)
                self.lstQueue.Append([program['title'],time.strftime(self.display_dateformat,program['date'])])
                self.lstQueue.SetItemData(i,qidx)

            idx = self.lstPrograms.GetNextSelected(idx)
        if self.queue:
            self.lstQueue.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.lstQueue.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.btnClearQueue.Enable( True )
            self.btnDownload.Enable( True )
            self.mitRemove.Enable( True )
            self.mitClearQueue.Enable( True )
            self.mitDownloadAll.Enable( True )
            self._ShowTab(self.idxQueue)

    def _ReadConfig(self):
        #read from a config file
        if 'APPDATA' in os.environ:
            configdir = os.path.join(os.environ['APPDATA'], APPNAME.lower())
        elif 'XDG_CONFIG_HOME' in os.environ:
            configdir = os.path.join(os.environ['XDG_CONFIG_HOME'], APPNAME.lower())
        else:
            confighome = os.path.join(wx.GetHomeDir(), '.config')
            if os.path.exists(confighome) and os.path.isdir(confighome):
                configdir = os.path.join(confighome, APPNAME.lower())
            else:
                configdir = os.path.join(wx.GetHomeDir(), '.'+APPNAME.lower())

        defaultconfig=os.path.join(data_path(),'config','defaults.ini')
        self.userconfig=os.path.join(configdir,'config.ini')
        self.config=ConfigParser.RawConfigParser(dict_type=ordereddict.OrderedDict)
        self.config.read([defaultconfig,self.userconfig])
        self.configspec=configspec.configspec
        self._CleanupConfig()

        #Already downloaded recordings
        self.downloadedcache=os.path.join(configdir,'downloaded.cache')
        try:self.downloaded=pickle.load( open(self.downloadedcache))
        except:self.downloaded=[]

        #Already deleted recordings
        self.deletedcache=os.path.join(configdir,'deleted.cache')
        try:self.deleted=pickle.load( open(self.deletedcache))
        except:self.deleted=[]

    def _Reset(self):
        self._ClearQueue()
        self._ClearPrograms()

    def _ScheduleDownload(self):
        schedulelist=self.schedulelist[:]
        showcancel=len(schedulelist)>0

        idx = self.lstPrograms.GetFirstSelected()

        while idx != -1:
            qidx = self.lstPrograms.GetItem(idx).Data
            pidx=self.programs.keys()[qidx]
            program = self.programs[pidx]
            if '*RECORDING' in program['title']:
                self._Log('Unable to schedule %s as it is currently recording.'%program['title'])
                self._ShowTab(self.idxLog)
            elif pidx not in self.schedulelist:
                filename = self._GetFileName(program)
                if filename:
                    self.programs[pidx]['filename']=filename
                    schedulelist.append(pidx)
                else:return

            idx = self.lstPrograms.GetNextSelected(idx)

        programs=[self.programs[pidx]['title'] for pidx in schedulelist]
        self._FadeOut(stop=200,delta=-25)
        sd=SchedulerDialog(self, programs, self.scheduletime, showcancel)
        self._FadeIn(start=200,delta=25)

        if sd.saved:
            for pidx in schedulelist:
                if pidx not in self.schedulelist:
                    program=self.programs[pidx]
                    program['device']=self.device
                    self.schedulelist.append(pidx)
                    self.schedulequeue.put(program)

            scheduletime=sd.GetValue()

            if self.ThreadedScheduler is None:
                self.scheduletime=scheduletime
                self.ThreadedScheduler = ThreadedScheduler(self, scheduletime,self.schedulequeue)

            elif scheduletime!=self.scheduletime:
                self.scheduletime=scheduletime
                self.ThreadedScheduler.reset(scheduletime)

            self.mitScheduled.Enable(len(self.schedulelist)>0)

        elif sd.cancelled:
            self.ThreadedScheduler.stop()
            self.ThreadedScheduler=None
            self.schedulelist=[]
            self.schedulequeue=Queue.Queue()
            self.scheduletime=None

    def _ScheduledDownloads(self):
        programs=[self.programs[pidx]['title'] for pidx in self.schedulelist]
        showcancel=len(programs)>0

        sd=SchedulerDialog(self, programs, self.scheduletime,showcancel)

        if sd.saved:
            scheduletime=sd.GetValue()
            if self.ThreadedScheduler and scheduletime!=self.scheduletime:
                self.scheduletime=scheduletime
                self.ThreadedScheduler.reset(scheduletime)
        elif sd.cancelled:
            self.ThreadedScheduler.stop()
            self.ThreadedScheduler=None
            self.schedulelist=[]
            self.schedulequeue=Queue.Queue()
            self.scheduletime=None

        self.mitScheduled.Enable(len(self.schedulelist)>0)

    def _SetCursor(self,cursor):
        self.SetCursor(cursor)
        for cw in self.GetChildren():
            cw.SetCursor(cursor)
            for cw in cw.GetChildren():
                cw.SetCursor(cursor)
                for cw in cw.GetChildren():
                    cw.SetCursor(cursor)

        self.SetCursor(cursor)

    def _SetTransparent(self):
        self.amount += self.delta
        if (self.amount <= self.stop and self.delta<0) or (self.amount >= self.stop and self.delta>0):
            self.SetTransparent(self.stop)
            self.fadetimer.Stop()
            if self.callback:self.callback()
            return
        self.SetTransparent(self.amount)

    def _ShowInfo(self):
        idx = self.lstPrograms.GetFocusedItem()
        if idx>-1:
            self.txtInfo.Clear()
            idx = self.lstPrograms.GetItem(idx).Data
            pidx=self.programs.keys()[idx]
            info=self.programs[pidx].get('info','No program information available')
            self.txtInfo.WriteText(info+'\n')
            self.txtInfo.SetInsertionPoint(0)
            self.txtInfo.ShowPosition(0)
            self._ShowTab(self.idxInfo)

    def _ShowTab(self,tabindex):
        self.nbTabArea.ChangeSelection(tabindex)

    def _UpdateProgram(self,event):
        idx=self.lstPrograms.FindItemData(-1,event.index)
        program=event.program
        if type(program['date']) is str:program['date']=time.strptime(program['date'],self.getwizpnp_dateformat)
        if program['index'] in self.programs:
            if self.programs[program['index']]['size']==0:
                self.total+=program['size']
            self.programs[program['index']].update(program)
        else:
            self.programs[program['index']]=program
            self.total+=program['size']
        if self.total>0 and not self._downloading:
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields(['Total recordings %sMB'%self.total])
        try:
            self.lstPrograms.SetStringItem(idx,0,program['title'])
            self.lstPrograms.SetStringItem(idx,1,program['channel'])
            self.lstPrograms.SetStringItem(idx,2,time.strftime(self.display_dateformat,program['date']))
            self.lstPrograms.SetStringItem(idx,3,"%0.1f" % program['size'])
            self.lstPrograms.SetStringItem(idx,4,program['length'])
        except:return #we're probably exiting

        self.lstPrograms.resizeLastColumn(self.mincolwidth)

        self._Log('Updated episode info for %s.'%program['title'])

    def _UpdateProgress(self,progress,message):
        self.gaugeProgressBar.Show()
        self.lblProgressText.Show()
        self.lblProgressText.SetToolTipString( message)

        #make sure lblProgressText doesn't overwrite the exit button
        if len(message)>0:
            mw=self.GetClientSizeTuple()[0]-self.btnExit.GetClientSizeTuple()[0]-self.gaugeProgressBar.GetClientSizeTuple()[0]
            tw=self.lblProgressText.GetTextExtent(message)[0]
            cw=int(tw/len(message))
            if tw>mw:message=message[0:int(mw/cw - 3*cw)]+'...'

        self.lblProgressText.SetLabelText(message)
        self.gaugeProgressBar.SetRange(100)
        if progress:
            self.gaugeProgressBar.SetValue(progress['percent'])
            if progress['total']>progress['size']:
                self.StatusBar.SetFieldsCount(5)
                fields=['Speed %sMB/S'%(progress['speed']),
                        'Remaining %s'%progress['time'],
                        'Total remaining %s'%progress['totaltime'],
                        'Downloaded %sMB/%sMB (%s%%)'%(progress['downloaded'],progress['size'],progress['percent']),
                        'Queued %sMB'%progress['total']
                        ]
                self.StatusBar.SetFields(fields)
                widths=[-2,-3,-4,-5,-2]
                self.StatusBar.SetStatusWidths(widths)
            else:
                self.StatusBar.SetFieldsCount(3)
                fields=['Speed %sMB/S'%(progress['speed']),
                        'Remaining %s'%progress['time'],
                        'Downloaded %sMB/%sMB (%s%%)'%(progress['downloaded'],progress['size'],progress['percent'])
                        ]
                self.StatusBar.SetFields(fields)
                self.StatusBar.SetStatusWidths([-2,-3,-4])

            self.filename=progress['filename']
            if vlcexe and self.filename and self.player is None:
                self.btnVLC.Enable(True)

        else:
            self.gaugeProgressBar.SetValue(0)
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields([''])

    def _UpdateSize(self):
        try:
            xsize,ysize=self.Size.x,self.Size.y
            xmin,ymin=self.GetScreenPositionTuple()
            self.config.set('Window', 'xsize', str(xsize))
            self.config.set('Window', 'ysize', str(ysize))
            self.config.set('Window', 'xmin', str(xmin))
            self.config.set('Window', 'ymin', str(ymin))
        except:pass

    def _WriteConfig(self):
        #Write self.config back
        self._UpdateSize()
        sections = self.config.sections()
        for section in sections:
            options = self.config.options(section)
            for option in options:
                val=self.config.get(section,option)
                if isinstance(val, unicode):
                    self.config.set(section,option,val.encode(filesysenc))

        if not os.path.exists(os.path.dirname(self.userconfig)):
            os.mkdir(os.path.dirname(self.userconfig))
        self.config.write(open(self.userconfig,'w'))

        pickle.dump( self.downloaded, open( self.downloadedcache, "w" ) )
        pickle.dump( self.deleted, open( self.deletedcache, "w" ) )

    def _sanitize(self,filename):
        chars=['\\','/',':','*','?','"','<','>','|','$']
        for char in chars:
            filename = filename.replace(char, '_')
        return filename
    #######################################################################
    #Event handlers
    #######################################################################
    def btnConnect_OnClick( self, event ):
        if not self._connecting:self._Connect()

    def btnExit_onClick( self, event):
        self.Close(True)

    def btnClearQueue_OnClick( self, event ):
        self._ClearQueue()
        event.Skip()

    def btnDownload_OnClick( self, event ):
        self._DownloadQueue()

    def btnPlay_OnClick( self, event ):#hiding and showing play etc... buttons isn't working on ubuntu 10.04
        self.btnPlay.Enable( False )
        self.btnPause.Enable( True )
        self.btnStop.Enable( True )
        self.Play.set()
        event.Skip()

    def btnPause_OnClick( self, event ):
        self.btnPlay.Enable( True )
        self.btnPause.Enable( False )
        self.Play.clear()

    def btnStop_OnClick( self, event ):
        self.Stop.set()

    def btnVLC_OnClick( self, event ):
        self._Play()
        self.btnVLC.Disable()

    def cbxDevice_OnCombobox( self, event ):
        self._Connect()
        
    def cbxDevice_OnKillFocus( self, event ):
        self.mitCheck.Enable( False )
        device=str(self.cbxDevice.GetValue())
        if device:
            if device in self.devices:
                self.device=self.devices[device]
            else:
                self.device=Device(device)
                self.devices[device]=self.device
                self.cbxDevice.Append(self.device.display)

            #Update config
            self.config.set('Settings','device',';'.join([str(dev) for dev in self.devices.values()]))

            logger.debug(self.config.get('Settings','device'))

    def cbxDevice_OnTextEnter( self, event ):
        self._Connect()

    def lstProgramsOnContextMenu( self, event ):
        item, result = self.lstPrograms.HitTest(event.GetPosition())
        if result == wx.NOT_FOUND:
            event.Skip()
            return
        for i in range(len(self.programs)):
            self.lstPrograms.SetItemState(i, 0, wx.LIST_STATE_SELECTED)
        self.lstPrograms.Select(item)
        self.lstPrograms.PopupMenu(self.mnuPrograms)

    def lstPrograms_OnDoubleClick( self, event ):
        self._Queue()

    def lstPrograms_OnRightClick( self, event ):
        self.lstPrograms.PopupMenu(self.mnuPrograms)

    def lstPrograms_OnSelect( self, event, showinfo=True ):
        if showinfo:self._ShowInfo()
        self.lstPrograms.SetFocus()

    def lstQueueOnContextMenu( self, event ):
        self.mitRemove.Enable( False )
        self.lstQueue.PopupMenu(self.mnuQueue)

    def lstQueue_OnRightClick( self, event ):
        self.lstQueue.PopupMenu(self.mnuQueue)

    def lstQueue_OnMiddleClick( self, event ):
        self.mitRemove_OnSelect(event)

    def mitCheck_OnSelect( self, event ):
        self._CheckWiz()

    def mitAbout_OnSelect( self, event ):
        self._FadeOut(stop=200,delta=-25)
        dlg=AboutDialog(self)
        self._FadeIn(start=200,delta=25)

    def mitClearQueue_OnSelect( self, event ):
        self._ClearQueue()

    def mitDelete_OnSelect( self, event ):
        self._DeleteFromWiz()

    def mitDownload_onSelect( self, event ):
        self._Queue(clear=True)
        self._DownloadQueue()

    def mitDownloadAll_OnSelect( self, event ):
        self._DownloadQueue()

    def mitHelp_OnSelect( self, event ):
        webbrowser.open_new_tab('http://code.google.com/p/yardwiz/wiki/Help')

    def mitPreferences_OnSelect( self, event ):
        self._FadeOut(stop=200,delta=-25)
        self.cbxDevice_OnKillFocus(None)          #Clicking a menu item doesn't move focus off a control,
        settings=SettingsDialog(self,self.config,self.configspec) #so make sure the device name get's updated.
        if settings.saved:
            self.config=settings.config
            self._ApplyConfig()
            self._WriteConfig()
        self._FadeIn(start=200,delta=25)

    def mitQueue_onSelect( self, event ):
        self._Queue()

    def mitRemove_OnSelect( self, event ):
        self._DeleteFromQueue()

    def mitScheduler_OnSelect( self, event ):
        self._ScheduleDownload()

    def mitScheduled_OnSelect( self, event ):
        self._FadeOut(stop=200,delta=-25)
        self._ScheduledDownloads()
        self._FadeIn(start=200,delta=25)

    def onActivate( self, event ):
        self._UpdateSize()
        event.Skip()

    def onCloseApp( self, event=None ):
        self._FadeOut(callback=self._Exit)

    def _Exit( self, event=None ):
        try:self.Hide()
        except:pass
        try:self.Stop.set()
        except:pass
        try:self._WriteConfig()
        except:pass
        try:del self.ThreadedConnector
        except:pass
        try:del self.ThreadedDownloader
        except:pass
        try:self.ThreadedScheduler.stop()
        except:pass
        try:self.Destroy()
        except:pass
        sys.exit(0)

    def onDownloadComplete( self, event ):
        self._DownloadComplete(event.index,event.stopped)

    def OnKeyDown( self, event ):
        if event.GetKeyCode() == wx.WXK_F5:
            self._Connect()
        else:
            event.Skip()

    def onLog( self, event ):
        self._Log(event.message)

    def onPlayComplete( self, event ):
        self.btnVLC.Disable()
        del self.player
        self.player=None

    def onUpdateProgress( self, event ):
        self._UpdateProgress(event.progress,event.message)

    def onScheduledDownloadComplete( self, event ):
        self._PostDownloadCommand(event.program)

    def onSchedulerComplete( self, event ):
        self.schedulelist=[]
        self.schedulequeue=Queue.Queue()
        self.scheduletime=None

    def OnSize( self, event ):
        self._UpdateSize()
        event.Skip()

class LicenseDialog( gui.LicenseDialog ):
    def __init__( self, parent ):
        gui.LicenseDialog.__init__(self,None)
        sxmin,symin=centrepos(self,parent)
        self.SetPosition((sxmin,symin))

class AboutDialog( gui.AboutDialog ):
    def __init__( self, parent ):
        gui.AboutDialog.__init__( self, None )
        #Set the icons here as wxFormBuilder relative path is relative to the working dir, not the app dir
        path=data_path()
        icons=os.path.join(path,u'icons')
        ico=os.path.join(icons, u"yardwiz.png")
        self.SetIcon( wx.Icon( ico, wx.BITMAP_TYPE_ANY ) )
        self.bmpIcon.SetBitmap( wx.Bitmap(ico , wx.BITMAP_TYPE_ANY ) )

        txtlicense=license()
        txtversion=version()[0]

        sxmin,symin=centrepos(self,parent)
        self.SetPosition((sxmin,symin))

        self.LicenseDialog=LicenseDialog(self)
        self.LicenseDialog.txtLicense.SetValue(txtlicense)
        self.lblVersion.SetLabel('Version: '+txtversion)
        self.lblCopyright.SetLabel(txtlicense.split('\n')[0].strip())

        self.ShowModal()

    def btnLicense_OnClick( self, event ):
        self.LicenseDialog.ShowModal()

class SchedulerDialog ( gui.SchedulerDialog ):
    cancelled=False
    saved=False
    def __init__( self, parent, programs , wxDateTime=None, showcancel=False):
        gui.SchedulerDialog.__init__(self, parent)
        if wxDateTime:self.dtcSchedule.SetValue(wxDateTime)
        if programs:
            self.lstSchedule.InsertColumn(0,u'')
            for program in programs:
                self.lstSchedule.Append([program])

            self.GetValue=self.dtcSchedule.GetValue
            self.btnCancel.Show(showcancel)
        else:
            self.btnSchedule.Show(False)
            self.btnCancel.Show(False)

        self.ShowModal()

    def OnCancel( self, event ):
        self.cancelled=True
        self.saved=False
        self.EndModal(0)

    def OnClose( self, event ):
        self.saved=False
        self.EndModal(0)

    def OnApply( self, event ):
        self.saved=True
        self.EndModal(0)

class SettingsDialog( gui.SettingsDialog ):
    def __init__( self, parent, config,  specs ):
        self.saved=False
        gui.SettingsDialog.__init__(self, parent)
        self.PropertyScrolledPanel.SetConfig(config, specs)
        self.Layout()
        self.Sizer.Fit( self )
        self.ShowModal()

    def OnCancel( self, event ):
        self.config=self.PropertyScrolledPanel.GetConfig(False)
        self.saved=False
        self.EndModal(0)

    def OnSave( self, event ):
        self.config=self.PropertyScrolledPanel.GetConfig(True)
        self.saved=True
        self.EndModal(0)

class ConfirmDelete( gui.ConfirmDelete ):
    def __init__( self, filename):
        gui.ConfirmDelete.__init__( self, None)

        self.delete=False

        bmp = wx.EmptyBitmap(32, 32)
        bmp = wx.ArtProvider_GetBitmap(wx.ART_QUESTION,wx.ART_MESSAGE_BOX, (32, 32))
        self.bmpIcon.SetBitmap(bmp)

        self._labelquestion=self.lblQuestion.GetLabelText()
        self._labelshowagain=self.chkShowAgain.GetLabelText()
        try:self.lblQuestion.SetLabelText(self._labelquestion%filename)
        except:
            self.lblQuestion.SetLabelText=self.lblQuestion.SetLabel
            self.lblReEnable.SetLabelText=self.lblReEnable.SetLabel
            self.chkShowAgain.SetLabelText=self.chkShowAgain.SetLabel
            self.lblQuestion.SetLabelText(self._labelquestion%filename)

        self.checked=self.chkShowAgain.IsChecked()
        self.Fit()
        self.Centre( wx.BOTH )
        self.ShowModal()

    # Handlers for ConfirmDelete events.
    def DialogButtonsOnNoButtonClick( self, event ):
        self.delete=False
        self.EndModal(True)

    def DialogButtonsOnYesButtonClick( self, event ):
        self.delete=True
        self.EndModal(True)

    def chkShowAgainOnCheckBox( self, event ):
        self.checked=event.IsChecked()
        if self.checked:
            self.lblReEnable.SetLabelText('You can re-enable this confirmation in Settings->Preferences.')
            self.DialogButtonsNo.Enable(False)
            self.chkShowAgain.Fit()
            self.Fit()
        else:
            self.lblReEnable.SetLabelText('')
            self.DialogButtonsNo.Enable(True)
            self.chkShowAgain.Fit()
            self.Fit()