#!/usr/bin/python
from distutils.core import setup
import os,sys,ConfigParser,shutil,zipfile,subprocess

config=ConfigParser.ConfigParser()
config.read('VERSION')
version=config.get('Version','VERSION')                 #N.N.N.N format version number
display_version=config.get('Version','DISPLAY_VERSION') #Version text string
short_version='.'.join(version.split('.')[:-1])

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

def writelicenseversion(version,display_version):
    #Create the license and version scripts
    #Doesn't get latest rev. for the working copy, only the directory
    #try:
    #    import pysvn
    #    client = pysvn.Client()
    #    info=client.info('.')
    #    rev=str(info.revision.number)
    #    version=version.split('.')
    #    version[-1]=rev
    #    version='.'.join(version)
    #except:
    #    pass
       
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


lib,scripts,data,prefix=getpaths()

setupargs={'name':'YARDWiz',
      'version':short_version,
      'description':'Yet Another Recording Downloader for the Wiz',
      'long_description':'YARDWiz is a simple GUI front end for prl\'s getWizPnP prgram. getWizPnP is a command line program allows that you (among other things) to list and download recordings from a Beyonwiz DP series PVR over the network using the WizPnP interface.',
      'platforms':['linux','windows','darwin'],
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
      'package_data':{'yardwizgui': ['config/defaults.ini','icons/*.*','sounds/*.wav','sounds/README']}
    }

if 'linux' in sys.platform and 'install' in sys.argv:
    try:
        import wx
        v=wx.VERSION
        if not v[0]>=2 and v[1]>=8:
            print 'wxPython v2.8+ is required, YARDWiz setup can not continue. Install wxPython 2.8 or later and then try again.'
            sys.exit(1)
    except:
        print 'wxPython is not installed or is not configured correctly, YARDWiz setup can not continue. Install wxPython and then try again.'
        sys.exit(1)

    setupargs['data_files']=[('share/pixmaps',['yardwizgui/icons/yardwiz.png']),('share/applications',['yardwiz.desktop'])]
    if os.path.exists('getWizPnP'):
        setupargs['data_files'].append(('bin',['getWizPnP']))
    desktop=open('yardwiz.desktop.in').read()%(short_version,data)
    open('yardwiz.desktop','w').write(desktop)

