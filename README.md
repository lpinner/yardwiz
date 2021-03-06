# YARDWiz - Yet Another Recording Downloader for the Wiz #

## Note ##
I am no longer developing/maintaining YARDWiz as I don't have a Beyonwiz DP series PVR anymore.

## Introduction ##

YARDWiz is a simple crossplatform GUI front end for prl's getWizPnP prgram.  getWizPnP is a command line program that allows you (among other things) to list and download recordings from a Beyonwiz DP series PVR over the network using the WizPnP interface. YARDWiz draws a lot of inspiration from the Two Wizards WizZilla software.

## Screenshots ##

| Linux | Windows | OSX|
| --------| ------------- | -----|
|[![Screenshot Linux](https://raw.githubusercontent.com/lpinner/yardwiz/wiki/images/thumbnail-ubuntu.png)](https://github.com/lpinner/yardwiz/tree/wiki/images/screenshot-ubuntu.png)|[![Screenshot Windows](https://raw.githubusercontent.com/lpinner/yardwiz/wiki/images/thumbnail-win7.png)](https://github.com/lpinner/yardwiz/tree/wiki/images/screenshot-win7.png)|[![Screenshot OSX](https://raw.githubusercontent.com/lpinner/yardwiz/wiki/images/thumbnail-osx.png)](https://github.com/lpinner/yardwiz/tree/wiki/images/screenshot-osx.png)|

## Downloads ##
Downloads are hosted on Bintray [![Latest version](https://api.bintray.com/packages/lukepinnerau/generic/YARDWiz/images/download.png)](http://goo.gl/KIcLUV)

## Help ##
Help is available on the [Wiki](https://github.com/lpinner/yardwiz/wiki)
## Requirements ##
YARDWiz has been tested successfully on Windows XP - 10, Ubuntu 10.04-14.04, OpenSuse 11.4, Fedora 14 & 15 and Mac OSX 10.8 - 10.10 with python 2.6 & 2.7, wxPython 2.8. It should work on other Windows and Linux flavours.

### Windows
A windows installer is available which is self contained and doesn't require the installation of python, wxpython or getWizPnP.

### OSX
An OSX application is available which is self contained and doesn't require the installation of python, wxpython or getWizPnP.

### Linux
An source archive is available which contains a compiled version of getWizPnP

### From source
Before running you will need to install the following software:

  * python >=2.6 and < 3.0  (http://www.python.org)
  * wxpython 2.8+  (http://www.wxpython.org)
  * getWizPnP   (http://www.openwiz.org/wiki/GetWizPnP_Release)
    * download a compiled version or install the perl package from source as per the installation notes in getWizPnP README.txt

## Installation

### Windows
Run the windows installer, this is self contained and doesn't require the prior installation of python, wxpython or getWizPnP.

### OSX
Mount the disk image (.dmg) and drag the YARDWiz app to your applications folder.

### From source
Currently no other OS specific installers have been created, just a simple python setup.py script. To install, unzip the source archive, then:

  * Windows - run `python setup.py install` in a command window (you _may_ need to run it as Administrator).
  * Linux & OSX - `sudo python setup.py install`

For easy access to the application, setup.py creates shortcuts in the Windows Start Menu/Linux Gnome Menu. Or on Linux and OSX, you can just type 'yardwiz' in a terminal.

## Uninstalling

### Uninstalling on Windows
Run the windows uninstaller.

### Uninstalling on OSX
Delete the YARDWiz app from your applications folder.

### When installed from source
To uninstall (assuming you still have a copy of the source :):
  * Windows - run `python setup.py uninstall` in a command window (you _may_ need to run it as Administrator).
  * Linux & OSX - `sudo python setup.py uninstall`

## Known issues

 * If you modify the default getwizpnp.conf (Windows) or .getwizpnp (Linux/Mac) you may break YARDWiz.
 * On Windows when running from pythonw.exe, the getwizpnp.exe subprocess has proven troublesome to kill (i.e if you want to pause or stop a download). I've had to fallback to using the taskkill.exe program that is included in most recent versions of Windows (XP and later). Taskkill.exe is _not_ included in Windows XP Home edition and I don't know if it is included in Windows Vista/7 basic/home/starter editions. If this is an issue, an alternative is to download PsTools.zip from http://technet.microsoft.com/en-us/sysinternals/bb896683 and extract PsKill.exe to somewhere on your PATH. YARDWiz will then attempt to use pskill instead.
 * Downloads may fail with the getWizPnP error - "Search for WizPnP devices failed" when connecting via a device name, even after listing programs succeeded using that device name.  This has only occurred on one Win 7 Ultimate PC that I'm aware of and the issue does not occurr on the same users Win XP PC.  Workaround (thanks to netmask from the Beyonwiz forum): connect using IP or IP:Port syntax. Another workaround has been implemented in 0.3.1, clear the Wiz server text box and click the connect button to let YARDWiz discover your Wiz.
 * The app really should use a lawnmower icon...
