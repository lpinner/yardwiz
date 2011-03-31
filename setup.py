#!/usr/bin/python
from distutils.core import setup
import sys,ConfigParser

config=ConfigParser.ConfigParser()
config.read('VERSION')
version=config.get('Version','VERSION')                 #N.N.N.N format version number
display_version=config.get('Version','DISPLAY_VERSION') #Version text string
short_version=version[:-2]

setupargs={'name':'YARDWiz',
      'version':short_version,
      'description':'Yet Another Recording Downloader for the Wiz',
      'long_description':'YARDWiz is a simple GUI front end for prl\'s getWizPnP prgram. getWixPnP is a command line program allows that you (among other things) to list and download recordings from a Beyonwiz DP series PVR over the network using the WizPnP interface.',
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
      'package_data':{'yardwizgui': ['config/defaults.ini','icons/*.*']},
    }


if len(sys.argv)>1 and sys.argv[1]=='uninstall':
    import os,shutil
    for p in sys.path:
        if os.path.dirname(os.path.abspath(sys.argv[0]))!=p: #Not the current dir
            f=os.path.join(p,'yardwizgui')
            if os.path.exists(f):
                print 'Removing '+f
                shutil.rmtree(f)
                break
    if sys.platform[0:3]=='win':
        f=os.path.join(sys.exec_prefix, 'Scripts','yardwiz')
    else:
        f='/usr/local/bin/yardwiz'
    print 'Removing '+f
    os.unlink(f)

    print 'Uninstall successfull'

elif len(sys.argv)>1 and sys.argv[1]=='py2exe':
    import py2exe,glob,os,subprocess,zipfile,shutil

    setupargs['windows'] = [{'script':'yardwiz',
                            'icon_resources':[(2, r'yardwizgui/icons/icon.ico')]
                            }]
    setupargs['data_files']=[('',['getwizpnp.exe']),
                             ('',['README']),
                             ('',['LICENSE']),
                             ('',['TODO']),
                             ('',['RELEASE']),
                             ('',['VERSION']),
                             ('config', ['yardwizgui/config/defaults.ini']),
                             ('icons', glob.glob('yardwizgui/icons/*.*'))]

    setup(**setupargs)

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

else:
    setup(**setupargs)

