# Copyright (c) 2015 Luke Pinner

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''Custom widgets'''

import wx,time,locale,ordereddict,sys, copy
iswin=sys.platform[0:3] == "win"
locale.setlocale(locale.LC_ALL,'')

from wx.lib.mixins.listctrl import ColumnSorterMixin,ListCtrlAutoWidthMixin
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.masked import TimeCtrl,EVT_TIMEUPDATE
from events import *
import datetime

class DateTimeCtrl(wx.Panel):
    def __init__(self, parent=None, id=wx.ID_ANY, value=None):

        wx.Panel.__init__(self, parent, id)

        if value is None:value=wx.DateTime_Now()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        self.dpc = wx.GenericDatePickerCtrl(self,  dt=value,
                                                 style = wx.DP_DROPDOWN|
                                                 wx.DP_SHOWCENTURY|
                                                 wx.DP_ALLOWNONE )

        self.dpc.SetSizeHintsSz( wx.Size( 120,-1 ), wx.DefaultSize )
        h = self.dpc.GetSize().height

        self.tc = wx.lib.masked.TimeCtrl( self, -1,value, wx.DefaultPosition , (-1,h),
                                          wx.TE_PROCESS_TAB|self.dpc.GetBorder(),
                                          display_seconds=False, useFixedWidthFont=False)

        self.tc.SetFont(self.dpc.GetFont())
        self.tc.SetForegroundColour(self.dpc.GetForegroundColour())

        sb = wx.SpinButton( self, -1, wx.DefaultPosition, (-1,h), wx.SP_VERTICAL )
        self.tc.BindSpinButton( sb )

        sizer.Add(self.dpc, 0, wx.ALIGN_CENTER)
        sizer.Add(self.tc, 0, wx.ALIGN_CENTER)
        sizer.Add(sb, 0, wx.ALIGN_CENTER)

        self.Bind(wx.EVT_DATE_CHANGED, self._OnDateTimeChanged, self.dpc)
        self.Bind(wx.lib.masked.EVT_TIMEUPDATE, self._OnDateTimeChanged, self.tc )

        self._OnDateTimeChanged()

    def GetValue( self):
        return self._dt

    def SetValue( self,dt):
        self._dt=dt
        self.dpc.SetValue(dt)
        self.tc.SetValue(dt)

    def _OnDateTimeChanged( self, *args,**kwargs):
        dt=self.dpc.GetValue()
        ti=self.tc.GetValue(as_wxDateTime=True)
        dt.Hour=ti.Hour
        dt.Minute=ti.Minute
        dt.Second=ti.Second
        self._dt=dt
        evt = DateTimeUpdated(wizEVT_DATETIMEUPDATED, -1, self._dt)
        try:wx.PostEvent(self.parent, evt)
        except:pass #we're probably exiting

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    """A wx.ListCtrl that auto-sizes the last column"""
    def __init__(self, *args, **kwargs):
        self._args=args
        self._kwargs=kwargs
        wx.ListCtrl.__init__(self,*args,**kwargs)
        ListCtrlAutoWidthMixin.__init__(self)

class SortableListCtrl(wx.ListCtrl, ColumnSorterMixin,ListCtrlAutoWidthMixin):
    """A sortable wx.ListCtrl"""

    #Some default values, can be overridden
    dateformat='%x'     #Locale's appropriate date time format code.
    timeformat='%X'     #Locale's appropriate date time format code.
    datetimeformat='%c' #Locale's appropriate date time format code.
    decsep=locale.localeconv()['mon_decimal_point']

    #So the user can set the secondary sort column (to break ties)
    SecondarySortColumn=-1

    def __init__(self, *args, **kwargs):
        self._args=args
        self._kwargs=kwargs

        #So we can disable sorting if required
        self._sortenabled=True

        wx.ListCtrl.__init__(self,*args,**kwargs)
        self.itemDataMap = ordereddict.OrderedDict()
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, 0)

        #As we override the default ColumnSorter
        self.DefaultSorter=self.ColumnSorter

    def ClearAll(self,*args,**kwargs):
        wx.ListCtrl.ClearAll(self)
        self.itemDataMap = {}

    def InsertColumn(self,*args,**kwargs):
        wx.ListCtrl.InsertColumn(self,*args,**kwargs)
        self.SetColumnCount(self.GetColumnCount())

    def Append(self,items):
        for itemdata in items:
            values=items[itemdata]
            self.itemDataMap[itemdata]=values
            wx.ListCtrl.Append(self,values)

            for col in range(self.GetColumnCount()):
                cwidth=self.GetColumnWidth(col)
                hwidth=self.HeaderWidths[col]
                twidth = self.GetTextExtent(values[col])[0]+10
                self.SetColumnWidth(col,max([cwidth,hwidth,twidth]))

    def DeleteItem(self,item):
        del self.itemDataMap[self.GetItemData(item)]
        wx.ListCtrl.DeleteItem(self,item)

    def SetStringItem(self,item,col,value):
        self.itemDataMap[self.itemDataMap.keys()[item]][col]=value
        wx.ListCtrl.SetStringItem(self,item,col,value)

        cwidth=self.GetColumnWidth(col)
        hwidth=self.HeaderWidths[col]
        twidth = self.GetTextExtent(value)[0]+15

        self.SetColumnWidth(col,max([cwidth,hwidth,twidth]))

    def GetListCtrl(self):
        return self

    def GetColumnSorter(self):
        return self.CustomSorter

    def ColumnSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]

        cmpVal = cmp(item1, item2)

        # If the items are equal then pick something else to make the sort value unique
        if cmpVal == 0:
            cmpVal = apply(cmp, self.GetSecondarySortValues(col, key1, key2))

        if ascending:
            return cmpVal
        else:
            return -cmpVal

    def SetSecondarySortColumn(self, col):
        self.SecondarySortColumn=col

    def GetSecondarySortValues(self, col, key1, key2) :
        #Default is to return orig keys
        val1,val2=key1,key2

        #Only if the user has set a SecondarySortColumn and it's not the current column
        if self.SecondarySortColumn > -1 and col!=self.SecondarySortColumn:
            #Assume it's a date/time/number and fall back to the actual values if this fails

            #Add in loop through CustomSorters...
            values=[self.NumValues,self.DateValues]
            for value in values:  #Assume it's a float or date and fall back to the default sorter if this fails
                try:
                    val1,val2= value(self.SecondarySortColumn,key1, key2)
                    #Make the secondary sort always sort ascending
                    asc = self._colSortFlag[col]
                    if asc: val1,val2 = min(val1,val2),max(val1,val2)
                    else:   val1,val2 = max(val1,val2),min(val1,val2)
                except:
                    if value==values[-1]:
                        val1 = self.itemDataMap[key1][self.SecondarySortColumn]
                        val2 = self.itemDataMap[key2][self.SecondarySortColumn]
                    else:pass
                else:break

            #Check for ties and return orig keys if required
            order = cmp(val1,val2)
            if order == 0:val1,val2=key1,key2

        return val1,val2

    def NumValues(self, col, key1, key2):
        val1 = float(self.itemDataMap[key1][col].replace(':',self.decsep))
        val2 = float(self.itemDataMap[key2][col].replace(':',self.decsep))
        return val1,val2

    def NumSorter(self, key1, key2):
        col = self._col
        asc = self._colSortFlag[col]
        val1,val2 = self.NumValues(col, key1, key2)
        order = cmp(val1, val2)
        if order == 0:
            order = cmp(*self.GetSecondarySortValues(col, key1, key2))
        if asc:return order
        else:return -order

    def DateValues(self, col, key1, key2):
        val1 = self.itemDataMap[key1][col]
        val2 = self.itemDataMap[key2][col]
        fmts=[self.dateformat,self.timeformat,self.datetimeformat]
        for fmt in fmts:
            try:
                date1 = time.mktime(time.strptime(val1,fmt))
                date2 = time.mktime(time.strptime(val2,fmt))
            except Exception, err:
                if fmt==fmts[-1]:raise
                else:pass
        return date1,date2

    def DateSorter(self, key1, key2):
        col = self._col
        asc = self._colSortFlag[col]
        date1,date2 = self.DateValues(col, key1, key2)
        order = cmp(date1, date2)
        if order == 0:
            order = cmp(*self.GetSecondarySortValues(col, key1, key2))
        if asc:return order
        else:return -order

    def CustomSorter(self, key1, key2):
        if self._sortenabled:
            CustomSorters=[self.NumSorter,self.DateSorter]
            for sorter in CustomSorters:  #Assume it's a float or date and fall back to the default sorter if this fails
                try:return sorter(key1, key2)
                except Exception as err: pass#print err# pass
            try:return self.DefaultSorter(key1, key2)
            except:
                raise

    def SetSortEnabled(self, enabled=True):
        self._sortenabled=enabled
        if enabled:
            self.Unbind( wx.EVT_LIST_COL_CLICK ) #Unbinding doesn't work, need to stop event propagation
            self.Bind(wx.EVT_LIST_COL_CLICK, self.__OnColClick)
        else:
            self.Unbind( wx.EVT_LIST_COL_CLICK ) #Unbinding doesn't work, need to stop event propagation
            self.Bind(wx.EVT_LIST_COL_CLICK, self.__OnColClickSortDisabled)

    def __OnColClickSortDisabled(self, evt):
        pass

    def __OnColClick(self, evt):
        oldCol = self._col
        self._col = col = evt.GetColumn()
        self._colSortFlag[col] = int(not self._colSortFlag[col])
        self.GetListCtrl().SortItems(self.GetColumnSorter())
        if wx.Platform != "__WXMAC__" or wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") == 1:
            self._ColumnSorterMixin__updateImages(oldCol)
        evt.StopPropagation()# Skip()
        self.OnSortOrderChanged()

class PropertyScrolledPanel(ScrolledPanel):
    def __init__(self, *args, **kwargs):
        self._config={}
        ScrolledPanel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.expanded=0
        self.panes=[]

        self._ScrollChildIntoView=ScrolledPanel.ScrollChildIntoView
        ScrolledPanel.ScrollChildIntoView=self.ScrollChildIntoView#Stop auto scrolling when selecting new control
        ScrolledPanel.OnChildFocus=self.OnChildFocus#Stop auto scrolling when selecting new control

    def OnChildFocus(self,*args,**kwargs):
        return None

    def ScrollChildIntoView(self,*args,**kwargs):
        return None

    def OnPaneChanged(self, evt=None):
        self.Freeze()
        expanded=-1
        for i,pane in enumerate(self.panes):
            if pane.Expanded:
                if i==self.expanded:pane.Collapse()
                else:expanded=i

        self.expanded=expanded

        self.Thaw()
        self.Layout()
        if not 'linux' in sys.platform:
            self._ScrollChildIntoView(self,self.panes[self.expanded])

    def SetConfig(self, config, specs={}):
        #specs format is {section:{option:[optionvalue, optiontype, tooltip, [optionargs]]}
        self._config={}
        #self.config=copy.deepcopy(config)
        self.config=copy.copy(config)
        sections = config.sections()
        for section in sections:
            cp = wx.CollapsiblePane(self,
                                    label=section,
                                    style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
            self.panes.append(cp)
            pane=cp.GetPane()
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
            addrSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=1)
            addrSizer.AddGrowableCol(1)
            options = config.options(section)
            opts={}
            for option in options:
                val=config.get(section, option)
                spec=specs.get(section, {}).get(option, [])
                if spec:
                    title, ctrl=spec[0:2]
                    if len(spec)>2:tooltip=spec[2]
                    else:tooltip=''
                    if len(spec)==4:args=spec[3]
                    else:args=[]
                    txtOption=wx.StaticText(pane, -1, title)
                    if ctrl=='str':
                        ctlOption=wx.TextCtrl( pane, wx.ID_ANY, val, wx.DefaultPosition, wx.DefaultSize, 0 )
                    elif ctrl=='bool':
                        ctlOption=wx.CheckBox( pane, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
                        if config.getboolean(section, option):
                            ctlOption.SetValue(True)
                    elif ctrl=='dir':
                        ctlOption=wx.DirPickerCtrl( pane, wx.ID_ANY, val, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE|wx.DIRP_USE_TEXTCTRL)
                    elif ctrl=='file':
                        if args:ext=args[0]
                        else:ext='*.*'
                        ctlOption=wx.FilePickerCtrl(pane, wx.ID_ANY, val, title, ext, wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_USE_TEXTCTRL)
                    else:continue
                    if tooltip:
                        txtOption.SetToolTip(wx.ToolTip(tooltip))
                        ctlOption.SetToolTip(wx.ToolTip(tooltip))

                    opts[option]=ctlOption
                    addrSizer.Add(txtOption, 0,wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 25)
                    addrSizer.Add(ctlOption, 0, wx.EXPAND)

            border = wx.BoxSizer()
            border.Add(addrSizer, 1, wx.EXPAND|wx.ALL, 5)
            pane.SetSizer(border)

            self.Sizer.Add(cp, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)

            self._config[section]=opts

        self.panes[0].Expand()
        self.panes[0].GetPane().SetFocus()
        self.Layout()
        self.SetupScrolling()

    def GetConfig(self, saved):
        if saved:
            for section in self._config:
                for option in self._config[section]:
                    try:value=str(self._config[section][option].GetValue())
                    except:value=self._config[section][option].GetPath()
                    self.config.set(section, option, value)
        return self.config



