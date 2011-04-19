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
import os,sys,threading,thread,time,ConfigParser
import locale,re,webbrowser
import ordereddict
import wx
import gui, configspec
from ordereddict import OrderedDict as odict
from events import *
from utilities import *

APPNAME='YARDWiz'
locale.setlocale(locale.LC_ALL,'')
decsep=locale.localeconv()['mon_decimal_point']

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
        ico = wx.Icon( os.path.join(icons, u"icon.png"), wx.BITMAP_TYPE_ANY )
        self.SetIcon(ico)
        self.btnConnect.SetBitmapLabel( wx.Bitmap( os.path.join(icons, u"reload.png"), wx.BITMAP_TYPE_ANY ) )
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

        self.version,self.display_version=version()

        self._ReadConfig()
        self._ApplyConfig()
        self.SetTitle('%s (%s)'%(self.GetTitle(),self.display_version))

        self._downloading=False
        self.total=0
        self.deleted=[]

        self.ThreadedConnector=None
        self.ThreadedDownloader=None
        self.Play=threading.Event()
        self.Stop=threading.Event()

        self.Bind(EVT_ADDPROGRAM, self._AddProgram)
        self.Bind(EVT_DELETEPROGRAM, self._DeleteProgram)
        self.Bind(EVT_UPDATEPROGRAM, self._UpdateProgram)
        self.Bind(EVT_CONNECTED, self._Connected)

        self.Bind(EVT_LOG, self.onLog)
        self.Bind(EVT_UPDATEPROGRESS, self.onUpdateProgress)
        self.Bind(EVT_DOWNLOADCOMPLETE, self.onDownloadComplete)
        self.lstPrograms.SetSortEnabled(True)

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

        self.gaugeProgressBar.Hide()

        #check for GetWizPnP
        errmsg='''Error: YARDWiz requires %s to communicate with your Beyonwiz.\n\nPlease install %s from: http://www.openwiz.org/wiki/GetWizPnP_Release'''%(wizexe,wizexe)
        ok=which(wizexe)
        if not ok:
            errdial = wx.MessageDialog(None,errmsg,'Missing GetWizPnP', wx.OK | wx.ICON_ERROR)
            errdial.ShowModal()
            sys.exit(1)

        #Regular expressions for IP, IP:port, and hostname
        self._regexip=r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$' #May not be a valid IP, but it's the right form...
        self._regexipport=self._regexip[:-1]+'(:(\d{1,5}))$'
        
    #######################################################################
    #Methods
    #######################################################################
    def _AddProgram(self,evt=None,program=None):

        if evt:
            program=evt.program #This will fail when the program is added manually, not via the AddProgram event
            program['date']=time.strptime(program['date'],self.getwizpnp_dateformat) #Already converted if added manually

        display_date=time.strftime(self.display_dateformat,program['date'])
        program['length']=program.get('length','').replace(':',decsep)
        program['size']=program.get('size',0)
        program['channel']=program.get('channel','')

        iidx=len(self.programs)
        self.programs[program['index']]=program

        self.lstPrograms.Append([program['title'],program['channel'],display_date,program['size'],program['length']])
        self.lstPrograms.SetItemData(iidx,iidx)

        self.total+=program['size']
        if self.total>0:self.StatusBar.SetFields(['','','Total recordings %sMB'%self.total])

        for j in range(self.lstPrograms.GetColumnCount()):
            self.lstPrograms.SetColumnWidth(j, autosize)
            if not iswin:
                c=self.lstPrograms.GetColumnWidth(j)
                h=self.lstPrograms.HeaderWidths[j]
                if h>c:self.lstPrograms.SetColumnWidth(j,h)
        self.lstPrograms.resizeLastColumn(self.mincolwidth)

        if evt:self._Log('Added %s - %s'%(program['title'],display_date))
        self.mitDownload.Enable( True )
        self.mitQueue.Enable( True )

    def _ApplyConfig(self):

        #write stuff to various controls, eg server & port
        device=self.config.get('Settings','device')
        self.cbxDevice.Clear()
        self.cbxDevice.SetValue(device)
        xsize=self.config.getint('Window','xsize')
        ysize=self.config.getint('Window','ysize')
        xmin=self.config.getint('Window','xmin')
        ymin=self.config.getint('Window','ymin')
        xres,yres=wx.GetClientDisplayRect()[2:]
        if [xsize,ysize,xmin,ymin]==[-1,-1,-1,-1]:
            #Set default sizing
            xres,yres=wx.GetClientDisplayRect()[2:]
            proportion=0.75
            aspectratio=1.25
            ysize=int(yres*proportion)
            xsize=int(ysize*aspectratio)
            self.SetSize( wx.Size( xsize,ysize ) )
            self.Centre( wx.BOTH )
        else:
            self.SetSize( wx.Size( xsize,ysize ) )
            #make sure it's on the screen
            xmin=max([xmin,0])
            ymin=max([ymin,0])
            xmin=min([xmin,xres-xsize])
            ymin=min([ymin,yres-ysize])
            self.SetPosition(wx.Point(xmin,ymin))

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
        if not self.downloadcompletesound or self.downloadcompletesound.lower()=='<default>':
            self.downloadcompletesound=os.path.join(data_path(),'sounds','downloadcomplete.wav')
            self.config.set('Sounds','downloadcomplete', self.downloadcompletesound)

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
        self._Reset()
        self.lstPrograms.SetSortEnabled(False)
        self.btnConnect.Enable( False )
        self.mitDelete.Enable( False )
        self.lblProgressText.SetLabelText('Connecting...')
        self.gaugeProgressBar.Show()
        self.gaugeProgressBar.Pulse()

        self.device=self.cbxDevice.GetValue().strip()
        self.ip,self.port=None,None
        if not self.device:
            self._Discover()
            self._Connected(False)
            if self.cbxDevice.GetCount()==1:self._Connect()
            return
        else:
            self.config.set('Settings','device',self.device)
            ipport=re.match(self._regexipport,self.device)
            iponly=re.match(self._regexip,self.device)
        if ipport:
            self.ip,self.port=self.device.split(':')
            self.device=None
        elif iponly:
            self.ip,self.port=self.device,'49152'
            self.device=None

        self._Log('Connecting to %s...'%self.config.get('Settings','device'))

        #Connect to the Wiz etc...
        self.ThreadedConnector=ThreadedConnector(self,device=self.device,ip=self.ip,port=self.port, deleted=self.deleted, quick=self.quicklisting)

    def _Connected(self,event=None):
        self.lblProgressText.SetLabelText('')
        self.gaugeProgressBar.Hide()

        if event and event.message:
            self._Log(event.message)
        self.btnConnect.Enable( True )
        self.mitDelete.Enable( True )
        self.lstPrograms.SetSortEnabled(True)

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
        i=-1
        programs=[]
        indices=[]
        prognames=[]
        
        while idx != -1:
            pidx = self.lstPrograms.GetItem(idx).Data
            pidx = self.programs.keys()[pidx]
            program = self.programs[pidx]
            
            if '*RECORDING' in program['title']:
                self._Log('Unable to delete %s as it is currently recording.'%program['title'])
                self._ShowTab(self.idxLog)
            elif '*LOCKED' in program['title']:
                self._Log('Unable to delete %s as it is LOCKED.'%program['title'])
                self._ShowTab(self.idxLog)
            else:
                prognames.append('%s-%s'%(program['title'],time.strftime(self.filename_dateformat,program['date'])))
                indices.append(idx)
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
            deletions=ThreadedDeleter(self,self.device,self.ip,self.port,programs,indices)
            #self._ClearPrograms()
            #for program in programs:
            #    if not program['index'] in deletions:
            #        self._AddProgram(program=program)

    def _DeleteProgram(self,event):
        idx=self.lstPrograms.FindItemData(-1,event.index)
        pidx=self.programs.keys()[event.index]
        self.deleted.append(pidx)
        self.lstPrograms.DeleteItem(idx)
        
    def _Discover(self):
        self._Log('Searching for Wizzes.')
        cmd=[wizexe,'--discover']
        cmd=subprocess.list2cmdline(cmd)
        proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
        stdout,stderr=proc.communicate()
        exit_code=proc.wait()
        stdout=stdout.strip()
        if stdout:
            self.cbxDevice.Clear()
            self.cbxDevice.SetValue('')
            for wiz in stdout.split('\n'):
                wiz=wiz.strip().split()
                if wiz and len(wiz)>1:
                    wizname=' '.join(wiz[1:])
                    self._Log('Discovered %s (%s).'%(wizname,wiz[0]))
                    self.cbxDevice.Append(wizname)
                    self.config.set('Settings','device',wizname)

            if self.cbxDevice.GetCount()>0:self.cbxDevice.SetSelection(0)
        else:
            self.cbxDevice.Clear()
            self.cbxDevice.SetValue('')
            self._Log('Unable to discover any Wizzes.')
            self._ShowTab(self.idxLog)

    def _DownloadQueue(self,*args):
        if self._downloading:return

        programs=[]
        size=0
        for pidx in self.queue:
            program = self.programs[pidx]
            filename = program.get('filename',None)

            if not filename:
                filename_date=time.strftime(self.filename_dateformat,program['date'])
                filename=self._sanitize('%s %s'%(program['title'],filename_date))
                dlg = wx.FileDialog(self, "Open", self.config.get('Settings','lastdir'), filename,"TS Files (*.ts)|*.ts|All Files|*.*", wx.FD_SAVE)
                if (dlg.ShowModal() == wx.ID_OK):
                    f=dlg.Filename
                    d=dlg.Directory
                    if d[-1]==':':d+=os.path.sep
                    if not f[-3:].lower()=='.ts':f+='.ts'
                    self.config.set('Settings','lastdir',d)
                    filename=os.path.join(d,f)
                else:return #Stop showing file dialogs if queue download is cancelled

            program['filename']=filename
            self.programs[pidx]['filename']=filename
            programs.append(program)
            size+=program['size']
            
        self._ShowTab(self.idxLog)
        if not programs:return

        if size==0:
            self.btnClearQueue.Enable( False )
            self.btnDownload.Enable( False )
            self.connecttimer = wx.PyTimer(self._DownloadQueue)
            self.connecttimer.Start(250,wx.TIMER_ONE_SHOT)
            return
        
        self.btnPlay.Enable( False )
        self.btnPause.Enable( True )
        self.btnStop.Enable( True )
        self.gaugeProgressBar.Show()
        #self.btnPlay.Show() #This produces 'unexpected results' on ubuntu 10.04 & 10.10
        #self.btnPause.Show()
        #self.btnStop.Show()
        self.btnClearQueue.Enable( False )
        self.btnDownload.Enable( False )
        self.btnConnect.Enable( False )
        self.btnExit.Enable( False )
        self.lstQueue.Enable( False )
        self.mitExit.Enable( False )
        self.mitQueue.Enable( False )
        self.mitDownload.Enable( False )
        self._downloading=True
        self.ThreadedDownloader=ThreadedDownloader(self,self.device,self.ip,self.port,programs,self.Play,self.Stop)

    def _DownloadComplete(self,index,stopped):
        pidx=0
        if len(self.queue)>0:
            pidx=self.queue[0]
            item=self.lstPrograms.FindItemData(-1,self.programs.keys().index(pidx))
            del self.queue[0]
            self.lstQueue.DeleteItem(0)
            if not stopped:
                try:self.lstPrograms.SetItemTextColour(item, wx.Colour(45,83,164))
                except:pass
                if self.playsounds:
                    sound = wx.Sound(self.downloadcompletesound)
                    try:sound.Play(wx.SOUND_SYNC)
                    except Exception, err:
                        self._Log(err)


        cmd=self.postcmd.split('#')[0].strip()
        if not stopped and pidx and cmd:
            program=self.programs[pidx]
            cmd=cmd.replace('%F', '"%s"'%program['filename'])
            cmd=cmd.replace('%D', '"%s"'%os.path.dirname(program['filename']))
            try:
                pid = subprocess.Popen(cmd,shell=True).pid #Don't wait, nor check the output, leave that up to the user
            except Exception,err:
                self._Log('Can\'t run post download command on %s'%program['filename'])
                self._Log(err)

        if len(self.queue)==0 or stopped:
            self._downloading=False
            #self.btnPlay.Hide() #This produces 'unexpected results' on ubuntu 10.04 & 10.10
            #self.btnPause.Hide()
            #self.btnStop.Hide()
            self.gaugeProgressBar.Hide()
            self.StatusBar.SetFields(['','',''])
            self.lblProgressText.SetLabelText('')
            self.btnPlay.Enable( False )
            self.btnPause.Enable( False )
            self.btnStop.Enable( False )
            self.btnConnect.Enable( True )
            self.btnExit.Enable( True )
            self.mitQueue.Enable(True)
            self.mitExit.Enable( True )
            self.mitDownload.Enable( True )
            if len(self.queue)==0:
                self.btnClearQueue.Enable( False )
                self.btnDownload.Enable( False )
                self.lstQueue.Enable( False )
            else:
                self.btnClearQueue.Enable( True )
                self.btnDownload.Enable( True )
                self.lstQueue.Enable( True )

    def _Hide(self,*args,**kwargs):
        self.progress_timer.Stop()
        self.gaugeProgressBar.SetRange(100)
        self.gaugeProgressBar.SetValue(0)
        self.gaugeProgressBar._Hide()

    def _Log(self,msg):
        self.txtLog.WriteText(msg+'\n')
        self.txtLog.ShowPosition(self.txtLog.GetLastPosition())

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
            confighome = os.path.join(os.environ['HOME'], '.config')
            if os.path.exists(confighome) and os.path.isdir(confighome):
                configdir = os.path.join(confighome, APPNAME.lower())
            else:
                configdir = os.path.join(os.environ['HOME'], '.'+APPNAME.lower())

        defaultconfig=os.path.join(data_path(),'config','defaults.ini')
        self.userconfig=os.path.join(configdir,'config.ini')
        self.config=ConfigParser.ConfigParser(dict_type=ordereddict.OrderedDict)
        self.config.read([defaultconfig,self.userconfig])
        self.configspec=configspec.configspec
        self._CleanupConfig()

    def _Reset(self):
        self._ClearQueue()
        self._ClearPrograms()

    def _ShowInfo(self):
        idx = self.lstPrograms.GetFocusedItem()
        if idx>-1:
            self.txtInfo.Clear()
            idx = self.lstPrograms.GetItem(idx).Data
            pidx=self.programs.keys()[idx]
            info=self.programs[pidx].get('info','No program information available')
            self.txtInfo.WriteText(info+'\n')
            self.txtInfo.ShowPosition(0)
            self._ShowTab(self.idxInfo)

    def _ShowTab(self,tabindex):
        self.nbTabArea.ChangeSelection(tabindex)

    def _UpdateProgram(self,event):
        idx=self.lstPrograms.FindItemData(-1,event.index)
        program=event.program
        if type(program['date']) is str:program['date']=time.strptime(program['date'],self.getwizpnp_dateformat)
        if program['index'] in self.programs:
            self.programs[program['index']].update(program)
        else:
            self.programs[program['index']]=program
        self.lstPrograms.SetStringItem(idx,0,program['title'])
        self.lstPrograms.SetStringItem(idx,1,program['channel'])
        self.lstPrograms.SetStringItem(idx,2,time.strftime(self.display_dateformat,program['date']))
        self.lstPrograms.SetStringItem(idx,3,"%0.1f" % program['size'])
        self.lstPrograms.SetStringItem(idx,4,program['length'])
        self._Log('Updated episode info for %s.'%program['title'])
        for j in range(self.lstPrograms.GetColumnCount()):
            self.lstPrograms.SetColumnWidth(j, autosize)
            if not iswin:
                c=self.lstPrograms.GetColumnWidth(j)
                h=self.lstPrograms.HeaderWidths[j]
                if h>c:self.lstPrograms.SetColumnWidth(j,h)
        self.lstPrograms.resizeLastColumn(self.mincolwidth)

    def _UpdateProgress(self,progress,message):
        self.gaugeProgressBar.Show()
        self.lblProgressText.SetLabelText(message)
        self.gaugeProgressBar.SetRange(100)
        if progress:
            self.gaugeProgressBar.SetValue(progress['percent'])
            self.StatusBar.SetFields(['Speed %sMB/S'%progress['speed'],
                                      'Downloaded %sMB/%sMB (%s%%)'%(progress['downloaded'],progress['size'],progress['percent']),
                                      'Queued %sMB'%progress['total']
                                      ])
        else:
            self.gaugeProgressBar.SetValue(0)
            self.StatusBar.SetFields(['','',''])

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
        if not os.path.exists(os.path.dirname(self.userconfig)):
            os.mkdir(os.path.dirname(self.userconfig))
        self.config.write(open(self.userconfig,'w'))
        #device=self.config.get('Settings','device')

    def _sanitize(self,filename):
        chars=['\\','/',':','*','?','"','<','>','|','$']
        for char in chars:
            filename = filename.replace(char, '_')
        return filename
    #######################################################################
    #Event handlers
    #######################################################################
    def onCloseApp( self, event ):
        self._WriteConfig()
        try:del self.ThreadedConnector
        except:pass
        try:del self.ThreadedDownloader
        except:pass
        event.Skip()
        sys.exit(0)

    def btnConnect_OnClick( self, event ):
        self._Connect()

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
        self.btnStop.Enable( False )
        self.Play.clear()

    def btnStop_OnClick( self, event ):
        self.Stop.set()

    def cbxDevice_OnKillFocus( self, event ):
        self.config.set('Settings','device',self.cbxDevice.GetValue())

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
        event.Skip()

    def lstPrograms_OnDeselect( self, event ):
        event.Skip()

    def lstPrograms_OnDoubleClick( self, event ):
        self._Queue()
        event.Skip()

    def lstPrograms_OnRightClick( self, event ):
        self.lstPrograms.PopupMenu(self.mnuPrograms)
        event.Skip()

    def lstPrograms_OnSelect( self, event, showinfo=True ):
        if showinfo:self._ShowInfo()
        event.Skip()

    def lstQueueOnContextMenu( self, event ):
        self.mitRemove.Enable( False )
        self.lstQueue.PopupMenu(self.mnuQueue)
        event.Skip()

    def lstQueue_OnRightClick( self, event ):
        self.lstQueue.PopupMenu(self.mnuQueue)
        event.Skip()

    def lstQueue_OnMiddleClick( self, event ):
        self.mitRemove_OnSelect(event)

    def mitAbout_OnSelect( self, event ):
        dlg=AboutDialog(self)

    def mitClearQueue_OnSelect( self, event ):
        self._ClearQueue()

    def mitDelete_OnSelect( self, event ):
        self._DeleteFromWiz()

    def mitDownload_onSelect( self, event ):
        self._Queue(clear=True)
        self._DownloadQueue()
        event.Skip()

    def mitDownloadAll_OnSelect( self, event ):
        self._DownloadQueue()
        event.Skip()

    def mitPreferences_OnSelect( self, event ):
        self.cbxDevice_OnKillFocus(None)          #Clicking a menu item doesn't move focus off a control,
        settings=SettingsDialog(self,self.config,self.configspec) #so make sure the device name get's updated.
        if settings.saved:
            self.config=settings.config
            self._ApplyConfig()
            self._WriteConfig()

    def mitQueue_onSelect( self, event ):
        self._Queue()

    def mitRemove_OnSelect( self, event ):
        self._DeleteFromQueue()

    def mitHelp_OnSelect( self, event ):
        webbrowser.open_new_tab('http://code.google.com/p/yardwiz/wiki/Help')

    def onLog( self, event ):
        self._Log(event.message)
        event.Skip()

    def onUpdateProgress( self, event ):
        self._UpdateProgress(event.progress,event.message)
        event.Skip()

    def OnSize( self, event ):
        self._UpdateSize()
        event.Skip()

    def onActivate( self, event ):
        self._UpdateSize()
        event.Skip()

    def onDownloadComplete( self, event ):
        self._DownloadComplete(event.index,event.stopped)
        event.Skip()

