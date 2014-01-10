import os,sys,time,signal,ctypes,copy,logging,logging.handlers,traceback
import subprocess,re,ConfigParser,socket,struct,glob,tempfile,shutil
import wx
from ordereddict import OrderedDict as odict
from collections import deque
from Queue import Queue
from threading import Thread,Event,Timer
from datetime import datetime, timedelta

from events import *

APPNAME='YARDWiz'

MB=1024.0**2
MiB=1000.0**2

#######################################################################
#Helper classes
#######################################################################
class ThreadedUtility( Thread ):

    def __init__( self, parent):

        Thread.__init__( self )
        self.parent=parent

        self.run_old = self.run
        self.run = self.run_with_except_hook

    def run_with_except_hook(self, *args, **kw):
        #Global exception handler with workaround for Threads
        #http://bugs.python.org/issue1230540#msg91244
        try:
            self.run_old(*args, **kw)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.excepthook(*sys.exc_info())

    def excepthook(self, type, value, tb):
        msg=''.join(traceback.format_exception(type, value, tb))
        if logger.getEffectiveLevel()==logging.DEBUG:
            self.Log(msg, logging.ERROR)
        else:
            self.Log("Errors occurred, see the logfile '%s' for details" % logfile, logging.ERROR)
        logger.error(msg)

    def Log(self,msg,*args,**kwargs):
        evt = Log(wizEVT_LOG, -1, msg,*args,**kwargs)
        self.PostEvent(evt)

    def PostEvent(self,evt):
        try:wx.PostEvent(self.parent,evt)
        except Exception as err:
            logger.error(str(err))
            pass #We're probably exiting

    def isonline(self, device):
        if device.ip:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.settimeout(10.0)
                s.connect((device.ip, int(device.port)))
                s.shutdown(2)
                self.Log('The WizPnP server is online.')
                return True
            except Exception as err:
                self.Log('Unable to contact the WizPnP server.\n'+str(err),logging.ERROR)
                return False
        else: return True

class ThreadedChecker( ThreadedUtility ):
    def __init__( self, parent, evtStop, device):
        ThreadedUtility.__init__( self, parent )
        self.parent=parent
        self.Stop=evtStop
        self.device=device
        self.start()
    def run(self):
        cmd=[wizexe,'--all','--check','--verbose']+self.device.args
        if not self.isonline(self.device):
            evt = CheckComplete(wizEVT_CHECKCOMPLETE, -1,False,None)
            self.PostEvent(evt)
            return
        try:
            self.proc=subproc(cmd,env=wizenv)
            while self.proc.poll() is None:
                time.sleep(0.1)
                if self.Stop.isSet():
                    kill(self.proc)
                    return
            exit_code=self.proc.poll()
            stdout,stderr=self.proc.communicate()
            stderr=stderr.replace('\r','').strip()

            #for line in stderr:
            #    logger.info('stderr:'+stderr)
            if exit_code:
                msg='Unable to check recordings'
                if stderr:msg=msg+': '+stderr
                raise Exception,msg
        except Exception,err:
            checked=False
            msg=str(err)
        else:
            checked=True
            msg='Finished checking recordings. '
            errors=self._parseerrors(stderr)
            if errors:msg+='\n'.join(['The following errors were found:',errors])
            else:msg+='No errors found.'
        evt = CheckComplete(wizEVT_CHECKCOMPLETE, -1,checked,msg)
        self.PostEvent(evt)

    def _parseerrors(self,stderr):
        lines=stderr.split('\n')
        errors=[]
        while True:
            try:line=lines.pop(0)
            except:break
            if line.strip()[-1]==':':
                program=line[:-1]
                while True:
                    try:line=lines.pop(0)
                    except:break
                    error=[]
                    if line.strip()[-1]==':':
                        lines.insert(0,line)
                        break
                    else:
                        error.append(line)
            if error:errors.extend([program]+error)
        return '\n'.join(errors)

