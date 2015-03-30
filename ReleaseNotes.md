# Release notes #
## 1.0 ##
### New in 1.0 ###
  * I think it's time to call this thing version 1!

### Fixed in 1.0 ###
  * Resolves Issue #41

## 0.4.6 ##
### Fixed in 0.4.6 ###
  * Fix truncated filename suggestions in OS X file picker dialog Issue #40.
  * Fix crash on startup on fresh installs.

## 0.4.5 ##
### New in 0.4.5 ###
  * Show error messages in a dialog box as well as in the log tab.

### Fixed in 0.4.5 ###
  * Fix sort after delete.
  * Fix post download command
  * Flush deleted and downloaded cache immediately
  * Fix path in Trunc class
  * Fix downloaded cache getting cleared when unable to connect
  * Fix GUI when deletes fail
  * Fix getting recording date where index doesn't contain a date

## 0.4.4 ##
### Fixed in 0.4.4 ###
  * Fix program list sorting.
  * Fix missing program info.

## 0.4.3 ##
### New in 0.4.3 ###
  * Add getWizPnP --retry option to retry downloads automatically if they fail.
  * Add option to disable WizPnP server address caching.
  * Replace separate Play and Pause buttons with a single button that switches between Play/Pause.
  * Add --delay and --wizpnpTimeout getWizPnP options for Windows.
  * Update getWizPnP to 0.5.4 in downloads that include a compiled version.

