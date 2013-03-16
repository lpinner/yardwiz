cachedevicetooltip='Cache Beyonwiz device addresses'
devicetooltip='Enter your Beyonwiz device in one of the following formats:\n\t- IP:port (e.g. 192.168.0.5:5678)\n\t- IP (port will default to 49152)\n\t- device name (e.g. Lounge Wiz)'
autoconnecttooltip='Automatically list recordings on startup.'
onselecttooltip='Automatically list recordings after selecting a device from the "Wiz Server:" list.'
tstooltip='Default download format: TS (checked) TVWIZ (unchecked).\nYou can also select the format for each download in the file  "save as" dialog.'
postdownloadtooltip='Usage: somecommand [%F] [%D]\n\tOptional %F and/or %D parameters are replaced by the filepath or the directory name of the file being downloaded\n# is the comment character, anything after this will be ignored'
dateformattooltip='The date format string is as per the python date/time format codes listed at:\nhttp://docs.python.org/library/time.html#time.strftime'
wizpnpdelaytooltip='Adds delays between HTTP requests, which may help with download failures'
wizpnptimeouttooltip='On Windows 7, sometimes getWizPnP fails to discover Beyonwiz servers on the network. The reason is not clear, but it can sometimes be worked around by specifying a larger timeout'
soundstooltip='Sound files must be 8 bit mono WAV format with no metadata tags.'
deletetooltip='Confirm that you really wish to delete a recording from your Beyonwiz.'
quicklistingtooltip='Note: enabling quick listing will show any files that have been deleted from your Wiz and will allow you to attempt to delete recordings that are locked, which will fail.'
fadetooltip='Use fade in/out effects.'
logfiletooltip='The path of the current log file. Changing this has no effect.'
vlctooltip='For more, see: http://wiki.videolan.org/VLC_command-line_help'
streamtooltip='Using a temporary file when playing in VLC allows you to pause and rewind.'
retriestooltip='Number of times to retry a failed download.'

configspec={
    'Settings':{
        'cachedevice':['Remember device addresses', 'bool',cachedevicetooltip],
        'device':['Device', 'str', devicetooltip],
        'autoconnect':['Auto list recordings', 'bool',autoconnecttooltip],
        'onselect':['Auto update recordings', 'bool',onselecttooltip],
        'lastdir':['Last directory', 'dir'],
        'tsformat':['Default to TS format for downloads', 'bool',tstooltip],
        'postdownloadcommand':['Post download command', 'str', postdownloadtooltip],
        'vlcargs':['VLC commandline arguments', 'str',vlctooltip],
        'tempfile':['Use temp file when playing', 'bool',streamtooltip],
        'display_dateformat':['Date format for display','str', dateformattooltip],
        'filename_dateformat':['Date format for filenames', 'str', dateformattooltip],
        'confirmdelete':['Confirm delete', 'bool'],
        'quicklisting':['Enable quick listing', 'bool',quicklistingtooltip ],
        'showtooltips':['Show ToolTips', 'bool'],
        'retries':['Retry failed downloads', 'str',retriestooltip],
        'delete':['Delete failed downloads', 'bool']
        },
    'getWizPnP':{ #This will only show on Windows
        'delay':['HTTP request delay', 'str',wizpnpdelaytooltip],
        'wizpnptimeout':['WizPnP Search Timeout', 'str', wizpnptimeouttooltip]
     },
    'Sounds':{ #This will need to be rewritten if we add more sounds...
        'playsounds':['Play sound after download', 'bool'],
        'downloadcomplete':['Sound file (.wav)',  'file', soundstooltip, ['*.wav']]
     },
    'Window':{
        'fade':['Fade', 'bool',fadetooltip],
        'xsize':['Width', 'str'],
        'ysize':['Height', 'str'],
        'xmin':['Left', 'str'],
        'ymin':['Top', 'str']
     },
    'Debug':{
        'debug':['Enable debug messages',  'bool'],
        'logfile':['Log file path',  'str', logfiletooltip]
     }
}