elif 'darwin' in sys.platform and 'py2app' in sys.argv:
    from setuptools import setup
    import glob,stat
        
    APP = [ 'YARDWiz.py']
    DATA_FILES = [('',['README']),
                  ('',['LICENSE']),
                  ('',['RELEASE']),
                  ('',['VERSION'])]
    OPTIONS = {'extension': '.app', 'packages': 'yardwizgui',
               'iconfile': 'yardwizgui/icons/yardwiz.icns',
               'excludes':['doctest','pdb','encodings.big5','encodings.big5hkscs','encodings.cp037',
               'encodings.cp1006','encodings.cp1026','encodings.cp1140','encodings.cp1250','encodings.cp1251',
               'encodings.cp1252','encodings.cp1253','encodings.cp1254','encodings.cp1255','encodings.cp1256',
               'encodings.cp1257','encodings.cp1258','encodings.cp424','encodings.cp437','encodings.cp500',
               'encodings.cp737','encodings.cp775','encodings.cp850','encodings.cp852','encodings.cp855',
               'encodings.cp856','encodings.cp857','encodings.cp860','encodings.cp861','encodings.cp862',
               'encodings.cp863','encodings.cp864','encodings.cp865','encodings.cp866','encodings.cp869',
               'encodings.cp874','encodings.cp875','encodings.cp932','encodings.cp949','encodings.cp950',
               'encodings.euc_jis_2004','encodings.euc_jisx0213','encodings.euc_jp','encodings.euc_kr',
               'encodings.gb18030','encodings.gb2312','encodings.gbk','encodings.hp_roman8','encodings.hz',
               'encodings.idna','encodings.iso2022_jp','encodings.iso2022_jp_1','encodings.iso2022_jp_2',
               'encodings.iso2022_jp_2004','encodings.iso2022_jp_3','encodings.iso2022_jp_ext',
               'encodings.iso2022_kr','encodings.iso8859_1','encodings.iso8859_10','encodings.iso8859_11',
               'encodings.iso8859_13','encodings.iso8859_14','encodings.iso8859_15','encodings.iso8859_16',
               'encodings.iso8859_2','encodings.iso8859_3','encodings.iso8859_4','encodings.iso8859_5',
               'encodings.iso8859_6','encodings.iso8859_7','encodings.iso8859_8','encodings.iso8859_9',
               'encodings.johab','encodings.koi8_r','encodings.koi8_u','encodings.mac_arabic',
               'encodings.mac_centeuro','encodings.mac_croatian','encodings.mac_cyrillic','encodings.mac_farsi',
               'encodings.mac_greek','encodings.mac_iceland','encodings.mac_latin2','encodings.mac_roman',
               'encodings.mac_romanian','encodings.mac_turkish','encodings.mbcs','encodings.palmos',
               'encodings.ptcp154','encodings.punycode','encodings.quopri_codec','encodings.rot_13',
               'encodings.shift_jis','encodings.shift_jis_2004','encodings.shift_jisx0213','encodings.tis_620',
               'encodings.uu_codec','encodings.bz2_codec','encodings.utf_16','encodings.utf_16_be',
               'encodings.utf_16_le','encodings.utf_32','encodings.utf_32_be','encodings.utf_32_le']}
    
    shutil.copy('yardwiz','YARDWiz.py')
    if os.path.exists('dist'):shutil.rmtree('dist')
    if os.path.exists('build'):shutil.rmtree('build')

    setup(app=APP,
          data_files=DATA_FILES,
          options={'py2app': OPTIONS},
          setup_requires=['py2app'])
  
    print 'Copying getWizPnP to app'
    shutil.copy('getWizPnP','dist/YARDWiz.app/Contents/Resources/getWizPnP')
    print 'Changing mode of getWizPnP to 755'
    os.chmod('dist/YARDWiz.app/Contents/Resources/getwizpnp',stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    os.unlink('YARDWiz.py')
    shutil.rmtree('build')
    print 'Creating disk image'
    cmd='hdiutil create -size 120m -imagekey zlib-level=9 -srcfolder dist/YARDWiz.app dist/YARDWiz-%s-OSX-10.6.dmg'%short_version
    proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr=proc.communicate()
    exit_code=proc.wait()
    if exit_code:print stderr
    sys.exit(0)

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

elif 'sdist' in sys.argv:
    writelicenseversion(version,display_version)

elif 'py2exe' in sys.argv:
    import py2exe,glob

    writelicenseversion(version,display_version)

    #setupargs['windows'] = [{'script':'yardwiz',
    #                        'icon_resources':[(2, r'yardwizgui/icons/icon.ico')]
    #                        }]
    setupargs['windows'] = [{'script':'yardwiz',
                            'icon_resources':[(2, r'yardwizgui/icons/icon.ico')],
                            
                            }]
    setupargs['options']={"py2exe":
                            {'excludes':['xml','ssl','random','httplib','urllib','xml','_ssl','email','doctest','pdb','unittest','inspect','pyreadline', 'pickle'],
                            'compressed':True
                            }
                        }
    setupargs['data_files']=[('',['getwizpnp.exe']),
                             ('',['README']),
                             ('',['LICENSE']),
                             ('',['RELEASE']),
                             ('',['VERSION']),
                             ('',['Microsoft.VC90.CRT.manifest']),
                             ('',glob.glob('msvc*90.dll')),
                             ('sounds', glob.glob('yardwizgui/sounds/*')),
                             ('config', ['yardwizgui/config/defaults.ini']),
                             ('icons', glob.glob('yardwizgui/icons/*.png')),
                             ('icons', glob.glob('yardwizgui/icons/*.ico'))]

s=setup(**setupargs)

if 'linux' in sys.platform and 'install' in sys.argv:
    import stat
    print 'Changing mode of %s/share/applications/yardwiz.desktop to 755'%data
    os.chmod(os.path.join(data,'share/applications/yardwiz.desktop'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    print 'Changing mode of %s/share/pixmaps/yardwiz.png to 744'%data
    os.chmod(os.path.join(data,'share/pixmaps/yardwiz.png'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IROTH)
    if os.path.exists('%s/bin/getWizPnP'%data):
        print 'Changing mode of %s/bin/getWizPnP to 755'%data
        os.chmod(os.path.join(data,'bin/getWizPnP'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

elif sys.platform[0:3]=='win' and 'install' in sys.argv:
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

