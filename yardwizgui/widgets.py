# Copyright (c) 2011 Luke Pinner

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

class SortableListCtrl(wx.ListCtrl, ColumnSorterMixin,ListCtrlAutoWidthMixin):
    """A sortable wx.ListCtrl"""

    #Some default values, can be overridden
    dateformat='%x'     #Locale's appropriate date time format code.
    timeformat='%X'     #Locale's appropriate date time format code.
    datetimeformat='%c' #Locale's appropriate date time format code.
    decsep=locale.localeconv()['mon_decimal_point']

    #So the user can set the secondary sort column (to break ties)
    SecondarySortColumn=-1

    #So we can disable sorting if required
    _sortenabled=True
    
    def __init__(self, *args, **kwargs):
        self._args=args
        self._kwargs=kwargs
        wx.ListCtrl.__init__(self,*args,**kwargs)
        self.itemDataMap = ordereddict.OrderedDict()
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, 0)

        #As we override the default ColumnSorter
        self.DefaultSorter=ColumnSorterMixin.GetColumnSorter(self)

    def ClearAll(self,*args,**kwargs):
        wx.ListCtrl.ClearAll(self)
        self.itemDataMap = {}

    def InsertColumn(self,*args,**kwargs):
        wx.ListCtrl.InsertColumn(self,*args,**kwargs)
        self.SetColumnCount(self.GetColumnCount())

    def SetStringItem(self,item,col,value):
        self.itemDataMap[self.itemDataMap.keys()[item]][col]=value
        wx.ListCtrl.SetStringItem(self,item,col,value)

    def GetListCtrl(self):
        return self

    def Append(self,values):
        self.itemDataMap[self.GetItemCount()]=values
        wx.ListCtrl.Append(self,values)

    def GetColumnSorter(self):
        return self.CustomSorter

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
        CustomSorters=[self.NumSorter,self.DateSorter]
        for sorter in CustomSorters:  #Assume it's a float or date and fall back to the default sorter if this fails
            try:return sorter(key1, key2)
            except: pass
        return self.DefaultSorter(key1, key2)

    def SetSortEnabled(self, enabled=True):
        if enabled:
            self.Bind(wx.EVT_LIST_COL_CLICK, self._ColumnSorterMixin__OnColClick,self)
        else:
            #self.Unbind( wx.EVT_LIST_COL_CLICK ) #Unbinding doesn't work, need to stop event propagation
            self.Bind(wx.EVT_LIST_COL_CLICK, self.__OnColClickSortDisabled)

    def __OnColClickSortDisabled(self, evt):
        pass
    
class PropertyScrolledPanel(ScrolledPanel):
    def __init__(self, *args, **kwargs):
        self._config={}
        ScrolledPanel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetupScrolling()
        self.expanded=0
        self.panes=[]

    def OnPaneChanged(self, evt=None):
        self.Freeze()
        expanded=-1
        for i,pane in enumerate(self.panes):
            if pane.Expanded:
                if i==self.expanded:pane.Collapse()
                else:expanded=i
        self.expanded=expanded
        self.Layout()
        self.SetupScrolling()
        self.Thaw()

    def SetConfig(self, config, specs={}):
        #specs format is {section:{option:[optionvalue, optiontype, tooltip, [optionargs]]}
        self._config={}
        self.config=copy.deepcopy(config)
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
                        ctlOption=wx.DirPickerCtrl( pane, wx.ID_ANY, val, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE|wx.DIRP_USE_TEXTCTRL )
                    elif ctrl=='file':
                        if args:ext=args[0]
                        else:ext='*.*'
                        ctlOption=wx.FilePickerCtrl(pane, wx.ID_ANY, val, title, ext, wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_USE_TEXTCTRL )
                    else:continue
                    if tooltip:
                        tooltip=wx.ToolTip(tooltip)
                        txtOption.SetToolTip(tooltip)
                        ctlOption.SetToolTip(tooltip)
                    opts[option]=ctlOption
                    addrSizer.Add(txtOption, 0,wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 25)
                    addrSizer.Add(ctlOption, 0, wx.EXPAND)

            border = wx.BoxSizer()
            border.Add(addrSizer, 1, wx.EXPAND|wx.ALL, 5)
            pane.SetSizer(border)

            self.Sizer.Add(cp, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)

            self._config[section]=opts

        self.panes[0].Expand()
        self.SetupScrolling()

    def GetConfig(self, saved):
        if saved:
            for section in self._config:
                for option in self._config[section]:
                    try:value=str(self._config[section][option].GetValue())
                    except:value=self._config[section][option].GetPath()
                    self.config.set(section, option, value)
        return self.config