### Fixed in 0.4.3 ###
  * Fix Wiz Server combobox size and font.
  * Fix bug setting preferences when GetWizPnP < 0.5.3 (http://www.beyonwiz.com.au/phpbb2/viewtopic.php?t=6351&postdays=0&postorder=asc&start=345=96362)
  * Don't use 0.0 speeds when calculating estimated download time.
  * Fix Unicode errors
  * Fix WizPnP server discovery loop bug
  * Fix segfault on Kubuntu 12.04
  * Resize Wiz Server combo box after discover
  * Fix OSError: [17] File exists when running setup.py install on linux with an existing installation
  * Fix crash when saving preferences and VLC is not installed.
  * Fix logfile display in class Stderr on OSX
  * Move '.' to end of path for security
  * Hardcode VLC path on OSX
  * Fix multiple --no-video-title arg when calling VLC
  * Create a limited environment for getWizPnP with HOME/APPDATA stripped out/empty GETWIZPNPCONF environment variable (getWizPnP 0.5.4+) so .getwizpnp/getwizpnp.conf doesn't get used. Resolves Issue #2.

## 0.4.2 ##
### New in 0.4.2 ###
  * Add "Play in VLC" item to programs menu.
  * Add option to play in VLC with or without a temporary file (getWizPnP 0.5.3+ only).
  * Add getWizPnP version info to Help->About... dialog.
  * Added auto list recordings on startup and on Wiz server list selection change options.
  * Make discovered device IP address visible in combobox.
  * Reselect previously selected device on preference save.
  * Move "Check recordings..." to Tools menu and add feedback when recordings are being checked.
  * Add feedback when recordings are being deleted.
  * Update getWizPnP to 0.5.3 in downloads that include a compiled version.

### Fixed in 0.4.2 ###
  * Fix sort bug after deleting when quick listing is enabled.
  * Handle exception when file dialog is cancelled.
  * Don't run post-download command if scheduled download is cancelled.
  * Don't allow downloading into an existing tvwiz dir.
  * Fix incorrect testing of file size (megabytes v.s mebibytes).
  * Fix bug when delete from Wiz fails.
  * Fix bug when download fails because of Wiz error.
  * Fix incorrect download complete message when download fails at the Wiz end.
  * Fix bug when delete from file system fails .
  * Catch 'Copy failed: Forbidden' getWizPnP response .
  * Advise user to rename a recording on the Wiz when multiple recordings with the same index exist.
  * Fix not listing recording name when there's a missing data file error .
  * Open logfile in "w" mode, not "wb" so line end is cr/lf not lf on Windows and it can be read properly in notepad.exe
  * Add better error handling in TVWiz to TS conversion.
  * Fix check recording menu item enabling bug.
  * Stop auto scrolling when selecting a control in the Tools->Options dialog.
  * Fix bug setting tooltip on option label in the Tools->Options dialog so both option label and option value display tooltips.
  * Symlink yardwiz.desktop to /usr/share/applications so it shows up in the Ubuntu Unity dash.
  * Include psutil in py2exe build. Resolves Issue #3.

---


## 0.4.1 ##
### Fixed in 0.4.1 ###
  * Handle multiple instant recording bug when quick listing is disabled.
  * Fix crash when rescheduling recordings previously scheduled for download.
  * Make log file unique

## 0.4.0 ##
### Fixed in 0.4.0 ###
  * Implement threading event to cancel TVWIZ to TS conversion on exit so as not to hang.
  * Conversion folder dialog now defaults to the last used directory from the config settings.
  * Fixed bug with [multiple instant recordings](http://www.beyonwiz.com.au/phpbb2/viewtopic.php?p=95311=95311).
  * Fixed hard crash (YARDWiz.exe has stopped working) on Windows.
  * Worked around segfault on Ubuntu 11.10 caused by wx.FileDialog

## 0.3.9 ##
### New in 0.3.9 ###
  * Added function to convert TVWIZ format to TS.

## 0.3.8 ##
### Fixed in 0.3.8 ###
  * Major rewrite of Beyonwiz device handling, multiple Beyonwiz device names in any of the accepted formats now handled correctly.
  * Fix to find the VLC executable on 64bit Windows (0.3.8.1).

## 0.3.7 ##
### Fixed in 0.3.7 ###
  * Fixed bug in downloads/deletions tracking.

## 0.3.6 ##
### New in 0.3.6 ###
  * Remember deletions and downloads between sessions.

### Fixed in 0.3.6 ###
  * Fixed unicode [issue](http://www.beyonwiz.com.au/phpbb2/viewtopic.php?p=92374=92374).
  * Make sure font colour in various widgets is the same when using a dark Linux theme.

## 0.3.5 ##
### Fixed in 0.3.5 ###
  * Fix the positioning of the progress bar and text.

## 0.3.4 ##
### Fixed in 0.3.4 ###
  * Clean up the GUI including standardising application fonts and moving the progress bar to the same level as the buttons.
  * Handle NoPyApp exception on close.
  * Better checking if the PVR is online (use socket connection instead of ping).

## 0.3.3 ##
### New in 0.3.3 ###
  * Added basic download scheduler.
  * Enabled downloads in .tvwiz format Issue #23.

### Fixed in 0.3.3 ###
  * Removed Beyonwiz subfolder names from downloaded filenames Issue #24.
  * Worked around column autosize bug truncating long titles on Win XP Issue #25.

## 0.3.2 ##
### New in 0.3.2 ###
  * getWizPnP updated to 0.5.2 in Windows, OSX and Linux
  * Added functionality to play currently downloading recording in VLC (http://www.videolan.org/vlc). Requires VLC to be installed separately.

### Fixed in 0.3.2 ###
  * Fixed bug with 9 decimal places after seconds in estimated download time remaining.
  * Worked around Issue #20 - YARDWiz <=v3.1 never finishes listing recordings
  * Worked around Issue #21 - YARDWiz hangs on completion of downloads on OSX
  * Other minor bug fixes.

## 0.3.1 ##
### New in 0.3.1 ###
  * getWizPnP updated to 0.5.1 in Windows, OSX and Linux
  * Re-added standalone OSX app
  * Added Linux versions which include a 32 or 64 bit compiled version of getWizPnP
  * Implemented the getWizPnP --check function
  * Added estimated download time remaining
  * Added ability to remember multiple wizzes, not just the last one used.
  * Added check to see if Wiz is online before attempting to connect. Doesn't work if connecting via typed in device name.
  * Set WM\_CLASS on Linux so app name is used by window managers.
  * Add some transparency bling in open/close and when about/preferences dialogs are shown. Doesn't work on Linux running compiz v.9x
  * Enable stop button when a download is paused.
  * Checks for wxPython>=2.8 in setup.py install on Linux

### Fixed in 0.3.1 ###
  * Fixed bug setting ip & port
  * Fixed device = None bug
  * Fixed debug output on OSX
  * Fixed ConfigParser issue on Ubuntu 10.04LTS
  * Fixed hang on application exit in Linux when a download is paused.
  * Worked around Issue #19 - Downloads may fail with the getWizPnP error - "Search for WizPnP devices failed".

## 0.3.0 ##
### New in 0.3.0 ###
  * Added debug output as a preference

### Changes in 0.3.0 ###
  * Removed standalone OSX YARDWiz.app as the compiled getWizPnP only runs on OSX 10.6.2

### Bugs in 0.3.0 ###
  * Downloads may fail with the getWizPnP error - "Search for WizPnP devices failed" when connecting via a device name, even after listing programs succeeded using that device name.  This has only occurred on one Win 7 Ultimate PC that I'm aware of and the issue does not occurr on the same users Win XP PC.
  * Workaround (thanks to netmask from the Beyonwiz forum): connect using IP or IP:Port syntax.

### Fixed in 0.3.0 ###
  * Fixed bug on linux where getWizPnP wouldn't terminate i.e pausing or stopping a download.
  * Fix to enable running on Python 2.7
  * Fixed bug with non-ASCII filenames
  * Fixed stdin bug when running under pythonw
  * Fixed asynch issue when using default listing option

## 0.2.9 ##
### New in 0.2.9 ###
  * A standalone YARDWiz.app which includes a compiled version of getWizPnP 0.4.3a is available for OSX

### Changes in 0.2.9 ###
  * Better behaviour of threads when closing the application
  * Minor tweaks for OSX

## 0.2.8 ##
### Fixed in 0.2.8 ###
  * Resolves Issue #16
  * Resolves Issue #17
  * Minor tweaks for OSX

## 0.2.7 ##
### New in 0.2.7 ###
  * Improved setup.py, creates Linux Gnome Menu launcher and Windows Start Menu short when installing from source.
### Fixed in 0.2.7 ###
  * Close the GUI quicker instead of becoming unresponsive when exiting the application while connecting or downloading.
  * Get install paths properly instead of guessing them (when installing from source).

## 0.2.6 ##
### New in 0.2.6 ###
  * Added link to online help.
### Fixed in 0.2.6 ###
  * Fixes issue with GUI becoming unresponsive when deleting Issue #14
  * Fixes issue with GUI appearing offscreen Issue #15

## 0.2.5 ##
### Fixed in 0.2.5 ###
  * Fixes issue with quicklisting where downloading before program info is updated causes an error.

## 0.2.4 ##
### New in 0.2.4 ###
  * Enabled quick listing of recordings as a non-default option.
### Fixed in 0.2.4 ###
  * Minor tweaks and bugfixes

## 0.2.3 ##
### New in 0.2.3 ###
  * Added About and Preferences dialogs
  * Added option to specify a command to be run after a download is complete
  * Added option to play a sound after a download is complete
### Fixed in 0.2.3 ###
  * Resolved Issue #4
  * Minor tweaks and bugfixes

## 0.2.2 ##
### New in 0.2.2 ###
  * Added recursive folders listing
### Fixed in 0.2.2 ###
  * Fixed the Wiz server box not responding to keyboard inputs after connect button clicked
  * Fixed the failure to delete if IP:port or IP address is used to connect

## 0.2.1 ##
### Fixed in 0.2.1 ###
  * Fixed the accidental moving of the Log control to the Queue tab

## 0.2.0 ##
### New in 0.2.0 ###
  * Added Wiz device discovery
  * Added ability to delete recordings on the Wiz
### Fixed in 0.2.0 ###
  * Fixed setup.py for installing from source
  * Worked around issue with program list where typing jumps to matching value in channel column rather than title column, by moving title to first column
  * Modified application colours

## 0.1.2 ##
### New in 0.1.2 ###
  * Included a NSIS compiled Windows installer.

## 0.1.1 ##
### New in 0.1.1 ###
  * Included a PY2EXE compiled Windows executable.

## 0.1.0 ##
Initial release