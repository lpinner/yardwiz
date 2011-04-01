# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov 17 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

from widgets import SortableListCtrl
import wx
import wx.combo

###########################################################################
## Class GUI
###########################################################################

class GUI ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Yet Another Recording Downloader for the Wiz", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 300,300 ), wx.DefaultSize )
		self.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer1 = wx.FlexGridSizer( 1, 4, 0, 0 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer1.SetMinSize( wx.Size( -1,25 ) ) 
		self.lblServerCombo = wx.StaticText( self, wx.ID_ANY, u"Wiz server:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblServerCombo.Wrap( -1 )
		self.lblServerCombo.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_CAPTIONTEXT ) )
		
		fgSizer1.Add( self.lblServerCombo, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.LEFT|wx.TOP, 5 )
		
		self.cbxDevice = wx.combo.BitmapComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, "", wx.TE_PROCESS_ENTER ) 
		self.cbxDevice.SetToolTipString( u"Enter your Beyonwiz device in one of the following formats:\n\n    - IP:port (e.g. 192.168.0.5:5678)\n    - IP (port will default to 49152)\n    - device name (e.g. LoungeWiz)\n\nIf you leave this field blank and click the Connect button, YARDWiz will try to discover your Beyonwiz." )
		self.cbxDevice.SetMinSize( wx.Size( 250,-1 ) )
		
		fgSizer1.Add( self.cbxDevice, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		fgSizer1.AddSpacer( ( 16, 0), 1, 0, 5 )
		
		self.btnConnect = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnConnect.SetToolTipString( u"Connect to the WizPnp server\nand get recording information" )
		
		self.btnConnect.SetToolTipString( u"Connect to the WizPnp server\nand get recording information" )
		
		fgSizer1.Add( self.btnConnect, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
		
		bSizer4.Add( fgSizer1, 0, wx.EXPAND, 5 )
		
		self.lstPrograms = SortableListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.lstPrograms.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		self.lstPrograms.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.lstPrograms.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		self.mnuPrograms = wx.Menu()
		self.mitQueue = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Queue for download", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitQueue )
		self.mitQueue.Enable( False )
		
		self.mitDownload = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Download now", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitDownload )
		self.mitDownload.Enable( False )
		
		self.mnuPrograms.AppendSeparator()
		
		self.mitDelete = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Delete...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitDelete )
		self.mitDelete.Enable( False )
		
		
		bSizer4.Add( self.lstPrograms, 2, wx.ALL|wx.EXPAND, 5 )
		
		self.nbTabArea = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0|wx.TAB_TRAVERSAL )
		self.nbTabArea.SetMinSize( wx.Size( -1,100 ) )
		self.nbTabArea.SetMaxSize( wx.Size( -1,250 ) )
		
		self.nbtabLog = wx.Panel( self.nbTabArea, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.txtLog = wx.TextCtrl( self.nbtabLog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.VSCROLL )
		bSizer7.Add( self.txtLog, 1, wx.EXPAND, 0 )
		
		self.nbtabLog.SetSizer( bSizer7 )
		self.nbtabLog.Layout()
		bSizer7.Fit( self.nbtabLog )
		self.nbTabArea.AddPage( self.nbtabLog, u"Log", True )
		self.nbtabInfo = wx.Panel( self.nbTabArea, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.txtInfo = wx.TextCtrl( self.nbtabInfo, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.VSCROLL )
		bSizer8.Add( self.txtInfo, 1, wx.EXPAND, 0 )
		
		self.nbtabInfo.SetSizer( bSizer8 )
		self.nbtabInfo.Layout()
		bSizer8.Fit( self.nbtabInfo )
		self.nbTabArea.AddPage( self.nbtabInfo, u"Info", False )
		self.nbtabQueue = wx.Panel( self.nbTabArea, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.lstQueue = wx.ListCtrl( self.nbtabQueue, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT|wx.NO_BORDER )
		self.lstQueue.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.lstQueue.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		self.mnuQueue = wx.Menu()
		self.mitRemove = wx.MenuItem( self.mnuQueue, wx.ID_ANY, u"Remove from queue", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuQueue.AppendItem( self.mitRemove )
		self.mitRemove.Enable( False )
		
		self.mnuQueue.AppendSeparator()
		
		self.mitClearQueue = wx.MenuItem( self.mnuQueue, wx.ID_ANY, u"Clear queue", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuQueue.AppendItem( self.mitClearQueue )
		self.mitClearQueue.Enable( False )
		
		self.mitDownloadAll = wx.MenuItem( self.mnuQueue, wx.ID_ANY, u"Download queue", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuQueue.AppendItem( self.mitDownloadAll )
		self.mitDownloadAll.Enable( False )
		
		
		bSizer5.Add( self.lstQueue, 1, wx.EXPAND, 5 )
		
		self.nbtabQueue.SetSizer( bSizer5 )
		self.nbtabQueue.Layout()
		bSizer5.Fit( self.nbtabQueue )
		self.nbTabArea.AddPage( self.nbtabQueue, u"Queue", False )
		
		bSizer4.Add( self.nbTabArea, 1, wx.ALL|wx.EXPAND, 5 )
		
		gSizer21 = wx.GridSizer( 2, 1, 0, 0 )
		
		gSizer21.SetMinSize( wx.Size( -1,25 ) ) 
		gSizer2 = wx.GridSizer( 1, 6, 0, 0 )
		
		self.btnClearQueue = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnClearQueue.Enable( False )
		self.btnClearQueue.SetToolTipString( u"Clear all in queue" )
		
		self.btnClearQueue.Enable( False )
		self.btnClearQueue.SetToolTipString( u"Clear all in queue" )
		
		gSizer2.Add( self.btnClearQueue, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 5 )
		
		self.btnDownload = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnDownload.Enable( False )
		self.btnDownload.SetToolTipString( u"Download all in queue" )
		
		self.btnDownload.Enable( False )
		self.btnDownload.SetToolTipString( u"Download all in queue" )
		
		gSizer2.Add( self.btnDownload, 0, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		
		gSizer2.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.btnPlay = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnPlay.Enable( False )
		self.btnPlay.SetToolTipString( u"Resume download" )
		
		self.btnPlay.Enable( False )
		self.btnPlay.SetToolTipString( u"Resume download" )
		
		gSizer2.Add( self.btnPlay, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 5 )
		
		self.btnPause = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnPause.Enable( False )
		self.btnPause.SetToolTipString( u"Pause download" )
		
		self.btnPause.Enable( False )
		self.btnPause.SetToolTipString( u"Pause download" )
		
		gSizer2.Add( self.btnPause, 0, wx.TOP|wx.BOTTOM, 5 )
		
		self.btnStop = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnStop.Enable( False )
		self.btnStop.SetToolTipString( u"Cancel download and\ndelete downloaded file" )
		
		self.btnStop.Enable( False )
		self.btnStop.SetToolTipString( u"Cancel download and\ndelete downloaded file" )
		
		gSizer2.Add( self.btnStop, 0, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		gSizer21.Add( gSizer2, 1, 0, 5 )
		
		gSizer3 = wx.GridSizer( 1, 4, 0, 0 )
		
		self.gaugeProgressBar = wx.Gauge( self, wx.ID_ANY, 150, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.gaugeProgressBar.SetMinSize( wx.Size( 100,-1 ) )
		
		gSizer3.Add( self.gaugeProgressBar, 2, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.TOP, 5 )
		
		self.lblProgressText = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.lblProgressText.Wrap( -1 )
		self.lblProgressText.SetMinSize( wx.Size( 50,-1 ) )
		
		gSizer3.Add( self.lblProgressText, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.TOP|wx.LEFT, 10 )
		
		
		gSizer3.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.btnExit = wx.Button( self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		gSizer3.Add( self.btnExit, 2, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		gSizer21.Add( gSizer3, 1, wx.EXPAND, 5 )
		
		bSizer4.Add( gSizer21, 0, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer4 )
		self.Layout()
		bSizer4.Fit( self )
		self.StatusBar = self.CreateStatusBar( 3, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.StatusBar.SetFont( wx.Font( 8, 70, 90, 90, False, wx.EmptyString ) )
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_ACTIVATE, self.onActivateApp )
		self.Bind( wx.EVT_CLOSE, self.onCloseApp )
		self.cbxDevice.Bind( wx.EVT_KILL_FOCUS, self.cbxDevice_OnKillFocus )
		self.cbxDevice.Bind( wx.EVT_TEXT_ENTER, self.cbxDevice_OnTextEnter )
		self.btnConnect.Bind( wx.EVT_BUTTON, self.btnConnect_OnClick )
		self.lstPrograms.Bind( wx.EVT_LEFT_DCLICK, self.lstPrograms_OnDoubleClick )
		self.lstPrograms.Bind( wx.EVT_LIST_COL_CLICK, self.lstPrograms_OnColClick )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_DESELECTED, self.lstPrograms_OnDeselect )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, self.lstPrograms_OnMiddleClick )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.lstPrograms_OnRightClick )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_SELECTED, self.lstPrograms_OnSelect )
		self.Bind( wx.EVT_MENU, self.mitQueue_onSelect, id = self.mitQueue.GetId() )
		self.Bind( wx.EVT_MENU, self.mitDownload_onSelect, id = self.mitDownload.GetId() )
		self.Bind( wx.EVT_MENU, self.mitDelete_OnSelect, id = self.mitDelete.GetId() )
		self.lstQueue.Bind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, self.lstQueue_OnMiddleClick )
		self.lstQueue.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.lstQueue_OnRightClick )
		self.Bind( wx.EVT_MENU, self.mitRemove_OnSelect, id = self.mitRemove.GetId() )
		self.Bind( wx.EVT_MENU, self.mitClearQueue_OnSelect, id = self.mitClearQueue.GetId() )
		self.Bind( wx.EVT_MENU, self.mitDownloadAll_OnSelect, id = self.mitDownloadAll.GetId() )
		self.btnClearQueue.Bind( wx.EVT_BUTTON, self.btnClearQueue_OnClick )
		self.btnDownload.Bind( wx.EVT_BUTTON, self.btnDownload_OnClick )
		self.btnPlay.Bind( wx.EVT_BUTTON, self.btnPlay_OnClick )
		self.btnPause.Bind( wx.EVT_BUTTON, self.btnPause_OnClick )
		self.btnStop.Bind( wx.EVT_BUTTON, self.btnStop_OnClick )
		self.btnExit.Bind( wx.EVT_BUTTON, self.btnExit_onClick )
	
	def __del__( self ):
		# Disconnect Events
		self.Unbind( wx.EVT_ACTIVATE )
		self.Unbind( wx.EVT_CLOSE )
		self.cbxDevice.Unbind( wx.EVT_KILL_FOCUS, None )
		self.cbxDevice.Unbind( wx.EVT_TEXT_ENTER, None )
		self.btnConnect.Unbind( wx.EVT_BUTTON, None )
		self.lstPrograms.Unbind( wx.EVT_LEFT_DCLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_COL_CLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_DESELECTED, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_RIGHT_CLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_SELECTED, None )
		self.Unbind( wx.EVT_MENU, id = self.mitQueue.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitDownload.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitDelete.GetId() )
		self.lstQueue.Unbind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, None )
		self.lstQueue.Unbind( wx.EVT_LIST_ITEM_RIGHT_CLICK, None )
		self.Unbind( wx.EVT_MENU, id = self.mitRemove.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitClearQueue.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitDownloadAll.GetId() )
		self.btnClearQueue.Unbind( wx.EVT_BUTTON, None )
		self.btnDownload.Unbind( wx.EVT_BUTTON, None )
		self.btnPlay.Unbind( wx.EVT_BUTTON, None )
		self.btnPause.Unbind( wx.EVT_BUTTON, None )
		self.btnStop.Unbind( wx.EVT_BUTTON, None )
		self.btnExit.Unbind( wx.EVT_BUTTON, None )
	
	
	# Virtual event handlers, overide them in your derived class
	def onActivateApp( self, event ):
		event.Skip()
	
	def onCloseApp( self, event ):
		event.Skip()
	
	def cbxDevice_OnKillFocus( self, event ):
		event.Skip()
	
	def cbxDevice_OnTextEnter( self, event ):
		event.Skip()
	
	def btnConnect_OnClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnDoubleClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnColClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnDeselect( self, event ):
		event.Skip()
	
	def lstPrograms_OnMiddleClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnRightClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnSelect( self, event ):
		event.Skip()
	
	def mitQueue_onSelect( self, event ):
		event.Skip()
	
	def mitDownload_onSelect( self, event ):
		event.Skip()
	
	def mitDelete_OnSelect( self, event ):
		event.Skip()
	
	def lstQueue_OnMiddleClick( self, event ):
		event.Skip()
	
	def lstQueue_OnRightClick( self, event ):
		event.Skip()
	
	def mitRemove_OnSelect( self, event ):
		event.Skip()
	
	def mitClearQueue_OnSelect( self, event ):
		event.Skip()
	
	def mitDownloadAll_OnSelect( self, event ):
		event.Skip()
	
	def btnClearQueue_OnClick( self, event ):
		event.Skip()
	
	def btnDownload_OnClick( self, event ):
		event.Skip()
	
	def btnPlay_OnClick( self, event ):
		event.Skip()
	
	def btnPause_OnClick( self, event ):
		event.Skip()
	
	def btnStop_OnClick( self, event ):
		event.Skip()
	
	def btnExit_onClick( self, event ):
		event.Skip()
	

###########################################################################
## Class ConfirmDelete
###########################################################################

class ConfirmDelete ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Confirm Delete?", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer4 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer2 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.bmpIcon = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 32,32 ), 0 )
		fgSizer2.Add( self.bmpIcon, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
		
		self.lblQuestion = wx.StaticText( self, wx.ID_ANY, u"Do you really want to delete The following program/s?\n%s", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.lblQuestion.Wrap( -1 )
		fgSizer2.Add( self.lblQuestion, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		fgSizer4.Add( fgSizer2, 1, wx.EXPAND, 5 )
		
		self.chkShowAgain = wx.CheckBox( self, wx.ID_ANY, u"Do not ask next time", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.chkShowAgain, 0, wx.ALIGN_TOP|wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.lblReEnable = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblReEnable.Wrap( -1 )
		fgSizer4.Add( self.lblReEnable, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		DialogButtons = wx.StdDialogButtonSizer()
		self.DialogButtonsYes = wx.Button( self, wx.ID_YES )
		DialogButtons.AddButton( self.DialogButtonsYes )
		self.DialogButtonsNo = wx.Button( self, wx.ID_NO )
		DialogButtons.AddButton( self.DialogButtonsNo )
		DialogButtons.Realize();
		fgSizer4.Add( DialogButtons, 1, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 5 )
		
		self.SetSizer( fgSizer4 )
		self.Layout()
		fgSizer4.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.chkShowAgain.Bind( wx.EVT_CHECKBOX, self.chkShowAgainOnCheckBox )
		self.DialogButtonsNo.Bind( wx.EVT_BUTTON, self.DialogButtonsOnNoButtonClick )
		self.DialogButtonsYes.Bind( wx.EVT_BUTTON, self.DialogButtonsOnYesButtonClick )
	
	def __del__( self ):
		# Disconnect Events
		self.chkShowAgain.Unbind( wx.EVT_CHECKBOX, None )
		self.DialogButtonsNo.Unbind( wx.EVT_BUTTON, None )
		self.DialogButtonsYes.Unbind( wx.EVT_BUTTON, None )
	
	
	# Virtual event handlers, overide them in your derived class
	def chkShowAgainOnCheckBox( self, event ):
		event.Skip()
	
	def DialogButtonsOnNoButtonClick( self, event ):
		event.Skip()
	
	def DialogButtonsOnYesButtonClick( self, event ):
		event.Skip()
	

