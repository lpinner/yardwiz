# YARDWiz - Yet Another Recording Downloader for the Wiz #

## Introduction ##
YARDWiz is a simple crossplatform GUI front end for prl's getWizPnP program.  getWizPnP is a command line program that allows you (among other things) to list and download recordings from a Beyonwiz DP series PVR over the network using the WizPnP interface. YARDWiz draws a lot of inspiration from the Two Wizards WizZilla software.

I wrote YARDWiz as I wanted a simple getWinPnP GUI that ran on my Linux laptop.
## News ##
  * YARDWiz 1.0 [released](https://code.google.com/p/yardwiz/wiki/ReleaseNotes).
  * YARDWiz downloads are hosted on [Bintray](https://bintray.com) as Google Code has [discontinued download hosting](http://google-opensource.blogspot.com.au/2013/05/a-change-to-google-code-download-service.html).

[![](https://api.bintray.com/packages/lukepinnerau/generic/YARDWiz/images/download.png)](http://goo.gl/KIcLUV)

## Screenshots ##
|**_Linux_**|**_Windows_**|**_OSX_**|
|:----------|:------------|:--------|
|[![](http://yardwiz.googlecode.com/svn/images/thumbnail-ubuntu.png)](http://code.google.com/p/yardwiz/wiki/ScreenshotLinux)|[![](http://yardwiz.googlecode.com/svn/images/thumbnail-win7.png)](http://code.google.com/p/yardwiz/wiki/ScreenshotWin7)|[![](http://yardwiz.googlecode.com/svn/images/thumbnail-osx.png)](http://code.google.com/p/yardwiz/wiki/ScreenshotOSX)|

## Requirements ##
YARDWiz has been tested successfully on the following OS's using python 2.6 & 2.7, wxPython 2.8 and getWizPnP 0.4.3a - 0.5.4.:
  * Windows (8 consumer preview, 7 Pro, Vista Home Premium, XP Pro)
  * Linux (Ubuntu 12.04+, OpenSuse 11.4, Fedora 14, 15 and 16), it should work on other linux flavours.
  * Mac OSX 10.8 (YARDWiz >=0.4.3) and 10.6 (YARDWiz <=0.4.2x) .

## Known issues ##
  * Downloads may fail with the getWizPnP error - "Search for WizPnP devices failed" when connecting via a device name, even after listing programs succeeded using that device name.  This has only occurred on one Win 7 Ultimate PC that I'm aware of and the issue does not occurr on the same users Win XP PC.  Workaround (thanks to netmask from the Beyonwiz forum): connect using IP or IP:Port syntax. Another workaround has been implemented in 0.3.1, clear the Wiz server text box and click the connect button to let YARDWiz discover your Wiz.
  * YARDWiz does not work on Beyonwiz FV-L1 PVR's running techguy's unlocked firmware.
  * The app really should use a lawnmower icon...


Coded using [![](http://wingware.com/images/wingware-logo-65x21.png)](http://wingware.com)