#!/usr/bin/python
from distutils.core import setup
import os,sys,ConfigParser,shutil

def getpaths():
    #fake a setup to get the paths
    lib,scripts,data,prefix=('','','','')
    args=sys.argv[:]
    if 'uninstall' in sys.argv:
        idx=sys.argv.index('uninstall')
        sys.argv[idx]='install'
    if 'install' in sys.argv:
        idx=sys.argv.index('install')
        sys.argv.insert(idx,'-q')
        sys.argv.insert(idx,'--dry-run')
        s=setup()
        lib=s.command_obj['install'].install_lib
        scripts=s.command_obj['install'].install_scripts
        data=s.command_obj['install'].install_data
        prefix=s.command_obj['install'].prefix
    sys.argv=args[:]
    return lib,scripts,data,prefix

def writelicenseversion():
    #Create the license and version scripts
    license=open('LICENSE').read().strip()
    v=open('yardwizgui/__version__.py', 'w')
    l=open('yardwizgui/__license__.py', 'w')
    v.write('#This file is generated by setup.py\n')
    l.write('#This file is generated by setup.py\n')
    v.write('version="%s"\n'%version)
    v.write('display_version="%s"\n'%display_version)
    l.write('license="""%s"""'%license)
    v.close()
    l.close()

def createshortcut(filename,target, arguments=None, startin=None, icon=None, description=None):
    try:
        import win32com.client #I'd really like to do this without pythonwin...
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(filename)
        shortcut.TargetPath = target
        if arguments:shortcut.Arguments = arguments
        if startin:shortcut.WorkingDirectory = startin
        if icon:shortcut.IconLocation=icon
        if description:shortcut.Description=description
        shortcut.save()
    except ImportError:
        print 'Can\'t create shortcut without pythonwin installed'

def getprogrammenu(allusers=True):
    import ctypes
    from ctypes.wintypes import HWND,HANDLE,DWORD,LPCWSTR,MAX_PATH,create_unicode_buffer
    GetFolderPath=ctypes.windll.shell32.SHGetFolderPathW
    if allusers:intFolder=23
    else:intFolder=2
    GetFolderPath.argtypes = [HWND, ctypes.c_int, HANDLE, DWORD, LPCWSTR]
    auPathBuffer = create_unicode_buffer(MAX_PATH)
    exit_code=GetFolderPath(0, intFolder, 0, 0, auPathBuffer)
    return auPathBuffer.value

config=ConfigParser.ConfigParser()
config.read('VERSION')
version=config.get('Version','VERSION')                 #N.N.N.N format version number
display_version=config.get('Version','DISPLAY_VERSION') #Version text string
short_version=version[:-2]

lib,scripts,data,prefix=getpaths()

setupargs={'name':'YARDWiz',
      'version':short_version,
      'description':'Yet Another Recording Downloader for the Wiz',
      'long_description':'YARDWiz is a simple GUI front end for prl\'s getWizPnP prgram. getWizPnP is a command line program allows that you (among other things) to list and download recordings from a Beyonwiz DP series PVR over the network using the WizPnP interface.',
      'platforms':['linux','windows'],
      'author':'Luke Pinner',
      'author_email':'tiliqua_au@yahoo.com.au',
      'url':'http://code.google.com/p/yardwiz',
      'license':'MIT License',
      'classifiers':['Development Status :: 4 - Beta',
                   'Environment :: Win32 (MS Windows)',
                   'Environment :: X11 Applications',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python',
                   'Topic :: Multimedia :: Video'],
      'packages':['yardwizgui'],
      'scripts':['yardwiz'],
      'package_data':{'yardwizgui': ['config/defaults.ini','icons/*.*','sounds/*.wav','sounds/README']},
      'data_files':[('share/pixmaps',['yardwizgui/icons/yardwiz.png']),('share/applications',['yardwiz.desktop.in'])]
    }

if 'linux' in sys.platform and 'install' in sys.argv:
    setupargs['data_files']=[('share/pixmaps',['yardwizgui/icons/yardwiz.png']),('share/applications',['yardwiz.desktop'])]
    desktop=open('yardwiz.desktop.in').read()%(short_version,data)
    open('yardwiz.desktop','w').write(desktop)