class ThreadedConnector( ThreadedUtility ):
    def __init__( self, parent, evtStop, device, quick=False,wizargs=[]):
        ThreadedUtility.__init__( self, parent )
        self.device=device
        self.parent=parent
        self.quick=quick
        self.wizargs=wizargs
        self.thread=None
        self._stop = evtStop
        self._stop.clear()
        self.start()

    def run(self):

        if not self.isonline(self.device):
            evt = Connected(wizEVT_CONNECTED, -1,False)
            self.PostEvent(evt)
            return

        if self.quick:
            exit_code,err=self._quicklistprograms()
        else:
            exit_code,err=self._listprograms()
        if exit_code > 0:
            evt = Connected(wizEVT_CONNECTED, -1,False)
            self.PostEvent(evt)
            self.Log('Unable to list programs on the WizPnP server:\n%s'%err, logging.ERROR)
        else:
            evt = Connected(wizEVT_CONNECTED, -1,True)
            self.PostEvent(evt)
            self.Log('Finished listing programs on the WizPnP server')

    def _quicklistprograms(self):
        cmd=[wizexe,'--all','--sort=fatd']+self.device.args+self.wizargs
        self.proc=subproc(cmd+['-q','--List'],env=wizenv)

        programs=[]
        import time
        index=-1
        for line in iter(self.proc.stdout.readline, ""):
            if self._stop.isSet():
                logger.debug('_stop.isSet')
                try:kill(self.proc)
                finally:return (0,'')
            line=line.strip()
            logger.debug('%s,%s'%(index+1,line))
            program=self._quickparseprogram(line)
            if not program['index'] in programs:
                index+=1
                programs.append(program['index'])
                evt = AddProgram(wizEVT_ADDPROGRAM,-1,program,index)
                self.PostEvent(evt)
            else:
                self.Log('There are multiple recordings with the index "%s" on the Beyonwiz. Only the first one can be displayed. Rename one on the PVR to allow YARDWiz to show them both.'%program['index'])

        exit_code=1
        try:
            exit_code=self.proc.wait()
            err=self.proc.stderr.read()
            if exit_code > 0:
                raise Exception,err
        except Exception,err:
            return exit_code,str(err)#We're probably exiting

        del self.proc

        cmd.extend(['-vv','--episode','--index'])
        self.proc=subproc(cmd,env=wizenv)
        proglines=[]
        exists=[]
        updated=[]
        for line in iter(self.proc.stdout.readline, ""):
            if self._stop.isSet():
                try:kill(self.proc)
                finally:return (0,'')
            line=line.strip()
            logger.debug(line)
            if line[0:13]!='Connecting to':
                if not line:#Start of next program in list
                    if proglines:
                        tmp=list(proglines)
                        proglines=[]
                        program=self._parseprogram(tmp)
                        if not program['index'] in updated:
                            updated.append(program['index'])
                            program['info']='\n'.join(tmp)
                            idx=programs.index(program['index'])
                            exists.append(program['index'])
                            evt = UpdateProgram(wizEVT_UPDATEPROGRAM, -1, program, idx)
                            self.PostEvent(evt)
                else:
                    proglines.append(line)

        exit_code=1
        try:
            exit_code=self.proc.wait()
            err=self.proc.stderr.read()
            if exit_code > 0:
                logger.debug('%s,%s'%(exit_code,err))
                raise Exception,err
        except Exception,err:
            return exit_code,str(err)#We're probably exiting

        for idx,pidx in enumerate(programs):
            if pidx not in exists: #It's been deleted from the wiz which hasn't been reindexed
                evt = DeleteProgram(wizEVT_DELETEPROGRAM, -1, programs,idx)
                self.PostEvent(evt)

        return exit_code,''

    def _listprograms(self):
        self.thread=None
        cmd=[wizexe,'--all','-v','-l','--episode','--index','--sort=fatd']+self.device.args+self.wizargs
        self.proc=subproc(cmd,env=wizenv)
        proglines=[]
        index=-1
        programs=[]
        for line in iter(self.proc.stdout.readline, ""):
            if self._stop.isSet():
                logger.debug('_stop.isSet')
                try:kill(self.proc)
                finally:return (0,'')
            line=line.strip()
            logger.debug(line)
            if line[0:13]=='Connecting to':
                self.thread=Thread(target=self._getinfo)
                self.thread.start()
            else:
                if not line:#Start of next program in list
                    if proglines:
                        tmp=list(proglines)
                        proglines=[]
                        program=self._parseprogram(tmp)
                        if not program['index'] in programs:
                            index+=1
                            programs.append(program['index'])
                            evt = AddProgram(wizEVT_ADDPROGRAM, -1, program, index)
                            self.PostEvent(evt)
                        else:
                            self.Log('There are multiple recordings with the index "%s" on the Beyonwiz. Only the first one can be displayed. Rename one on the PVR to allow YARDWiz to show them both.'%program['index'])
                else:
                    proglines.append(line)
        exit_code=1
        try:
            exit_code=self.proc.wait()
            err=self.proc.stderr.read()
            if self.thread:
                self.thread.join()
            if exit_code > 0:
                raise Exception,err
        except Exception,err:
            return exit_code,str(err)#We're probably exiting

        return exit_code,''

    def _quickparseprogram(self,index):
        program=index.split()
        datetime=program[-1].split('-')[0] #Handle multiple instant recording bug - http://www.beyonwiz.com.au/phpbb2/viewtopic.php?p=95311#95311
                                           #Index can be recordings/<NAME>_<DATETIME>-<N> so strip off the "<-N>"
                                           #E.g. recordings/_Sunrise _live_ Feb.14.2012_6.14-1
        title=' '.join(program[:-1]).replace('/_','/')
        title='/'.join(title.split('/')[1:])
        title=title.replace('_',':') #Strip off the root folder
        return {'index':index.strip(),'date':datetime,'title':title.strip()}

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

        program={'title':title.strip('*').strip(),'channel':channel}
        if len(info) > 0:
            info=('/').join(info[1:]).strip()
            if info and len(info)<50:
                program['title']='%s - %s'%(title.strip(),info.strip())
                info=''
        else:
            info=''

        otherlines=[]
        for line in proglines[1:]:
            if 'Index name' in line:
                program['index']=line.split(':')[1].strip()
                dirs=program['index'].split('/')
                if len(dirs)>2:
                    program['title']='%s/%s'%('/'.join(dirs[1:-1]),program['title'])
                datetime=program['index'].split()
                program['date']=datetime[-1].split('-')[0]#Handle multiple instant recording bug - http://www.beyonwiz.com.au/phpbb2/viewtopic.php?p=95311#95311
                                                          #Index can be recordings/<NAME>_<DATETIME>-<N> so strip off the "<-N>"
                                                          #E.g. recordings/_Sunrise _live_ Feb.14.2012_6.14-1

            elif 'playtime' in line:
                playtime=line
                line=line.split()
                program['length']=line[1]
                program['size']=(float(line[4])*MiB)/MB #Convert megabytes to mebibytes
            elif 'autoDelete' in line:
                pass
            else:
                otherlines.append(line.strip())
                
        info='\n'.join([info]+otherlines).strip()
        if info:
            program['info'] = '%s: %s \n%s\n%s'%(channel,title,info,playtime)
        else:
            program['info'] = '%s: %s \n%s'%(channel,title,playtime)

        return program

    def _getinfo(self):
        time.sleep(0.5)
        cmd=[wizexe,'-vv','--all','-l','--episode','--index','--sort=fatd']+self.device.args
        proc=subproc(cmd,env=wizenv)
        proglines=[]
        index=-1
        programs=[]
        for line in iter(proc.stdout.readline, ""):
            if self._stop.isSet():
                logger.debug('_stop.isSet')
                try:
                    kill(proc)
                    del proc
                finally:return
            line=line.strip()
            logger.debug(line)
            if line[0:13]!='Connecting to':
                if not line:#Start of next program in list
                    if proglines:
                        tmp=list(proglines)
                        proglines=[]
                        program=self._parseprogram(tmp)
                        if not program['index'] in programs:
                            programs.append(program['index'])
                            index+=1
                            evt = UpdateProgram(wizEVT_UPDATEPROGRAM, -1, program, index)
                            self.PostEvent(evt)
                else:
                    proglines.append(line)

        try:
            exit_code=proc.wait()
            err=self.proc.stderr.read()
            logger.debug('%s,%s'%(exit_code,stderr))
            return exit_code,err
        except Exception,err:
            return 1,str(err)

    def __del__(self):
        try:
            kill(self.proc)
            del self.proc
        except:pass

