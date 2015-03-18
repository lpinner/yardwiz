# YARDWiz Help #

## Introduction ##
YARDWiz is a simple crossplatform GUI front end for prl's getWizPnP prgram. getWizPnP is a command line program allows that you (among other things) to list and download recordings from a Beyonwiz DP series PVR over the network using the WizPnP interface. YARDWiz draws a lot of inspiration from the Two Wizards [WizZilla](http://www.openwiz.org/wiki/Software#WizZilla) software.

## Installation ##
### Installing on Windows [^](#YARDWiz_Help.md) ###
Run the windows installer, this is self contained and doesn't require the prior installation of python, wxpython or getWizPnP.

### Installing on OSX 10.8 [^](#YARDWiz_Help.md) ###
Mount the disk image (.dmg), drag the YARDWiz app to your applications folder. The YARDWiz app is self contained and doesn't require the prior installation of python, wxpython or getWizPnP.

### From source [^](#YARDWiz_Help.md) ###
Before installing you will need to install the following software:
  * python >=2.6 and < 3.0  (http://www.python.org)
  * wxpython 2.8+  (http://www.wxpython.org)
  * getWizPnP   (http://www.openwiz.org/wiki/GetWizPnP_Release)
On Linux, you can also download and install the source archive that contains a pre-compiled version of getWizPnP.

Currently no other OS specific installers have been created, just a simple python setupy.py script. To install, unzip the source archive, then:
  * Windows - run `python setup.py install` in a command window (you _may_ need to run it as Administrator).
  * Linux - `sudo python setupy.py install `

For easy access to the application, setup.py creates shortcuts in the Windows Start Menu/Linux Gnome Menu. Or on Linux and OSX, you can just type 'yardwiz' in a terminal.

## Uninstalling ##
### Uninstalling on Windows [^](#YARDWiz_Help.md) ###
Run the windows uninstaller.

### Uninstalling on OSX ###
Delete the YARDWiz app from your applications folder.

### When installed from source [^](#YARDWiz_Help.md) ###
  * Windows - run `python setup.py uninstall` in a command window (you _may_ need to run it as Administrator).
  * Linux - `sudo python setupy.py uninstall`

## Using YARDWiz ##
Run YARDWiz by from your start menu shortcut (Windows) or, if you installed from source on Linux, type `yardwiz` in a terminal. For easy access to the YARDWiz on Linux, I create a launcher in my Gnome Menu to /usr/local/bin/yardwiz. To bling up your launcher, there is an icon in the /usr/local/lib/python(version)>/dist-packages/yardwizgui/icons folder.

### YARDWiz controls [^](#YARDWiz_Help.md) ###
_Buttons_
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/reload.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/reload.png) | Discover a Wiz and/or load program list|
|:--------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/clear.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/clear.png) | Clear the download queue|
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/download.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/download.png) | Start downloading all programs in the queue|
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/pause.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/pause.png) | Pause a download temporarily|
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/play.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/play.png) | Restart a paused download|
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/stop.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/stop.png) | Stop the current download and delete the partially downloaded file|
| ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/vlc.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/vlc.png) | Play the current download in [VLC](http://www.videolan.org)|

### YARDWiz preferences [^](#YARDWiz_Help.md) ###
#### Settings [^](#YARDWiz_Help.md) ####
  * _Device_: The last used Beyonwiz device [IP address or device name](#Connecting_to_your_Wiz.md).
  * _Auto list recordings_: Automatically connect to to the first Beyonwiz device listed and list recordings on startup (0.4.2+).
  * _Auto update recordings_: Automatically list recordings after selecting a different Beyonwiz device from the "Wiz Server:" list (0.4.2+).
  * _Last directory_: The last directory you have downloaded a recording to.
  * _Default to TS format for downloads_: The file dialog for selecting downloaded recording filenames will default to [TS](http://en.wikipedia.org/wiki/MPEG_transport_stream) (`*`.ts) format. If you uncheck this preference, the file dialog will default to Beyonwiz [TVWIZ](http://www.openwiz.org/wiki/Recorded_Files) format (`*`.tvwiz). Both formats are available in the file dialog, so you can still select TVWIZ format for each download if you like without changing this preference.
  * _Post download command_: A command to run once a recording has downloaded. You can pass the full filepath and/or download directory to the command as an argument using the %F and/or %D variables respectively.
  * _VLC command line arguments_: Additional command line configuration arguments for [VLC](http://www.videolan.org). More info can be found at: [wiki.videolan.org](http://wiki.videolan.org/VLC_command-line_help)
  * _Use temp file when playing_: Using a temporary file when playing in VLC allows you to pause and rewind (0.4.2+).
  * _Date format for display_: Specify the date/time format that will be shown in the program list. The format is as per the python date/time [format codes](http://docs.python.org/library/time.html#time.strftime).
  * _Date format for filenames_: Specify a date/time format that will be used to create a default filename for each recording. You can still change the filename to anything you like when you select it for download. The format is as per the python date/time [format codes](http://docs.python.org/library/time.html#time.strftime).
  * _Confirm delete_: Ask you for confirmation before deleting a recording.
  * _Enable quick listing_: Enabling quick listing will show your program list much quicker by simply reading the Wiz's index. However, it will also show you any files that have been [deleted](#Deleting_a_recording.md) from your Wiz and will allow you to attempt to delete recordings that are locked and download programs which are currently recording on the Wiz, both of which will fail.

#### Sounds [^](#YARDWiz_Help.md) ####
  * _Play sound after download_: Play a sound after each download is complete.
  * _Sound file_: An 8 bit mono [.wav](http://en.wikipedia.org/wiki/WAV) file. Note: the .wav file will not play if it has metadata tags. You can export most sound formats (and remove metadata tags) to .wav format with [Audacity](http://audacity.sourceforge.net), an open source audio editor and recorder.

#### Debug [^](#YARDWiz_Help.md) ####
  * _Enable Debug Messages_: Enable debug logging which can assist resolving problems.
  * _Log File Path_: Full path to the debug log.

### Connecting to your Wiz [^](#YARDWiz_Help.md) ###
Enter your Beyonwiz device in the _Wiz server_: box in one of the following formats:
  * IP:port (e.g. 192.168.0.5:5678)
  * IP (port will default to 49152)
  * device name (e.g. LoungeWiz).
If you leave this field blank and click the Connect button or press Enter, YARDWiz will try to discover your Beyonwiz. YARDWiz will connect automatically if only one Wiz is found, otherwise it will list the discovered Wizzes.

### Checking the recordings on your Wiz [^](#YARDWiz_Help.md) ###
Select File->Check Recordings, this will do some basic consistency checks of recordings on your Wiz. Note: this will take a while, depending on how many recordings there are on your Wiz.  Paraphrased from the getWizPnP documentation:

> _Perform some basic consistency checks on the recordings on the Beyonwiz, indicating missing and misnamed (in some instances) header files, and checking that the sizes of the header files are correct. Also check that all recording data files mentioned in the header files are on the Beyonwiz._

> _Specifically:_
    * _Checks that the main header file exists (if one is expected) and that it is the correct size, but it cannot distinguish between a completely missing recording folder and a folder that is missing its header file._
    * _Checks that the trunc header file exists (if one is expected) and that it is a valid size, and whether it is present but under a known incorrect name._
    * _Checks that the stat header file exists (if one is expected) and that it is the correct size, and whether it is present but under a known incorrect name._
    * _Checks that the data file indicated by each trunc file entry is large enough to contain tha span of data indicated in the enrty. Makes no attempt to check the contents of the data files._

### Downloading a recording [^](#YARDWiz_Help.md) ###
You can download or queue one or more recordings by selecting them in the program list and clicking _Download now_ or _Queue for download_ in the right-click menu. You can also add a program to the queue by double-clicking it.  Programs may be downloaded in [TS](http://en.wikipedia.org/wiki/MPEG_transport_stream) (`*`.ts) or Beyonwiz [TVWIZ](http://www.openwiz.org/wiki/Recorded_Files) format (`*`.tvwiz) format, just change the file type in the file dialog.   Note: see [Issue 19](http://code.google.com/p/yardwiz/issues/detail?id=19) if downloads fail even after successfully listing when connecting via device name.

### Playing a recording [^](#YARDWiz_Help.md) ###
_New in YARDWiz 0.4.2_

If you have [VLC](http://www.videolan.org) installed, you can also play a recording directly without saving it to a filepath.  To do this, connect to your Beyonwiz device and list recordings. Right-click a recording and select "Play in VLC" from the context menu.  If you have set the [File #YARDWiz\_preferences](Temporary.md) preference, the recording will be downloaded to a temporary file and removed after you close VLC, otherwise it will be streamed directly to VLC. When streaming directly to VLC, you won't be able to pause or rewind the recording.

If you have successfully installed VLC and the "Play in VLC" context menu item is not enabled, YARDWiz may not be able to find the VLC executable.  YARDWiz first searches the directories in the "PATH" environment variable and finally checks '%ProgramFiles%\VideoLAN\VLC' and '%ProgramFiles(x86)%\VideoLAN\VLC'. If you have installed VLC to a non-standard path, you may need to add the VLC directory to your "PATH". See [setting environment variables](http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/sysdm_advancd_environmnt_addchange_variable.mspx?mfr=true) for more help (for Windows XP, but also applies to later Windows versions).

_New in YARDWiz 0.3.2_

If you have [VLC](http://www.videolan.org) installed, you can also play a recording as it downloads by clicking the VLC icon - ![http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/vlc.png](http://yardwiz.googlecode.com/svn/trunk/yardwizgui/icons/vlc.png)

If you have successfully installed VLC and the VLC icon is not enabled in YARDWiz when downloading a recording, YARDWiz may not be able to find the VLC executable.  YARDWiz first searches the directories in the "PATH" environment variable and finally checks '%ProgramFiles%\VideoLAN\VLC' and '%ProgramFiles(x86)%\VideoLAN\VLC'. If you have installed VLC to a non-standard path, you may need to add the VLC directory to your "PATH". See [setting environment variables](http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/sysdm_advancd_environmnt_addchange_variable.mspx?mfr=true) for more help (for Windows XP, but also applies to later Windows versions).

**Note**: playing in VLC works best when downloading in TS format. It can be a bit flaky when downloading in TVWIZ format.

### Scheduling a recording for download [^](#YARDWiz_Help.md) ###
_New in YARDWiz 0.3.3_
You can schedule one or more recordings for download by selecting them in the program list and clicking _Schedule for Download..._ in the right-click menu. Programs may be downloaded in [TS](http://en.wikipedia.org/wiki/MPEG_transport_stream) (`*`.ts) or Beyonwiz [TVWIZ](http://www.openwiz.org/wiki/Recorded_Files) format (`*`.tvwiz). Once you have selected file names for each of the recordings, set the download date and time in the schedule dialog which appears. If you wish to cancel or modify the scheduled time, select _Scheduled Downloads_ from the _Tools_ menu.  Recordings are queued sequentially and whilst you may schedule multiple recordings, you may set only a single schedule date/time. You may add recordings to the schedule, even after the scheduled downloads have begun, however you can not remove recordings from the schedule.  You may cancel a schedule at any time, even whilst downloading from _Scheduled Downloads_ in the _Tools_ menu.

**Note:**
  * The scheduler is very basic and does _not_ make use of underlying OS scheduling functionality. The scheduler will only download your recordings if the YARDWiz instance that scheduled them is running. The computer and the PVR must also be running, there is no "wake up" functionality.
  * The scheduler is intended for unattended downloading. The progress bar and the 'Play in VLC' button will not be shown for scheduled downloads.  Post-download commands will still be run on completion of each scheduled download.

### Post-download processing [^](#YARDWiz_Help.md) ###
You can specify a command to run after a recording is downloaded (including scheduled downloads) via the [settings](#YARDWiz_settings.md). You can pass the full filepath and/or download directory to the command as an argument using the %F and/or %D modifiers respectively.

You might use the post download command to process the downloaded TS file with [ProjectX](http://www.openwiz.org/wiki/ProjectX) and [AVIDemux](http://avidemux.sourceforge.net).

### Deleting a recording [^](#YARDWiz_Help.md) ###
The delete operation uses an undocumented WizPnP feature which has a number of consequences. Note the following from prl's [getWizPnP](http://www.openwiz.org/wiki/GetWizPnP_Release) documentation:
> _A recording can be deleted while it is being played on the Beyonwiz. Normally, the playback will simply finish abruptly. The same happens if getWizPnP deletes a recording on the WizPnP server while another Beyonwiz is playing the recording remotely using WizPnP._

> _When a recording is deleted, the file player view won't be updated. Navigating in the file player, or exiting it and re-entering it does not update the view._

> _The WizPnP's index of recordings on the Beyonwiz doesn't get updated when the recording on the Beyonwiz is deleted. If you view the recordings on the Beyonwiz using WizFX, entries for deleted recordings appear in the WizFX list of recordings. These entries have no name, a date of 17/11/1858, and a size of 256kB. They can't be copied using WizFX. A recording deleted using getWizPnP on a Beyonwiz WizPnP server will appear normal in the file player on a Beyonwiz WizPnP client, but the recording cannot be played._

You can update the index on your Beyonwiz whilst in the file list by pressing the soundtrack button on the bottom right of your remote control (looks like a speaker with a question mark next to it).

### Converting from TVWIZ to TS [^](#YARDWiz_Help.md) ###
_New in YARDWiz 0.3.9_

Recordings downloaded in [TVWIZ](http://www.openwiz.org/wiki/Recorded_Files) format can be converted to [TS](http://en.wikipedia.org/wiki/MPEG_transport_stream) from the Tools menu.