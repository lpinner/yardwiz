import os,sys,threading,thread,time,signal,ctypes,copy
import locale,subprocess,re
import wx
from ordereddict import OrderedDict as odict
from events import *

#Workarounds for crossplatform issues
iswin=sys.platform[0:3] == "win"
if iswin:
    wizexe='getWizPnP.exe'
    CTRL_C_EVENT = 0
    CREATE_NEW_PROCESS_GROUP=0x00000200 #getwizpnp kicks off child processes which the subprocess module doesn't kill unless a new process group is created.
    STARTF_USESHOWWINDOW=1 #subprocess.STARTF_USESHOWWINDOW raises
    creationflags=CREATE_NEW_PROCESS_GROUP
    startupinfo=subprocess.STARTUPINFO()#Windows starts up a console when a subprocess is run from a non-concole app like pythonw
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW #subprocess.STARTF_USESHOWWINDOW
    Popen_kwargs={'creationflags':creationflags,'startupinfo':startupinfo}
    autosize=wx.LIST_AUTOSIZE_USEHEADER #for ListCtrls

else:
    wizexe='getWizPnP.pl'
    Popen_kwargs={}
    autosize=wx.LIST_AUTOSIZE #for ListCtrls

#######################################################################
#Helper classes
#######################################################################
class ThreadedDeleter( threading.Thread ):
    def __init__( self, parent, device, ip, port, programs,indices):
        threading.Thread.__init__( self )
        self.parent=parent
        self.device=device
        self.ip=ip
        self.port=port
        self.programs=programs
        self.indices=indices
        self.start()
    def run(self):
        if self.device:
            cmd=[wizexe,'--device','--all','--BWName']
        else:
            cmd=[wizexe,'-H',self.ip,'-p',self.port,'--all','--BWName']

        self.parent.SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
        for idx,program in zip(self.indices,self.programs):
            cmddel=subprocess.list2cmdline(cmd+['--delete',program['index']])
            cmdchk=subprocess.list2cmdline(cmd+['--list',program['index']])
            try:
                self.proc=subprocess.Popen(cmddel, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
                exit_code=self.proc.wait()
                self.proc=subprocess.Popen(cmdchk, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
                exit_code=self.proc.wait()
                stdout,stderr=self.proc.communicate()
                if stdout.strip() or exit_code:raise Exception,'Unable to delete %s\n%s'%(program['title'],stderr.strip())
            except Exception,err:
                self._Log(err)
            else:
                self._Log('Deleted %s.'%program['title'])
                evt = DeleteProgram(wizEVT_DELETEPROGRAM, -1,program,idx)
                try:wx.PostEvent(self.parent, evt)
                except:pass

        self.parent.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def _Log(self,message):
        evt = Log(wizEVT_LOG, -1,message)
        try:wx.PostEvent(self.parent, evt)
        except:pass #we're probably exiting
        
class ThreadedConnector( threading.Thread ):
    def __init__( self, parent, device, ip, port, deleted=[], quick=False):
        threading.Thread.__init__( self )
        self.device=device
        self.ip=ip
        self.port=port
        self.parent=parent
        self.deleted=deleted
        self.quick=quick
        self.start()
    def run(self):
        if self.quick:
            exit_code,err=self._quicklistprograms()
        else:
            exit_code,err=self._listprograms()

        if exit_code > 0:
            evt = Connected(wizEVT_CONNECTED, -1,'Unable to list programs on the WizPnP server:\n%s'%err)
            try:wx.PostEvent(self.parent, evt)
            except:pass #we're probably exiting
        else:
            evt = Connected(wizEVT_CONNECTED, -1,'Finished listing programs on the WizPnP server')
            try:wx.PostEvent(self.parent, evt)
            except:pass

    def _quicklistprograms(self):
        if self.device:
            cmd=[wizexe,'--device',self.device]
        else:
            cmd=[wizexe,'-H',self.ip,'-p',self.port]
        cmd.extend(['--all','--sort=fatd'])
        self.proc=subprocess.Popen(cmd+['-q','--List'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)

        programs=[]
        for line in iter(self.proc.stdout.readline, ""):
            line=line.strip()
            program=self._quickparseprogram(line)
            programs.append(program['index'])
            evt = AddProgram(wizEVT_ADDPROGRAM, -1, program)
            try:wx.PostEvent(self.parent, evt)
            except:pass #we're probably exiting
        del self.proc

        cmd.extend(['-vv','--episode','--index'])
        self.proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
        proglines=[]
        exists=[]
        for line in iter(self.proc.stdout.readline, ""):
            line=line.strip()
            if line[0:13]!='Connecting to':
                if not line:#Start of next program in list
                    if proglines:
                        tmp=list(proglines)
                        proglines=[]
                        program=self._parseprogram(tmp)
                        program['info']='\n'.join(tmp)
                        if program['index'] not in self.deleted:
                            idx=programs.index(program['index'])
                            exists.append(program['index'])
                            evt = AddProgram(wizEVT_UPDATEPROGRAM, -1, program, idx)
                            try:wx.PostEvent(self.parent, evt)
                            except:pass #we're probably exiting
                else:
                    proglines.append(line)

        exit_code=self.proc.wait()
        for idx,pidx in enumerate(programs):
            if pidx not in exists: #It's been deleted from the wiz which hasn't been reindexed
                evt = DeleteProgram(wizEVT_DELETEPROGRAM, -1, programs,idx)
                try:wx.PostEvent(self.parent, evt)
                except:pass #we're probably exiting
        return exit_code,self.proc.stderr.read()

    def _listprograms(self):
        if self.device:
            cmd=[wizexe,'--device',self.device]
        else:
            cmd=[wizexe,'-H',self.ip,'-p',self.port]
        cmd.extend(['--all','-v','-l','--episode','--index','--sort=fatd'])
        self.proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)

        proglines=[]
        index=-1
        for line in iter(self.proc.stdout.readline, ""):
            line=line.strip()
            if line[0:13]!='Connecting to':
                if not line:#Start of next program in list
                    if proglines:
                        tmp=list(proglines)
                        proglines=[]
                        program=self._parseprogram(tmp)
                        if program['index'] not in self.deleted:
                            index+=1
                            evt = AddProgram(wizEVT_ADDPROGRAM, -1, program)
                            try:
                                wx.PostEvent(self.parent, evt)
                                if not 'info' in program:
                                    thread.start_new_thread(self._getinfo, (program,index))
                            except:pass #we're probably exiting
                else:
                    proglines.append(line)

        exit_code=self.proc.wait()
        return exit_code,self.proc.stderr.read()

    def _quickparseprogram(self,index):
        program=index.split()
        datetime=program[-1]
        title=' '.join(program[:-1]).replace('/_','/')
        title='/'.join(title.split('/')[1:])
        title=title.replace('_',':') #Strip off the root folder
        return {'index':index.strip(),'date':datetime.strip(),'title':title.strip()}

    def _parseprogram(self,proglines):
        flaglist=['*LOCKED','*RECORDING NOW']
        flags=[]
        prog=proglines[0].replace('*AC3','')
        for flag in flaglist:
            if flag in prog:
                flags.append(flag)
                prog=prog.replace(flag,'')
        flags=' '.join(flags)
        prog=prog.split(':')
        channel=prog[0].strip()
        info=':'.join(prog[1:]) #in case there are more ':''s in the program title
        info=info.split('/')
        title=' '.join([info[0].strip(),flags])

        program={'title':title.strip('*'),'channel':channel}
        if len(info) > 0:
            info=('/').join(info[1:]).strip()
            if info and len(info)<50:
                program['title']='%s - %s'%(title.strip(),info.strip())
                info=None
        else:
            info=None

        for line in proglines[1:]:
            if 'Index name' in line:
                program['index']=line.split(':')[1].strip()
                dirs=program['index'].split('/')
                if len(dirs)>2:
                    program['title']='%s/%s'%('/'.join(dirs[1:-1]),program['title'])
                datetime=program['index'].split()
                program['date']=datetime[-1]

            elif 'playtime' in line:
                playtime=line
                line=line.split()
                program['length']=line[1]
                program['size']=float(line[4])
            elif 'autoDelete' in line:
                pass
            else:
                datetime=line.split('-')[0].strip()
        if info:
            program['info'] = '%s: %s \n%s\n%s\n%s'%(channel,title,info,datetime,playtime)
        return program

    def _getinfo(self,program,idx):
        pidx=program['index']
        if self.device:
            cmd=[wizexe,'--device',self.device]
        else:
            cmd=[wizexe,'-H',self.ip,'-p',self.port]
        cmd.extend(['-vv','--all','-l','--BWName',pidx])
        cmd=subprocess.list2cmdline(cmd)
        #This fails for some reason (on Win32) if a wx.FileDialog is open (i.e.) a download is started.
        #Workaround is to set shell=True
        #self.proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
        proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
        stdout,stderr=proc.communicate()
        exit_code=proc.wait()

        #print '\n'.join((pidx,stdout,stderr))
        if exit_code==0:
            info=[]
            for line in stdout.split('\n'):
                line=line.strip()
                if not 'Connecting to' in line:
                    info.append(line)
            program['info']='\n'.join(info)
            evt = UpdateProgram(wizEVT_UPDATEPROGRAM, -1, program, idx)
            try:wx.PostEvent(self.parent, evt)
            except:pass #we're probably exiting

    def __del__(self):
        try:
            self.proc.kill()
            del self.proc
        except:pass

class ThreadedDownloader( threading.Thread ):
    def __init__(self, parent, device, ip, port, programs, evtPlay, evtStop):
        threading.Thread.__init__( self )

        self.parent=parent
        self.device=device
        self.ip=ip
        self.port=port
        self.programs=programs
        self.Play=evtPlay
        self.Stop=evtStop
        self.Play.set()
        self.Stop.clear()
        self.proc=None

        self.total=0
        for program in self.programs:
            self.total+=program['size']

        self.start()

    def run(self):
        for program in self.programs:
            self._updateprogress([],'Downloading %s...'%program['title'])
            self.Play.set()
            self.Stop.clear()
            self._download(program)
            self.total-=program['size']
            if self.Stop.isSet():break

    def _download(self,program):
        self._log('Downloading %s...'%program['title'])
        d=os.path.dirname(program['filename'])
        f=os.path.splitext(os.path.basename(program['filename']))[0]
        if self.device:
            cmd=[wizexe,'--device',self.device]
        else:
            cmd=[wizexe,'-H',self.ip,'-p',self.port]
        cmd.extend(['--all','-q','-t','-R','--BWName','-O',d,'-T',f,program['index']])
        try:
            self.proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
        except Exception,err:
            self._log('Error, unable to download %s.'%program['filename'])
            self._log(str(err))

        f=program['filename']
        MB=1024.0**2
        MiB=1000.0**2
        s=program['size']*MiB
        start=time.time()
        if os.path.exists(f):prevsize=os.stat(f).st_size
        else:prevsize=0.0
        while self.proc.poll() is None:
            if self.Stop.isSet(): #Stop button pressed
                self.Play.clear()
                self._downloadcomplete(index=program['index'],stopped=True)
                try:
                    self._stopdownload()
                    os.unlink(program['filename'])
                except Exception,err:
                    self._log('Unable to stop download or delete %s.'%program['filename'])
                    self._log(str(err))
                else:
                    self._log('Download cancelled.')
                return

            elif not self.Play.isSet():#We're paused
                try:
                    self._stopdownload()
                except:
                    self._log('Unable to pause download.')
                    raise
                self._log('Download paused.')
                self.Play.wait() #block until Play is set
                self._download(program)
                return
            else: #We're still downloading, update the progress
                time.sleep(1)
                if os.path.exists(f):#getwizpnp might not be going yet...
                    size=os.stat(f).st_size
                    now=time.time()
                    speed="%0.2f" % ((size-prevsize)/(now-start)/MB)
                    progress={'percent':int(size/s*100),
                              'downloaded':round(size/MB, 1),
                              'size':round(program['size'], 1),
                              'total':round(self.total, 1),
                              'speed':speed}
                    self._updateprogress(progress,'Downloading %s...'%program['title'])
                    start=time.time()
                    prevsize=size

        exit_code=self.proc.poll()
        stdout,stderr=self.proc.communicate()
        if exit_code or not os.path.exists(f):
            self._log('Error, unable to download %s.'%program['filename'])
            self._log(stderr)
            self._downloadcomplete(index=program['index'])
        else:
            #Should check filesize v. getwizpnp reported size...
            progress={'percent':100,
                      'downloaded':round(program['size']/MB*MiB, 1),
                      'size':round(program['size']/MB*MiB, 1),
                      'total':self.total,
                      'speed':speed}
            self._updateprogress(progress)
            self._log('Download of %s complete.'%program['filename'])
            self._downloadcomplete(index=program['index'])

    def _log(self,msg):
        evt = Log(wizEVT_LOG, -1, msg)
        try:wx.PostEvent(self.parent, evt)
        except:pass #we're probably exiting

    def _updateprogress(self,progress=[], message=''):
        evt = UpdateProgress(wizEVT_UPDATEPROGRESS, -1, progress,message)
        try:wx.PostEvent(self.parent, evt)
        except:pass #we're probably exiting

    def _downloadcomplete(self,index=-1,stopped=False):
        evt = DownloadComplete(wizEVT_DOWNLOADCOMPLETE, -1,index, stopped)
        try:wx.PostEvent(self.parent, evt)
        except:pass #we're probably exiting

    def _stopdownload(self):
        if iswin:
            #killing using self.proc.kill() doesn't seem to work on getwizpnp.exe
            CTRL_C_EVENT = 0
            ctypes.windll.kernel32.GenerateConsoleCtrlEvent(CTRL_C_EVENT, self.proc.pid)
            if self.proc.poll() is None: #Nup, get nastier...
                #There doesn't seem to be any way to kill getwizpnp from within python
                #when it is kicked off by pythonw.exe (even tried ctypes.windll.kernel32.TerminateProcess)
                #other than taskkill/pskill (or manually with task manager -> kill process tree)
                #Killing with sigint works fine when process is started by python.exe... I'm stumped!
                #
                #NOTE: taskkill.exe is NOT available in WinNT, Win2K or WinXP Home Edition.
                #      It is available on WinXP Pro, Win 7 Pro , no idea about Vista or Win 7 starter/basic/home
                try:
                    cmd = ['pskill','/accepteula', '-t',str(self.proc.pid)]
                    proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
                    exit_code=proc.wait()
                except WindowsError,err:
                    try:
                        cmd = ['taskkill','/F','/t','/PID',str(self.proc.pid)]
                        proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**Popen_kwargs)
                        exit_code=proc.wait()
                    except WindowsError,err:
                        if err.winerror==2:
                            msg= '%s\nYour version of Windows does not include the "taskkill" command, '
                            msg+='you will need to end all GetWizPnP.exe processess manually using '
                            msg+='the Windows Task Manager (Ctrl-Alt-Delete).\n\n'
                            msg+='If you wish to make use of the stop and pause functionality, download '
                            msg+='PsTools.zip from http://technet.microsoft.com/en-us/sysinternals/bb896683 '
                            msg+='and copy PsKill.exe to the %s directory\n%s'
                            self._log(msg%('#'*10,APPNAME,'#'*10))
                        else:
                            self._log(str(err))

        else:
            self.proc.send_signal(signal.SIGINT)
        time.sleep(1)

    def __del__(self):
        try:
            self.proc.kill()
            del self.proc
        except:pass

class Stderr(object):
    #This is modified from py2exe class Stderr
    ##Copyright (c) 2000-2008 Thomas Heller, Mark Hammond, Jimmy Retzlaff
    ##
    ##Permission is hereby granted, free of charge, to any person obtaining
    ##a copy of this software and associated documentation files (the
    ##"Software"), to deal in the Software without restriction, including
    ##without limitation the rights to use, copy, modify, merge, publish,
    ##distribute, sublicense, and/or sell copies of the Software, and to
    ##permit persons to whom the Software is furnished to do so, subject to
    ##the following conditions:
    ##
    ##The above copyright notice and this permission notice shall be
    ##included in all copies or substantial portions of the Software.
    ##
    ##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    ##EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    ##MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    ##NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    ##LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    ##OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    ##WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    softspace = 0
    _file = None
    _error = None
    tmp=os.environ.get('TEMP',os.environ.get('TMP','.'))
    fname=os.path.join(tmp, 'yardwiz.log')
    def errordialog(self,message, caption):
        import wx
        wxapp = wx.PySimpleApp(0)
        dlg = wx.MessageDialog(None,message, caption, wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def write(self, text,*args,**kwargs):
        if self._file is None and self._error is None:
            try:
                self._file = open(self.fname, 'a')
            except Exception, details:
                self._error = details
                import atexit
                atexit.register(self.errordialog,
                                "The logfile '%s' could not be opened:\n %s" % \
                                (self.fname, details),
                                "Errors occurred")
            else:
                import atexit
                atexit.register(self.errordialog,
                                "See the logfile '%s' for details" % self.fname,
                                "Errors occurred")
        if self._file is not None:
            self._file.write(text)
            self._file.flush()
    def flush(self):
        if self._file is not None:
            self._file.flush()

#######################################################################
#Utility helper functions
#######################################################################
def which(name, returnfirst=True, flags=os.F_OK | os.X_OK, path=None):
    # This function is from the MetaGETA utilities module:
    # http://code.google.com/p/metageta/source/browse/trunk/lib/utilities.py
    #
    # Copyright (c) 2011 Australian Government, Department of Sustainability, Environment, Water, Population and Communities
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.
    ''' Search PATH for executable files with the given name.

        On newer versions of MS-Windows, the PATHEXT environment variable will be
        set to the list of file extensions for files considered executable. This
        will normally include things like ".EXE". This fuction will also find files
        with the given name ending with any of these extensions.

        On MS-Windows the only flag that has any meaning is os.F_OK. Any other
        flags will be ignored.

        Derived mostly from U{http://code.google.com/p/waf/issues/detail?id=531} with
        additions from Brian Curtins patch - U{http://bugs.python.org/issue444582}

        @type name: C{str}
        @param name: The name for which to search.
        @type returnfirst: C{boolean}
        @param returnfirst: Return the first executable found.
        @type flags: C{int}
        @param flags: Arguments to U{os.access<http://docs.python.org/library/os.html#os.access>}.

        @rtype: C{str}/C{list}
        @return: Full path to the first matching file found or a list of the full paths to all files found,
                 in the order in which they were found.
    '''
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    if not path:
        path = os.environ.get("PATH", os.defpath)
    if not path[0]=='.':path='.'+os.pathsep+path
    for p in path.split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            if returnfirst:return p
            else:result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                if returnfirst:return pext
                else:result.append(pext)
    return result

def errordialog(message, caption):
    dlg = wx.MessageDialog(None,message, caption, wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()
def frozen():
    return hasattr(sys, "frozen")

def version():
    try:
        import __version__
        version=__version__.version
        display_version=__version__.display_version
    except ImportError:
        version=ConfigParser.ConfigParser()
        version.read(os.path.join(os.path.dirname(sys.argv[0]),'VERSION'))
        display_version= version.get('Version','DISPLAY_VERSION')
        version = version.get('Version','VERSION')
    return version,display_version

def license():
    try:
        import __license__
        license=__license__.license
    except ImportError:
        license=open(os.path.join(os.path.dirname(sys.argv[0]),'LICENSE')).read().strip()
    return license

def data_path():
    if frozen():return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def centrepos(self,parent):
    pxsize,pysize=parent.GetSizeTuple()
    pxmin,pymin=parent.GetPositionTuple()
    sxsize,sysize=self.GetSizeTuple()
    pxcen=pxmin+pxsize/2.0
    pycen=pymin+pysize/2.0
    sxmin=pxcen-sxsize/2.0
    symin=pycen-sysize/2.0
    return sxmin,symin

