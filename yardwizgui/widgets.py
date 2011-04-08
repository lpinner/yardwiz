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

import wx,time,locale,ordereddict,sys
from wx.lib.mixins.listctrl import ColumnSorterMixin,ListCtrlAutoWidthMixin
from wx.gizmos import TreeListCtrl

iswin=sys.platform[0:3] == "win"
class SortableListCtrl(wx.ListCtrl, ColumnSorterMixin,ListCtrlAutoWidthMixin):
    """A sortable wx.ListCtrl"""

    #Some default values, can be overridden
    dateformat='%x'     #Locale's appropriate date time format code.
    timeformat='%X'     #Locale's appropriate date time format code.
    datetimeformat='%c' #Locale's appropriate date time format code.

    #So the user can set the secondary sort column (to break ties)
    SecondarySortColumn=-1

    def __init__(self, *args, **kwargs):
        self._args=args
        self._kwargs=kwargs
        wx.ListCtrl.__init__(self,*args,**kwargs)
        self.itemDataMap = {}
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
        val1 = float(self.itemDataMap[key1][col])
        val2 = float(self.itemDataMap[key2][col])
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

class PropertyTreeList( TreeListCtrl):
    def __init__(self,*args,**kwargs):
        TreeListCtrl.__init__(self,*args,**kwargs)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnTreeSelChanged)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind( wx.EVT_TREE_END_LABEL_EDIT, self.OnTreeEndLabelEdit )
        self.Bind( wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnTreeBeginLabelEdit )
        self.Bind( wx.EVT_LEFT_UP, self.OnLeftUp )
        self.Bind( wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnTreeBeginLabelEdit )

    def SetConfig(self,config):
        self.config=config
        self.AddColumn('Property')
        self.AddColumn('Value')
        self.root = self.AddRoot("root")
        sections = config.sections()
        for section in sections:
            sec=self.AppendItem(self.root, section)
            options = config.options(section)
            for option in options:
                opt=self.AppendItem(sec, option)
                self.SetItemText(opt, config.get(section, option), 1)
        self.OnSize()

    def OnSize(self, event=None):
        if self.GetColumnCount() > 0:
            width=self.GetSizeTuple()[0] / 2.0
            for col in [0,1]:
                self.GetColumn(col).SetWidth(width)
            self.Refresh()
        if event:event.Skip()

    def OnLeftUp( self, event ):
       #Col 1 doesn't like firing OnTreeSelChanged, so
       #trap clicks and force it so the column becomes editable
        x,y = event.GetPosition()
        minx=min(x,50)#self.GetColumnWidth(1)/2)
        item = self.HitTest((minx,y))[0]
        if item.IsOk():
            self.OnTreeSelChanged(item=item)
            self.SelectItem(item)
        event.Skip()

    def OnTreeSelChanged(self, event=None, item=None):
        if event:item=event.GetItem()
        if not item:return
        if self.HasChildren(item):
            self.SetColumnEditable(1,False)
            pass
        else:
            self.SetColumnEditable(1,True)
            self.EditLabel(item, 1)
        if event:event.Skip()

    def OnTreeBeginLabelEdit( self, event ):
        event.Skip()

    def OnTreeEndLabelEdit( self, event ):
        #Don't know why, but column 0 was getting updated instead of column 1
        #The code below works around that
        item=event.GetItem()
        section=self.GetItemText(self.GetItemParent(item),0)
        option=self.GetItemText(item, 0)
        value=event.Label
        self.SetItemText(item, option, 0) #Reset column 0
        self.SetItemText(item, value, 1) #Explicitly set column 1
        self.config.set(section, option, value)
        event.Veto() #Cancel the edit as we've already written the new value to column 1