class ThreadedConverter( ThreadedUtility ):
    def __init__( self, parent, evtStop, folders):
        ThreadedUtility.__init__( self, parent )
        self.folders=folders
        self.parent=parent
        self.stop = evtStop
        self.stop.clear()
        self.start()

    def run(self):

        for d in self.folders:
            if wx.Platform == '__WXGTK__':
                p=d.split(os.sep)
                if p[0]=='Home directory':
                    p[0] = wx.GetHomeDir()
                    d=os.sep.join(p)
                elif p[0] == 'Desktop':
                    p.insert(0, wx.GetHomeDir())
                    d=os.sep.join(p)

            elif wx.Platform == '__WXMAC__':
                p=d.split(os.sep)
                if p[0] != os.sep:
                    d=os.path.join(os.sep,'Volumes',d)

            ts=os.path.splitext(d)[0]+'.ts'
            try:
                self.Log('Converting %s to TS format...'%d)
                o=open(ts,'wb')
                TVWiz(d,self.stop).copyto(o)
                if self.stop.isSet():
                    self.Log('Cancelled conversion of %s.'%d)
                    os.unlink(ts)
                    break
                else:
                    self.Log('Created %s.'%ts)
            except Exception,err:
                self.Log(str(err),logging.ERROR)
            finally:
                try:o.close()
                except:pass

        evt = ConvertComplete(wizEVT_CONVERTCOMPLETE, -1)
        self.PostEvent(evt)

class ThreadedDeleter( ThreadedUtility ):
    def __init__( self, parent, evtStop, device, programs,indices,wizargs=[]):
        ThreadedUtility.__init__( self, parent )
        self.parent=parent
        self.Stop=evtStop
        self.device=device
        self.programs=programs
        self.indices=indices
        self.wizargs=wizargs
        self.start()

    def run(self):
        if not self.isonline(self.device):
            evt = DeleteProgram(wizEVT_DELETEPROGRAM, -1)
            self.PostEvent(evt)
            return

        cmd=[wizexe,'--all','--BWName']+self.device.args+self.wizargs

        for idx,program in zip(self.indices,self.programs):
            cmddel=cmd+['--delete',program['index']]
            cmdchk=cmd+['--list',program['index']]
            try:
                self.proc=subproc(cmddel,env=wizenv)
                while self.proc.poll() is None:
                    time.sleep(0.1)
                    if self.Stop.isSet():return
                exit_code=self.proc.poll()
                stdout,stderr=self.proc.communicate()
                if stderr.strip() or exit_code:raise Exception,'Unable to delete %s\n%s'%(program['title'],stderr.strip())
                self.proc=subproc(cmdchk,env=wizenv)
                exit_code=self.proc.wait()
                stdout,stderr=self.proc.communicate()
                if stdout.strip():raise Exception,'Unable to delete %s'%(program['title'])
            except Exception,err:
                self.Log(str(err),logging.ERROR)
                evt = DeleteProgram(wizEVT_DELETEPROGRAM, -1)
                self.PostEvent(evt)
            else:
                self.Log('Deleted %s.'%program['title'])
                evt = DeleteProgram(wizEVT_DELETEPROGRAM, -1,program,idx)
                self.PostEvent(evt)

        evt = DeleteComplete(wizEVT_DELETECOMPLETE, -1)
        self.PostEvent(evt)

