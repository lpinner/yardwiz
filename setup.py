#!/usr/bin/python
from distutils.core import setup
import sys

setupargs={'name':'YARDWiz',
      'version':'0.1.1',
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
    import py2exe,glob,os
    setupargs['windows'] = [{'script':'yardwiz',
                            'icon_resources':[(2, r'yardwizgui/icons/icon.ico')]
                            }]
    setupargs['data_files']=[('',['getwizpnp.exe']),('config', ['yardwizgui/config/defaults.ini']), ('icons', glob.glob('yardwizgui/icons/*.*'))]
    #setupargs['options'] = {'py2exe': {'bundle_files': 1}}
    #setupargs['zipfile'] = None
    setup(**setupargs)

else:        
    setup(**setupargs)