class LicenseDialog( gui.LicenseDialog ):
    def __init__( self, parent ):
        gui.LicenseDialog.__init__(self,None)
        sxmin,symin=centrepos(self,parent)
        self.SetPosition((sxmin,symin))
        #self.Centre( wx.BOTH )

class AboutDialog( gui.AboutDialog ):
    def __init__( self, parent ):
        gui.AboutDialog.__init__( self, None )
        #Set the icons here as wxFormBuilder relative path is relative to the working dir, not the app dir
        path=data_path()
        icons=os.path.join(path,u'icons')
        ico=os.path.join(icons, u"icon.png")
        self.SetIcon( wx.Icon( ico, wx.BITMAP_TYPE_ANY ) )
        self.bmpIcon.SetBitmap( wx.Bitmap(ico , wx.BITMAP_TYPE_ANY ) )

        txtlicense=license()
        txtversion=version()[0]

        sxmin,symin=centrepos(self,parent)
        self.SetPosition((sxmin,symin))
        #self.Centre( wx.BOTH )

        self.LicenseDialog=LicenseDialog(self)
        self.LicenseDialog.txtLicense.SetValue(txtlicense)
        self.lblVersion.SetLabel('Version: '+txtversion)
        self.lblCopyright.SetLabel(txtlicense.split('\n')[0].strip())

        self.ShowModal()

    def btnLicense_OnClick( self, event ):
        self.LicenseDialog.ShowModal()

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

#######################################################################
#Workarounds for py2exe
#######################################################################
if iswin and frozen():
    sys.stderr = Stderr()
    del Stderr
