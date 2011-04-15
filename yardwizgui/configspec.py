devicetooltip='Enter your Beyonwiz device in one of the following formats:\n\t- IP:port (e.g. 192.168.0.5:5678)\n\t- IP (port will default to 49152)\n\t- device name (e.g. Lounge Wiz)'
postdownloadtooltip='Usage: somecommand [%F] [%D]\n\tOptional %F and/or %D parameters are replaced by the filepath or the directory name of the file being downloaded\n# is the comment character, anything after this will be ignored'
dateformattooltip='The date format string is as per the python date/time format codes listed at:\nhttp://docs.python.org/library/time.html#time.strftime'
soundstooltip='Sound files must be 8 bit mono WAV format with no metadata tags.'
deletetooltip='Confirm that you really wish to delete a recording from your Beyonwiz.'
quicklistingtooltip='Warning: enabling quick listing will show any files that have been deleted from your Wiz and will allow you to attempt to delete recordings that are locked, which will fail.'
configspec={
    'Settings':{
        'device':['Device', 'str', devicetooltip],
        'lastdir':['Last directory', 'dir'],
        'postdownloadcommand':['Post download command', 'str', postdownloadtooltip],
        'display_dateformat':['Date format for display','str', dateformattooltip],
        'filename_dateformat':['Date format for filenames', 'str', dateformattooltip],
        'confirmdelete':['Confirm delete', 'bool'],
        'quicklisting':['Enable quick listing', 'bool',quicklistingtooltip ]
        },
    'Sounds':{ #This will need to be rewritten if we add more sounds...
        'playsounds':['Play sound after download', 'bool'],
        'downloadcomplete':['Sound file (.wav)',  'file', soundstooltip, ['*.wav']]
     },
    'Window':{
        'xsize':['Width', 'str'],
        'ysize':['Height', 'str'],
        'xmin':['Left', 'str'],
        'ymin':['Top', 'str'],
     }
}