class ThreadedDownloader( ThreadedUtility ):
    def __init__(self, parent, device, programs, evtPlay, evtStop,retries=1,deletefail=1,wizargs=[]):
        ThreadedUtility.__init__( self, parent )

        self.parent=parent
        self.device=device
        self.programs=programs
        self.Play=evtPlay
        self.Stop=evtStop
        self.Play.set()
        self.Stop.clear()
        self.proc=None
        self.retries=retries
        self.deletefail=deletefail
        self.wizargs=wizargs

        v=getwizpnpversion()

        if v>=[0,5,4]:
            self.wizargs+=['--retry=30']

        self.total=0
        for program in self.programs:
            self.total+=program['size']

        self.start()

    def run(self):

        if not self.isonline(self.device):
            self._downloadcomplete(stopped=True)
            return

        for program in self.programs:
            self._updateprogress({},'Downloading %s...'%program['title'])
            self.Play.set()
            self.Stop.clear()
            self.attempts=0
            self._download(program)
            self.total-=program['size']
            if self.Stop.isSet():break

    def _delete(self, f,n=5):
        if os.path.exists(f):
            for i in range(n):#Try to delete the file n times
                try:
                    time.sleep(1)
                    os.unlink(f)
                except:
                    if i==n-1:raise
                    else:continue
                else:return
        else:return

    def _download(self,program):
        self.attempts+=1

        self.Log('Downloading %s...'%program['title'])

        fd=program['filename'].encode(filesysenc)
        d=os.path.dirname(fd)
        f,e=os.path.splitext(os.path.basename(fd))

        cmd=[wizexe,'--all','-q','-R','--BWName','-O',d,'-T',f,program['index']]+self.device.args+self.wizargs
        if 'ts' in e.lower():cmd+=['-t']

        try:
            self.proc=subproc(cmd,env=wizenv)
        except Exception,err:
            self.Log('Error, unable to download %s.'%program['filename'],logging.ERROR)
            self.Log(str(err),logging.ERROR)

        f=program['filename']
        s=program['size']*MB
        total=self.total*MB
        start=time.time()
        if os.path.exists(f):prevsize=filesize(f)
        else:prevsize=0.0
        speeds=deque([],maxlen=120)
        percent=0
        while self.proc.poll() is None:
            if self.Stop.isSet(): #Stop button pressed
                self.Play.clear()
                self._downloadcomplete(index=program['index'],stopped=True)
                try:
                    self._stopdownload()
                    for i in range(3):#Try to delete the file 3 times
                        try:
                            time.sleep(1)
                            delete(program['filename'])
                        except:
                            if i==2:raise
                            else:continue
                        else:break

                except Exception,err:
                    msg='Unable to stop download or delete %s\n%s.'%(program['filename'],str(err))
                    self.Log(msg,logging.ERROR)
                else:
                    self.Log('Download cancelled.')
                return

            elif not self.Play.isSet():#We're paused
                try:
                    self._stopdownload()
                except:
                    self.Log('Unable to pause download.',logging.ERROR)
                    raise
                #if '.tvwiz' in f:delete(sorted(glob.glob(os.path.join(f,'[0-9][0-9][0-9][0-9]')))[-1])
                self.Log('Download paused.')
                while True:
                    self.Play.wait(0.5) #block until Play is set
                    if self.Stop.isSet():
                        self._downloadcomplete(index=program['index'],stopped=True)
                        try:
                            delete(program['filename'])
                        except Exception,err:
                            msg='Unable to delete %s.\n%s'%(program['filename'],str(err))
                            self.Log(msg,logging.ERROR)
                        else:
                            self.Log('Download cancelled.')
                        return
                    elif self.Play.isSet():
                        break
                self.attempts=0
                self._download(program)
                return
            else: #We're still downloading, update the progress
                time.sleep(1)
                if os.path.exists(f):#getwizpnp might not be going yet...
                    size=filesize(f)
                    try:percent=int(size/s*100+0.5)
                    except ZeroDivisionError:percent=0

                    now=time.time()
                    speed=((size-prevsize)/(now-start))
                    if speed>0.0001:speeds.append(speed)
                    else:speed=0.0
                    n=float(len(speeds))
                    esttime=''
                    totaltime=''
                    if n<10:
                        esttime='calculating...'
                        totaltime='calculating...'
                    else:
                        try:
                            #avspeed=sorted(speeds)[int(n/2+0.5)] ##Pseudo median
                            avspeed=sum(speeds)/n                 ##Mean
                            esttime=timefromsecs((s-size)/avspeed)
                            if total>s:totaltime=timefromsecs((total-size)/avspeed)
                        except ZeroDivisionError:
                            esttime='unknown'
                            totaltime='unknown'

                    progress={'filename':f,
                              'percent':percent,
                              'downloaded':round(size/MB, 1),
                              'size':round(program['size'], 1),
                              'total':round(self.total, 1),
                              'time':esttime,
                              'totaltime':totaltime,
                              'speed':"%0.2f" % (speed/MB)}
                    self._updateprogress(progress,'Downloading %s...'%program['title'])
                    start=time.time()
                    prevsize=size
                elif time.time()-start>10: #No file after 10 seconds
                    try:
                        self._stopdownload()
                    except:
                        self.Log('Unable to download.',logging.ERROR)
                        raise

        try:exit_code=self.proc.poll()
        except:return#We're probably exiting
        stdout,stderr=self.proc.communicate()
        if exit_code or not os.path.exists(f) or percent < 100:
            msg='Error, unable to download %s.\n'%program['filename']
            msg+='getWizPnP STDOUT:%s'%stdout
            msg+='getWizPnP STDERR:%s'%stderr
            self.Log(msg,logging.ERROR)
            if self.attempts<self.retries:
                self.Log('Retrying (attempt %s).'%(self.attempts+1))
                #if '.tvwiz' in f:delete(sorted(glob.glob(os.path.join(f,'[0-9][0-9][0-9][0-9]')))[-1])
                return self._download(program)
            if not 'Copy failed: Forbidden' in stderr and self.deletefail:
                try:delete(program['filename'])
                except:self.Log('Error: Unable to delete %s'%program['filename'],logging.ERROR)
            self._downloadcomplete(index=program['index'],stopped=True)
        else:
            progress={'filename':'',
                      'percent':100,
                      'downloaded':(program['size'], 1),
                      'size':round(program['size'], 1),
                      'total':self.total,
                      'time':'0',
                      'totaltime':'',
                      'speed':speed}
            self._updateprogress(progress)
            self.Log('Download of %s complete.'%program['filename'])
            self._downloadcomplete(index=program['index'])

    def _updateprogress(self,progress=[], message=''):
        evt = UpdateProgress(wizEVT_UPDATEPROGRESS, -1, progress,message)
        self.PostEvent(evt)

    def _downloadcomplete(self,index=-1,stopped=False):
        evt = DownloadComplete(wizEVT_DOWNLOADCOMPLETE, -1,index, stopped)
        self.PostEvent(evt)

    def _stopdownload(self):
        try:
            kill(self.proc)
        except Exception,err:self.Log(str(err),logging.ERROR)
    def __del__(self):
        try:
            kill(self.proc)
            del self.proc
        except:pass

