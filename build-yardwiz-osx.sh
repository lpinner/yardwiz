#!/bin/bash
if [ -d /Volumes/yardwiz-trunk ]; then
  YWDIR=/Volumes/yardwiz-trunk
elif [ -d /Volumes/YARDWiz/yardwiz-trunk ]; then
  YWDIR=/Volumes/YARDWiz/yardwiz-trunk
elif [ -d /Volumes/Other/Development/YARDWiz/yardwiz-trunk ]; then
  YWDIR=/Volumes/Other/Development/YARDWiz/yardwiz-trunk
else
  echo "Unable to determine YARDWiz dir"
  exit 1
fi
cd ~
rm -rf YARDWiz-[0-9].[0-9].[0-9]*
cp $YWDIR/dist/YARDWiz-[0-9].[0-9].[0-9].zip .
unzip YARDWiz-[0-9].[0-9].[0-9]*.zip
cd YARDWiz-[0-9].[0-9].[0-9]
cp $YWDIR/buildfiles/getWizPnP-OSX getWizPnP
chmod +x getWizPnP
/Library/Frameworks/Python.framework/Versions/2.7/bin/python setup.py py2app
cp dist/YARDWiz-[0-9].[0-9].[0-9]*.dmg $YWDIR/dist/