elif 'uninstall' in sys.argv:
    import shutil
    f=os.path.join(lib,'YARDWiz-%s.egg-info'%short_version)
    if os.path.exists(f):
        os.unlink(f)
        print 'Removed '+f
    f=os.path.join(lib,'yardwizgui')
    if os.path.exists(f):
        shutil.rmtree(f)
        print 'Removed '+f
    f=os.path.join(scripts,'yardwiz')
    if os.path.exists(f):
        os.unlink(os.path.join(scripts,'yardwiz'))
        print 'Removed '+f
    f=os.path.join(data,'share/applications/yardwiz.desktop')
    if os.path.exists(f):
        os.unlink(f)
        print 'Removed '+f
    f=os.path.join(data,'share/pixmaps/yardwiz.png')
    if os.path.exists(f):
        os.unlink(f)
        print 'Removed '+f
    try:
        sm=getprogrammenu()
        if os.path.exists(f):
            os.unlink(f)
            print 'Removed '+f
        sm=getprogrammenu(False)
        f='%s\\yardwiz.lnk'%sm
        if os.path.exists(f):
            os.unlink(f)
            print 'Removed '+f
    except:pass
    sys.exit(0)

elif 'sdist' in sys.argv in sys.argv:
    writelicenseversion()

elif 'py2exe' in sys.argv:
    import py2exe,glob,subprocess,zipfile,shutil

    writelicenseversion()

    setupargs['windows'] = [{'script':'yardwiz',
                            'icon_resources':[(2, r'yardwizgui/icons/icon.ico')]
                            }]
    setupargs['data_files']=[('',['getwizpnp.exe']),
                             ('',['README']),
                             ('',['LICENSE']),
                             ('',['RELEASE']),
                             ('',['VERSION']),
                             ('',['Microsoft.VC90.CRT.manifest']),
                             ('',glob.glob('msvc*90.dll')),
                             ('sounds', glob.glob('yardwizgui/sounds/*')),
                             ('config', ['yardwizgui/config/defaults.ini']),
                             ('icons', glob.glob('yardwizgui/icons/*.*'))]

s=setup(**setupargs)

if 'linux' in sys.platform and 'install' in sys.argv:
    import stat
    print 'Changing mode of %s/share/applications/yardwiz.desktop to 755'%data
    os.chmod(os.path.join(data,'share/applications/yardwiz.desktop'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    print 'Changing mode of %s/share/pixmaps/yardwiz.png to 744'%data
    os.chmod(os.path.join(data,'share/pixmaps/yardwiz.png'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IROTH)

elif 'win' in sys.platform and 'install' in sys.argv:
    filename='YARDWiz.lnk'
    target='%s\\pythonw.exe'%prefix
    arguments='%s\\yardwiz'%scripts
    startin=prefix
    icon='%s\\yardwizgui\\icons\\icon.ico'%lib
    description=setupargs['description']
    try:#Assume admin privileges
        createshortcut(os.path.join(getprogrammenu(),filename),target, arguments, startin, icon, description)
    except:
        createshortcut(os.path.join(getprogrammenu(False),filename),target, arguments, startin, icon, description)

elif 'py2exe' in sys.argv:
    print 'Compiling installer.'
    cmd=[r'C:\Program Files\NSIS\makensis','/V2','/DVERSION=',version,'/DDISPLAY_VERSION=',display_version,'build.nsi']
    cmd=subprocess.list2cmdline(cmd).replace('= ','=')
    proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr=proc.communicate()
    exit_code=proc.wait()
    if exit_code:print stderr
    else:
        print stdout
        print 'Zipping files'
        fout='dist/YARDWiz-%s-win32setup.zip'%short_version
        zout=zipfile.ZipFile(fout,'w',zipfile.ZIP_DEFLATED)
        zout.write('dist/setup.exe','setup.exe')
        zout.close()
        for f in os.listdir('dist'):
            f='dist/'+f
            if not f==fout:
                if os.path.isdir(f):shutil.rmtree(f)
                else:os.unlink(f)

try:
    shutil.rmtree('build')
except:pass
try:
    os.unlink('yardwiz.desktop')
except:pass

