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

import wx,time,locale
from wx.lib.mixins.listctrl import ColumnSorterMixin,ListCtrlAutoWidthMixin

class SortableListCtrl(wx.ListCtrl, ColumnSorterMixin,ListCtrlAutoWidthMixin):
    """A sortable wx.ListCtrl"""
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self,*args,**kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
        self.itemDataMap = {}

        #Some default values, can be overridden
        self.dateformat='%x'     #Locale's appropriate date time format code.
        self.timeformat='%X'     #Locale's appropriate date time format code.
        self.datetimeformat='%c' #Locale's appropriate date time format code.

        #As we override the default ColumnSorter
        self.DefaultSorter=ColumnSorterMixin.GetColumnSorter(self)

        #So the user can set the secondary sort column (to break ties)
        self.SecondarySortColumn=-1

    def InsertColumn(self,*args,**kwargs):
        wx.ListCtrl.InsertColumn(self,*args,**kwargs)
        ColumnSorterMixin.__init__(self, self.GetColumnCount())
        
    def GetListCtrl(self):
        return self

    def Append(self,values):
        self.itemDataMap[self.GetItemCount()]=values
        wx.ListCtrl.Append(self,values)
        
    def GetColumnSorter(self):
        return self.CustomSorter

    def SetSecondarySortColumn(self, col):
        self.SecondarySortColumn=col-1

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
    