class ThreadedPlayer( ThreadedUtility ):
    def __init__( self, parent, evtStop, evtPlay,filename,vlcargs=[]):
        ThreadedUtility.__init__( self, parent )
        self.parent=parent
        self.Stop=evtStop
        self.Play=evtPlay
        self.filename=filename
        self.vlcargs=vlcargs

        self.start()

    def run(self):

        self.port=self.getfreeport()
        cmd=[vlcexe,'--extraintf=rc','--rc-host=localhost:%s'%self.port,'--quiet','--verbose=0']
        if not iswin:cmd+=['--rc-fake-tty']
        cmd+=self.vlcargs
        cmd+=[self.filename.encode(filesysenc)]

        try:
            self.proc=subproc(cmd)
            try:
                self.socket=self.getsocket(self.port)
                data=self.getdata()
            except Exception as err:
                self.proc.kill()
                #self.Log(str(err),logging.ERROR)
            while self.proc.poll() is None:
                time.sleep(0.1)
                if self.Stop.isSet():
                    self.quit()
                    return
                elif not self.Play.isSet():#We're paused
                    self.cmd('pause')
                    while self.proc.poll() is None:
                        self.Play.wait(0.1) #wait until Play is set
                        if self.Stop.isSet():
                            self.quit()
                            return
                        elif self.Play.isSet():
                            self.cmd('pause')
                            break

            exit_code=self.proc.poll()
            stdout,stderr=self.proc.communicate()
            stderr=stderr.strip()
            stdout=stdout.strip()
            if exit_code:
                msg='Unable to play recording'
                if stderr:msg=msg+': '+stderr
                raise Exception,msg
        except Exception,err:
            self.quit()
            self.Log(str(err),logging.ERROR)
        else:
            msg='Finished playing recording'
            if stdout:
                msg=msg+'\n'+stdout
            if stderr:
                msg=msg+'\n'+stderr
            self.Log(msg)

        self.quit()

    def getfreeport(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost',0))
        port=s.getsockname()[1]
        s.close();del s
        return port

    def getsocket(self,port,attempts=5):
        for i in range(attempts):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                time.sleep(0.5)
                s.connect(('localhost', port))
            except Exception,err:
                del s
                if i==attempts-1:raise
                else:continue
            else:return s

    def quit(self):
        try:
            self.cmd('shutdown')
            self.cmd('quit')
            time.sleep(0.1)
        except:pass
        try:kill(self.proc)
        except:pass
        evt = PlayComplete(wizEVT_PLAYCOMPLETE, -1)
        self.PostEvent(evt)

    def getdata(self):
        data=''
        while True:
            try:part=self.socket.recv(1024)
            except socket.timeout:part=''
            if part:data+=part.strip()
            else:break
        return data

    def cmd(self,cmd):
        self.socket.sendall(cmd+os.linesep)
        data=self.getdata()

    def is_playing(self):
        self.socket.send('is_playing'+os.linesep)
        data=self.getdata()
        return data.strip('>').strip()=='1'

class ThreadedScheduler( ThreadedUtility, wx.EvtHandler):
    def __init__( self, parent, startDateTime, prgQueue,retries,deletefail,wizargs=[]):
        ThreadedUtility.__init__( self, parent )
        wx.EvtHandler.__init__( self )

        self.parent=parent
        self.startDateTime=wxdatetime_to_datetime(startDateTime)
        self.Queue=prgQueue
        self.evtStop=Event()
        self.evtPlay=Event()
        self.downloading=False
        self.timeremaining=None
        self.retries=retries
        self.deletefail=deletefail
        self.wizargs=wizargs

        self.Bind(EVT_DOWNLOADCOMPLETE, self._ondownloadcomplete)
        self.Bind(EVT_LOG, self._onlog)
        self.Bind(EVT_UPDATEPROGRESS, self._onupdateprogress)

        self.start()

    def reset(self,startDateTime):
        if self.downloading:
            self.Log('Can\'t reschedule once downloading',logging.ERROR)
        else:
            self.timer.cancel()
            self.startDateTime=wxdatetime_to_datetime(startDateTime)
            self.run()

    def stop(self):
        if self.downloading:
            self.evtStop.set()
        else:
            self.timer.cancel()

    def run(self):
        td=(self.startDateTime-datetime.now())
        try: start=td.total_seconds() #python 2.7
        except: start=(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        if start<=0:start=0
        self.timer = Timer(start,self._downloadqueue)
        self.timer.start()

    def _downloadqueue(self):
        self.downloading=True

        while not self.Queue.empty():
            if self.evtStop.is_set():return
            program = self.Queue.get()
            td= ThreadedDownloader( self, program['device'], [program], self.evtPlay, self.evtStop,self.retries,self.deletefail,wizargs=self.wizargs)
            td.join()#Block until  download is complete
            if self.evtStop.is_set():return
            self.Queue.task_done()
            evt = ScheduledDownloadComplete(wizEVT_SCHEDULEDDWONLOADCOMPLETE, -1,program)
            self.PostEvent(evt)

        evt = SchedulerComplete(wizEVT_SCHEDULERCOMPLETE, -1)
        self.PostEvent(evt)

    def _ondownloadcomplete(self,event):
        self.timeremaining=None

    def _onupdateprogress(self,event):
        progress = event.progress

        if progress.get('time',None)!=self.timeremaining \
           and 'second' not in progress['time']  \
           and 'calculating' not in progress['time']:
            self.timeremaining=progress['time']
            f=os.path.basename(progress['filename'])
            msg='Downloaded %s%% (%s MB) of %s, %s remaining.'
            msg=msg%(progress['percent'],progress['downloaded'],f,progress['time'])
            self.Log(msg)

    def _onlog(self,event):
        self.PostEvent(event)

    def __del__( self):
        try:self.stop()
        except:pass

class ThreadedStreamPlayer( ThreadedUtility, wx.EvtHandler):
    def __init__( self, parent, device, program, Stop, usetempfile=False, vlcargs=[],wizargs=[]):
        ThreadedUtility.__init__( self, parent )
        wx.EvtHandler.__init__( self )

        self.parent=parent
        self.device=device
        self.program=copy.copy(program)
        self.vlcargs=vlcargs
        self.wizargs=wizargs
        self.stream=not usetempfile
        self.Play=Event()
        self.Play.set()
        self.Stop=Stop
        self.Stop.clear()
        self.td=None
        self.tp=None

        v=getwizpnpversion()

        if v>=[0,5,4]:
            self.wizargs+=['--retry','30']

        if self.stream and v<[0,5,3]:
            self.stream=False
            self.Log('Unable to play recordings without a tempfile with getWizPnP<0.5.3')

        if not self.stream:
            self.program['filename']=tempfile.mktemp(suffix='.ts')
            logger.debug(self.program['filename'])

        self.Bind(EVT_DOWNLOADCOMPLETE, self._ondownloadcomplete)
        self.Bind(EVT_LOG, self._onlog)
        self.Bind(EVT_UPDATEPROGRESS, self._onupdateprogress)
        self.Bind(EVT_PLAYCOMPLETE, self._onplaycomplete)

        self.start()

    def stop(self):
        self.Stop.set()
        if not self.stream:
            try:self.td.join()
            except:pass
            try:self.tp.join()
            except:pass
            try:delete(self.program['filename'])
            except:self.Log('Error: Unable to delete %s'%self.program['filename'],logging.ERROR)
            evt = StreamComplete(wizEVT_STREAMCOMPLETE, -1)
            self.PostEvent(evt)
        else:
            trc=[]
            msg=[]
            try:
                exit_code=self.wizproc.poll()
                if exit_code is None:
                    try:kill(self.wizproc)
                    except:pass
                    exit_code=self.wizproc.poll()
                if exit_code:
                    msg+=[self.wizproc.stderr.read()]
            except Exception as err:
                trc+=[str(err)]
            try:
                exit_code=self.vlcproc.poll()
                if exit_code is None:
                    try:kill(self.vlcproc)
                    except:pass
                    exit_code=self.vlcproc.poll()
                if exit_code:
                    msg+=[self.vlcproc.stderr.read()]
            except Exception as err:
                trc+=[str(err)]

            evt = StreamComplete(wizEVT_STREAMCOMPLETE, -1)
            self.PostEvent(evt)
            return [msg,trc]

    def run(self):
        if not self.stream:
            self.td= ThreadedDownloader( self, self.device, [self.program], self.Play, self.Stop,wizargs=self.wizargs)
        else:
            cmd=[wizexe,'--stdout','--all','-R','--BWName',self.program['index']]+self.device.args+self.wizargs
            try:
                self.wizproc=subproc(cmd,env=wizenv)
                cmd=[vlcexe,'--no-video-title','-']+self.vlcargs
                self.vlcproc = subproc(cmd,stdin=self.wizproc.stdout)
                while self.vlcproc.poll() is None:
                    if self.wizproc.poll():raise Exception('getWizPnP is no longer running!')
                    if self.Stop.isSet():
                        self.stop()
                        return
                    else:time.sleep(1)
                self.stop()
            except Exception as err:
                msg,trc=self.stop()
                trc=[str(err)]+trc
                self.Log('Error, unable to stream %s.'%self.program['title'],logging.ERROR)
                if msg:self.Log('\n'.join(msg),logging.ERROR)
                if trc:logger.debug('\n'.join(trc))


    def _ondownloadcomplete(self,event):
        if event.stopped:self.stop()
        #pass

    def _onplaycomplete(self,event):
        self.stop()

    def _onupdateprogress(self,event):
        if not self.tp and event.progress.get('downloaded',0)>5:
            if not '--no-video-title' in self.vlcargs:self.vlcargs+=['--no-video-title']
            self.tp=ThreadedPlayer( self, self.Stop, self.Play,self.program['filename'],self.vlcargs)
        #pass

    def _onlog(self,event):
        if event.severity!=logging.INFO:
            self.PostEvent(event)

    def __del__( self):
        try:self.stop()
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
    _first = 1

    def __init__(self,logfile):
        self.logfile=logfile

    def errordialog(self,message, caption):
        import wx
        wxapp = wx.PySimpleApp(0)
        dlg = wx.MessageDialog(None,message, caption, wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def write(self, text,*args,**kwargs):
        if self._first:
            self._first=0
            self.errordialog("Errors occurred, see the logfile '%s' for details" % self.logfile, "Errors occurred")
        logger.error(text.strip())

    def flush(self):
        pass

class Callback:

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.callback(*self.args,**self.kwargs)

class Device(object):

    def __init__(self,device):

        self.ip,self.port,self.name=('','','')

        self.device=' '.join(device.split())
        device=self._parse(device)
        if device['ip']:self.ip=device['ip']
        if device['port']:self.port,self._port=device['port'],device['port']
        else:self.port,self._port='49152',''
        if device['name']:self.name=device['name']
        self.args=self._args()
        self.display=self._display()
        logger.debug('Adding new Device')
        logger.debug('Device IP,Port,Name="%s,%s,%s"'%(self.ip,self.port,self.name))
        logger.debug('Device display="%s"'%self.display)
        logger.debug('Device args="%s"'%self.args)
        logger.debug('Device str="%s"'%self.device)

    def __str__(self):
        '''String representation that can be parsed as a new Device.'''
        return self.device

    def _args(self):
        if self.ip:
            cmd=['-H',self.ip,'-p',self.port]
        else:
            cmd=['--device',self.name]
        return cmd

    def _display(self):
        '''String representation for display only.
          Handles the case where a device is 'discovered'
          and only the device name should be shown'''
        if self.ip and not self.name:
            s=self.ip
            if self._port:s+=':'+self._port
        elif self.ip and self._port and self.name:
            s='%s (%s:%s)'%(self.name,self.ip,self.port)
        else: s=self.name
        return s

    def _parse(self,device):
        import re
        try:
            reg='((?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})*(:(?P<port>\d{1,5}))*(\s*(?P<name>.*$)))'
            pat=re.compile(reg)
            mat=pat.search(device)
            return mat.groupdict()
        except: raise ValueError('Unable to parse device from"%s"'%device)

class Trunc(object):
    ''' A parser for the "trunc" file in a TVWiz directory.
        It is iterable, yielding tuples:
        wizOffset, fileNum, flags, offset, size
        as described at: http://openwiz.org/wiki/Recorded_Files#trunc_file
    '''
    #Modified from Cameron Simpson's scripts.
    #Documentation and source available from http://www.cskk.ezoshosting.com/cs/css/
    #
    #Licence:
    #  You're free to use, modify and redistribute these scripts provided that:
    #    - you leave my code marked as mine and your modifications (if any) marked as yours
    #    - you make recipients aware that the scripts can be obtained for free from my own web page

    def __init__(self, path):
        self.__path = path

    def __iter__(self):
        ''' The iterator to yield record tuples.
        '''
        try:fp = open(self.__path,'rb') #LP 03/01/2012 - open as rb so code works on windows
        except:
            if not os.path.exists(path): #LP 06/03/2012 - Raise a more understandable error
                raise TypeError('%s is not a TVWiz directory'%os.path.dirname(self.__path))
            else:raise
        while True:
            buf = fp.read(24)
            if len(buf) == 0:
                break
            assert len(buf) == 24
            yield struct.unpack("<QHHQL", buf)

class TVWiz(object):
    ''' Class to support access to Beyonwiz TVWiz data structures.
    '''
    #Modified from Cameron Simpson's scripts.
    #Documentation and source available from http://www.cskk.ezoshosting.com/cs/css/
    #
    #Licence:
    #  You're free to use, modify and redistribute these scripts provided that:
    #    - you leave my code marked as mine and your modifications (if any) marked as yours
    #    - you make recipients aware that the scripts can be obtained for free from my own web page

    def __init__(self, wizdir,evtstop): #LP 07/01/2012 - use threading event event to stop copy if required
        self.__dir = wizdir
        self.__stop = evtstop
        self.__stop.clear()

    def trunc(self):
        ''' Obtain a Trunc object for this TVWiz dir.
        '''
        return Trunc(os.path.join(self.__dir, "trunc"))

    def data(self):
        ''' A generator that yields MPEG2 data from the stream.
        '''
        T = self.trunc()
        lastFileNum = None
        for wizOffset, fileNum, flags, offset, size in T:
            if lastFileNum is None or lastFileNum != fileNum:
                if lastFileNum is not None:
                    fp.close()
                fp = open(os.path.join(self.__dir, "%04d"%fileNum),'rb') #LP 03/01/2012 - open as rb so code works on windows
                filePos = 0
                lastFileNum = fileNum
            if filePos != offset:
                fp.seek(offset)
            while size > 0:
                rsize = min(size, 8192)
                buf = fp.read(rsize)
                assert len(buf) <= rsize
                if len(buf) == 0:
                    raise IOError("%s: unexpected EOF", fp) #LP 03/01/2012 - remove dependency on custom CS error function
                yield buf
                size -= len(buf)
        if lastFileNum is not None:
            fp.close()

    def copyto(self, output):
        ''' Transcribe the uncropped content to a file named by output.
        '''
        if type(output) is str:
            with open(output, "wb") as out: #LP 03/01/2012 - open as wb so code works on windows
                self.copyto(out)
        else:
            for buf in self.data():
                if self.__stop.isSet():
                    break
                else:
                    output.write(buf)

#######################################################################
#Utility helper functions
#######################################################################
def data_path():
    if frozen() and sys.frozen!='macosx_app':
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def delete(f,n=5):
    if os.path.exists(f):
        for i in range(n):#Try to delete the file n times
            try:
                time.sleep(1)
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.unlink(f)
            except:
                if i==n-1:raise
                else:continue
            else:return
    else:return

def errordialog(message, caption):
    dlg = wx.MessageDialog(None,message, caption, wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def centrepos(self,parent):
    pxsize,pysize=parent.GetSizeTuple()
    pxmin,pymin=parent.GetPositionTuple()
    sxsize,sysize=self.GetSizeTuple()
    pxcen=pxmin+pxsize/2.0
    pycen=pymin+pysize/2.0
    sxmin=pxcen-sxsize/2.0
    symin=pycen-sysize/2.0
    return sxmin,symin

def datetime_to_wxdatetime(pydatetime):
    return wx.DateTimeFromTimeT(time.mktime(pydatetime.timetuple()))

def wxdatetime_to_datetime(wxdatetime):
    return datetime.fromtimestamp(wxdatetime.GetTicks())

def filesize(path):
    if os.path.isfile(path):return os.path.getsize(path)
    elif os.path.isdir(path):
        s=0
        for f in os.listdir(path):
            f=os.path.join(path,f)
            if os.path.isfile(f): s+=os.path.getsize(f)
        return s

def frozen():
    return hasattr(sys, "frozen")

def getwizpnpversion(as_string=False):
    if as_string :version='<=0.4.3a'
    else:version=[0,0,0]
    cmd = [wizexe,'--version']
    try:
        proc=subproc(cmd,env=wizenv)
        exit_code=proc.wait()
        stdout,stderr=proc.communicate()
        #version=[int(x) for x in stdout.strip()[0:5].split('.')]
        version=[int(x) for x in stderr.strip()[0:5].split('.')]
        if as_string:version=stderr.strip()
    except Exception as err:
        print str(err)
    return version
def kill(proc):

    if iswin:
        #killing using self.proc.kill() doesn't seem to work on getwizpnp.exe
        CTRL_C_EVENT = 0
        ctypes.windll.kernel32.GenerateConsoleCtrlEvent(CTRL_C_EVENT, proc.pid)
        if proc.poll() is None: #Nup, get nastier...
            #There doesn't seem to be any way to kill getwizpnp from within python
            #when it is kicked off by pythonw.exe (even tried ctypes.windll.kernel32.TerminateProcess)
            #other than taskkill/pskill (or manually with task manager -> kill process tree)
            #Killing with sigint works fine when process is started by python.exe... I'm stumped!
            #
            #NOTE: taskkill.exe is NOT available in WinNT, Win2K or WinXP Home Edition.
            #      It is available on WinXP Pro, Win 7 Pro , no idea about Vista or Win 7 starter/basic/home
            try:
                import psutil
                try:parent = psutil.Process(proc.pid)
                except:
                    logger.debug('No such process %s'%(proc.pid))
                    return
                for child in parent.get_children():
                    try:child.kill()
                    except:pass
                try:parent.kill()
                except:pass
            except ImportError:
                try:
                    cmd = ['pskill','/accepteula', '-t',str(proc.pid)]
                    killproc=subproc(cmd)
                    exit_code=killproc.wait()
                except WindowsError,err:
                    try:
                        cmd = ['taskkill','/F','/t','/PID',str(proc.pid)]
                        killproc=subproc(cmd)
                        exit_code=killproc.wait()
                    except WindowsError,err:
                        if err.winerror==2:
                            msg= '%s\nYour version of Windows does not include the "taskkill" command, '
                            msg+='you will need to end all GetWizPnP.exe processess manually using '
                            msg+='the Windows Task Manager (Ctrl-Alt-Delete).\n\n'
                            msg+='If you wish to make use of the stop and pause functionality, download '
                            msg+='PsTools.zip from http://technet.microsoft.com/en-us/sysinternals/bb896683 '
                            msg+='and copy PsKill.exe to the %s directory\n%s'
                            raise WindowsError,msg%('#'*10,APPNAME,'#'*10)
                        else:
                            raise
    else:
        proc.send_signal(signal.SIGINT)
    time.sleep(0.5)
    logger.debug('Killed process %s, %s'%(proc.pid,proc.poll()))

def license():
    try:
        import __license__
        license=__license__.license
    except ImportError:
        license=open(os.path.join(os.path.dirname(sys.argv[0]),'LICENSE')).read().strip()
    return license

def subproc(cmd,stdin=False,env=os.environ):
    logger.debug(subprocess.list2cmdline(cmd))
    logger.debug(str(cmd))
    if stdin:
        if type(stdin) is not file:stdin=subprocess.PIPE
        proc=subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=env,**Popen_kwargs)
    else:
        if 'pythonw.exe' in sys.executable:
            proc=subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=env,**Popen_kwargs)
            proc.stdin.close()
        else:
            proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=env,**Popen_kwargs)
    return proc

def timefromsecs(secs):
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    if h==0:
        if m==0:
            if s==1:return "1 second"
            else:return "%1d seconds" % (s)
        elif m==1:return "1 minute"
        else:return "%1d minutes" % (m)
    elif h==1 and m==0:return "1 hour"
    else:return "%1d:%02d hours" % (h, m)

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
    if result:return result
    else:return ''

#######################################################################
#Setup logging
#######################################################################
tmp=tempfile.gettempdir() #os.environ.get('TEMP',os.environ.get('TMP','/tmp'))
now=time.time()
logtime=time.strftime('%Y%m%d.%H%M%S',time.localtime(now))+'.%s'%int(now%1*10000)
logfile=os.path.join(tmp, '%s.%s.log'%(APPNAME,logtime))
#Clean up old log files
for f in glob.glob(os.path.join(tmp,'%s.*.log'%APPNAME)):
    if now-os.stat(f).st_mtime>(86400*5): #> 5 days
        os.unlink(f)
f=os.path.join(tmp,'%s.log'%APPNAME)
if os.path.exists(f):
    os.unlink(f)
formatter = logging.Formatter('%(levelname)s %(module)s.%(funcName)s: %(message)s')
handler=logging.FileHandler(logfile,mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger(APPNAME)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

del f,logtime,tmp,now,formatter,handler

#######################################################################
#Workarounds for py2exe/py2app
#######################################################################
if frozen() or 'pythonw.exe' in sys.executable:
    sys.stderr = Stderr(logfile)

#######################################################################
#Workarounds for crossplatform issues
#######################################################################
iswin=sys.platform[0:3] == 'win'
isnix='linux' in sys.platform
isosx=sys.platform == 'darwin'

filesysenc=sys.getfilesystemencoding()

path = os.environ.get("PATH", os.defpath)
if not '.' in path.split(os.pathsep):path=path+os.pathsep+'.'
p=os.path.abspath(os.path.dirname(sys.argv[0]))
if not p in path.split(os.pathsep):path=path+os.pathsep+p
os.environ['PATH']=path
getwizpnp=['getWizPnP.exe','getWizPnP.pl','getWizPnP','getwizpnp']
wizexe=''

#Create a limited environment for getWizPnP with HOME and APPDATA stripped out
# so .getwizpnp/getwizpnp.conf don't get used.
#This can be changed later on to use the new GETWIZPNPCONF environment variable (0.5.4+)
wizenv=os.environ.copy()
wizenv['HOME']=''
wizenv['APPDATA']=''
wizenv['GETWIZPNPCONF']=''

if not iswin:del getwizpnp[0]
for f in getwizpnp:
    if which(f):
        wizexe=f
        break

vlc=['VLC','vlc']
vlcexe=''

if iswin:
    p=r'VideoLAN\VLC'
    programfiles=[os.environ['ProgramFiles']]
    pf86=os.environ.get('ProgramFiles(x86)')
    if pf86:programfiles.append(pf86)
    for pf in programfiles:
        vlcpath=os.path.join(pf,p)
        if not vlcpath in path.split(os.pathsep):
            path=vlcpath+os.pathsep+path
    os.environ['PATH']=path
    vlc.append('vlc.exe')
elif isosx:
    os.environ['PATH']=path+os.pathsep+'/Applications/VLC.app/Contents/MacOS'

for f in vlc:
    if which(f):
        vlcexe=f
        break

if iswin:
    CTRL_C_EVENT = 0
    CREATE_NEW_PROCESS_GROUP=0x00000200 #getwizpnp kicks off child processes which the subprocess module doesn't kill unless a new process group is created.
    STARTF_USESHOWWINDOW=1 #subprocess.STARTF_USESHOWWINDOW raises
    creationflags=CREATE_NEW_PROCESS_GROUP
    startupinfo=subprocess.STARTUPINFO()#Windows starts up a console when a subprocess is run from a non-concole app like pythonw
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW #subprocess.STARTF_USESHOWWINDOW
    Popen_kwargs={'creationflags':creationflags,'startupinfo':startupinfo}
    autosize=wx.LIST_AUTOSIZE_USEHEADER #for ListCtrls
else:
    Popen_kwargs={}
    autosize=wx.LIST_AUTOSIZE #for ListCtrls

if 'linux' in sys.platform:
    try:#Set WM_CLASS on linux
        import gtk
        gtk.gdk.set_program_class(APPNAME)
    except:pass
