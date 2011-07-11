import sys
import os
import ConfigParser
import googlecode_upload

try:
    ok=raw_input('Are you sure you want to upload to googlecode? [y/N]')
    if ok.upper()=='Y':pass
    else:sys.exit(0)
except:sys.exit(0)

config=ConfigParser.ConfigParser()
config.read('VERSION')
version=config.get('Version','VERSION')#N.N.N.N format version number
short_version='.'.join(version.split('.')[:-1])
project='yardwiz'

uploads={
    'YARDWiz-%s-OSX-10.6.dmg':{
        '--summary':'YARDWiz %s (OSX App)'%short_version,
        '--description':'This App was compiled and tested on OSX10.6.7.\nTo install, mount the disk image (.dmg) and drag the YARWiz App to your Applications folder.',
        '--labels':'Featured,Type-Archive,OpSys-OSX'},
    'YARDWiz-%s-linux-x64.tar.gz':{
        '--summary':'YARDWiz %s (Linux x64)'%short_version,
        '--description':'This version of YARDWiz includes a version of getWizPnP compiled for 64 bit architectures.\nInstall using "sudo python setup.py install"',
        '--labels':'Featured,Type-Archive,OpSys-Linux'},
    'YARDWiz-%s-linux-x86.tar.gz':{
        '--summary':'YARDWiz %s (Linux x86)'%short_version,
        '--description':'This version of YARDWiz includes a version of getWizPnP compiled for 32 bit architectures.\nInstall using "sudo python setup.py install"',
        '--labels':'Featured,Type-Archive,OpSys-Linux'},
    'YARDWiz-%s.zip':{
        '--summary':'YARDWiz %s (Source)'%short_version,
        '--description':'YARDWiz source archive',
        '--labels':'Featured,Type-Source,OpSys-All'},
    'YARDWiz-%s-win32setup.zip':{
        '--summary':'YARDWiz %s (Windows installer)'%short_version,
        '--description':'YARDWiz Windows installer',
        '--labels':'Featured,Type-Installer,OpSys-Windows'}
    }

for f in uploads:
    if len(sys.argv)>1:del sys.argv[1:]
    filename=os.path.join('dist',f%short_version)
    sys.argv.extend(['--project',project])
    for opt in uploads[f]:
        sys.argv.extend([opt,uploads[f][opt]])
    sys.argv.append(filename)
    googlecode_upload.main()