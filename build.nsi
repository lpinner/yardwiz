    ######################################################################
    #      NSIS Installation Script
    #
    #       This install script requires the following symbols to be
    #       defined via the /D commandline switch.
    #
    #       VERSION           N.N.N.N format version number
    #       DISPLAY_VERSION   Version text string
    #
    #       Example:
    #       makensis /DVERSION=1.2.0.123 /DDISPLAY_VERSION=1.2 RC1 yardwiz.nsi
    #
    ######################################################################
    !define /date YEAR "%Y"

    !define APP_NAME "YARDWiz"
    !define APP_DIR "dist"
    !define COMP_NAME "Luke Pinner"
    !define WEB_SITE "http://code.google.com/p/yardwiz"
    !define COPYRIGHT "${COMP_NAME} © ${YEAR}"
    !define DESCRIPTION "YARDWiz - Yet Another Recording Downloader for the Wiz"
    !define LICENSE_TXT "${APP_DIR}\LICENSE"
    ;!define MUI_WELCOMEFINISHPAGE_BITMAP "icon.bmp"
    !define REG_START_MENU "Start Menu Folder"
    !define MUI_ICON "${APP_DIR}\icons\icon.ico"

    var /GLOBAL StartMenuFolder
    var /GLOBAL ConfigFile

    ######################################################################

    SetCompressor LZMA
    Name "${APP_NAME}"
    Caption "${APP_NAME}"
    OutFile "dist\setup.exe"
    BrandingText "${APP_NAME}"
    XPStyle on

    ######################################################################

    !define INSTALL_PATH "Software\${APP_NAME}"
    !define UNINSTALL_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    !define MULTIUSER_EXECUTIONLEVEL Highest
    !define MULTIUSER_MUI
    !define MULTIUSER_INSTALLMODE_COMMANDLINE
    !define MULTIUSER_INSTALLMODE_INSTDIR "${APP_NAME}"
    !define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY "${UNINSTALL_PATH}"
    !define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "UninstallString"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "${INSTALL_PATH}"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "InstallLocation"
    !define REG_ROOT "SHCTX"

    !include "FileFunc.nsh"
    !include "MultiUser.nsh"
    !include "MUI.nsh"

    !define MUI_ABORTWARNING
    !define MUI_UNABORTWARNING

    !define MUI_STARTMENUPAGE_DEFAULTFOLDER "${APP_NAME}"
    !define MUI_STARTMENUPAGE_REGISTRY_ROOT "${REG_ROOT}"
    !define MUI_STARTMENUPAGE_REGISTRY_KEY "${UNINSTALL_PATH}"
    !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${REG_START_MENU}"
    ######################################################################

    !ifdef VERSION
        VIProductVersion  "${VERSION}"
        VIAddVersionKey "FileVersion"  "${VERSION}"
        VIAddVersionKey "ProductName"  "${APP_NAME}"
        VIAddVersionKey "CompanyName"  "${COMP_NAME}"
        VIAddVersionKey "LegalCopyright"  "${COPYRIGHT}"
        VIAddVersionKey "FileDescription"  "${DESCRIPTION}"
    !endif

    ######################################################################

    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_LICENSE "${LICENSE_TXT}"
    !insertmacro MULTIUSER_PAGE_INSTALLMODE
    !insertmacro MUI_PAGE_DIRECTORY

    ; Optional components
    !define MUI_PAGE_CUSTOMFUNCTION_PRE startmenu_pre
    !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
    !define MUI_PAGE_CUSTOMFUNCTION_PRE UninstallPrevious
    !insertmacro MUI_PAGE_INSTFILES
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !insertmacro MUI_PAGE_FINISH
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES
    !insertmacro MUI_UNPAGE_FINISH
    !insertmacro MUI_LANGUAGE "English"

    ######################################################################
    Section "Application" sec_main
        ;${INSTALL_TYPE}
        SetOverwrite ifnewer
        SetOutPath $INSTDIR
        File "${MUI_ICON}"
        File /r /x ${APP_NAME}*.zip "${APP_DIR}\*"
        WriteUninstaller "$INSTDIR\Uninstall.exe"
        WriteRegStr ${REG_ROOT} "${INSTALL_PATH}"  "InstallPath" "$INSTDIR"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayName" "${APP_NAME}"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "UninstallString" "$INSTDIR\uninstall.exe"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayIcon" "$INSTDIR\${APP_NAME}\lib\wm_icon.ico"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayVersion" "${DISPLAY_VERSION}"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "Publisher" "${COMP_NAME}"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "URLInfoAbout" "${WEB_SITE}"
    SectionEnd


    ######################################################################
    # Optional sections
    Section "Start Menu shortcuts" sec_startmenu
        !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
            CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk" "$INSTDIR\${APP_NAME}.exe" "" "$INSTDIR\icons\icon.ico" 0 SW_SHOWNORMAL
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"
            WriteIniStr "$INSTDIR\${APP_NAME} website.url" "InternetShortcut" "URL" "${WEB_SITE}"
            CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME} Website.lnk" "$INSTDIR\${APP_NAME} website.url" "" "$SYSDIR\SHELL32.dll" 13 SW_SHOWMAXIMIZED
        !insertmacro MUI_STARTMENU_WRITE_END
    SectionEnd

    ######################################################################
    ;Section decriptions
    !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
      !insertmacro MUI_DESCRIPTION_TEXT ${sec_startmenu} "Add ${APP_NAME} shortcuts to your Windows Start Menu"
    !insertmacro MUI_FUNCTION_DESCRIPTION_END

    ######################################################################

    Section Uninstall sec_uninstall
        ReadEnvStr $1 APPDIR
        RMDir /r "$1\${APP_NAME}"
        RMDir /r "$INSTDIR"
        !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
        RMDir /r "$SMPROGRAMS\$StartMenuFolder"
        DeleteRegKey ${REG_ROOT} "${UNINSTALL_PATH}"
        DeleteRegKey ${REG_ROOT} "${INSTALL_PATH}"
    SectionEnd

    ######################################################################

    ;Installer Functions
    Function .onInit
      !insertmacro MULTIUSER_INIT
    FunctionEnd

    ;Uninstaller Functions
    Function un.onInit
      !insertmacro MULTIUSER_UNINIT
    FunctionEnd

    Function UninstallPrevious 
        ; Check for uninstaller.
        ReadRegStr $R0 ${REG_ROOT} "${UNINSTALL_PATH}" "UninstallString"
        ${If} $R0 != ""
            ReadEnvStr $1 APPDATA
            IfFileExists "$1\${APP_NAME}\config.ini" existingconfig rununinstaller
            existingconfig:
                DetailPrint "Backing up user config file."
                GetTempFileName $ConfigFile
                ;CreateDirectory $ConfigFile
                CopyFiles /SILENT $1\${APP_NAME}\config.ini $ConfigFile
            rununinstaller:
                ; Run the uninstaller silently.
                DetailPrint "Removing previous installation."
                ExecWait '"$R0" /S _?=$INSTDIR'
                ${If} $ConfigFile != ""
                    CopyFiles /SILENT $ConfigFile $1\${APP_NAME}\config.ini
                    Delete $ConfigFile
                ${EndIf}
        ${EndIf}
    FunctionEnd

    Function startmenu_pre
        ${Unless} ${SectionIsSelected} ${sec_startmenu}
          Abort
        ${EndUnless}
    FunctionEnd

