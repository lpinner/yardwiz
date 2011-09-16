# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

from widgets import SortableListCtrl
from widgets import PropertyScrolledPanel
from widgets import AutoWidthListCtrl
import wx
import wx.combo
from widgets import DateTimeCtrl

###########################################################################
## Class GUI
###########################################################################

class GUI ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Yet Another Recording Downloader for the Wiz", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 300,300 ), wx.DefaultSize )
		self.SetFont( wx.Font( 12, 70, 90, 90, False, "Arial" ) )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer81 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.lblServerCombo = wx.StaticText( self, wx.ID_ANY, u"Wiz server:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblServerCombo.Wrap( -1 )
		self.lblServerCombo.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		self.lblServerCombo.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_CAPTIONTEXT ) )
		
		bSizer81.Add( self.lblServerCombo, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.LEFT|wx.TOP, 5 )
		
		self.cbxDevice = wx.combo.BitmapComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), "", wx.TE_PROCESS_ENTER ) 
		self.cbxDevice.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		self.cbxDevice.SetToolTipString( u"Enter your Beyonwiz device in one of the following formats:\n\n    - IP:port (e.g. 192.168.0.5:5678)\n    - IP (port will default to 49152)\n    - device name (e.g. LoungeWiz)\n\nIf you leave this field blank and click the Connect button, YARDWiz will try to discover your Beyonwiz." )
		self.cbxDevice.SetMinSize( wx.Size( 250,-1 ) )
		
		bSizer81.Add( self.cbxDevice, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		self.btnConnect = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 28,28 ), wx.BU_AUTODRAW )
		self.btnConnect.SetToolTipString( u"Connect to the WizPnP server\nand get recording information" )
		
		bSizer81.Add( self.btnConnect, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
		
		bSizer4.Add( bSizer81, 0, wx.EXPAND, 0 )
		
		self.lstPrograms = SortableListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.lstPrograms.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		self.mnuPrograms = wx.Menu()
		self.mitDownload = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Download now", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitDownload )
		self.mitDownload.Enable( False )
		
		self.mitQueue = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Queue for download", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitQueue )
		self.mitQueue.Enable( False )
		
		self.mitScheduler = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Schedule for dowload...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitScheduler )
		
		self.mnuPrograms.AppendSeparator()
		
		self.mitDelete = wx.MenuItem( self.mnuPrograms, wx.ID_ANY, u"Delete...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuPrograms.AppendItem( self.mitDelete )
		self.mitDelete.Enable( False )
		
		
		bSizer4.Add( self.lstPrograms, 2, wx.EXPAND, 5 )
		
		self.nbTabArea = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0|wx.NO_BORDER|wx.TAB_TRAVERSAL )
		self.nbTabArea.SetMinSize( wx.Size( -1,100 ) )
		self.nbTabArea.SetMaxSize( wx.Size( -1,300 ) )
		
		self.nbtabLog = wx.Panel( self.nbTabArea, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.txtLog = wx.TextCtrl( self.nbtabLog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER|wx.VSCROLL )
		self.txtLog.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer7.Add( self.txtLog, 1, wx.EXPAND, 0 )
		
		self.nbtabLog.SetSizer( bSizer7 )
		self.nbtabLog.Layout()
		bSizer7.Fit( self.nbtabLog )
		self.nbTabArea.AddPage( self.nbtabLog, u"Log", True )
		self.nbtabInfo = wx.Panel( self.nbTabArea, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.txtInfo = wx.TextCtrl( self.nbtabInfo, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER|wx.VSCROLL )
		self.txtInfo.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer8.Add( self.txtInfo, 1, wx.EXPAND, 0 )
		
		self.nbtabInfo.SetSizer( bSizer8 )
		self.nbtabInfo.Layout()
		bSizer8.Fit( self.nbtabInfo )
		self.nbTabArea.AddPage( self.nbtabInfo, u"Info", False )
		self.nbtabQueue = wx.Panel( self.nbTabArea, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.lstQueue = wx.ListCtrl( self.nbtabQueue, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT|wx.NO_BORDER )
		self.lstQueue.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
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
		
		bSizer4.Add( self.nbTabArea, 1, wx.EXPAND, 0 )
		
		self.bSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_panel4 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btnDownload = wx.BitmapButton( self.m_panel4, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnDownload.Enable( False )
		self.btnDownload.SetToolTipString( u"Download all in queue" )
		
		bSizer12.Add( self.btnDownload, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.LEFT|wx.TOP, 5 )
		
		self.btnClearQueue = wx.BitmapButton( self.m_panel4, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnClearQueue.Enable( False )
		self.btnClearQueue.SetToolTipString( u"Clear all in queue" )
		
		bSizer12.Add( self.btnClearQueue, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.RIGHT|wx.TOP, 5 )
		
		self.btnPlay = wx.BitmapButton( self.m_panel4, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnPlay.Enable( False )
		self.btnPlay.SetToolTipString( u"Resume download" )
		
		bSizer12.Add( self.btnPlay, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.LEFT|wx.TOP, 5 )
		
		self.btnPause = wx.BitmapButton( self.m_panel4, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnPause.Enable( False )
		self.btnPause.SetToolTipString( u"Pause download" )
		
		bSizer12.Add( self.btnPause, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.TOP, 5 )
		
		self.btnStop = wx.BitmapButton( self.m_panel4, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnStop.Enable( False )
		self.btnStop.SetToolTipString( u"Cancel download and\ndelete downloaded file" )
		
		bSizer12.Add( self.btnStop, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.RIGHT|wx.TOP, 5 )
		
		self.btnVLC = wx.BitmapButton( self.m_panel4, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		self.btnVLC.Enable( False )
		self.btnVLC.SetToolTipString( u"Play in VLC" )
		
		bSizer12.Add( self.btnVLC, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		
		self.m_panel4.SetSizer( bSizer12 )
		self.m_panel4.Layout()
		bSizer12.Fit( self.m_panel4 )
		self.bSizer.Add( self.m_panel4, 0, wx.EXPAND, 0 )
		
		self.m_panel5 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.bProgressSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.gaugeProgressBar = wx.Gauge( self.m_panel5, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( -1,-1 ), wx.GA_HORIZONTAL )
		self.gaugeProgressBar.SetMinSize( wx.Size( 150,21 ) )
		self.gaugeProgressBar.SetMaxSize( wx.Size( -1,30 ) )
		
		self.bProgressSizer.Add( self.gaugeProgressBar, 2, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.lblProgressText = wx.StaticText( self.m_panel5, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.lblProgressText.Wrap( -1 )
		self.lblProgressText.SetFont( wx.Font( 10, 70, 90, 90, False, "Tahoma" ) )
		self.lblProgressText.SetMinSize( wx.Size( 50,-1 ) )
		
		self.bProgressSizer.Add( self.lblProgressText, 3, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		self.bProgressSizer.AddSpacer( ( 5, 0), 1, wx.EXPAND, 5 )
		
		self.btnExit = wx.Button( self.m_panel5, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.bProgressSizer.Add( self.btnExit, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL|wx.RIGHT, 5 )
		
		self.m_panel5.SetSizer( self.bProgressSizer )
		self.m_panel5.Layout()
		self.bProgressSizer.Fit( self.m_panel5 )
		self.bSizer.Add( self.m_panel5, 1, wx.EXPAND, 5 )
		
		bSizer4.Add( self.bSizer, 0, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer4 )
		self.Layout()
		bSizer4.Fit( self )
		self.StatusBar = self.CreateStatusBar( 3, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.StatusBar.SetFont( wx.Font( 8, 70, 90, 90, False, wx.EmptyString ) )
		
		self.mbrMenu = wx.MenuBar( 0 )
		self.mnuFile = wx.Menu()
		self.mitCheck = wx.MenuItem( self.mnuFile, wx.ID_ANY, u"Check recordings", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuFile.AppendItem( self.mitCheck )
		self.mitCheck.Enable( False )
		
		self.mitExit = wx.MenuItem( self.mnuFile, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuFile.AppendItem( self.mitExit )
		
		self.mbrMenu.Append( self.mnuFile, u"File" ) 
		
		self.mnuTools = wx.Menu()
		self.mitScheduled = wx.MenuItem( self.mnuTools, wx.ID_ANY, u"Scheduled Downloads...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuTools.AppendItem( self.mitScheduled )
		
		self.mitPreferences = wx.MenuItem( self.mnuTools, wx.ID_ANY, u"Options...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuTools.AppendItem( self.mitPreferences )
		
		self.mbrMenu.Append( self.mnuTools, u"Tools" ) 
		
		self.mnuHelp = wx.Menu()
		self.mitHelp = wx.MenuItem( self.mnuHelp, wx.ID_ANY, u"Online Help...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuHelp.AppendItem( self.mitHelp )
		
		self.mitAbout = wx.MenuItem( self.mnuHelp, wx.ID_ANY, u"About...", wx.EmptyString, wx.ITEM_NORMAL )
		self.mnuHelp.AppendItem( self.mitAbout )
		
		self.mbrMenu.Append( self.mnuHelp, u"Help" ) 
		
		self.SetMenuBar( self.mbrMenu )
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_ACTIVATE, self.onActivate )
		self.Bind( wx.EVT_ACTIVATE_APP, self.onActivateApp )
		self.Bind( wx.EVT_CLOSE, self.onCloseApp )
		self.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateUI )
		self.cbxDevice.Bind( wx.EVT_COMBOBOX, self.cbxDevice_OnCombobox )
		self.cbxDevice.Bind( wx.EVT_KILL_FOCUS, self.cbxDevice_OnKillFocus )
		self.cbxDevice.Bind( wx.EVT_TEXT_ENTER, self.cbxDevice_OnTextEnter )
		self.btnConnect.Bind( wx.EVT_BUTTON, self.btnConnect_OnClick )
		self.lstPrograms.Bind( wx.EVT_LEFT_DCLICK, self.lstPrograms_OnDoubleClick )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_DESELECTED, self.lstPrograms_OnDeselect )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, self.lstPrograms_OnMiddleClick )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.lstPrograms_OnRightClick )
		self.lstPrograms.Bind( wx.EVT_LIST_ITEM_SELECTED, self.lstPrograms_OnSelect )
		self.Bind( wx.EVT_MENU, self.mitDownload_onSelect, id = self.mitDownload.GetId() )
		self.Bind( wx.EVT_MENU, self.mitQueue_onSelect, id = self.mitQueue.GetId() )
		self.Bind( wx.EVT_MENU, self.mitScheduler_OnSelect, id = self.mitScheduler.GetId() )
		self.Bind( wx.EVT_MENU, self.mitDelete_OnSelect, id = self.mitDelete.GetId() )
		self.lstQueue.Bind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, self.lstQueue_OnMiddleClick )
		self.lstQueue.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.lstQueue_OnRightClick )
		self.Bind( wx.EVT_MENU, self.mitRemove_OnSelect, id = self.mitRemove.GetId() )
		self.Bind( wx.EVT_MENU, self.mitClearQueue_OnSelect, id = self.mitClearQueue.GetId() )
		self.Bind( wx.EVT_MENU, self.mitDownloadAll_OnSelect, id = self.mitDownloadAll.GetId() )
		self.btnDownload.Bind( wx.EVT_BUTTON, self.btnDownload_OnClick )
		self.btnClearQueue.Bind( wx.EVT_BUTTON, self.btnClearQueue_OnClick )
		self.btnPlay.Bind( wx.EVT_BUTTON, self.btnPlay_OnClick )
		self.btnPause.Bind( wx.EVT_BUTTON, self.btnPause_OnClick )
		self.btnStop.Bind( wx.EVT_BUTTON, self.btnStop_OnClick )
		self.btnVLC.Bind( wx.EVT_BUTTON, self.btnVLC_OnClick )
		self.btnExit.Bind( wx.EVT_BUTTON, self.btnExit_onClick )
		self.Bind( wx.EVT_MENU, self.mitCheck_OnSelect, id = self.mitCheck.GetId() )
		self.Bind( wx.EVT_MENU, self.btnExit_onClick, id = self.mitExit.GetId() )
		self.Bind( wx.EVT_MENU, self.mitScheduled_OnSelect, id = self.mitScheduled.GetId() )
		self.Bind( wx.EVT_MENU, self.mitPreferences_OnSelect, id = self.mitPreferences.GetId() )
		self.Bind( wx.EVT_MENU, self.mitHelp_OnSelect, id = self.mitHelp.GetId() )
		self.Bind( wx.EVT_MENU, self.mitAbout_OnSelect, id = self.mitAbout.GetId() )
	
	def __del__( self ):
		# Disconnect Events
		self.Unbind( wx.EVT_ACTIVATE )
		self.Unbind( wx.EVT_ACTIVATE_APP )
		self.Unbind( wx.EVT_CLOSE )
		self.Unbind( wx.EVT_KEY_DOWN )
		self.Unbind( wx.EVT_SIZE )
		self.Unbind( wx.EVT_UPDATE_UI )
		self.cbxDevice.Unbind( wx.EVT_COMBOBOX, None )
		self.cbxDevice.Unbind( wx.EVT_KILL_FOCUS, None )
		self.cbxDevice.Unbind( wx.EVT_TEXT_ENTER, None )
		self.btnConnect.Unbind( wx.EVT_BUTTON, None )
		self.lstPrograms.Unbind( wx.EVT_LEFT_DCLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_DESELECTED, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_RIGHT_CLICK, None )
		self.lstPrograms.Unbind( wx.EVT_LIST_ITEM_SELECTED, None )
		self.Unbind( wx.EVT_MENU, id = self.mitDownload.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitQueue.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitScheduler.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitDelete.GetId() )
		self.lstQueue.Unbind( wx.EVT_LIST_ITEM_MIDDLE_CLICK, None )
		self.lstQueue.Unbind( wx.EVT_LIST_ITEM_RIGHT_CLICK, None )
		self.Unbind( wx.EVT_MENU, id = self.mitRemove.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitClearQueue.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitDownloadAll.GetId() )
		self.btnDownload.Unbind( wx.EVT_BUTTON, None )
		self.btnClearQueue.Unbind( wx.EVT_BUTTON, None )
		self.btnPlay.Unbind( wx.EVT_BUTTON, None )
		self.btnPause.Unbind( wx.EVT_BUTTON, None )
		self.btnStop.Unbind( wx.EVT_BUTTON, None )
		self.btnVLC.Unbind( wx.EVT_BUTTON, None )
		self.btnExit.Unbind( wx.EVT_BUTTON, None )
		self.Unbind( wx.EVT_MENU, id = self.mitCheck.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitExit.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitScheduled.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitPreferences.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitHelp.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.mitAbout.GetId() )
	
	
	# Virtual event handlers, overide them in your derived class
	def onActivate( self, event ):
		event.Skip()
	
	def onActivateApp( self, event ):
		event.Skip()
	
	def onCloseApp( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	def OnSize( self, event ):
		event.Skip()
	
	def OnUpdateUI( self, event ):
		event.Skip()
	
	def cbxDevice_OnCombobox( self, event ):
		event.Skip()
	
	def cbxDevice_OnKillFocus( self, event ):
		event.Skip()
	
	def cbxDevice_OnTextEnter( self, event ):
		event.Skip()
	
	def btnConnect_OnClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnDoubleClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnDeselect( self, event ):
		event.Skip()
	
	def lstPrograms_OnMiddleClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnRightClick( self, event ):
		event.Skip()
	
	def lstPrograms_OnSelect( self, event ):
		event.Skip()
	
	def mitDownload_onSelect( self, event ):
		event.Skip()
	
	def mitQueue_onSelect( self, event ):
		event.Skip()
	
	def mitScheduler_OnSelect( self, event ):
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
	
	def btnDownload_OnClick( self, event ):
		event.Skip()
	
	def btnClearQueue_OnClick( self, event ):
		event.Skip()
	
	def btnPlay_OnClick( self, event ):
		event.Skip()
	
	def btnPause_OnClick( self, event ):
		event.Skip()
	
	def btnStop_OnClick( self, event ):
		event.Skip()
	
	def btnVLC_OnClick( self, event ):
		event.Skip()
	
	def btnExit_onClick( self, event ):
		event.Skip()
	
	def mitCheck_OnSelect( self, event ):
		event.Skip()
	
	
	def mitScheduled_OnSelect( self, event ):
		event.Skip()
	
	def mitPreferences_OnSelect( self, event ):
		event.Skip()
	
	def mitHelp_OnSelect( self, event ):
		event.Skip()
	
	def mitAbout_OnSelect( self, event ):
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
	

###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About YARDWiz", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.Size( 400,250 ), wx.DefaultSize )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.bmpIcon = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 32,32 ), 0 )
		bSizer5.Add( self.bmpIcon, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.lblTitle = wx.StaticText( self, wx.ID_ANY, u"YARDWiz\nYet Another Recording Downloader for the Wiz", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.lblTitle.Wrap( 250 )
		self.lblTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer5.Add( self.lblTitle, 0, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		self.lblVersion = wx.StaticText( self, wx.ID_ANY, u"Version", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.lblVersion.Wrap( -1 )
		bSizer5.Add( self.lblVersion, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.lblCopyright = wx.StaticText( self, wx.ID_ANY, u"Copyright", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.lblCopyright.Wrap( -1 )
		self.lblCopyright.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 93, 91, False, wx.EmptyString ) )
		
		bSizer5.Add( self.lblCopyright, 0, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		self.lblDescription = wx.StaticText( self, wx.ID_ANY, u"YARDWiz is a simple crossplatform GUI front end for prl's getWizPnP program. ", wx.DefaultPosition, wx.Size( 250,-1 ), wx.ALIGN_CENTRE )
		self.lblDescription.Wrap( 250 )
		bSizer5.Add( self.lblDescription, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.urlWebpage = wx.HyperlinkCtrl( self, wx.ID_ANY, u"YARDWiz Website", u"http://code.google.com/p/yardwiz", wx.DefaultPosition, wx.DefaultSize, wx.HL_ALIGN_CENTRE|wx.HL_DEFAULT_STYLE )
		bSizer5.Add( self.urlWebpage, 0, wx.ALIGN_CENTER|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )
		
		self.btnLicense = wx.Button( self, wx.ID_ANY, u"License...", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER|wx.NO_BORDER )
		bSizer5.Add( self.btnLicense, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )
		
		self.SetSizer( bSizer5 )
		self.Layout()
		bSizer5.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.btnLicense.Bind( wx.EVT_BUTTON, self.btnLicense_OnClick )
	
	def __del__( self ):
		# Disconnect Events
		self.btnLicense.Unbind( wx.EVT_BUTTON, None )
	
	
	# Virtual event handlers, overide them in your derived class
	def btnLicense_OnClick( self, event ):
		event.Skip()
	

###########################################################################
## Class LicenseDialog
###########################################################################

class LicenseDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"License", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.txtLicense = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 450,300 ), wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH|wx.TE_WORDWRAP|wx.VSCROLL )
		bSizer6.Add( self.txtLicense, 0, wx.ALL|wx.EXPAND, 5 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
		m_sdbSizer2.Realize();
		bSizer6.Add( m_sdbSizer2, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		self.SetSizer( bSizer6 )
		self.Layout()
		bSizer6.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class SettingsDialog
###########################################################################

class SettingsDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.Size( 500,300 ), wx.DefaultSize )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.PropertyScrolledPanel = PropertyScrolledPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.PropertyScrolledPanel.SetScrollRate( 5, 5 )
		self.PropertyScrolledPanel.SetMinSize( wx.Size( 500,250 ) )
		
		sizer.Add( self.PropertyScrolledPanel, 1, wx.ALIGN_LEFT|wx.EXPAND, 0 )
		
		sdbSaveCancel = wx.StdDialogButtonSizer()
		self.sdbSaveCancelSave = wx.Button( self, wx.ID_SAVE )
		sdbSaveCancel.AddButton( self.sdbSaveCancelSave )
		self.sdbSaveCancelCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSaveCancel.AddButton( self.sdbSaveCancelCancel )
		sdbSaveCancel.Realize();
		sizer.Add( sdbSaveCancel, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )
		
		self.SetSizer( sizer )
		self.Layout()
		sizer.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.sdbSaveCancelCancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.sdbSaveCancelSave.Bind( wx.EVT_BUTTON, self.OnSave )
	
	def __del__( self ):
		# Disconnect Events
		self.sdbSaveCancelCancel.Unbind( wx.EVT_BUTTON, None )
		self.sdbSaveCancelSave.Unbind( wx.EVT_BUTTON, None )
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnSave( self, event ):
		event.Skip()
	

###########################################################################
## Class SchedulerDialog
###########################################################################

class SchedulerDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Download Schedule", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.Size( 300,-1 ), wx.DefaultSize )
		
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		self.dtcSchedule=DateTimeCtrl(self)
		bSizer9.Add( self.dtcSchedule, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.lstSchedule = AutoWidthListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT|wx.NO_BORDER )
		self.lstSchedule.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.lstSchedule.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		bSizer9.Add( self.lstSchedule, 1, wx.EXPAND, 5 )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel schedule", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnCancel.SetToolTipString( u"Cancel all scheduled downloads" )
		
		bSizer10.Add( self.btnCancel, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		bSizer10.AddSpacer( ( 100, 0), 1, wx.ALIGN_CENTER|wx.EXPAND, 5 )
		
		self.btnSchedule = wx.Button( self, wx.ID_ANY, u"Schedule", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnSchedule.SetToolTipString( u"Schedule new downloads or update existing schedule" )
		
		bSizer10.Add( self.btnSchedule, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.btnClose = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnClose.SetToolTipString( u"Close without making changes" )
		
		bSizer10.Add( self.btnClose, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		bSizer9.Add( bSizer10, 0, wx.ALIGN_CENTER|wx.EXPAND, 5 )
		
		self.SetSizer( bSizer9 )
		self.Layout()
		bSizer9.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.btnCancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.btnSchedule.Bind( wx.EVT_BUTTON, self.OnApply )
		self.btnClose.Bind( wx.EVT_BUTTON, self.OnClose )
	
	def __del__( self ):
		# Disconnect Events
		self.btnCancel.Unbind( wx.EVT_BUTTON, None )
		self.btnSchedule.Unbind( wx.EVT_BUTTON, None )
		self.btnClose.Unbind( wx.EVT_BUTTON, None )
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnApply( self, event ):
		event.Skip()
	
	def OnClose( self, event ):
		event.Skip()
	

