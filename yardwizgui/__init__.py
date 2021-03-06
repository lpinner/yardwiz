# Copyright (c) 2015 Luke Pinner

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
HELP_URL='https://github.com/lpinner/yardwiz/wiki'

class GUI( gui.GUI ):

    #tab indices
    idxLog=0
    idxInfo=1
    idxQueue=2
    mincolwidth=60

    def __init__( self):
        gui.GUI.__init__( self, parent=None )

        if 'APPDATA' in os.environ:
            self.configdir = os.path.join(os.environ['APPDATA'], APPNAME.lower())
        elif 'XDG_CONFIG_HOME' in os.environ:
            self.configdir = os.path.join(os.environ['XDG_CONFIG_HOME'], APPNAME.lower())
        else:
            confighome = os.path.join(wx.GetHomeDir(), '.config')
            if os.path.exists(confighome) and os.path.isdir(confighome):
                self.configdir = os.path.join(confighome, APPNAME.lower())
            else:
                self.configdir = os.path.join(wx.GetHomeDir(), '.'+APPNAME.lower())
        if not os.path.exists(self.configdir): mkdirs(self.configdir)

        #Set the icons here as wxFormBuilder relative path is relative to the working dir, not the app dir
        self.icons=os.path.join(data_path(),u'icons')
        ico = wx.Icon( os.path.join(self.icons, u"yardwiz.png"), wx.BITMAP_TYPE_ANY )
        self.SetIcon(ico)
        self.btnConnect.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"reload.png"), wx.BITMAP_TYPE_ANY ))
        self.btnConnect.SetBitmapDisabled( wx.Bitmap( os.path.join(self.icons, u"reload_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnClearQueue.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"clear.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnClearQueue.SetBitmapDisabled( wx.Bitmap( os.path.join(self.icons, u"clear_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnDownload.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"download.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnDownload.SetBitmapDisabled( wx.Bitmap( os.path.join(self.icons, u"download_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnPlayPause.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"play.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnPlayPause.SetBitmapDisabled( wx.Bitmap( os.path.join(self.icons, u"play_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnStop.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"stop.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnStop.SetBitmapDisabled( wx.Bitmap( os.path.join(self.icons, u"stop_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnVLC.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"vlc.png"), wx.BITMAP_TYPE_ANY ) )
        self.btnVLC.SetBitmapDisabled( wx.Bitmap( os.path.join(self.icons, u"vlc_disabled.png"), wx.BITMAP_TYPE_ANY ) )
        self.mitCheck.Enable(False)
        self.mitScheduled.Enable(False)
        self.btnVLC.Disable()

        self.version,self.display_version=version()
        self.SetTitle('%s (%s)'%(self.GetTitle(),self.display_version))
        self.StatusBar.SetFieldsCount(1)

        self._checking=False
        self._connecting=False
        self._deleting=False
        self._downloading=False
        self.deletedcache=os.path.join(self.configdir,'deleted.cache')
        self.downloadedcache=os.path.join(self.configdir,'downloaded.cache')
        self.deleted=PickledSet(self.deletedcache)
        self.downloaded=PickledSet(self.downloadedcache)
        self.player=None
        self.playpause=True
        self.total=0
        self.tempfile=False
        self.schedulelist=[]
        self.schedulequeue=Queue.Queue()
        self.scheduletime=None

        self.ThreadedConnector=None
        self.ThreadedConverter=None
        self.ThreadedDownloader=None
        self.ThreadedScheduler=None

        self.Play=threading.Event()
        self.Stop=threading.Event()
        self.StopStreaming=threading.Event()
        self.CancelConversion=threading.Event()

        self.Bind(EVT_ADDPROGRAM, self._AddProgram)
        self.Bind(EVT_CHECKCOMPLETE, self._CheckComplete)
        self.Bind(EVT_CONNECTED, self._Connected)
        self.Bind(EVT_DELETECOMPLETE, self._DeleteComplete)
        self.Bind(EVT_DELETEPROGRAM, self._DeleteProgram)
        self.Bind(EVT_UPDATEPROGRAM, self._UpdateProgram)
        self.Bind(EVT_DOWNLOADCOMPLETE, self.onDownloadComplete)
        self.Bind(EVT_LOG, self.onLog)
        self.Bind(EVT_SCHEDULEDDWONLOADCOMPLETE, self.onScheduledDownloadComplete)
        self.Bind(EVT_SCHEDULERCOMPLETE, self.onSchedulerComplete)
        self.Bind(EVT_PLAYCOMPLETE, self.onPlayComplete)
        self.Bind(EVT_STREAMCOMPLETE, self.onStreamComplete)
        self.Bind(EVT_UPDATEPROGRESS, self.onUpdateProgress)
        self.lstPrograms.SetSortEnabled(False)

        #Bind F5 to connect
        self._BindEvent( wx.EVT_KEY_DOWN, self.OnKeyDown,self )

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

        self._Enable()
        self._FadeIn()
        self.Show()

        if self.device and self.config.getboolean('Settings','autoconnect'):
            self._Connect()


    #######################################################################
    #Methods
    #######################################################################
    def _AddProgram(self,event=None,program=None):

        if event:
            program=event.program #This will fail when the program is added manually, not via the AddProgram event
            iidx=event.index

        for p in program:
            if type(program[p]) is str:program[p]=unicode(program[p],errors='ignore')
            elif type(program[p]) is unicode:program[p]=unicode(program[p].encode(errors='ignore'))

        if type(program['date']) is unicode:
            program['date']=time.strptime(program['date'],self.getwizpnp_dateformat) #Already converted if added manually

        display_date=time.strftime(self.display_dateformat,program['date'])
        program['length']=program.get('length',u'')
        program['size']=program.get('size',0)
        program['channel']=program.get('channel',u'')

        if program['index'] in self.programs:
            if len(self.programs[program['index']].get('info','')) > len(program['info']):
                del program['info']
            self.programs[program['index']].update(program)
        else:
            self.programs[program['index']]=program

        iidx=self.programs.keys().index(program['index'])
        lidx=self.lstPrograms.FindItemData(-1,iidx)

        if  program['index'] in self.deleted:
            if lidx>-1:self.lstPrograms.DeleteItem(lidx)
            return

        if lidx>-1:
            self.lstPrograms.SetStringItem(lidx,0,program['title'])
            self.lstPrograms.SetStringItem(lidx,1,program['channel'])
            self.lstPrograms.SetStringItem(lidx,2,time.strftime(self.display_dateformat,program['date']))
            self.lstPrograms.SetStringItem(lidx,3,u"%0.1f" % program['size'])
            self.lstPrograms.SetStringItem(lidx,4,program['length'])
        else:
            lidx=self.lstPrograms.GetItemCount()
            self.lstPrograms.Append({iidx:[program['title'],program['channel'],display_date,u"%0.1f" % program['size'],program['length']]})
            self.lstPrograms.SetItemData(lidx,iidx)
            self.total+=program['size']

        if  program['index'] in self.downloaded:
            self.lstPrograms.SetItemTextColour(lidx, wx.Colour(45,83,164))

        if self.total>0 and not self._downloading:
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields(['Total recordings %sMB'%round(self.total,1)])

        self.lstPrograms.resizeLastColumn(self.mincolwidth)

        if event:self._Log('Added %s - %s'%(program['title'],display_date))
        self.mitDownload.Enable( True )
        self.mitQueue.Enable( True )

    def _ApplyConfig(self):

        v=getwizpnpversion()

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
        devices=self.config.get('Settings','device').strip()
        logger.debug('Devices="%s"'%devices)
        if self.cbxDevice.GetCount()>0:
            d=self.cbxDevice.Value
        else:
            d=''
        self.cbxDevice.Clear()
        if devices:
            devices=devices.split(';')
            logger.debug('Devices="%s"'%devices)
            for device in devices:
                if device!='':
                    device=Device(device)
                    self.devices[device.display]=device
                    self.cbxDevice.Append(device.display)

        if self.cbxDevice.GetCount()>0:
            try:
                self.cbxDevice.SetSelection(self.cbxDevice.Items.index(d))
                self.device=self.devices[d]
            except:
                self.cbxDevice.SetSelection(0)
                self.device=self.devices.values()[0]

            sx,sy=self.cbxDevice.GetClientSizeTuple()
            self.cbxDevice.SetMinSize((self.cbxDevice.GetWidestItemWidth()+self.cbxDevice.GetButtonSize().x+20,sy))

        self.config.set('Settings','device',';'.join(map(str,self.devices.values())))

        logger.debug(self.config.get('Settings','device'))
        logger.debug(str(self.devices))
        logger.debug(self.devices.values())

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
                    logger.debug('Checking for gnome shell')
                    proc=subproc(['gnome-shell','--version'])
                    gstdout,gstderr=proc.communicate()
                    gexit_code=proc.wait()
                    gstdout,gstderr=gstdout.strip(),gstderr.strip()
                    logger.debug('exit_code: %s'%gexit_code)
                    logger.debug('stdout: %s'%gstdout)
                    logger.debug('stderr: %s'%gstderr)
                except Exception,err:
                    logger.debug('Exception,err: %s'%str(err))
                    gexit_code=1

                try:
                    logger.debug('Checking compiz')
                    proc=subproc(['compiz', '--version'])
                    cstdout,cstderr=proc.communicate()
                    cexit_code=proc.wait()
                    cstdout,cstderr=cstdout.strip(),cstderr.strip()
                    logger.debug('exit_code: %s'%cexit_code)
                    logger.debug('stdout: %s'%cstdout)
                    logger.debug('stderr: %s'%cstderr)
                except Exception,err:
                    logger.debug('Exception,err: %s'%str(err))
                    cexit_code=1

                if cexit_code != 0 and gexit_code!=0:
                    self.fade=self.config.getboolean('Window','fade') #Assume we're not running compiz/gnome3, so use the preference
                elif cexit_code==0:
                    comver=[int(v) for v in cstdout.split()[-1].split('.')]
                    logger.debug('compiz version: %s'%str(comver))
                    if comver>=[0,8,6]:
                        showfade=False
                        self.fade=False
                    else:
                        self.fade=self.config.getboolean('Window','fade') #Assume we're not running compiz, so use the preference
                elif gexit_code==0:
                    if os.environ.get('DESKTOP_SESSION',False)=='gnome':
                        showfade=False
                        self.fade=False
                    else:
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

        #getWizPnP
        self.wizargs=[]
        if iswin:
            self.wizargs+=['--wizpnpTimeout=%s'%self.config.get('getWizPnP','wizpnptimeout')]
            if v>=[0,5,4]:
                self.wizargs+=['--delay=%s'%self.config.get('getWizPnP','delay')]
            else:
                del self.configspec['getWizPnP']['delay']
                self.config.remove_option('getWizPnP','delay')
        else:
            try:
                del self.configspec['getWizPnP']
                self.config.remove_section('getWizPnP')
            except:pass

        #VLC Player
        logger.debug('VLC path: %s'%vlcexe)
        if vlcexe:
            self.vlcargs=self.config.get('Settings','vlcargs').split()
            if not iswin and '--qt-minimal-view' in self.vlcargs:
                self.vlcargs.remove('--qt-minimal-view')
                self.config.set('Settings','vlcargs',' '.join(self.vlcargs))

            self.btnVLC.Disable()
            self.mitStream.Enable()
            pos=-1
            for pos,mit in enumerate(self.mnuPrograms.GetMenuItems()):
                if mit.Label == self.mitStream.Label:break
            if pos>-1 and not self.mnuPrograms.FindItemByPosition(pos-1).IsSeparator():
                self.mnuPrograms.InsertSeparator(pos)

            if v<[0,5,3]:
                try:del self.configspec['Settings']['tempfile']
                except:pass
                self.tempfile=True
            else:
                self.tempfile=self.config.getboolean('Settings','tempfile')

        else:
            self.tempfile=False
            if 'vlcargs' in self.configspec['Settings']:
                try:del self.configspec['Settings']['vlcargs']
                except:pass
                try:del self.configspec['Settings']['tempfile']
                except:pass
            self.btnVLC.Hide()
            try:self.mnuPrograms.DeleteItem(self.mitStream)
            except:pass

        #Quick listing, can include deleted files
        self.quicklisting=self.config.getboolean('Settings','quicklisting')
        self.enableinfo=self.config.getboolean('Settings','enableinfo')

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

        #postdownload sound
        self.retries=self.config.getint('Settings','retries')
        self.deletefail=self.config.getboolean('Settings','delete')

    def _BindEvent(self,event,handler,window):
        try:window.Bind(event,handler)
        except:pass
        try:
            for cw in window.GetChildren():
                try:self._BindEvent(event,handler,cw)
                except:pass
        except:pass

    def _CheckComplete(self,event):
        if event and event.message:self._Log(event.message)
        self._checking=False
        self._Enable()
        self.lstPrograms.SetSortEnabled()

        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def _CheckWiz(self):
        if self._connecting or self._deleting or self._downloading:return
        if not self.device:return
        self._checking=True
        self.Stop.clear()
        self.lstPrograms.SetSortEnabled(False)
        self.mitCheck.Enable( False )
        self.btnConnect.Enable( False )
        self.cbxDevice.Enable( False )
        self.mitDelete.Enable( False )
        self.gaugeProgressBar.Show()
        self.gaugeProgressBar.Pulse()
        self.lblProgressText.Show()
        self.lblProgressText.SetLabelText('Checking recordings...')

        self._ShowTab(self.idxLog)
        self.mitCheck.Enable( False )
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
        self._Log('Checking recordings...')
        checker=ThreadedChecker(self,self.Stop,self.device)

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
        if self._connecting or self._checking or self._deleting or self._downloading:return
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
            device=str(self.cbxDevice.GetValue()).strip()
            if not device:return

        if device in self.devices:
            self.device=self.devices[device]
        else:
            self.device=Device(device)
            self.devices[self.device.display]=self.device
            self.cbxDevice.Append(self.device.display)
            self.config.set('Settings','device',';'.join([str(dev) for dev in self.devices.values()]))

        logger.debug('Connecting to %s'%(str(self.device)))
        self._Log('Connecting to %s...'%self.device.display)

        #Connect to the Wiz etc...
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
        self.ThreadedConnector=ThreadedConnector(self,self.Stop,device=self.device,
                                                 quick=self.quicklisting,wizargs=self.wizargs,
                                                 enableinfo=self.enableinfo)

    def _Connected(self,event=None):

        #if event and event.connected:
        #    if event.message:self._Log(event.message)
        #elif event and not event.connected:
        #    error_message(self,str(event.message))

        self._connecting=False
        self._Enable()

        if event and event.connected:
            downloaded,deleted=list(self.downloaded)[:],list(self.deleted)[:]
            for pidx in downloaded:
                #if pidx not in self.programs:del self.downloaded[self.downloaded.index(pidx)]
                if pidx not in self.programs:self.downloaded.remove(pidx)
            for pidx in deleted:
                #if pidx not in self.programs:del self.deleted[self.deleted.index(pidx)]
                if pidx not in self.programs:self.deleted.remove(pidx)

            self.lstPrograms.SetSortEnabled()

        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def _Convert(self):

        self.CancelConversion.clear()
        #dirdlg=mdd.MultiDirDialog(self, message='Select one or more tvwiz folders.',
        #                          agwStyle=mdd.DD_MULTIPLE|mdd.DD_DIR_MUST_EXIST)
        dirdlg=wx.DirDialog(self, message='Select a tvwiz folder.',
                            defaultPath=self.config.get('Settings','lastdir'),
                            style=wx.DD_DIR_MUST_EXIST)

        if dirdlg.ShowModal() == wx.ID_OK:
            #folders=dirdlg.GetPaths()
            folders=[dirdlg.GetPath()]
            if not folders:return

            self.ThreadedConverter=ThreadedConverter(self,self.CancelConversion,folders)

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
        if self._connecting or self._checking:return
        idx = self.lstPrograms.GetFirstSelected()
        programs=[]
        indices=[]
        prognames=[]

        while idx != -1:
            lidx = self.lstPrograms.GetItemData(idx)
            pidx = self.programs.keys()[lidx]
            program = self.programs[pidx]

            if '*RECORDING' in program['title']:
                msg='Unable to delete %s as it is currently recording.'%program['title']
                self._Log(msg,logging.ERROR)
                self._ShowTab(self.idxLog)
            elif '*LOCKED' in program['title']:
                msg='Unable to delete %s as it is LOCKED.'%program['title']
                self._Log(msg,logging.ERROR)
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
            self._deleting=True
            if not self._downloading:
                self.lstPrograms.SetSortEnabled(False)
                self.mitCheck.Enable( False )
                self.btnConnect.Enable( False )
                self.cbxDevice.Enable( False )
                self.mitDelete.Enable( False )
                self.mitCheck.Enable( False )
                self.gaugeProgressBar.Show()
                self.gaugeProgressBar.Pulse()
                self.lblProgressText.Show()
                self.lblProgressText.SetLabelText('Deleting recordings...')

            self._ShowTab(self.idxLog)
            indices.reverse()
            programs.reverse()
            logger.debug('_DeleteFromWiz, indices: %s'%str(indices))
            logger.debug('_DeleteFromWiz, programs: %s'%str(programs))
            self._SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
            deletions=ThreadedDeleter(self,self.Stop,self.device,programs,indices)

    def _DeleteComplete(self,event):
        self._SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self._deleting=False
        if not self._downloading:
            self._Enable()
            self.lstPrograms.SetSortEnabled(True)

    def _DeleteProgram(self,event):
        if event.index>-1:
            lidx=self.lstPrograms.FindItemData(-1,event.index)
            if lidx>-1:
                pidx=self.programs.keys()[event.index]
                if pidx not in self.deleted:self.deleted.add(pidx)
                self.lstPrograms.DeleteItem(lidx)
                self.total-=self.programs[pidx]['size']
                if not self._downloading:
                    self.StatusBar.SetFieldsCount(1)
                    self.StatusBar.SetFields(['Total recordings %sMB'%round(self.total,1)])
            qidx=self.lstQueue.FindItemData(-1,event.index)
            if qidx>-1:
                del self.queue[self.queue.index(pidx)]
                self.lstQueue.DeleteItem(qidx)

    def _Discover(self):
        self._Log('Searching for Wizzes.')
        cmd=[wizexe,'--discover']
        #if iswin:cmd+=['--wizpnpTimeout=2']
        try:
            proc=subproc(cmd)
        except Exception,err:
            logger.error(str(err))
            self._Log('Error searching for Wizzes:')
            self._Log(str(err))
            error_message(self, str(err),'Error searching for Wizzes:')
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
                sx,sy=self.cbxDevice.GetClientSizeTuple()
                self.cbxDevice.SetMinSize((self.cbxDevice.GetWidestItemWidth()+self.cbxDevice.GetButtonSize().x+20,sy))

        else:
            #self.cbxDevice.Clear()
            #self.cbxDevice.SetValue('')
            msg='Unable to discover any Wizzes.'
            self._Log(msg,logging.ERROR)
            self._ShowTab(self.idxLog)

        #Update config
        self.config.set('Settings','device',';'.join([str(dev) for dev in self.devices.values()]))

    def _DownloadQueue(self,getfilenames=True):
        if self._downloading:return

        programs=[]
        size=0
        for pidx in self.queue:
            program = self.programs[pidx]
            if getfilenames:filename = self._GetFileName(program)
            else: filename=program.get('filename',None)
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
            self.connecttimer = wx.PyTimer(Callback(self._DownloadQueue,False))
            self.connecttimer.Start(250,wx.TIMER_ONE_SHOT)
            return

        self.btnPlayPause.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"pause.png"), wx.BITMAP_TYPE_ANY ) )
        self.playpause=False
        self.btnPlayPause.Enable( True )
        self.btnPlayPause.SetToolTipString('Pause download')
        self.btnStop.Enable( True )
        self.lblProgressText.SetLabelText('')
        self.gaugeProgressBar.Hide()
        self.gaugeProgressBar.Show()
        self.btnClearQueue.Enable( False )
        self.btnDownload.Enable( False )
        self.btnConnect.Enable( False )
        self.lstQueue.Enable( False )
        self.mitExit.Enable( False )
        self.mitQueue.Enable( False )
        self.mitDownload.Enable( False )
        self._downloading=True
        self.ThreadedDownloader=ThreadedDownloader(self,self.device,programs,self.Play,self.Stop, self.retries,self.deletefail,wizargs=self.wizargs)

    def _DownloadComplete(self,index,stopped):
        pidx=0
        if len(self.queue)>0:
            pidx=self.queue[0]
            item=self.lstPrograms.FindItemData(-1,self.programs.keys().index(pidx))
            del self.queue[0]
            self.lstQueue.DeleteItem(0)
            if not stopped:
                self.downloaded.add(pidx)

                try:
                    self.lstPrograms.SetItemTextColour(item, wx.Colour(45,83,164))
                    self.lstPrograms.Select(item, 0) #Deselect
                except:pass
                if self.playsounds:
                    try:
                        if not os.path.exists(self.downloadcompletesound):
                            raise IOError, 'No such file or directory: %f'%self.downloadcompletesound
                        sound = wx.Sound(self.downloadcompletesound)
                        sound.Play(wx.SOUND_ASYNC)
                    except Exception, err:
                        self._Log(str(err))
                        error_message(self, str(err))

        if not stopped and pidx:
            program=self.programs[pidx]
            self._PostDownloadCommand(program)

        if len(self.queue)==0 or stopped:
            self._downloading=False
            self.gaugeProgressBar.Hide()
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields([''])
            self.lblProgressText.SetLabelText('')
            self.lblProgressText.Hide()
            self.btnPlayPause.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"play.png"), wx.BITMAP_TYPE_ANY ) )
            self.playpause=True
            self.btnPlayPause.Enable( False )
            self.btnPlayPause.SetToolTipString('Resume download')

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

    def _Enable(self):
        self.Stop.clear()
        self.mitDelete.Enable( True )
        if self.device: 
            self.mitCheck.Enable( True )
        if not self._downloading:
            self.btnConnect.Enable( True )
            self.cbxDevice.Enable( True )
            self.lblProgressText.SetLabelText('')
            self.lblProgressText.Hide()
            self.gaugeProgressBar.Hide()

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

            try: #Kludge to work around segfault on Ubuntu 11.10 (Issue 30)
                import pygtk,gtk,warnings
                pygtk.require('2.0')
                assert gtk.pygtk_version >= (2,3,90)
                warnings.filterwarnings('ignore','',gtk.Warning)
                dialog = gtk.FileChooserDialog("Save as..",
                                               None,gtk.FILE_CHOOSER_ACTION_SAVE,
                                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
                dialog.set_default_response(gtk.RESPONSE_OK)
                dialog.set_current_folder(self.config.get('Settings','lastdir'))
                dialog.set_current_name(os.path.basename(filename))

                tsfilter = gtk.FileFilter()
                tsfilter.set_name("TS Files (*.ts)")
                tsfilter.add_pattern("*.ts")

                twfilter = gtk.FileFilter()
                twfilter.set_name("TVWIZ format (*.tvwiz)")
                twfilter.add_pattern("*.tvwiz")

                if self.tsformat:
                    dialog.add_filter(tsfilter)
                    dialog.add_filter(twfilter)
                else:
                    dialog.add_filter(twfilter)
                    dialog.add_filter(tsfilter)

                response = dialog.run()

                if response == gtk.RESPONSE_OK:
                    filename=dialog.get_filename()
                    filter=dialog.get_filter().get_name()
                    if filter=='TS Files (*.ts)':ext='.ts'
                    else:ext='.tvwiz'
                    if not os.path.splitext(filename)[1].lower()==ext:filename+=ext
                    self.config.set('Settings','lastdir',os.path.dirname(filename))
                else:filename=None
                dialog.destroy()

            except:
                tsspec='TS Files (*.ts)|*.ts'
                twspec='TVWIZ format (*.tvwiz)|*.tvwiz'
                if self.tsformat:
                    filespec='|'.join([tsspec,twspec])
                    ext=['.ts','.tvwiz']
                else:
                    filespec='|'.join([twspec,tsspec])
                    ext=['.tvwiz','.ts']
                #Issue 40
                if isosx:filename+='.foo'
                dlg = wx.FileDialog(self, "Save As...", self.config.get('Settings','lastdir'), filename,filespec, wx.FD_SAVE)
                if (dlg.ShowModal() == wx.ID_OK):
                    f=dlg.Filename#.encode(filesysenc)
                    d=dlg.Directory#.encode(filesysenc)
                    if d[-1]==':':d+=os.path.sep
                    ext=ext[dlg.GetFilterIndex()]
                    if not os.path.splitext(f)[1].lower()==ext:f+=ext
                    self.config.set('Settings','lastdir',d)
                    filename=os.path.join(d,f)

                else:filename=None

            try:
                d,f=os.path.split(filename)
                if d.lower().endswith('.tvwiz'):
                    filename=os.path.join(os.path.dirname(d),f)
            except:filename=None
            return filename

    def _Hide(self,*args,**kwargs):
        self.progress_timer.Stop()
        self.gaugeProgressBar.SetRange(100)
        self.gaugeProgressBar.SetValue(0)
        self.gaugeProgressBar._Hide()

    def _Log(self,msg,severity=logging.INFO):
        self.txtLog.SetInsertionPointEnd()
        msg=msg.strip()
        if msg:
            try:self.txtLog.WriteText(msg+'\n')
            except:self.txtLog.WriteText(str(msg)+'\n')
            self.txtLog.ShowPosition(self.txtLog.GetLastPosition())
            logger.debug(msg)
            if severity > logging.INFO:error_message(self,msg)

    def _Play(self,filename=None):
        if filename is None:filename=self.filename
        if filename:
            self.player=ThreadedPlayer(self, self.Stop, self.Play,self.filename,vlcargs=self.vlcargs)

    def _PostDownloadCommand(self,program):
        cmd=self.postcmd.split('#')[0].strip()

        if cmd:
            import shlex
            cmd=cmd.replace('%F', '"%s"'%program['filename'])
            cmd=cmd.replace('%D', '"%s"'%os.path.dirname(program['filename']))
            cmd=shlex.split(cmd)
            logger.debug('Postdownload command: %s'%cmd)
            try:
                #pid = subprocess.Popen(cmd,shell=True).pid #Don't wait, nor check the output, leave that up to the user
                pid = subprocess.Popen(cmd).pid #Don't wait, nor check the output, leave that up to the user
            except Exception,err:
                self._Log('Can\'t run post download command on %s'%program['filename'])
                self._Log(str(err))
                error_message(self, 'Can\'t run post download command\n'+str(err))

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
                msg='Unable to download %s as it is currently recording.'%program['title']
                self._Log(msg,logging.ERROR)
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
        configdir=self.configdir
        defaultconfig=os.path.join(data_path(),'config','defaults.ini')
        self.userconfig=os.path.join(configdir,'config.ini')
        self.config=ConfigParser.RawConfigParser(dict_type=ordereddict.OrderedDict)
        self.config.read([defaultconfig,self.userconfig])
        self.configspec=configspec.configspec
        self._CleanupConfig()

        #Add logfile to config so it shows in "Tools->Options..." dialog
        self.config.set('Debug','logfile',logfile)

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
                msg='Unable to schedule %s as it is currently recording.'%program['title']
                self._Log(msg,logging.ERROR)
                self._ShowTab(self.idxLog)
            elif pidx not in self.schedulelist:
                filename = self._GetFileName(program)
                if filename:
                    self.programs[pidx]['filename']=filename
                    schedulelist.append(pidx)
                else:return

            idx = self.lstPrograms.GetNextSelected(idx)

        if not schedulelist:return
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
                self.ThreadedScheduler = ThreadedScheduler(self, scheduletime,self.schedulequeue,self.retries,self.deletefail,self.wizargs)

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

    def _SetCursor(self,cursor,window=None):
        if not window:window=self
        try:window.SetCursor(cursor)
        except:pass
        try:
            for cw in window.GetChildren():
                try:self._SetCursor(cursor,cw)
                except:pass
        except:pass

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

    def _ShowSelectedSize(self):
        idx = self.lstPrograms.GetFirstSelected()
        if idx == -1:
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields(['Total recordings %sMB'%round(self.total,1)])
        else:
            size=0
            i=0
            while idx != -1:
                i+=1
                lidx = self.lstPrograms.GetItem(idx).Data
                pidx = self.programs.keys()[lidx]
                program = self.programs[pidx]
                size+=program['size']

                idx = self.lstPrograms.GetNextSelected(idx)

            self.StatusBar.SetFieldsCount(2)
            if i==1:msg='Selected recording %sMB'%round(size,1)
            else:msg='Selected recordings %sMB'%round(size,1)
            self.StatusBar.SetFields(['Total recordings %sMB'%round(self.total,1),msg])

    def _ShowTab(self,tabindex):
        self.nbTabArea.ChangeSelection(tabindex)

    def _Stream(self):
        idx = self.lstPrograms.GetFirstSelected()
        if idx == -1:return
        qidx = self.lstPrograms.GetItem(idx).Data
        pidx=self.programs.keys()[qidx]
        program = self.programs[pidx]
        if '*RECORDING' in program['title']:
            msg='Unable to play %s as it is currently recording.'%program['title']
            self._Log(msg,logging.ERROR)
            self._ShowTab(self.idxLog)
            return
        self.mitStream.Enable(False)
        tp=ThreadedStreamPlayer(self, self.device, program, self.StopStreaming, self.tempfile, self.vlcargs, self.wizargs)

    def _UpdateProgram(self,event):
        program=event.program

        for p in program:
            if type(program[p]) is str:program[p]=unicode(program[p],errors='ignore')
            elif type(program[p]) is unicode:program[p]=unicode(program[p].encode(errors='ignore'))

        if type(program['date']) is unicode:program['date']=time.strptime(program['date'],self.getwizpnp_dateformat)
        if program['index'] in self.programs:
            idx=self.lstPrograms.FindItemData(-1,self.programs.keys().index(program['index']))
            if self.programs[program['index']]['size']==0:
                self.total+=program['size']
            self.programs[program['index']].update(program)
        else:
            self._AddProgram(program=program)
            return
        if self.total>0 and not self._downloading:
            self.StatusBar.SetFieldsCount(1)
            self.StatusBar.SetFields(['Total recordings %sMB'%round(self.total,1)])
        try:
            self.lstPrograms.SetStringItem(idx,0,program['title'])
            self.lstPrograms.SetStringItem(idx,1,program['channel'])
            self.lstPrograms.SetStringItem(idx,2,unicode(time.strftime(self.display_dateformat,program['date'])))
            self.lstPrograms.SetStringItem(idx,3,u"%0.1f" % program['size'])
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

        #Remove logfile so it doesn't get written out
        self.config.remove_option('Debug', 'logfile')

        if not self.config.getboolean('Settings','cachedevice'):
            self.config.set('Settings','device','')

        sections = self.config.sections()
        for section in sections:
            logger.debug(repr(section))
            options = self.config.options(section)
            for option in options:
                val=self.config.get(section,option)
                logger.debug('    %s=%s'%(repr(option),repr(val)))
                if isinstance(val, unicode):
                    self.config.set(section,option,val.encode(filesysenc))

        if not os.path.exists(os.path.dirname(self.userconfig)):
            os.mkdir(os.path.dirname(self.userconfig))
        self.config.write(open(self.userconfig,'w'))

        #Add logfile back in so it shows in "Tools->Options..." dialog
        self.config.set('Debug', 'logfile', logfile)

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

    def btnPlayPause_OnClick( self, event ):
        if self.playpause:self.btnPlay_OnClick(event)
        else:self.btnPause_OnClick(event)

    def btnPlay_OnClick( self, event ):
        self.btnPlayPause.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"pause.png"), wx.BITMAP_TYPE_ANY ) )
        self.playpause=False
        self.btnPlayPause.Enable( True )
        self.btnPlayPause.SetToolTipString('Pause download')

        self.btnStop.Enable( True )
        self.Play.set()
        event.Skip()

    def btnPause_OnClick( self, event ):
        self.btnPlayPause.SetBitmapLabel( wx.Bitmap( os.path.join(self.icons, u"play.png"), wx.BITMAP_TYPE_ANY ) )
        self.playpause=True
        self.btnPlayPause.Enable( True )
        self.btnPlayPause.SetToolTipString('Resume download')

        self.Play.clear()

    def btnStop_OnClick( self, event ):
        self.Stop.set()

    def btnVLC_OnClick( self, event ):
        self._Play()
        self.btnVLC.Disable()

    def cbxDevice_OnCombobox( self, event ):
        if self.config.getboolean('Settings','onselect'):
            self._Connect()

    def cbxDevice_OnKillFocus( self, event ):
        if self.cbxDevice.IsEnabled():
            device=str(self.cbxDevice.GetValue())
            if device:
                if device in self.devices:
                    self.device=self.devices[device]
                else:
                    self.device=Device(device)
                    self.devices[device]=self.device
                    self.cbxDevice.Append(self.device.display)
                self._Enable()

                #Update config
                self.config.set('Settings','device',';'.join(map(str,self.devices.values())))
                logger.debug(self.config.get('Settings','device'))
                logger.debug(str(self.devices))
                logger.debug(self.devices.values())

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

    def lstPrograms_OnDeselect( self, event ):
        self._ShowSelectedSize()

    def lstPrograms_OnDoubleClick( self, event ):
        self._Queue()

    def lstPrograms_OnRightClick( self, event ):
        self.lstPrograms.PopupMenu(self.mnuPrograms)

    def lstPrograms_OnSelect( self, event, showinfo=True ):
        if showinfo:self._ShowInfo()
        self.lstPrograms.SetFocus()
        self._ShowSelectedSize()

    def lstQueueOnContextMenu( self, event ):
        self.mitRemove.Enable( False )
        self.lstQueue.PopupMenu(self.mnuQueue)

    def lstQueue_OnRightClick( self, event ):
        self.lstQueue.PopupMenu(self.mnuQueue)

    def lstQueue_OnMiddleClick( self, event ):
        self.mitRemove_OnSelect(event)

    def mitAbout_OnSelect( self, event ):
        self._FadeOut(stop=200,delta=-25)
        dlg=AboutDialog(self)
        self._FadeIn(start=200,delta=25)

    def mitCheck_OnSelect( self, event ):
        self._CheckWiz()

    def mitClearQueue_OnSelect( self, event ):
        self._ClearQueue()

    def mitConvert_OnSelect( self, event ):
        self._Convert()

    def mitDelete_OnSelect( self, event ):
        self._DeleteFromWiz()

    def mitDownload_onSelect( self, event ):
        self._Queue(clear=True)
        self._DownloadQueue()

    def mitDownloadAll_OnSelect( self, event ):
        self._DownloadQueue()

    def mitHelp_OnSelect( self, event ):
        webbrowser.open_new_tab(HELP_URL)

    def mitPreferences_OnSelect( self, event ):
        self._FadeOut(stop=200,delta=-25)
        self.cbxDevice_OnKillFocus(None) #Clicking a menu item doesn't move focus off a control,
                                         #so make sure the device name gets updated.
        settings=SettingsDialog(self,self.config,self.configspec)
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

    def mitStream_OnSelect( self, event ):
        self._Stream()

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
        try:self.StopStreaming.set()
        except:pass
        try:self.CancelConversion.set()
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
        self._Log(event.message, event.severity)

    def onPlayComplete( self, event ):
        self.btnVLC.Disable()
        del self.player
        self.player=None

    def onStreamComplete( self, event ):
        self.mitStream.Enable()

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
        txtversion=version()[1]
        txtgetwizpnp=getwizpnpversion(True)

        sxmin,symin=centrepos(self,parent)
        self.SetPosition((sxmin,symin))

        self.LicenseDialog=LicenseDialog(self)
        self.LicenseDialog.txtLicense.SetValue(txtlicense)
        self.lblVersion.SetLabel('Version: '+txtversion)
        self.lblGetWizPnPversion.SetLabel('GetWizPnP version: '+txtgetwizpnp)
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
        self.Sizer.Fit( self )
        self.PropertyScrolledPanel.SetAutoLayout(1)
        self.PropertyScrolledPanel.SetConfig(config, specs)
        self.PropertyScrolledPanel.SetupScrolling()
        self.Layout()
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

def info_message(parent,message,caption='Info'):
    dlg = wx.MessageDialog(
    parent=parent,
    message=message,
    caption=caption,
    style=wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP,
    pos=(200,200)
    )
    dlg.ShowModal()
    dlg.Destroy()

def error_message(parent,message,caption='Error'):
    dlg = wx.MessageDialog(
    parent=parent,
    message=message,
    caption=caption,
    style=wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP
    )
    dlg.ShowModal()
    dlg.Destroy()


